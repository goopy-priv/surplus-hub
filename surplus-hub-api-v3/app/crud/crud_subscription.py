from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionResponse


class CRUDSubscription(CRUDBase[Subscription, SubscriptionResponse, dict]):
    def get_active_subscription(
        self, db: Session, *, user_id: int
    ) -> Optional[Subscription]:
        now = datetime.now(timezone.utc)
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        ).first()

    def is_premium(self, db: Session, *, user_id: int) -> bool:
        sub = self.get_active_subscription(db, user_id=user_id)
        if not sub:
            return False
        if sub.plan == "free":
            return False
        if sub.expires_at and sub.expires_at < datetime.now(timezone.utc):
            return False
        return True

    def verify_receipt(
        self,
        db: Session,
        *,
        user_id: int,
        receipt_id: str,
        platform: str,
    ) -> Subscription:
        """
        Stub for IAP receipt verification.
        In production, this would verify with Apple/Google servers.
        """
        # For now, create/update a subscription record
        existing = self.get_active_subscription(db, user_id=user_id)
        if existing:
            existing.iap_receipt_id = receipt_id
            existing.plan = "premium"
            existing.status = "active"
            db.commit()
            db.refresh(existing)
            return existing

        db_obj = Subscription(
            user_id=user_id,
            plan="premium",
            status="active",
            iap_receipt_id=receipt_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_subscription = CRUDSubscription(Subscription)
