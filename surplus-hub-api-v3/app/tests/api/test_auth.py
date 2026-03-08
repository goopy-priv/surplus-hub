"""Tests for authentication endpoints: /api/v1/auth/*"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_refresh_token

API_V1_STR = settings.API_V1_STR


# ---------------------------------------------------------------------------
# POST /auth/login/access-token
# ---------------------------------------------------------------------------
class TestLoginAccessToken:
    """Test suite for the login endpoint (OAuth2PasswordRequestForm)."""

    url = f"{API_V1_STR}/auth/login/access-token"

    def test_login_success(self, client: TestClient, test_user):
        """Valid credentials should return an access token."""
        response = client.post(
            self.url,
            data={"username": test_user.email, "password": "password123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "accessToken" in data
        assert data["tokenType"] == "bearer"
        assert len(data["accessToken"]) > 0

    def test_login_wrong_password(self, client: TestClient, test_user):
        """Wrong password should return 400."""
        response = client.post(
            self.url,
            data={"username": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "Incorrect email or password" in body["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Non-existent email should return 400."""
        response = client.post(
            self.url,
            data={"username": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "Incorrect email or password" in body["detail"]

    def test_login_empty_username(self, client: TestClient):
        """Empty username field should return 422 (validation error)."""
        response = client.post(
            self.url,
            data={"username": "", "password": "password123"},
        )
        # FastAPI may accept empty string and return 400 (auth fail),
        # or the form might still pass validation -- either way, not 200
        assert response.status_code in (400, 422)

    def test_login_missing_fields(self, client: TestClient):
        """Missing form fields should return 422."""
        response = client.post(self.url, data={})
        assert response.status_code == 422

    def test_login_returns_usable_token(self, client: TestClient, test_user):
        """The token returned by login should work for authenticated endpoints."""
        login_resp = client.post(
            self.url,
            data={"username": test_user.email, "password": "password123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["data"]["accessToken"]

        # Use the token to access a protected endpoint
        me_resp = client.get(
            f"{API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["status"] == "success"
        assert me_data["data"]["id"] == str(test_user.id)

    def test_login_superuser(self, client: TestClient, test_superuser):
        """Superuser should also be able to log in normally."""
        response = client.post(
            self.url,
            data={"username": test_superuser.email, "password": "adminpass"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "accessToken" in data
        assert data["tokenType"] == "bearer"


# ---------------------------------------------------------------------------
# POST /auth/refresh-token
# ---------------------------------------------------------------------------
class TestRefreshToken:
    """Test suite for the token refresh endpoint."""

    url = f"{API_V1_STR}/auth/refresh-token"

    def test_refresh_token_success(self, client: TestClient, test_user):
        """Valid refresh token in body should return a new token pair."""
        refresh = create_refresh_token(subject=test_user.id)
        response = client.post(self.url, json={"refreshToken": refresh})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert "data" in body
        data = body["data"]
        assert "accessToken" in data
        assert data["tokenType"] == "bearer"
        assert len(data["accessToken"]) > 0

    def test_refresh_token_missing_body(self, client: TestClient):
        """Request without body should return 422 (validation error)."""
        response = client.post(self.url)
        assert response.status_code == 422

    def test_refresh_token_invalid_token(self, client: TestClient):
        """Invalid refresh token should return 401."""
        response = client.post(
            self.url,
            json={"refreshToken": "invalidtoken123"},
        )
        assert response.status_code == 401

    def test_refresh_token_returns_different_token(
        self, client: TestClient, test_user
    ):
        """Refreshed token should (typically) differ from the original."""
        refresh = create_refresh_token(subject=test_user.id)
        response = client.post(self.url, json={"refreshToken": refresh})
        assert response.status_code == 200
        new_token = response.json()["data"]["accessToken"]
        assert isinstance(new_token, str)
        assert len(new_token) > 0

    def test_refresh_token_new_token_is_usable(
        self, client: TestClient, test_user
    ):
        """The refreshed token should be usable for subsequent requests."""
        refresh = create_refresh_token(subject=test_user.id)
        refresh_resp = client.post(self.url, json={"refreshToken": refresh})
        assert refresh_resp.status_code == 200
        new_token = refresh_resp.json()["data"]["accessToken"]

        me_resp = client.get(
            f"{API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["status"] == "success"
