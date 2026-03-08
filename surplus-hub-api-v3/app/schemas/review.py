from typing import Optional
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime


class ReviewCreate(BaseModel):
    # B6: targetUserId, target_user_id, reviewee_id 모두 허용
    target_user_id: int = Field(
        ...,
        validation_alias=AliasChoices("targetUserId", "target_user_id", "reviewee_id"),
    )
    material_id: Optional[int] = Field(None, alias="materialId")
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None

    model_config = {"populate_by_name": True}


class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int = Field(..., alias="reviewerId")
    reviewer_name: Optional[str] = Field(None, alias="reviewerName")
    target_user_id: int = Field(..., alias="targetUserId")
    material_id: Optional[int] = Field(None, alias="materialId")
    rating: int
    content: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}
