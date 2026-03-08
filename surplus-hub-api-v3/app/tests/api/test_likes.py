"""Tests for like/wishlist endpoints.

Material likes:  POST/GET /api/v1/materials/{id}/like
Post likes:      POST /api/v1/community/posts/{id}/like
Wishlist:        GET  /api/v1/users/me/wishlist
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API_V1_STR = settings.API_V1_STR
MAT_PREFIX = f"{API_V1_STR}/materials"
COM_PREFIX = f"{API_V1_STR}/community"
USR_PREFIX = f"{API_V1_STR}/users"

# HTTPBearer returns 401 in newer FastAPI/Starlette versions, 403 in older ones.
_NO_AUTH_CODES = (401, 403)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_material(client: TestClient, auth_headers: dict) -> int:
    """Create a material and return its ID."""
    payload = {
        "title": "Like Test Material",
        "description": "For like testing",
        "price": 10000,
        "location": {"address": "Seoul"},
        "quantity": 1,
        "quantityUnit": "ea",
        "tradeMethod": "DIRECT",
    }
    resp = client.post(f"{MAT_PREFIX}/", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Material creation failed: {resp.text}"
    return resp.json()["data"]["id"]


def _create_post(client: TestClient, auth_headers: dict) -> int:
    """Create a community post and return its ID."""
    payload = {
        "title": "Like Test Post",
        "content": "Post content for like testing",
        "category": "general",
    }
    resp = client.post(
        f"{COM_PREFIX}/posts", json=payload, headers=auth_headers
    )
    assert resp.status_code == 200, f"Post creation failed: {resp.text}"
    return resp.json()["data"]["id"]


# ---------------------------------------------------------------------------
# Auth guards
# ---------------------------------------------------------------------------
class TestLikeAuthGuards:
    """All like endpoints reject unauthenticated requests."""

    def test_toggle_material_like_requires_auth(self, client: TestClient):
        resp = client.post(f"{MAT_PREFIX}/1/like")
        assert resp.status_code in _NO_AUTH_CODES

    def test_check_material_like_requires_auth(self, client: TestClient):
        resp = client.get(f"{MAT_PREFIX}/1/like")
        assert resp.status_code in _NO_AUTH_CODES

    def test_wishlist_requires_auth(self, client: TestClient):
        resp = client.get(f"{USR_PREFIX}/me/wishlist")
        assert resp.status_code in _NO_AUTH_CODES

    def test_toggle_post_like_requires_auth(self, client: TestClient):
        resp = client.post(f"{COM_PREFIX}/posts/1/like")
        assert resp.status_code in _NO_AUTH_CODES


# ---------------------------------------------------------------------------
# Material likes
# ---------------------------------------------------------------------------
class TestMaterialLike:
    """POST /materials/{id}/like -- toggle like on/off."""

    def test_like_then_unlike(self, client: TestClient, auth_headers):
        """First toggle should like, second should unlike."""
        material_id = _create_material(client, auth_headers)

        # Like
        like_resp = client.post(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers
        )
        assert like_resp.status_code == 200
        like_body = like_resp.json()
        assert like_body["status"] == "success"
        assert like_body["data"]["isLiked"] is True
        assert like_body["data"]["likesCount"] >= 1

        # Unlike (toggle)
        unlike_resp = client.post(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers
        )
        assert unlike_resp.status_code == 200
        unlike_body = unlike_resp.json()
        assert unlike_body["data"]["isLiked"] is False

    def test_like_nonexistent_material(self, client: TestClient, auth_headers):
        """Liking a non-existent material should return 404."""
        resp = client.post(
            f"{MAT_PREFIX}/99999/like", headers=auth_headers
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Check like status
# ---------------------------------------------------------------------------
class TestCheckMaterialLike:
    """GET /materials/{id}/like -- check current like status."""

    def test_check_not_liked(self, client: TestClient, auth_headers):
        """Fresh material should not be liked by user."""
        material_id = _create_material(client, auth_headers)
        resp = client.get(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["isLiked"] is False
        assert data["likesCount"] >= 0

    def test_check_after_like(
        self, client: TestClient, auth_headers, auth_headers2
    ):
        """After liking, status should reflect isLiked=True."""
        material_id = _create_material(client, auth_headers)

        # user2 likes it
        client.post(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers2
        )

        # user2 checks
        resp = client.get(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers2
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["isLiked"] is True

    def test_check_nonexistent_material(self, client: TestClient, auth_headers):
        resp = client.get(
            f"{MAT_PREFIX}/99999/like", headers=auth_headers
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Wishlist
# ---------------------------------------------------------------------------
class TestWishlist:
    """GET /users/me/wishlist -- list of liked materials."""

    def test_wishlist_returns_liked_materials(
        self, client: TestClient, auth_headers, auth_headers2
    ):
        """After liking a material, it should appear in wishlist."""
        material_id = _create_material(client, auth_headers)

        # user2 likes it
        like_resp = client.post(
            f"{MAT_PREFIX}/{material_id}/like", headers=auth_headers2
        )
        assert like_resp.status_code == 200
        assert like_resp.json()["data"]["isLiked"] is True

        # user2 checks wishlist
        wishlist_resp = client.get(
            f"{USR_PREFIX}/me/wishlist", headers=auth_headers2
        )
        assert wishlist_resp.status_code == 200
        body = wishlist_resp.json()
        assert body["status"] == "success"
        assert isinstance(body["data"], list)

        # The liked material should be in the wishlist
        wishlist_ids = [m["id"] for m in body["data"]]
        assert material_id in wishlist_ids

        # Check meta pagination fields exist
        assert "meta" in body
        assert "totalCount" in body["meta"]
        assert "page" in body["meta"]

    def test_wishlist_empty_for_new_user(
        self, client: TestClient, superuser_headers
    ):
        """A user who has not liked anything should get an empty wishlist."""
        resp = client.get(
            f"{USR_PREFIX}/me/wishlist", headers=superuser_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert isinstance(body["data"], list)


# ---------------------------------------------------------------------------
# Community post likes
# ---------------------------------------------------------------------------
class TestPostLike:
    """POST /community/posts/{id}/like -- toggle post like."""

    def test_like_post(self, client: TestClient, auth_headers):
        """Like a community post."""
        post_id = _create_post(client, auth_headers)

        resp = client.post(
            f"{COM_PREFIX}/posts/{post_id}/like", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["isLiked"] is True

    def test_unlike_post(self, client: TestClient, auth_headers):
        """Toggle like twice to unlike a post."""
        post_id = _create_post(client, auth_headers)

        # Like
        client.post(
            f"{COM_PREFIX}/posts/{post_id}/like", headers=auth_headers
        )
        # Unlike
        resp = client.post(
            f"{COM_PREFIX}/posts/{post_id}/like", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["isLiked"] is False

    def test_like_nonexistent_post(self, client: TestClient, auth_headers):
        """Liking a non-existent post should return 404."""
        resp = client.post(
            f"{COM_PREFIX}/posts/99999/like", headers=auth_headers
        )
        assert resp.status_code == 404
