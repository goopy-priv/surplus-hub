from typing import Optional, List
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime


class NotificationBase(BaseModel):
    type: str
    title: str
    body: str
    reference_type: Optional[str] = Field(None, alias="referenceType")
    reference_id: Optional[int] = Field(None, alias="referenceId")


class NotificationCreate(NotificationBase):
    user_id: int = Field(..., alias="userId")
    model_config = {"populate_by_name": True}


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    body: str
    reference_type: Optional[str] = Field(None, alias="referenceType")
    reference_id: Optional[int] = Field(None, alias="referenceId")
    is_read: bool = Field(False, alias="isRead")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class DeviceTokenCreate(BaseModel):
    # B4/B5: token, device_token, deviceToken 모두 허용
    token: str = Field(
        ...,
        validation_alias=AliasChoices("token", "device_token", "deviceToken"),
    )
    platform: str = "ios"

    model_config = {"populate_by_name": True}


class DeviceTokenResponse(BaseModel):
    id: int
    token: str
    platform: str
    is_active: bool = Field(True, alias="isActive")

    model_config = {"populate_by_name": True, "from_attributes": True}


class UnreadCountResponse(BaseModel):
    unread_count: int = Field(..., alias="unreadCount")
    
    model_config = {"populate_by_name": True}
