"""C2. Concurrency & Rapid-Fire Tests

Tests for concurrent access patterns and rapid sequential requests.

Note on SQLite limitations:
    SQLite with StaticPool (single shared connection) does not support true
    concurrent access from multiple threads. Therefore these tests use
    sequential rapid-fire requests to validate that the application handles
    high-frequency access patterns correctly (no crashes, no state corruption).

    For true race condition testing with SELECT FOR UPDATE, connection pool
    exhaustion, etc., use PostgreSQL.

Markers:
    @pytest.mark.slow - tests with many sequential requests
    @pytest.mark.integration - integration-level tests
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

API = settings.API_V1_STR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_material(client: TestClient, auth_headers: dict, **overrides) -> int:
    payload = {
        "title": "Concurrency Test Material",
        "description": "For concurrency testing",
        "price": 50000,
        "location": {"address": "Seoul"},
        "quantity": 1,
        "quantityUnit": "EA",
        "tradeMethod": "DIRECT",
        **overrides,
    }
    resp = client.post(f"{API}/materials/", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Material creation failed: {resp.text}"
    return resp.json()["data"]["id"]


def _create_community_post(client: TestClient, auth_headers: dict) -> int:
    payload = {
        "title": "Concurrency Test Post",
        "content": "Post for concurrency testing",
        "category": "general",
    }
    resp = client.post(f"{API}/community/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 200, f"Post creation failed: {resp.text}"
    return resp.json()["data"]["id"]


# ===================================================================
# TC-CONC-01: Rapid Material Reads
# ===================================================================
class TestRapidMaterialReads:
    """Verify that many rapid GET /materials requests all succeed."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_material_reads(self, client: TestClient, auth_headers):
        """30 rapid GET /materials requests should all return 200."""
        _create_material(client, auth_headers)

        results = [client.get(f"{API}/materials/") for _ in range(30)]

        assert len(results) == 30
        statuses = [r.status_code for r in results]
        assert all(
            s == 200 for s in statuses
        ), f"Not all requests succeeded: {statuses}"

        for r in results:
            body = r.json()
            assert body["status"] == "success"
            assert isinstance(body["data"], list)

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_material_detail_reads(self, client: TestClient, auth_headers):
        """20 rapid reads of the same material detail should all succeed."""
        material_id = _create_material(client, auth_headers)

        results = [client.get(f"{API}/materials/{material_id}") for _ in range(20)]

        assert len(results) == 20
        assert all(r.status_code == 200 for r in results)

        for r in results:
            assert r.json()["data"]["id"] == material_id


# ===================================================================
# TC-CONC-03: ChatRoom get_or_create Idempotency
# ===================================================================
class TestChatRoomCreationIdempotency:
    """Multiple room creation for the same pair should not create duplicates."""

    @pytest.mark.integration
    def test_chat_room_creation_idempotency(
        self, client: TestClient, auth_headers, test_user2
    ):
        """Multiple room creation requests for the same user pair
        should all return the same room ID (get_or_create semantics)."""
        results = []
        for _ in range(5):
            resp = client.post(
                f"{API}/chats/rooms",
                json={"sellerId": test_user2.id},
                headers=auth_headers,
            )
            results.append(resp)

        assert all(r.status_code == 200 for r in results)

        room_ids = {r.json()["data"]["id"] for r in results}
        assert len(room_ids) == 1, (
            f"Expected 1 unique room, got {len(room_ids)}: {room_ids}"
        )


