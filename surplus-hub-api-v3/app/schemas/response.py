from typing import Optional, List, Any
from pydantic import BaseModel, Field

# Generic Response Wrapper
class ResponseMeta(BaseModel):
    totalCount: int
    page: int
    limit: int
    hasNextPage: bool
    totalPages: Optional[int] = None


class CursorMeta(BaseModel):
    """Cursor-based pagination metadata for mobile infinite scroll."""
    nextCursor: Optional[int] = None
    hasMore: bool = False
    limit: int = 20


class StandardResponse(BaseModel):
    status: str
    data: Any
    meta: Optional[ResponseMeta] = None
