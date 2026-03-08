from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.crud_category import crud_category
from app.schemas.category import Category as CategorySchema

router = APIRouter()


@router.get(
    "/",
    response_model=dict,
    summary="List Categories",
    description="Get all active material categories.",
)
def read_categories(
    db: Session = Depends(get_db),
) -> Any:
    categories = crud_category.get_active(db)

    # Seed if empty
    if not categories:
        categories = crud_category.seed_categories(db)

    return {
        "status": "success",
        "data": [CategorySchema.model_validate(c) for c in categories],
    }
