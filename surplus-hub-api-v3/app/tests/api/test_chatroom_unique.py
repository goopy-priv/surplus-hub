"""TC-CONC-UQ: ChatRoom UNIQUE constraint tests.

Validates that the UNIQUE(material_id, buyer_id, seller_id) constraint
on chat_rooms works correctly with the get_or_create pattern.

Test environment uses SQLite in-memory (conftest.py), so true multi-thread
concurrency is not possible. Instead we verify:
1. API-level idempotency (same params -> same room_id)
2. CRUD-level IntegrityError handling (simulated race condition)
"""

import pytest
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.core.config import settings
from app.crud.crud_chat import crud_chat_room
from app.models.chat import ChatRoom

API = settings.API_V1_STR


# ===================================================================
# API-level: UNIQUE constraint idempotency
# ===================================================================
class TestChatRoomUniqueConstraintAPI:
    """API-level: same (material_id, buyer_id, seller_id) always returns same room."""

    def test_same_params_return_same_room(
        self, client: TestClient, auth_headers, test_user2
    ):
        """Two creation requests with identical params -> same room_id."""
        payload = {"sellerId": test_user2.id}
        resp1 = client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)
        resp2 = client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["data"]["id"] == resp2.json()["data"]["id"]

    @pytest.mark.integration
    def test_rapid_creation_all_return_same_id(
        self, client: TestClient, auth_headers, test_user2
    ):
        """10 rapid creation requests -> all return the same room_id."""
        payload = {"sellerId": test_user2.id}
        results = [
            client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)
            for _ in range(10)
        ]
        assert all(r.status_code == 200 for r in results)
        room_ids = {r.json()["data"]["id"] for r in results}
        assert len(room_ids) == 1, f"Expected 1 unique room, got {room_ids}"

    def test_both_requests_return_200(
        self, client: TestClient, auth_headers, test_user2
    ):
        """Even under duplicate creation, both requests return 200 (not 409)."""
        payload = {"sellerId": test_user2.id}
        responses = [
            client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)
            for _ in range(3)
        ]
        for resp in responses:
            assert resp.status_code == 200
            assert resp.json()["status"] == "success"
            assert "id" in resp.json()["data"]


# ===================================================================
# CRUD-level: IntegrityError handling
# ===================================================================
class TestChatRoomUniqueConstraintCRUD:
    """CRUD-level: get_or_create handles IntegrityError gracefully."""

    def test_get_or_create_returns_existing(self, db, test_user, test_user2):
        """Existing (material_id, buyer_id, seller_id) -> returns existing, created=False."""
        room1, created1 = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        assert room1 is not None

        room2, created2 = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        assert room2 is not None
        assert room1.id == room2.id
        assert created2 is False

    def test_get_or_create_idempotent_result(self, db, test_user, test_user2):
        """Calling get_or_create N times yields the same room object."""
        rooms = []
        for _ in range(5):
            room, _ = crud_chat_room.get_or_create(
                db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
            )
            rooms.append(room)

        ids = {r.id for r in rooms}
        assert len(ids) == 1

    def test_integrity_error_path_returns_existing(self, db, test_user, test_user2):
        """Simulate race condition: force IntegrityError on commit,
        verify fallback SELECT returns the existing record."""
        # Ensure a room exists
        room_orig, _ = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        original_id = room_orig.id

        # Patch the first query().filter().first() to return None (simulating
        # the race where another thread hasn't committed yet), and patch
        # commit() to raise IntegrityError (simulating the other thread winning).
        real_query = db.query

        first_call = [True]

        def patched_query(*args, **kwargs):
            q = real_query(*args, **kwargs)
            if args and args[0] is ChatRoom and first_call[0]:
                original_filter = q.filter

                def patched_filter(*fargs, **fkwargs):
                    result = original_filter(*fargs, **fkwargs)
                    if first_call[0]:
                        original_first = result.first

                        def patched_first():
                            if first_call[0]:
                                first_call[0] = False
                                return None  # Simulate "not found" in race
                            return original_first()

                        result.first = patched_first
                    return result

                q.filter = patched_filter
            return q

        real_commit = db.commit

        commit_should_fail = [True]

        def patched_commit():
            if commit_should_fail[0]:
                commit_should_fail[0] = False
                db.rollback()
                raise IntegrityError("mock unique violation", {}, Exception())
            return real_commit()

        with patch.object(db, 'query', side_effect=patched_query), \
             patch.object(db, 'commit', side_effect=patched_commit):
            room2, created = crud_chat_room.get_or_create(
                db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
            )

        assert room2 is not None
        assert room2.id == original_id
        assert created is False
