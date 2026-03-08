from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate


class CRUDReview(CRUDBase[Review, ReviewCreate, dict]):
    def create_review(
        self,
        db: Session,
        *,
        reviewer_id: int,
        target_user_id: int,
        material_id: Optional[int],
        rating: int,
        content: Optional[str],
    ) -> Review:
        db_obj = Review(
            reviewer_id=reviewer_id,
            target_user_id=target_user_id,
            material_id=material_id,
            rating=rating,
            content=content,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update target user's manner temperature
        self._update_manner_temperature(db, target_user_id)

        return db_obj

    def get_user_reviews(
        self, db: Session, *, target_user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Review], int]:
        query = db.query(Review).filter(
            Review.target_user_id == target_user_id
        ).order_by(desc(Review.created_at))

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_review_count(self, db: Session, *, user_id: int) -> int:
        return db.query(Review).filter(
            Review.target_user_id == user_id
        ).count()

    def get_average_rating(self, db: Session, *, user_id: int) -> Optional[float]:
        result = db.query(func.avg(Review.rating)).filter(
            Review.target_user_id == user_id
        ).scalar()
        return float(result) if result else None

    def _update_manner_temperature(self, db: Session, user_id: int):
        """
        Calculate manner temperature based on review ratings.
        Base: 36.5, Scale: avg_rating maps to 0-100 range.
        1 star avg -> ~10, 3 star avg -> ~50, 5 star avg -> ~90
        """
        avg_rating = self.get_average_rating(db, user_id=user_id)
        if avg_rating is None:
            return

        # Map 1-5 rating to temperature (scale: ~10 to ~90)
        # Formula: (avg_rating - 1) / 4 * 80 + 10
        temperature = (avg_rating - 1) / 4 * 80 + 10

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.manner_temperature = round(temperature, 1)
            db.commit()


crud_review = CRUDReview(Review)
