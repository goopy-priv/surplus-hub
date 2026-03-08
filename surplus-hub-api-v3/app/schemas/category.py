from typing import Optional
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None
    display_order: int = Field(0, alias="displayOrder")
    is_active: bool = Field(True, alias="isActive")

    model_config = {"populate_by_name": True}


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    model_config = {"populate_by_name": True, "from_attributes": True}
