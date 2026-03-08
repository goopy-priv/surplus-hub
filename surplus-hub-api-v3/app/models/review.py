from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)

    rating = Column(Integer, nullable=False)  # 1-5
    content = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reviewer = relationship("User", foreign_keys=[reviewer_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    material = relationship("Material")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
        UniqueConstraint("reviewer_id", "material_id", name="uq_review_per_material"),
    )
