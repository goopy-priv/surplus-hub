from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_notification import crud_notification, crud_device_token
from app.models.user import User
from app.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter()


@router.post(
    "/device-token",
    summary="Register Device Token",
    description="Register an FCM device token for push notifications.",
)
def register_device_token(
    token_in: DeviceTokenCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    device_token = crud_device_token.register_token(
        db, user_id=current_user.id, token=token_in.token, platform=token_in.platform
    )
    return {
        "status": "success",
        "data": DeviceTokenResponse.model_validate(device_token),
    }


@router.delete(
    "/device-token",
    summary="Unregister Device Token",
    description="Deactivate an FCM device token.",
)
def unregister_device_token(
    token_in: DeviceTokenCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    success = crud_device_token.deactivate_token(
        db, token=token_in.token, user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Device token not found")
    return {"status": "success", "data": {"message": "Device token deactivated"}}


@router.get(
    "/",
    summary="List Notifications",
    description="Get the current user's notifications. Supports both offset and cursor pagination.",
)
def list_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    page: int = 1,
    limit: int = 20,
    cursor: Optional[int] = None,
) -> Any:
    # Cursor-based pagination
    if cursor is not None or page == 0:
        items, next_cursor = crud_notification.get_user_notifications_cursor(
            db, user_id=current_user.id, cursor=cursor, limit=limit
        )
        return {
            "status": "success",
            "data": [NotificationResponse.model_validate(n) for n in items],
            "meta": {
                "nextCursor": next_cursor,
                "hasMore": next_cursor is not None,
                "limit": limit,
            },
        }

    # Offset-based pagination
    skip = (page - 1) * limit
    notifications, total = crud_notification.get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "status": "success",
        "data": [NotificationResponse.model_validate(n) for n in notifications],
        "meta": {
            "totalCount": total,
            "page": page,
            "limit": limit,
            "hasNextPage": page < total_pages,
            "totalPages": total_pages,
        },
    }


@router.patch(
    "/{notification_id}/read",
    summary="Mark Notification as Read",
)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    notification = crud_notification.mark_as_read(
        db, notification_id=notification_id, user_id=current_user.id
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {
        "status": "success",
        "data": NotificationResponse.model_validate(notification),
    }


@router.patch(
    "/read-all",
    summary="Mark All Notifications as Read",
)
def mark_all_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    count = crud_notification.mark_all_as_read(db, user_id=current_user.id)
    return {
        "status": "success",
        "data": {"message": f"{count} notifications marked as read"},
    }


@router.get(
    "/unread-count",
    summary="Get Unread Count",
)
def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    count = crud_notification.get_unread_count(db, user_id=current_user.id)
    return {
        "status": "success",
        "data": {"unreadCount": count},
    }
