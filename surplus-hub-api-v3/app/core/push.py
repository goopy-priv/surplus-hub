"""
Push notification service using Firebase Cloud Messaging.

Note: Requires firebase-admin SDK and a service account key.
Set FIREBASE_CREDENTIALS_PATH in .env to the path of your service account JSON.
Falls back to a no-op mode if Firebase is not configured.
"""
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy initialization of Firebase
_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)
        if not cred_path:
            logger.warning("FIREBASE_CREDENTIALS_PATH not set. Push notifications disabled.")
            return None
        
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully.")
        return _firebase_app
    except Exception as e:
        logger.warning(f"Failed to initialize Firebase: {e}. Push notifications disabled.")
        return None


def send_push_notification(
    tokens: List[str],
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> dict:
    """
    Send push notification to multiple device tokens.
    Returns dict with success/failure counts.
    """
    if not tokens:
        return {"success": 0, "failure": 0}
    
    app = _get_firebase_app()
    if app is None:
        logger.debug(f"Push skipped (Firebase not configured): {title}")
        return {"success": 0, "failure": 0, "skipped": True}
    
    try:
        from firebase_admin import messaging
        
        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    )
                )
            ),
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default",
                ),
            ),
        )
        
        response = messaging.send_each_for_multicast(message)
        
        # Log failed tokens
        if response.failure_count > 0:
            for i, send_response in enumerate(response.responses):
                if not send_response.success:
                    logger.warning(
                        f"Failed to send to token {tokens[i][:20]}...: "
                        f"{send_response.exception}"
                    )
        
        return {
            "success": response.success_count,
            "failure": response.failure_count,
        }
    except Exception as e:
        logger.error(f"Push notification error: {e}")
        return {"success": 0, "failure": len(tokens), "error": str(e)}


def send_chat_notification(
    tokens: List[str],
    sender_name: str,
    message_preview: str,
    room_id: int,
):
    """Send chat message notification."""
    return send_push_notification(
        tokens=tokens,
        title=f"{sender_name}",
        body=message_preview[:100],
        data={
            "type": "CHAT",
            "roomId": str(room_id),
        },
    )
