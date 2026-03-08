from typing import Optional, List
from pydantic import BaseModel
from app.schemas.response import StandardResponse
from app.schemas.material import Material as MaterialSchema

class MaterialListResponse(StandardResponse):
    data: List[MaterialSchema]
