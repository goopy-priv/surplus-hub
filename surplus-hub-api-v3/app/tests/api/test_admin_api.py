"""Tests for admin endpoints: /api/v1/admin/*

Admin review workflow: create material -> admin approves/rejects.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API_V1_STR = settings.API_V1_STR
ADMIN_PREFIX = f"{API_V1_STR}/admin"
MAT_PREFIX = f"{API_V1_STR}/materials"

# HTTPBearer returns 401 in newer FastAPI/Starlette versions, 403 in older ones.
_NO_AUTH_CODES = (401, 403)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _create_material_for_review(client: TestClient, auth_headers: dict) -> int:
    """Create a material (owned by test_user) and return its ID."""
    payload = {
        "title": "Admin Review Material",
        "description": "Needs admin review",
        "price": 30000,
        "location": {"address": "Seoul"},
        "quantity": 5,
        "quantityUnit": "ea",
        "tradeMethod": "DIRECT",
    }
    resp = client.post(f"{MAT_PREFIX}/", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Material creation failed: {resp.text}"
    return resp.json()["data"]["id"]


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------
class TestAdminAuthGuard:
    """Admin endpoints reject unauthenticated and non-admin users."""

    def test_review_requires_auth(self, client: TestClient):
        """No token -> 401/403."""
        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/1/review",
            json={"action": "approve", "note": "OK"},
        )
        assert resp.status_code in _NO_AUTH_CODES

    def test_review_non_superuser_rejected(
        self, client: TestClient, auth_headers
    ):
        """Regular user -> 400 (not enough privileges)."""
        material_id = _create_material_for_review(client, auth_headers)
        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/{material_id}/review",
            json={"action": "approve", "note": "Looks good"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "privileges" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Admin review actions
# ---------------------------------------------------------------------------
class TestAdminReviewMaterial:
    """PATCH /admin/materials/{id}/review -- approve and reject flows."""

    def test_approve_material(
        self, client: TestClient, auth_headers, superuser_headers
    ):
        """Admin approves a material -> status becomes ACTIVE."""
        material_id = _create_material_for_review(client, auth_headers)

        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/{material_id}/review",
            json={"action": "approve", "note": "Looks good"},
            headers=superuser_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "ACTIVE"

    def test_reject_material(
        self, client: TestClient, auth_headers, superuser_headers
    ):
        """Admin rejects a material -> status becomes HIDDEN."""
        material_id = _create_material_for_review(client, auth_headers)

        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/{material_id}/review",
            json={"action": "reject", "note": "Inappropriate content"},
            headers=superuser_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "HIDDEN"

    def test_invalid_action(
        self, client: TestClient, auth_headers, superuser_headers
    ):
        """An action other than approve/reject should return 400."""
        material_id = _create_material_for_review(client, auth_headers)

        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/{material_id}/review",
            json={"action": "suspend", "note": "Invalid action test"},
            headers=superuser_headers,
        )
        assert resp.status_code == 400
        assert "invalid action" in resp.json()["detail"].lower()

    def test_review_nonexistent_material(
        self, client: TestClient, superuser_headers
    ):
        """Reviewing a non-existent material should return 404."""
        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/99999/review",
            json={"action": "approve", "note": "Does not exist"},
            headers=superuser_headers,
        )
        assert resp.status_code == 404

    def test_approve_without_note(
        self, client: TestClient, auth_headers, superuser_headers
    ):
        """Approve with empty note (note is optional, defaults to empty)."""
        material_id = _create_material_for_review(client, auth_headers)

        resp = client.patch(
            f"{ADMIN_PREFIX}/materials/{material_id}/review",
            json={"action": "approve"},
            headers=superuser_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "ACTIVE"
