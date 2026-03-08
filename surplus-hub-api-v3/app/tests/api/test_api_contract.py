"""C1. API Schema Contract Tests

Validates that backend API responses match the expected schema format
for frontend consumption. Catches mismatches in field naming (camelCase
vs snake_case), field presence, and response structure.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token

API = settings.API_V1_STR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_material(client: TestClient, auth_headers: dict, **overrides) -> int:
    payload = {
        "title": "Contract Test Material",
        "description": "For API contract testing",
        "price": 30000,
        "location": {"address": "Seoul"},
        "quantity": 1,
        "quantityUnit": "EA",
        "tradeMethod": "DIRECT",
        **overrides,
    }
    resp = client.post(f"{API}/materials/", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Material creation failed: {resp.text}"
    return resp.json()["data"]["id"]


# ===================================================================
# Auth Response Format Tests
# ===================================================================
class TestLoginResponseFormat:
    """POST /auth/login/access-token -- verify response key casing."""

    def test_login_response_format(self, client: TestClient, test_user):
        """Login response should use camelCase and be wrapped in {status, data}
        (unified with register and refresh endpoints)."""
        resp = client.post(
            f"{API}/auth/login/access-token",
            data={"username": test_user.email, "password": "password123"},
        )
        assert resp.status_code == 200
        body = resp.json()

        # All auth endpoints now use unified {status, data} wrapper with camelCase
        assert body["status"] == "success"
        assert "data" in body

        data = body["data"]
        assert "accessToken" in data, "Missing 'accessToken' in login response"
        assert "tokenType" in data, "Missing 'tokenType' in login response"
        assert data["tokenType"] == "bearer"
        assert len(data["accessToken"]) > 0

        # Login also returns user info (id, email, name)
        assert "id" in data
        assert "email" in data
        assert "name" in data


class TestRegisterResponseFormat:
    """POST /auth/register -- verify response format."""

    def test_register_response_format(self, client: TestClient):
        """Register response should use camelCase and be wrapped in {status, data}."""
        resp = client.post(
            f"{API}/auth/register",
            json={
                "email": "contract_test_register@example.com",
                "password": "password123",
                "name": "Contract Tester",
            },
        )
        # May fail if email already registered (from prior test runs)
        if resp.status_code == 400:
            pytest.skip("Email already registered from previous test run")

        assert resp.status_code == 200
        body = resp.json()

        # Register wraps in {status, data}
        assert body["status"] == "success"
        assert "data" in body

        data = body["data"]
        # Register uses _build_token_pair which returns camelCase
        assert "accessToken" in data, "Missing 'accessToken' in register response"
        assert "refreshToken" in data, "Missing 'refreshToken' in register response"
        assert "tokenType" in data, "Missing 'tokenType' in register response"
        assert data["tokenType"] == "bearer"

        # Extra user fields
        assert "id" in data
        assert "email" in data
        assert "name" in data


# ===================================================================
# Chat Room Response Structure Tests
# ===================================================================
class TestChatRoomResponseStructure:
    """Verify chat room list response has expected fields."""

    @pytest.fixture()
    def room_id(self, client: TestClient, auth_headers, test_user2) -> int:
        resp = client.post(
            f"{API}/chats/rooms",
            json={"sellerId": test_user2.id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        return resp.json()["data"]["id"]

    def test_chatroom_has_other_user_name(
        self, client: TestClient, auth_headers, room_id
    ):
        """GET /chats/rooms response items should contain otherUserName."""
        resp = client.get(f"{API}/chats/rooms", headers=auth_headers)
        assert resp.status_code == 200

        rooms = resp.json()["data"]
        assert len(rooms) > 0, "No chat rooms found"

        room = next((r for r in rooms if r["id"] == room_id), None)
        assert room is not None, f"Room {room_id} not in response"

        # Backend schema has otherUserName (camelCase alias)
        assert "otherUserName" in room, "Missing otherUserName in chat room response"
        assert isinstance(room["otherUserName"], str)

    def test_chatroom_last_message_structure(
        self, client: TestClient, auth_headers, room_id
    ):
        """lastMessage should be a string (content only), not a full ChatMessage object."""
        # Send a message first
        client.post(
            f"{API}/chats/rooms/{room_id}/messages",
            json={"content": "Contract test msg", "messageType": "TEXT"},
            headers=auth_headers,
        )

        resp = client.get(f"{API}/chats/rooms", headers=auth_headers)
        assert resp.status_code == 200

        rooms = resp.json()["data"]
        room = next((r for r in rooms if r["id"] == room_id), None)
        assert room is not None

        # Backend sends lastMessage as Optional[str] (content string, not object)
        if room.get("lastMessage") is not None:
            assert isinstance(
                room["lastMessage"], str
            ), f"lastMessage should be str, got {type(room['lastMessage'])}"

        # lastMessageTime should be present when lastMessage exists
        if room.get("lastMessage"):
            assert "lastMessageTime" in room, "Missing lastMessageTime when lastMessage is set"

    def test_chatroom_has_unread_count(
        self, client: TestClient, auth_headers, room_id
    ):
        """Chat room response should include unreadCount field."""
        resp = client.get(f"{API}/chats/rooms", headers=auth_headers)
        assert resp.status_code == 200

        rooms = resp.json()["data"]
        room = next((r for r in rooms if r["id"] == room_id), None)
        assert room is not None
        assert "unreadCount" in room, "Missing unreadCount in chat room response"
        assert isinstance(room["unreadCount"], int)


# ===================================================================
# Material Response Tests
# ===================================================================
class TestMaterialCategoryNullable:
    """POST /materials -- category can be null."""

    def test_material_category_nullable(self, client: TestClient, auth_headers):
        """Creating a material without category should succeed (Optional[str])."""
        payload = {
            "title": "No Category Material",
            "description": "Testing null category",
            "price": 10000,
            "location": {"address": "Seoul"},
        }
        resp = client.post(f"{API}/materials/", json=payload, headers=auth_headers)
        assert resp.status_code == 200

        data = resp.json()["data"]
        # category is Optional[str] = None in schema
        # It may be null or absent
        category = data.get("category")
        assert category is None or isinstance(category, str)

    def test_material_category_with_value(self, client: TestClient, auth_headers):
        """Creating a material with a category should include it in response."""
        material_id = _create_material(client, auth_headers, category="steel")
        resp = client.get(f"{API}/materials/{material_id}")
        assert resp.status_code == 200

        data = resp.json()["data"]
        assert data.get("category") == "steel"


class TestMaterialResponseHasLikesCount:
    """GET /materials/{id}/like -- response includes likesCount."""

    def test_material_like_response_has_likes_count(
        self, client: TestClient, auth_headers
    ):
        """Like status response should contain both isLiked and likesCount."""
        material_id = _create_material(client, auth_headers)

        resp = client.get(
            f"{API}/materials/{material_id}/like", headers=auth_headers
        )
        assert resp.status_code == 200

        data = resp.json()["data"]
        assert "isLiked" in data, "Missing isLiked in like status response"
        assert "likesCount" in data, "Missing likesCount in like status response"
        assert isinstance(data["isLiked"], bool)
        assert isinstance(data["likesCount"], int)
        assert data["likesCount"] >= 0

    def test_material_toggle_like_response_has_likes_count(
        self, client: TestClient, auth_headers
    ):
        """Toggle like response should also contain likesCount."""
        material_id = _create_material(client, auth_headers)

        resp = client.post(
            f"{API}/materials/{material_id}/like", headers=auth_headers
        )
        assert resp.status_code == 200

        data = resp.json()["data"]
        assert "isLiked" in data
        assert "likesCount" in data
        assert data["isLiked"] is True
        assert data["likesCount"] >= 1


# ===================================================================
# Response Wrapper Structure Tests
# ===================================================================
class TestResponseWrapperFormat:
    """Verify standard {status, data, meta} wrapper across endpoints."""

    def test_materials_list_has_wrapper(self, client: TestClient):
        """GET /materials/ should return {status, data, meta}."""
        resp = client.get(f"{API}/materials/")
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "success"
        assert isinstance(body["data"], list)
        assert "meta" in body

        meta = body["meta"]
        for key in ("totalCount", "page", "limit", "hasNextPage", "totalPages"):
            assert key in meta, f"Missing meta key: {key}"

    def test_chat_rooms_list_has_wrapper(self, client: TestClient, auth_headers):
        """GET /chats/rooms should return {status, data, meta}."""
        resp = client.get(f"{API}/chats/rooms", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "success"
        assert isinstance(body["data"], list)
        assert "meta" in body

    def test_user_me_has_wrapper(self, client: TestClient, auth_headers):
        """GET /users/me should return {status, data}."""
        resp = client.get(f"{API}/users/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "success"
        assert "data" in body
        assert "id" in body["data"]
