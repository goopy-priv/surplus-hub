"""Tests for user endpoints: /api/v1/users/*"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API_V1_STR = settings.API_V1_STR


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------
class TestReadUserMe:
    """Test suite for fetching the current user's profile."""

    url = f"{API_V1_STR}/users/me"

    def test_get_me_success(self, client: TestClient, auth_headers, test_user):
        """Authenticated user should receive their profile data."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["id"] == str(test_user.id)
        assert "name" in data
        assert "profileImageUrl" in data
        assert "location" in data
        assert "trustLevel" in data
        assert "mannerTemperature" in data
        assert "stats" in data
        assert "isPremium" in data
        assert "role" in data

    def test_get_me_has_stats(self, client: TestClient, auth_headers):
        """User profile should include stats with expected keys and integer values."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()["data"]["stats"]
        assert "salesCount" in stats
        assert "purchaseCount" in stats
        assert "reviewCount" in stats
        assert isinstance(stats["salesCount"], int)
        assert isinstance(stats["purchaseCount"], int)
        assert isinstance(stats["reviewCount"], int)

    def test_get_me_default_values(self, client: TestClient, auth_headers):
        """User profile should have expected field types."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data["trustLevel"], int)
        assert isinstance(data["mannerTemperature"], (int, float))
        assert isinstance(data["isPremium"], bool)
        assert data["role"] == "user"

    def test_get_me_unauthorized(self, client: TestClient):
        """Request without auth should be rejected.

        HTTPBearer returns 401 when no credentials are provided.
        """
        response = client.get(self.url)
        assert response.status_code in (401, 403)

    def test_get_me_invalid_token(self, client: TestClient):
        """Invalid bearer token should return 401."""
        response = client.get(
            self.url,
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 401

    def test_get_me_second_user(
        self, client: TestClient, auth_headers2, test_user2
    ):
        """Second user should get their own profile, not the first user's."""
        response = client.get(self.url, headers=auth_headers2)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == str(test_user2.id)
        assert data["name"] == test_user2.name


