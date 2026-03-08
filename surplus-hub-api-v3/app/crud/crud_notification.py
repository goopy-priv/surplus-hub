from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.notification import Notification, DeviceToken
from app.schemas.notification import NotificationCreate, DeviceTokenCreate


class CRUDNotification(CRUDBase[Notification, NotificationCreate, dict]):
    def get_user_notifications(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Notification], int]:
        query = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(desc(Notification.created_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_user_notifications_cursor(
        self, db: Session, *, user_id: int, cursor: Optional[int] = None, limit: int = 20
    ) -> tuple[List[Notification], Optional[int]]:
        """Cursor-based pagination for notifications."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if cursor:
            query = query.filter(Notification.id < cursor)

        query = query.order_by(desc(Notification.id))
        items = query.limit(limit + 1).all()

        next_cursor = None
        if len(items) > limit:
            items = items[:limit]
            next_cursor = items[-1].id

        return items, next_cursor

    def create_notification(
        self,
        db: Session,
        *,
        user_id: int,
        type: str,
        title: str,
        body: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
    ) -> Notification:
        db_obj = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_as_read(self, db: Session, *, notification_id: int, user_id: int) -> Optional[Notification]:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()
        if notif:
            notif.is_read = True
            db.commit()
            db.refresh(notif)
        return notif

    def mark_all_as_read(self, db: Session, *, user_id: int) -> int:
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).update({"is_read": True})
        db.commit()
        return count

    def get_unread_count(self, db: Session, *, user_id: int) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).count()


class CRUDDeviceToken(CRUDBase[DeviceToken, DeviceTokenCreate, dict]):
    def register_token(
        self, db: Session, *, user_id: int, token: str, platform: str = "ios"
    ) -> DeviceToken:
        # Check if token already exists
        existing = db.query(DeviceToken).filter(
            DeviceToken.token == token
        ).first()
        
        if existing:
            # Update ownership and reactivate
            existing.user_id = user_id
            existing.platform = platform
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
        
        db_obj = DeviceToken(
            user_id=user_id,
            token=token,
            platform=platform,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate_token(self, db: Session, *, token: str, user_id: int) -> bool:
        db_token = db.query(DeviceToken).filter(
            DeviceToken.token == token,
            DeviceToken.user_id == user_id,
        ).first()
        if db_token:
            db_token.is_active = False
            db.commit()
            return True
        return False

    def get_user_tokens(self, db: Session, *, user_id: int) -> List[DeviceToken]:
        return db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.is_active == True,
        ).all()


crud_notification = CRUDNotification(Notification)
crud_device_token = CRUDDeviceToken(DeviceToken)
