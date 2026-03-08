from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SubscriptionResponse(BaseModel):
    id: int
    plan: str
    status: str
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class SubscriptionVerify(BaseModel):
    receipt_id: str = Field(..., alias="receiptId")
    platform: str = "ios"

    model_config = {"populate_by_name": True}
