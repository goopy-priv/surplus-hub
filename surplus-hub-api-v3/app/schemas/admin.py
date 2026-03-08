from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AdminRoleUpdate(BaseModel):
    admin_role: Optional[str] = Field(None, alias="adminRole")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AuditLogResponse(BaseModel):
    id: int
    admin_id: int = Field(..., alias="adminId")
    action: str
    target_type: Optional[str] = Field(None, alias="targetType")
    target_id: Optional[int] = Field(None, alias="targetId")
    details: Optional[str] = None
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AdminUserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    admin_role: Optional[str] = Field(None, alias="adminRole")
    is_active: bool = Field(..., alias="isActive")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AdminRoleListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
