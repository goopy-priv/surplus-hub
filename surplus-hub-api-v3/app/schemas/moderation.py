from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    target_type: str = Field(..., alias="targetType")
    target_id: int = Field(..., alias="targetId")
    reason: str
    description: Optional[str] = None

    model_config = {"populate_by_name": True, "from_attributes": True}


class ReportResponse(BaseModel):
    id: int
    reporter_id: int = Field(..., alias="reporterId")
    target_type: str = Field(..., alias="targetType")
    target_id: int = Field(..., alias="targetId")
    reason: str
    description: Optional[str] = None
    status: str
    reviewed_by: Optional[int] = Field(None, alias="reviewedBy")
    reviewed_at: Optional[datetime] = Field(None, alias="reviewedAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class ReportUpdateStatus(BaseModel):
    status: str  # "reviewed", "resolved", "dismissed"

    model_config = {"populate_by_name": True, "from_attributes": True}


class SanctionCreate(BaseModel):
    sanction_type: str = Field(..., alias="sanctionType")  # "WARNING", "SUSPENSION", "BAN"
    reason: str
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class SanctionResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    admin_id: int = Field(..., alias="adminId")
    sanction_type: str = Field(..., alias="sanctionType")
    reason: str
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    is_active: bool = Field(..., alias="isActive")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AdminNoteCreate(BaseModel):
    content: str

    model_config = {"populate_by_name": True, "from_attributes": True}


class AdminNoteResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    admin_id: int = Field(..., alias="adminId")
    content: str
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class BannedWordCreate(BaseModel):
    word: str

    model_config = {"populate_by_name": True, "from_attributes": True}


class BannedWordResponse(BaseModel):
    id: int
    word: str
    created_by: Optional[int] = Field(None, alias="createdBy")
    is_active: bool = Field(..., alias="isActive")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class ModerationQueueResponse(BaseModel):
    id: int
    item_type: str = Field(..., alias="itemType")  # "report"
    target_type: str = Field(..., alias="targetType")
    target_id: int = Field(..., alias="targetId")
    reason: str
    status: str
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class BulkActionRequest(BaseModel):
    ids: List[int]
    action: str  # "dismiss", "resolve", "review"

    model_config = {"populate_by_name": True, "from_attributes": True}
