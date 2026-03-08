from fastapi.testclient import TestClient
from app.core.config import settings

PREFIX = f"{settings.API_V1_STR}/reviews"


# ---------------------------------------------------------------------------
# Auth requirement checks
# ---------------------------------------------------------------------------
class TestReviewAuth:
    """Creating a review requires authentication; reading does not."""

    def test_create_review_requires_auth(self, client: TestClient):
        response = client.post(
            f"{PREFIX}/",
            json={"targetUserId": 2, "rating": 5, "content": "Great!"},
        )
        assert response.status_code == 401

    def test_get_review_no_auth_needed(self, client: TestClient):
        """GET single review is public -- expect 404 (not 401) for missing id."""
        response = client.get(f"{PREFIX}/99999")
        assert response.status_code == 404

    def test_get_user_reviews_no_auth_needed(self, client: TestClient):
        """GET user reviews is public -- expect 404 for non-existent user."""
        response = client.get(f"{PREFIX}/user/99999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
class TestReviewValidation:
    """Input validation for review creation."""

    def test_cannot_review_yourself(
        self, client: TestClient, test_user, auth_headers: dict
    ):
        response = client.post(
            f"{PREFIX}/",
            json={
                "targetUserId": test_user.id,
                "rating": 5,
                "content": "Self review",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "yourself" in response.json()["detail"].lower()

    def test_review_target_user_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        response = client.post(
            f"{PREFIX}/",
            json={
                "targetUserId": 99999,
                "rating": 4,
                "content": "Ghost user",
            },
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_rating_below_minimum(self, client: TestClient, auth_headers: dict):
        """Rating must be between 1 and 5 (schema-level validation)."""
        response = client.post(
            f"{PREFIX}/",
            json={"targetUserId": 2, "rating": 0, "content": "Bad rating"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_rating_above_maximum(self, client: TestClient, auth_headers: dict):
        """Rating must be between 1 and 5 (schema-level validation)."""
        response = client.post(
            f"{PREFIX}/",
            json={"targetUserId": 2, "rating": 6, "content": "Bad rating"},
            headers=auth_headers,
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Full CRUD flow
# ---------------------------------------------------------------------------
class TestReviewCRUD:
    """End-to-end review creation and retrieval flow."""

    def test_create_review(
        self, client: TestClient, test_user, test_user2, auth_headers: dict
    ):
        response = client.post(
            f"{PREFIX}/",
            json={
                "targetUserId": test_user2.id,
                "rating": 5,
                "content": "Great seller!",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["reviewerId"] == test_user.id
        assert data["targetUserId"] == test_user2.id
        assert data["rating"] == 5
        assert data["content"] == "Great seller!"

    def test_get_review(self, client: TestClient, test_user, test_user2):
        """Retrieve the review created in the previous test."""
        # Since session-scoped DB persists, the review from test_create_review
        # should still exist. Query via the user's reviews endpoint.
        response = client.get(f"{PREFIX}/user/{test_user2.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert len(body["data"]) >= 1

        # Now get the individual review by its id
        review_id = body["data"][0]["id"]
        detail_response = client.get(f"{PREFIX}/{review_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["status"] == "success"
        assert detail["data"]["id"] == review_id
        assert detail["data"]["rating"] == 5

    def test_get_user_reviews_with_meta(
        self, client: TestClient, test_user2
    ):
        """User reviews endpoint returns pagination meta and average rating."""
        response = client.get(f"{PREFIX}/user/{test_user2.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert "meta" in body
        assert body["meta"]["totalCount"] >= 1
        assert body["meta"]["averageRating"] is not None
        assert "mannerTemperature" in body["meta"]

    def test_create_review_without_content(
        self, client: TestClient, test_user2, auth_headers: dict
    ):
        """Content is optional for reviews."""
        response = client.post(
            f"{PREFIX}/",
            json={"targetUserId": test_user2.id, "rating": 4},
            headers=auth_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["rating"] == 4
        assert body["data"]["content"] is None

    def test_create_review_by_second_user(
        self, client: TestClient, test_user, auth_headers2: dict
    ):
        """test_user2 reviews test_user."""
        response = client.post(
            f"{PREFIX}/",
            json={
                "targetUserId": test_user.id,
                "rating": 3,
                "content": "Decent buyer",
            },
            headers=auth_headers2,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["targetUserId"] == test_user.id
        assert body["data"]["rating"] == 3