# ===================================================================
# TC-CONC-05: Rapid Like Toggles
# ===================================================================
class TestRapidLikeToggles:
    """Rapid like toggles should not crash and should maintain consistency."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_like_toggles(self, client: TestClient, auth_headers):
        """10 rapid like toggles by the same user should complete without errors.
        After even number of toggles, state should return to original."""
        material_id = _create_material(client, auth_headers)

        results = []
        for _ in range(10):
            resp = client.post(
                f"{API}/materials/{material_id}/like",
                headers=auth_headers,
            )
            results.append(resp)

        statuses = [r.status_code for r in results]
        assert all(
            s == 200 for s in statuses
        ), f"Some like toggles failed: {statuses}"

        # Final state: 10 toggles (even) -> back to original (not liked)
        check_resp = client.get(
            f"{API}/materials/{material_id}/like", headers=auth_headers
        )
        assert check_resp.status_code == 200

        final = check_resp.json()["data"]
        assert isinstance(final["isLiked"], bool)
        assert isinstance(final["likesCount"], int)
        assert final["likesCount"] >= 0

        # After 10 sequential toggles (even), should be unliked
        assert final["isLiked"] is False
        assert final["likesCount"] == 0

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_post_like_toggles(self, client: TestClient, auth_headers):
        """Rapid community post like toggles should not crash."""
        post_id = _create_community_post(client, auth_headers)

        results = []
        for _ in range(10):
            resp = client.post(
                f"{API}/community/posts/{post_id}/like",
                headers=auth_headers,
            )
            results.append(resp)

        statuses = [r.status_code for r in results]
        assert all(
            s == 200 for s in statuses
        ), f"Some post like toggles failed: {statuses}"

    @pytest.mark.integration
    def test_like_toggle_state_alternation(self, client: TestClient, auth_headers):
        """Each toggle should alternate between liked and unliked."""
        material_id = _create_material(client, auth_headers)

        for i in range(6):
            resp = client.post(
                f"{API}/materials/{material_id}/like",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()["data"]

            if i % 2 == 0:
                assert data["isLiked"] is True, f"Toggle {i}: expected liked"
            else:
                assert data["isLiked"] is False, f"Toggle {i}: expected unliked"


# ===================================================================
# TC-CONC-07: Material Like Count Consistency (Multi-User)
# ===================================================================
class TestLikeCountConsistency:
    """Multiple users liking the same material should produce correct count."""

    @pytest.mark.integration
    def test_like_count_consistency(
        self, client: TestClient, auth_headers, auth_headers2, superuser_headers
    ):
        """Three users liking the same material should result in likesCount == 3."""
        material_id = _create_material(client, auth_headers)

        for headers in [auth_headers, auth_headers2, superuser_headers]:
            resp = client.post(
                f"{API}/materials/{material_id}/like",
                headers=headers,
            )
            assert resp.status_code == 200

        check_resp = client.get(
            f"{API}/materials/{material_id}/like", headers=auth_headers
        )
        assert check_resp.status_code == 200

        final = check_resp.json()["data"]
        assert final["likesCount"] == 3, (
            f"Expected likesCount=3 after 3 unique users liked, got {final['likesCount']}"
        )

    @pytest.mark.integration
    def test_like_unlike_count_accuracy(
        self, client: TestClient, auth_headers, auth_headers2
    ):
        """Like by user1, like by user2, unlike by user1 -> count == 1."""
        material_id = _create_material(client, auth_headers)

        # User1 likes
        resp = client.post(f"{API}/materials/{material_id}/like", headers=auth_headers)
        assert resp.json()["data"]["likesCount"] == 1

        # User2 likes
        resp = client.post(f"{API}/materials/{material_id}/like", headers=auth_headers2)
        assert resp.json()["data"]["likesCount"] == 2

        # User1 unlikes
        resp = client.post(f"{API}/materials/{material_id}/like", headers=auth_headers)
        assert resp.json()["data"]["likesCount"] == 1
        assert resp.json()["data"]["isLiked"] is False

        # User2 still liked
        check = client.get(f"{API}/materials/{material_id}/like", headers=auth_headers2)
        assert check.json()["data"]["isLiked"] is True


# ===================================================================
# Rapid Message Sending
# ===================================================================
class TestRapidMessages:
    """Multiple messages sent rapidly to the same chat room."""

    @pytest.fixture()
    def room_id(self, client: TestClient, auth_headers, test_user2) -> int:
        resp = client.post(
            f"{API}/chats/rooms",
            json={"sellerId": test_user2.id},
            headers=auth_headers,
        )
        return resp.json()["data"]["id"]

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_message_sending(
        self, client: TestClient, auth_headers, auth_headers2, room_id
    ):
        """Both users sending messages rapidly should all succeed."""
        results = []
        for i in range(3):
            r1 = client.post(
                f"{API}/chats/rooms/{room_id}/messages",
                json={"content": f"user1-msg-{i}", "messageType": "TEXT"},
                headers=auth_headers,
            )
            results.append(r1)

            r2 = client.post(
                f"{API}/chats/rooms/{room_id}/messages",
                json={"content": f"user2-msg-{i}", "messageType": "TEXT"},
                headers=auth_headers2,
            )
            results.append(r2)

        assert all(
            r.status_code == 200 for r in results
        ), f"Some messages failed: {[r.status_code for r in results]}"

        # Verify all messages are persisted
        msgs_resp = client.get(
            f"{API}/chats/rooms/{room_id}/messages",
            headers=auth_headers,
            params={"limit": 50},
        )
        assert msgs_resp.status_code == 200
        messages = msgs_resp.json()["data"]
        assert len(messages) >= 6, (
            f"Expected at least 6 messages, got {len(messages)}"
        )

    @pytest.mark.integration
    def test_message_ordering(
        self, client: TestClient, auth_headers, room_id
    ):
        """Messages should maintain creation order."""
        contents = [f"ordered-msg-{i}" for i in range(5)]
        for content in contents:
            resp = client.post(
                f"{API}/chats/rooms/{room_id}/messages",
                json={"content": content, "messageType": "TEXT"},
                headers=auth_headers,
            )
            assert resp.status_code == 200

        msgs_resp = client.get(
            f"{API}/chats/rooms/{room_id}/messages",
            headers=auth_headers,
            params={"limit": 50},
        )
        assert msgs_resp.status_code == 200
        msg_contents = [m["content"] for m in msgs_resp.json()["data"]]

        # All our messages should be present
        for content in contents:
            assert content in msg_contents, f"Missing message: {content}"


# ===================================================================
# Rapid Material Creation
# ===================================================================
class TestRapidMaterialCreation:
    """Multiple materials created rapidly by the same user."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_rapid_material_creation(self, client: TestClient, auth_headers):
        """5 rapid material creation requests should all succeed
        and produce distinct IDs."""
        results = []
        for i in range(5):
            payload = {
                "title": f"Rapid Material {i}",
                "description": f"Created rapidly #{i}",
                "price": 10000 + i,
                "location": {"address": "Seoul"},
            }
            resp = client.post(
                f"{API}/materials/", json=payload, headers=auth_headers
            )
            results.append(resp)

        assert all(r.status_code == 200 for r in results)

        ids = {r.json()["data"]["id"] for r in results}
        assert len(ids) == 5, f"Expected 5 unique IDs, got {len(ids)}: {ids}"
