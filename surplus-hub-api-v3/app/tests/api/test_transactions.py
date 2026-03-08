"""Tests for transaction endpoints: /api/v1/transactions/*

Full transaction lifecycle: create material -> buyer creates transaction
-> seller confirms -> either party completes.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API_V1_STR = settings.API_V1_STR
TX_PREFIX = f"{API_V1_STR}/transactions"
MAT_PREFIX = f"{API_V1_STR}/materials"

# HTTPBearer returns 401 in newer FastAPI/Starlette versions, 403 in older ones.
_NO_AUTH_CODES = (401, 403)


# ---------------------------------------------------------------------------
# Helper: create a material owned by test_user (seller) via the API
# ---------------------------------------------------------------------------
def _create_material(client: TestClient, auth_headers: dict) -> int:
    """Create a material and return its ID."""
    payload = {
        "title": "TX Test Material",
        "description": "For transaction test",
        "price": 50000,
        "location": {"address": "Busan"},
        "quantity": 1,
        "quantityUnit": "ea",
        "tradeMethod": "DIRECT",
    }
    resp = client.post(f"{MAT_PREFIX}/", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Material creation failed: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    return data["data"]["id"]


# ---------------------------------------------------------------------------
# Auth guard tests (no token)
# ---------------------------------------------------------------------------
class TestTransactionAuthGuards:
    """All transaction endpoints must reject unauthenticated requests."""

    def test_create_requires_auth(self, client: TestClient):
        resp = client.post(f"{TX_PREFIX}/", json={"materialId": 1})
        assert resp.status_code in _NO_AUTH_CODES

    def test_list_requires_auth(self, client: TestClient):
        resp = client.get(f"{TX_PREFIX}/")
        assert resp.status_code in _NO_AUTH_CODES

    def test_get_detail_requires_auth(self, client: TestClient):
        resp = client.get(f"{TX_PREFIX}/1")
        assert resp.status_code in _NO_AUTH_CODES

    def test_confirm_requires_auth(self, client: TestClient):
        resp = client.patch(f"{TX_PREFIX}/1/confirm")
        assert resp.status_code in _NO_AUTH_CODES

    def test_complete_requires_auth(self, client: TestClient):
        resp = client.patch(f"{TX_PREFIX}/1/complete")
        assert resp.status_code in _NO_AUTH_CODES


# ---------------------------------------------------------------------------
# Validation & business-rule tests
# ---------------------------------------------------------------------------
class TestCreateTransactionValidation:
    """POST /transactions/ edge cases."""

    def test_material_not_found(self, client: TestClient, auth_headers2):
        """Buying a non-existent material should return 404."""
        resp = client.post(
            f"{TX_PREFIX}/",
            json={"materialId": 99999},
            headers=auth_headers2,
        )
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_cannot_buy_own_material(self, client: TestClient, auth_headers):
        """Seller cannot buy their own material."""
        material_id = _create_material(client, auth_headers)
        resp = client.post(
            f"{TX_PREFIX}/",
            json={"materialId": material_id},
            headers=auth_headers,  # same user who created the material
        )
        assert resp.status_code == 400
        assert "own material" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Full lifecycle test
# ---------------------------------------------------------------------------
class TestTransactionLifecycle:
    """
    End-to-end transaction flow:
    1. user1 (seller) creates a material
    2. user2 (buyer) creates a transaction
    3. user1 (seller) confirms
    4. user2 (buyer) completes
    """

    def test_full_lifecycle(
        self,
        client: TestClient,
        auth_headers,
        auth_headers2,
        test_user,
        test_user2,
    ):
        # -- Step 1: Seller creates a material --
        material_id = _create_material(client, auth_headers)

        # -- Step 2: Buyer creates a transaction --
        create_resp = client.post(
            f"{TX_PREFIX}/",
            json={"materialId": material_id, "note": "I need this urgently"},
            headers=auth_headers2,
        )
        assert create_resp.status_code == 200
        tx_data = create_resp.json()
        assert tx_data["status"] == "success"
        tx = tx_data["data"]
        tx_id = tx["id"]

        assert tx["materialId"] == material_id
        assert tx["buyerId"] == test_user2.id
        assert tx["sellerId"] == test_user.id
        assert tx["status"] == "PENDING"
        assert tx["note"] == "I need this urgently"
        assert tx["price"] == 50000

        # -- Step 3: List transactions (buyer sees it) --
        list_resp = client.get(f"{TX_PREFIX}/", headers=auth_headers2)
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["status"] == "success"
        assert isinstance(list_data["data"], list)
        tx_ids = [t["id"] for t in list_data["data"]]
        assert tx_id in tx_ids

        # -- Step 4: Get transaction detail (buyer) --
        detail_resp = client.get(
            f"{TX_PREFIX}/{tx_id}", headers=auth_headers2
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["data"]["id"] == tx_id

        # -- Step 5: Get transaction detail (seller) --
        detail_resp_seller = client.get(
            f"{TX_PREFIX}/{tx_id}", headers=auth_headers
        )
        assert detail_resp_seller.status_code == 200

        # -- Step 6: Buyer cannot confirm (only seller can) --
        buyer_confirm = client.patch(
            f"{TX_PREFIX}/{tx_id}/confirm", headers=auth_headers2
        )
        assert buyer_confirm.status_code == 403
        assert "seller" in buyer_confirm.json()["detail"].lower()

        # -- Step 7: Seller confirms --
        confirm_resp = client.patch(
            f"{TX_PREFIX}/{tx_id}/confirm", headers=auth_headers
        )
        assert confirm_resp.status_code == 200
        assert confirm_resp.json()["data"]["status"] == "CONFIRMED"

        # -- Step 8: Cannot confirm again (not pending) --
        re_confirm = client.patch(
            f"{TX_PREFIX}/{tx_id}/confirm", headers=auth_headers
        )
        assert re_confirm.status_code == 400
        assert "not pending" in re_confirm.json()["detail"].lower()

        # -- Step 9: Complete (buyer) --
        complete_resp = client.patch(
            f"{TX_PREFIX}/{tx_id}/complete", headers=auth_headers2
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["data"]["status"] == "COMPLETED"

    def test_complete_before_confirm_fails(
        self, client: TestClient, auth_headers, auth_headers2
    ):
        """Cannot complete a transaction that has not been confirmed yet."""
        material_id = _create_material(client, auth_headers)

        # Buyer creates transaction
        create_resp = client.post(
            f"{TX_PREFIX}/",
            json={"materialId": material_id},
            headers=auth_headers2,
        )
        assert create_resp.status_code == 200
        tx_id = create_resp.json()["data"]["id"]

        # Try to complete without confirming first
        complete_resp = client.patch(
            f"{TX_PREFIX}/{tx_id}/complete", headers=auth_headers2
        )
        assert complete_resp.status_code == 400
        assert "confirmed" in complete_resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------
class TestTransactionAccessControl:
    """Only transaction participants should access the detail."""

    def test_non_participant_cannot_view(
        self,
        client: TestClient,
        auth_headers,
        auth_headers2,
        superuser_headers,
    ):
        """A third user (superuser here) should not see another pair's transaction."""
        material_id = _create_material(client, auth_headers)

        create_resp = client.post(
            f"{TX_PREFIX}/",
            json={"materialId": material_id},
            headers=auth_headers2,
        )
        assert create_resp.status_code == 200
        tx_id = create_resp.json()["data"]["id"]

        # Superuser is not a participant
        detail_resp = client.get(
            f"{TX_PREFIX}/{tx_id}", headers=superuser_headers
        )
        assert detail_resp.status_code == 403

    def test_transaction_not_found(self, client: TestClient, auth_headers):
        resp = client.get(f"{TX_PREFIX}/99999", headers=auth_headers)
        assert resp.status_code == 404
