from pydantic import BaseModel, Field, ConfigDict


class LikeStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_liked: bool = Field(..., alias="isLiked")
    likes_count: int = Field(..., alias="likesCount")
