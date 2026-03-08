"""Tests for subscription endpoints: /api/v1/users/me/subscription*

Free-plan default and IAP receipt verification.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API_V1_STR = settings.API_V1_STR
SUB_PREFIX = f"{API_V1_STR}/users/me/subscription"

# HTTPBearer returns 401 in newer FastAPI/Starlette versions, 403 in older ones.
_NO_AUTH_CODES = (401, 403)


# ---------------------------------------------------------------------------
# Auth guards
# ---------------------------------------------------------------------------
class TestSubscriptionAuthGuards:
    """Subscription endpoints reject unauthenticated requests."""

    def test_get_subscription_requires_auth(self, client: TestClient):
        resp = client.get(SUB_PREFIX)
        assert resp.status_code in _NO_AUTH_CODES

    def test_verify_subscription_requires_auth(self, client: TestClient):
        resp = client.post(
            f"{SUB_PREFIX}/verify",
            json={"receiptId": "test-receipt-123", "platform": "ios"},
        )
        assert resp.status_code in _NO_AUTH_CODES


# ---------------------------------------------------------------------------
# GET /users/me/subscription
# ---------------------------------------------------------------------------
class TestGetSubscription:
    """New users should have the free plan by default."""

    def test_default_free_plan(self, client: TestClient, auth_headers):
        """Authenticated user with no subscription returns free plan."""
        resp = client.get(SUB_PREFIX, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"

        data = body["data"]
        assert data["plan"] == "free"
        assert data["status"] == "active"
        assert data["isPremium"] is False

    def test_free_plan_different_user(self, client: TestClient, auth_headers2):
        """Second user should also default to free plan."""
        resp = client.get(SUB_PREFIX, headers=auth_headers2)
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["plan"] == "free"
        assert body["data"]["isPremium"] is False


# ---------------------------------------------------------------------------
# POST /users/me/subscription/verify
# ---------------------------------------------------------------------------
class TestVerifySubscription:
    """IAP receipt verification endpoint."""

    def test_verify_receipt_ios(self, client: TestClient, auth_headers):
        """Verify an iOS IAP receipt."""
        resp = client.post(
            f"{SUB_PREFIX}/verify",
            json={"receiptId": "test-receipt-123", "platform": "ios"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["isPremium"] is True

    def test_verify_receipt_android(self, client: TestClient, auth_headers2):
        """Verify an Android IAP receipt."""
        resp = client.post(
            f"{SUB_PREFIX}/verify",
            json={"receiptId": "android-receipt-456", "platform": "android"},
            headers=auth_headers2,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["isPremium"] is True

    def test_subscription_updated_after_verify(
        self, client: TestClient, auth_headers
    ):
        """After verification, GET should reflect premium status."""
        # First verify
        verify_resp = client.post(
            f"{SUB_PREFIX}/verify",
            json={"receiptId": "verify-then-check", "platform": "ios"},
            headers=auth_headers,
        )
        assert verify_resp.status_code == 200

        # Then check subscription status
        get_resp = client.get(SUB_PREFIX, headers=auth_headers)
        assert get_resp.status_code == 200
        data = get_resp.json()["data"]
        assert data["isPremium"] is True
