import json

from fastapi.testclient import TestClient
from app.core.config import settings

PREFIX = f"{settings.API_V1_STR}/notifications"


# ---------------------------------------------------------------------------
# Auth requirement checks (all endpoints require authentication)
# ---------------------------------------------------------------------------
class TestNotificationAuthRequired:
    """Verify that all notification endpoints reject unauthenticated requests."""

    def test_list_notifications_requires_auth(self, client: TestClient):
        response = client.get(f"{PREFIX}/")
        assert response.status_code == 401

    def test_register_device_token_requires_auth(self, client: TestClient):
        response = client.post(
            f"{PREFIX}/device-token",
            json={"token": "fcm_test_token_123", "platform": "ios"},
        )
        assert response.status_code == 401

    def test_unregister_device_token_requires_auth(self, client: TestClient):
        response = client.request(
            "DELETE",
            f"{PREFIX}/device-token",
            json={"token": "fcm_test_token_123", "platform": "ios"},
        )
        assert response.status_code == 401

    def test_mark_read_requires_auth(self, client: TestClient):
        response = client.patch(f"{PREFIX}/1/read")
        assert response.status_code == 401

    def test_mark_all_read_requires_auth(self, client: TestClient):
        response = client.patch(f"{PREFIX}/read-all")
        assert response.status_code == 401

    def test_unread_count_requires_auth(self, client: TestClient):
        response = client.get(f"{PREFIX}/unread-count")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Device token registration and deactivation
# ---------------------------------------------------------------------------
class TestDeviceToken:
    """Test FCM device token registration and deactivation flow."""

    def test_register_device_token(self, client: TestClient, auth_headers: dict):
        response = client.post(
            f"{PREFIX}/device-token",
            json={"token": "fcm_test_token_123", "platform": "ios"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["token"] == "fcm_test_token_123"
        assert body["data"]["platform"] == "ios"
        assert body["data"]["isActive"] is True

    def test_register_device_token_android(self, client: TestClient, auth_headers: dict):
        response = client.post(
            f"{PREFIX}/device-token",
            json={"token": "fcm_android_token_456", "platform": "android"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["platform"] == "android"

    def test_register_duplicate_token_reactivates(
        self, client: TestClient, auth_headers: dict
    ):
        """Registering the same token again should reactivate it."""
        response = client.post(
            f"{PREFIX}/device-token",
            json={"token": "fcm_test_token_123", "platform": "ios"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["isActive"] is True

    def test_deactivate_device_token(self, client: TestClient, auth_headers: dict):
        response = client.request(
            "DELETE",
            f"{PREFIX}/device-token",
            json={"token": "fcm_test_token_123", "platform": "ios"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"

    def test_deactivate_nonexistent_token(self, client: TestClient, auth_headers: dict):
        response = client.request(
            "DELETE",
            f"{PREFIX}/device-token",
            json={"token": "nonexistent_token_xyz", "platform": "ios"},
            headers=auth_headers,
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Notification listing, read status, and unread count
# ---------------------------------------------------------------------------
class TestNotificationCRUD:
    """Test notification listing, marking as read, and unread counts."""

    def test_list_notifications_empty(self, client: TestClient, auth_headers: dict):
        response = client.get(f"{PREFIX}/", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert isinstance(body["data"], list)
        assert "meta" in body
        assert body["meta"]["totalCount"] >= 0

    def test_unread_count_initial(self, client: TestClient, auth_headers: dict):
        response = client.get(f"{PREFIX}/unread-count", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert "unreadCount" in body["data"]
        assert isinstance(body["data"]["unreadCount"], int)

    def test_mark_notification_read_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        response = client.patch(f"{PREFIX}/99999/read", headers=auth_headers)
        assert response.status_code == 404

    def test_mark_all_read(self, client: TestClient, auth_headers: dict):
        response = client.patch(f"{PREFIX}/read-all", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"

    def test_list_notifications_with_pagination(
        self, client: TestClient, auth_headers: dict
    ):
        response = client.get(
            f"{PREFIX}/", headers=auth_headers, params={"page": 1, "limit": 5}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["meta"]["page"] == 1
        assert body["meta"]["limit"] == 5
