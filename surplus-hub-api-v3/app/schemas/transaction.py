from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TransactionCreate(BaseModel):
    material_id: int = Field(..., alias="materialId")
    note: Optional[str] = None

    model_config = {"populate_by_name": True}


class TransactionResponse(BaseModel):
    id: int
    material_id: int = Field(..., alias="materialId")
    material_title: Optional[str] = Field(None, alias="materialTitle")
    seller_id: int = Field(..., alias="sellerId")
    seller_name: Optional[str] = Field(None, alias="sellerName")
    buyer_id: int = Field(..., alias="buyerId")
    buyer_name: Optional[str] = Field(None, alias="buyerName")
    price: int
    status: str
    note: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
    confirmed_at: Optional[datetime] = Field(None, alias="confirmedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}
