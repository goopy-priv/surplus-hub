from typing import Generator, Optional
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

security_scheme = HTTPBearer()

CLERK_JWKS_URL = settings.CLERK_JWKS_URL or "https://adapted-perch-14.clerk.accounts.dev/.well-known/jwks.json"
_jwks_client = PyJWKClient(CLERK_JWKS_URL)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    try:
        # 1. 먼저 Clerk 토큰 검증 시도 (RS256)
        signing_key = _jwks_client.get_signing_key_from_jwt(token.credentials)
        
        payload = jwt.decode(
            token.credentials,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False} # audience 검증은 필요시 활성화
        )
        
        # Clerk payload에서 user_id 추출 (sub)
        user_id = payload.get("sub")
        email = payload.get("email") # Clerk 설정에 따라 다를 수 있음
        
        if not user_id:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials (no sub)",
            )

        # 2. DB에서 사용자 조회
        # 먼저 clerk_id로 조회 시도
        user = db.query(User).filter(User.clerk_id == user_id).first()
        
        # 없으면 이메일로 조회 시도 (기존 가입자 연동)
        if not user:
            user = db.query(User).filter(User.email == payload.get("email", "")).first()
            # 이메일로 찾았다면 clerk_id 업데이트
            if user:
                user.clerk_id = user_id
                db.commit()
                db.refresh(user)
        
        if not user:
            # 사용자가 없으면 자동 생성 (Auto-SignUp)
            user = User(
                email=payload.get("email", f"{user_id}@clerk.user"),
                clerk_id=user_id,
                hashed_password=None, # Clerk 로그인이므로 비밀번호 없음
                name=payload.get("name", "Clerk User"),
                profile_image_url=payload.get("picture", None),
                is_active=True,
                is_superuser=False,
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return user

    except (jwt.PyJWTError, Exception) as e:
        # Clerk 검증 실패 시, 기존 로컬 검증 시도 (하위 호환성)
        try:
            payload = jwt.decode(
                token.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            # Reject refresh tokens used as access tokens
            token_type = payload.get("type")
            if token_type == "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token cannot be used for authentication",
                )
            user_id: str = payload.get("sub")
            if user_id is None:
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except Exception:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
            )

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_admin_user(min_role: str = "MODERATOR"):
    """Factory function that returns a dependency checking admin role."""
    from app.core.permissions import ROLE_HIERARCHY

    def _dep(current_user: User = Depends(get_current_active_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.admin_role or "", 0)
        required_level = ROLE_HIERARCHY.get(min_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient admin privileges",
            )
        return current_user

    return _dep