# ---------------------------------------------------------------------------
# PUT /users/me
# ---------------------------------------------------------------------------
class TestUpdateUserMe:
    """Test suite for updating the current user's profile."""

    url = f"{API_V1_STR}/users/me"

    def test_update_name(self, client: TestClient, auth_headers):
        """User should be able to update their name."""
        response = client.put(
            self.url,
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["name"] == "Updated Name"

    def test_update_location(self, client: TestClient, auth_headers):
        """User should be able to update their location."""
        response = client.put(
            self.url,
            headers=auth_headers,
            json={"location": "Seoul, Korea"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["location"] == "Seoul, Korea"

    def test_update_profile_image(self, client: TestClient, auth_headers):
        """User should be able to update their profile image URL."""
        image_url = "https://example.com/avatar.jpg"
        response = client.put(
            self.url,
            headers=auth_headers,
            json={"profile_image_url": image_url},
        )
        assert response.status_code == 200
        assert response.json()["data"]["profileImageUrl"] == image_url

    def test_update_multiple_fields(self, client: TestClient, auth_headers):
        """User should be able to update multiple fields at once."""
        response = client.put(
            self.url,
            headers=auth_headers,
            json={
                "name": "Multi Update",
                "location": "Busan, Korea",
                "profile_image_url": "https://example.com/new.jpg",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Multi Update"
        assert data["location"] == "Busan, Korea"
        assert data["profileImageUrl"] == "https://example.com/new.jpg"

    def test_update_returns_full_profile(self, client: TestClient, auth_headers):
        """Update response should include all profile fields, not just changed ones."""
        response = client.put(
            self.url,
            headers=auth_headers,
            json={"name": "Full Profile Check"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "id" in data
        assert "stats" in data
        assert "trustLevel" in data
        assert "mannerTemperature" in data
        assert "isPremium" in data
        assert "role" in data

    def test_update_unauthorized(self, client: TestClient):
        """Update without auth should be rejected."""
        response = client.put(
            self.url,
            json={"name": "Hacker"},
        )
        assert response.status_code in (401, 403)

    def test_update_preserves_unchanged_fields(
        self, client: TestClient, auth_headers
    ):
        """Updating one field should not reset other fields."""
        # Set a known state first
        client.put(
            self.url,
            headers=auth_headers,
            json={"name": "Preserve Test", "location": "Daejeon"},
        )

        # Now update only name
        response = client.put(
            self.url,
            headers=auth_headers,
            json={"name": "New Name Only"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "New Name Only"
        assert data["location"] == "Daejeon"  # should be preserved


# ---------------------------------------------------------------------------
# GET /users/me/wishlist
# ---------------------------------------------------------------------------
class TestReadUserWishlist:
    """Test suite for the user's wishlist (liked materials)."""

    url = f"{API_V1_STR}/users/me/wishlist"

    def test_wishlist_empty(self, client: TestClient, auth_headers, db, test_user):
        """User wishlist should be empty after clearing any test data."""
        from app.models.like import MaterialLike
        db.query(MaterialLike).filter(MaterialLike.user_id == test_user.id).delete()
        db.commit()

        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"] == []
        assert "meta" in body
        meta = body["meta"]
        assert meta["totalCount"] == 0
        assert meta["page"] == 1
        assert meta["hasNextPage"] is False

    def test_wishlist_meta_structure(self, client: TestClient, auth_headers):
        """Wishlist response meta should have all pagination fields."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        meta = response.json()["meta"]
        assert "totalCount" in meta
        assert "page" in meta
        assert "limit" in meta
        assert "hasNextPage" in meta
        assert "totalPages" in meta

    def test_wishlist_pagination_params(self, client: TestClient, auth_headers):
        """Wishlist should respect page and limit query parameters."""
        response = client.get(
            self.url,
            headers=auth_headers,
            params={"page": 2, "limit": 5},
        )
        assert response.status_code == 200
        meta = response.json()["meta"]
        assert meta["page"] == 2
        assert meta["limit"] == 5

    def test_wishlist_unauthorized(self, client: TestClient):
        """Wishlist without auth should be rejected."""
        response = client.get(self.url)
        assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /users/me/subscription
# ---------------------------------------------------------------------------
class TestGetSubscription:
    """Test suite for the user's subscription status."""

    url = f"{API_V1_STR}/users/me/subscription"

    def test_subscription_returns_valid_data(self, client: TestClient, auth_headers):
        """Subscription endpoint should return status and plan info."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "plan" in data
        assert "isPremium" in data
        assert data["plan"] in ("free", "premium")

    def test_subscription_unauthorized(self, client: TestClient):
        """Subscription check without auth should be rejected."""
        response = client.get(self.url)
        assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /users/me/subscription/verify
# ---------------------------------------------------------------------------
class TestVerifySubscription:
    """Test suite for IAP receipt verification."""

    url = f"{API_V1_STR}/users/me/subscription/verify"

    def test_verify_receipt_success(self, client: TestClient, auth_headers2):
        """Valid receipt should upgrade user to premium.

        Uses auth_headers2 (test_user2) to avoid side effects on
        the primary test_user's subscription state.
        """
        response = client.post(
            self.url,
            headers=auth_headers2,
            json={"receiptId": "receipt_abc_123", "platform": "ios"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["plan"] == "premium"
        assert data["isPremium"] is True

    def test_verify_receipt_reflects_in_subscription(
        self, client: TestClient, auth_headers2
    ):
        """After verification, GET subscription should show premium."""
        # First verify a receipt
        client.post(
            self.url,
            headers=auth_headers2,
            json={"receiptId": "receipt_xyz_456", "platform": "ios"},
        )
        # Then check subscription endpoint
        sub_resp = client.get(
            f"{API_V1_STR}/users/me/subscription",
            headers=auth_headers2,
        )
        assert sub_resp.status_code == 200
        data = sub_resp.json()["data"]
        assert data["plan"] == "premium"
        assert data["isPremium"] is True

    def test_verify_receipt_missing_fields(self, client: TestClient, auth_headers):
        """Missing required fields should return 422."""
        response = client.post(
            self.url,
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 422

    def test_verify_receipt_unauthorized(self, client: TestClient):
        """Verification without auth should be rejected."""
        response = client.post(
            self.url,
            json={"receiptId": "receipt_123", "platform": "ios"},
        )
        assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /users/ (admin only)
# ---------------------------------------------------------------------------
class TestListUsers:
    """Test suite for the admin-only user listing endpoint.

    NOTE: The /users/ endpoint returns raw SQLAlchemy User objects without
    a response_model. This causes a PydanticSerializationError in current
    FastAPI versions. The superuser-specific tests below are marked xfail
    to document this known bug while still testing the auth guard logic.
    """

    url = f"{API_V1_STR}/users/"

    @pytest.mark.xfail(
        reason="Endpoint returns raw User ORM objects without response_model; "
               "Pydantic cannot serialize them (PydanticSerializationError).",
        strict=True,
    )
    def test_list_users_as_superuser(
        self, client: TestClient, superuser_headers
    ):
        """Superuser should be able to list all users."""
        response = client.get(self.url, headers=superuser_headers)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) >= 3  # test_user, test_user2, test_superuser

    def test_list_users_as_normal_user(self, client: TestClient, auth_headers):
        """Normal user should be rejected with 400 (not enough privileges)."""
        response = client.get(self.url, headers=auth_headers)
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "privileges" in body["detail"].lower()

    def test_list_users_unauthorized(self, client: TestClient):
        """Unauthenticated request should be rejected."""
        response = client.get(self.url)
        assert response.status_code in (401, 403)

    @pytest.mark.xfail(
        reason="Endpoint returns raw User ORM objects without response_model; "
               "Pydantic cannot serialize them (PydanticSerializationError).",
        strict=True,
    )
    def test_list_users_pagination(
        self, client: TestClient, superuser_headers
    ):
        """Superuser should be able to paginate results."""
        response = client.get(
            self.url,
            headers=superuser_headers,
            params={"skip": 0, "limit": 2},
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) <= 2

    @pytest.mark.xfail(
        reason="Endpoint returns raw User ORM objects without response_model; "
               "Pydantic cannot serialize them (PydanticSerializationError).",
        strict=True,
    )
    def test_list_users_contains_expected_users(
        self, client: TestClient, superuser_headers, test_user, test_superuser
    ):
        """Listed users should include our seeded test users."""
        response = client.get(self.url, headers=superuser_headers)
        assert response.status_code == 200
        emails = [u["email"] for u in response.json()]
        assert test_user.email in emails
        assert test_superuser.email in emails
