from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate, dict]):
    def get_active(self, db: Session) -> List[Category]:
        return (
            db.query(Category)
            .filter(Category.is_active == True)
            .order_by(Category.display_order)
            .all()
        )

    def get_by_name(self, db: Session, *, name: str):
        return db.query(Category).filter(Category.name == name).first()

    def seed_categories(self, db: Session) -> List[Category]:
        """Seed default categories if none exist."""
        existing = db.query(Category).count()
        if existing > 0:
            return self.get_active(db)

        default_categories = [
            {"name": "철근", "icon": "construction", "display_order": 1},
            {"name": "목재", "icon": "forest", "display_order": 2},
            {"name": "시멘트", "icon": "foundation", "display_order": 3},
            {"name": "벽돌/블록", "icon": "grid_view", "display_order": 4},
            {"name": "타일", "icon": "dashboard", "display_order": 5},
            {"name": "배관자재", "icon": "plumbing", "display_order": 6},
            {"name": "전기자재", "icon": "electrical_services", "display_order": 7},
            {"name": "페인트", "icon": "format_paint", "display_order": 8},
            {"name": "단열재", "icon": "thermostat", "display_order": 9},
            {"name": "기타", "icon": "more_horiz", "display_order": 10},
        ]

        categories = []
        for cat_data in default_categories:
            cat = Category(**cat_data)
            db.add(cat)
            categories.append(cat)

        db.commit()
        for cat in categories:
            db.refresh(cat)

        return categories


crud_category = CRUDCategory(Category)
