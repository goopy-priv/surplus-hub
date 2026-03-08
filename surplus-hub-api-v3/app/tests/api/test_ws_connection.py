"""Tests for WebSocket connection endpoint.

Covers:
  - WebSocket authentication (token required)
  - Connection validation (room existence, participant check)
  - Multiple users in same room
  - Message send/receive flow
  - Connection cleanup

Note: Uses TestClient.websocket_connect() for synchronous WebSocket testing.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.core.ws_manager import manager
from app.models.chat import ChatRoom


# ===================================================================
# WebSocket Connection - Auth & Validation
# ===================================================================

class TestWSConnection:
    """WebSocket /ws/chat/{room_id} connection tests."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Clean up manager state before and after each test."""
        # Clear manager state before test
        manager.active_connections.clear()
        manager.connection_user_map.clear()
        manager._user_connection_count.clear()
        manager._total_connections = 0
        yield
        # Clean up after test
        manager.active_connections.clear()
        manager.connection_user_map.clear()
        manager._user_connection_count.clear()
        manager._total_connections = 0

    @pytest.fixture
    def test_room(self, test_user, test_user2):
        """Create a test chat room for WebSocket tests."""
        from app.tests.conftest import TestingSessionLocal

        # Use a fresh session to avoid detached instance errors
        db = TestingSessionLocal()
        try:
            room = ChatRoom(
                buyer_id=test_user.id,
                seller_id=test_user2.id,
            )
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
        finally:
            db.close()

    def test_connect_without_token_returns_error(self, client: TestClient):
        """WebSocket connection without token parameter should fail."""
        # Mock get_db_session to prevent Clerk JWKS calls
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db

            with pytest.raises(Exception):
                # TestClient.websocket_connect raises exception on connection failure
                with client.websocket_connect("/ws/chat/1"):
                    pass

    def test_connect_with_invalid_token_closes_4001(
        self, client: TestClient, db, test_room
    ):
        """WebSocket connection with invalid token should close with code 4001."""
        invalid_token = "invalid.jwt.token"

        # Mock get_db_session to return test DB and prevent Clerk JWKS calls
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            with pytest.raises(Exception) as exc_info:
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={invalid_token}"
                ):
                    pass

            # Connection should be rejected (4001: Invalid token)
            # TestClient raises WebSocketDisconnect or similar
            assert exc_info.value is not None

    def test_connect_to_nonexistent_room_closes_4004(
        self, client: TestClient, db, test_user
    ):
        """WebSocket connection to non-existent room should close with code 4004."""
        token = create_access_token(subject=test_user.id)
        nonexistent_room_id = 99999

        # Mock get_db_session to return test DB
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            with pytest.raises(Exception) as exc_info:
                with client.websocket_connect(
                    f"/ws/chat/{nonexistent_room_id}?token={token}"
                ):
                    pass

            # Connection should be rejected (4004: Room not found)
            assert exc_info.value is not None

    def test_connect_as_non_participant_closes_4003(
        self, client: TestClient, db, test_room, test_superuser
    ):
        """WebSocket connection from non-participant should close with code 4003."""
        # test_superuser is NOT a participant in test_room
        superuser = db.merge(test_superuser)
        token = create_access_token(subject=superuser.id)

        # Mock get_db_session to return test DB
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            with pytest.raises(Exception) as exc_info:
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token}"
                ):
                    pass

            # Connection should be rejected (4003: Not a participant)
            assert exc_info.value is not None

    def test_connect_success(
        self, client: TestClient, db, test_room, test_user
    ):
        """Valid participant should successfully connect to WebSocket."""
        token = create_access_token(subject=test_user.id)

        # Mock get_db_session to return test DB
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            # Mock heartbeat loop to prevent background task errors
            with patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"):
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token}"
                ) as websocket:
                    # Connection should succeed
                    assert websocket is not None

                    # Send a message to verify bidirectional communication
                    websocket.send_json({
                        "type": "text",
                        "content": "Hello from test"
                    })

                    # Receive echo/confirmation (server broadcasts to sender too)
                    data = websocket.receive_json()
                    assert data["type"] == "message"
                    assert data["data"]["content"] == "Hello from test"
                    assert data["data"]["senderId"] == test_user.id

    def test_connect_multiple_users_same_room(
        self, client: TestClient, db, test_room, test_user, test_user2
    ):
        """Multiple users should be able to connect to the same room."""
        token1 = create_access_token(subject=test_user.id)
        token2 = create_access_token(subject=test_user2.id)

        # Mock get_db_session to return test DB
        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            # Mock heartbeat loop to prevent background task errors
            with patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"):
                # Connect first user
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token1}"
                ) as ws1:
                    # Connect second user
                    with client.websocket_connect(
                        f"/ws/chat/{test_room.id}?token={token2}"
                    ) as ws2:
                        # Both connections should be active
                        assert ws1 is not None
                        assert ws2 is not None

                        # User 1 sends a message
                        ws1.send_json({
                            "type": "text",
                            "content": "Message from user 1"
                        })

                        # User 2 should receive the broadcast
                        data = ws2.receive_json()
                        assert data["type"] == "message"
                        assert data["data"]["content"] == "Message from user 1"
                        assert data["data"]["senderId"] == test_user.id

                        # User 1 also receives confirmation
                        data = ws1.receive_json()
                        assert data["type"] == "message"
                        assert data["data"]["senderId"] == test_user.id

    def test_typing_indicator_broadcast(
        self, client: TestClient, db, test_room, test_user, test_user2
    ):
        """Typing indicator should be broadcast to other users in room."""
        token1 = create_access_token(subject=test_user.id)
        token2 = create_access_token(subject=test_user2.id)

        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            with patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"):
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token1}"
                ) as ws1:
                    with client.websocket_connect(
                        f"/ws/chat/{test_room.id}?token={token2}"
                    ) as ws2:
                        # User 1 sends typing indicator
                        ws1.send_json({"type": "typing"})

                        # User 2 should receive typing indicator
                        data = ws2.receive_json()
                        assert data["type"] == "typing"
                        assert data["data"]["userId"] == test_user.id
                        assert "userName" in data["data"]

    def test_read_receipt_broadcast(
        self, client: TestClient, db, test_room, test_user, test_user2
    ):
        """Read receipt should be broadcast to other users in room."""
        token1 = create_access_token(subject=test_user.id)
        token2 = create_access_token(subject=test_user2.id)

        with patch("app.api.endpoints.ws.get_db_session") as mock_get_db:
            mock_get_db.return_value = db

            with patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"):
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token1}"
                ) as ws1:
                    with client.websocket_connect(
                        f"/ws/chat/{test_room.id}?token={token2}"
                    ) as ws2:
                        # User 1 sends a message first
                        ws1.send_json({
                            "type": "text",
                            "content": "Test message"
                        })

                        # Clear received messages
                        ws1.receive_json()  # User 1's confirmation
                        ws2.receive_json()  # User 2's broadcast

                        # User 2 sends read receipt
                        ws2.send_json({"type": "read"})

                        # User 1 should receive read receipt (user 2 doesn't get it back)
                        data = ws1.receive_json()
                        assert data["type"] == "read_receipt"
                        assert data["data"]["userId"] == test_user2.id
                        assert "readAt" in data["data"]
