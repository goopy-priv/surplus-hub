from typing import Optional
from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    total_users: int = Field(..., alias="totalUsers")
    active_users: int = Field(..., alias="activeUsers")
    new_users_today: int = Field(..., alias="newUsersToday")
    total_materials: int = Field(..., alias="totalMaterials")
    active_materials: int = Field(..., alias="activeMaterials")
    total_transactions: int = Field(..., alias="totalTransactions")
    completed_transactions: int = Field(..., alias="completedTransactions")
    pending_reports: int = Field(..., alias="pendingReports")

    model_config = {"populate_by_name": True, "from_attributes": True}


class StatsDataPoint(BaseModel):
    date: str
    count: int

    model_config = {"populate_by_name": True, "from_attributes": True}


class StatsResponse(BaseModel):
    data: list[StatsDataPoint]
    period: str  # "day", "week", "month"

    model_config = {"populate_by_name": True, "from_attributes": True}


class ExportRequest(BaseModel):
    export_type: str = Field(..., alias="exportType")  # "users", "materials", "transactions"
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")

    model_config = {"populate_by_name": True, "from_attributes": True}
