from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.event import Event
from app.schemas.event import EventResponse


class CRUDEvent(CRUDBase[Event, EventResponse, dict]):
    def get_active_events(
        self, db: Session, *, skip: int = 0, limit: int = 20
    ) -> tuple[List[Event], int]:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        query = db.query(Event).filter(
            Event.is_active == True,
        ).order_by(desc(Event.created_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total


crud_event = CRUDEvent(Event)
