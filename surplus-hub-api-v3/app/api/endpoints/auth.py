from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.rate_limit import limiter
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1)


def _build_token_pair(user_id: int) -> dict:
    """Generate access + refresh token pair."""
    access_token = security.create_access_token(subject=user_id)
    refresh_token = security.create_refresh_token(subject=user_id)
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer",
    }


@router.post("/register", summary="Register")
@limiter.limit("10/minute")
def register(
    request: Request,
    body: RegisterRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Email + password registration. No phone verification required."""
    existing = crud_user.get_by_email(db, email=body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud_user.create(
        db, obj_in=UserCreate(email=body.email, password=body.password, name=body.name)
    )
    tokens = _build_token_pair(user.id)
    return {
        "status": "success",
        "data": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            **tokens,
        },
    }


@router.post("/login/access-token")
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    tokens = _build_token_pair(user.id)
    return {
        "status": "success",
        "data": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            **tokens,
        },
    }


@router.post("/refresh-token", summary="Refresh Access Token")
@limiter.limit("10/minute")
def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get a fresh access + refresh token pair using a valid refresh token.
    No Bearer header required — only the refresh token in the request body.
    """
    user_id = security.decode_refresh_token(body.refresh_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = crud_user.get(db, id=int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    tokens = _build_token_pair(user.id)
    return {
        "status": "success",
        "data": tokens,
    }
