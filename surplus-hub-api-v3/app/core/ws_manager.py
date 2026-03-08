import asyncio
import logging
import time
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 10   # seconds grace period after missed pong
MAX_CONNECTIONS_PER_USER = 5
MAX_TOTAL_CONNECTIONS = 1000


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self):
        # room_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id mapping
        self.connection_user_map: Dict[WebSocket, int] = {}
        # websocket -> heartbeat task
        self._heartbeat_tasks: Dict[WebSocket, asyncio.Task] = {}
        # websocket -> last pong timestamp
        self._last_pong: Dict[WebSocket, float] = {}
        # user_id -> connection count
        self._user_connection_count: Dict[int, int] = defaultdict(int)
        # total connection count
        self._total_connections: int = 0

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        # Check total connection limit
        if self._total_connections >= MAX_TOTAL_CONNECTIONS:
            await websocket.accept()
            await websocket.close(code=4029, reason="Too many connections")
            return

        # Check per-user connection limit
        if self._user_connection_count[user_id] >= MAX_CONNECTIONS_PER_USER:
            await websocket.accept()
            await websocket.close(code=4029, reason="Too many connections")
            return

        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        self.connection_user_map[websocket] = user_id
        self._user_connection_count[user_id] += 1
        self._total_connections += 1
        self._last_pong[websocket] = time.monotonic()
        # Start heartbeat for this connection
        task = asyncio.create_task(self._heartbeat_loop(websocket, room_id))
        self._heartbeat_tasks[websocket] = task

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        # Decrement connection counters
        user_id = self.connection_user_map.pop(websocket, None)
        if user_id is not None:
            self._user_connection_count[user_id] = max(0, self._user_connection_count[user_id] - 1)
            if self._user_connection_count[user_id] == 0:
                del self._user_connection_count[user_id]
            self._total_connections = max(0, self._total_connections - 1)
        self._last_pong.pop(websocket, None)
        # Cancel heartbeat task
        task = self._heartbeat_tasks.pop(websocket, None)
        if task and not task.done():
            task.cancel()

    def record_pong(self, websocket: WebSocket):
        """Update last pong timestamp when client responds to ping."""
        self._last_pong[websocket] = time.monotonic()

    async def _heartbeat_loop(self, websocket: WebSocket, room_id: int):
        """Periodically send ping and check for stale connections."""
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL)

                # Check if client responded to previous ping
                last_pong = self._last_pong.get(websocket, 0)
                if time.monotonic() - last_pong > HEARTBEAT_INTERVAL + HEARTBEAT_TIMEOUT:
                    logger.info(
                        f"Heartbeat timeout for user "
                        f"{self.connection_user_map.get(websocket)} in room {room_id}"
                    )
                    self.disconnect(websocket, room_id)
                    try:
                        await websocket.close(code=1001, reason="Heartbeat timeout")
                    except Exception:
                        pass
                    break

                # Send ping (non-blocking best-effort)
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    logger.info(
                        f"Failed to send ping to user "
                        f"{self.connection_user_map.get(websocket)} in room {room_id}"
                    )
                    self.disconnect(websocket, room_id)
                    break
        except asyncio.CancelledError:
            pass

    async def broadcast_to_room(self, room_id: int, message: dict, exclude: WebSocket = None):
        """Send message to all connections in a room except the excluded one."""
        if room_id not in self.active_connections:
            return
        disconnected = []
        for connection in self.active_connections[room_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn, room_id)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    def is_user_online_in_room(self, room_id: int, user_id: int) -> bool:
        """Check if a user is connected to a specific room."""
        if room_id not in self.active_connections:
            return False
        for conn in self.active_connections[room_id]:
            if self.connection_user_map.get(conn) == user_id:
                return True
        return False

    def get_online_user_ids(self, room_id: int) -> set:
        """Get all online user IDs in a room."""
        if room_id not in self.active_connections:
            return set()
        return {
            self.connection_user_map[conn]
            for conn in self.active_connections[room_id]
            if conn in self.connection_user_map
        }


manager = ConnectionManager()
