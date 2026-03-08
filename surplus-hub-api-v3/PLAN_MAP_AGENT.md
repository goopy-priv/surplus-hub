# P3: 지도 연동 구현 계획서

## 1. 현재 LOCATION 처리 상태 (실제 코드 기반)

### Message 모델 (`app/models/chat.py:24-38`)
- `message_type` 필드: `Column(String, default="TEXT")` 주석에 `# TEXT, IMAGE, LOCATION`이 명시됨
- `content` 필드: `Column(Text, nullable=False)` - 단순 텍스트 필드
- **LOCATION 타입은 DB 스키마에 정의되어 있으나, 처리 로직이 전혀 구현되어 있지 않음**

### WebSocket (`app/api/endpoints/ws.py:131`)
- `msg_type in ("text", "image")` 조건만 처리 -- `"location"` 타입은 무시됨
- LOCATION 메시지 전송 시 아무 에러 없이 조용히 무시되는 상태

### REST API (`app/api/endpoints/chats.py:160-218`)
- `MessageCreate` 스키마: `message_type: str = Field("TEXT", alias="messageType")` -- 어떤 문자열이든 가능
- `create_message` 라우트는 `message_type`을 그대로 DB에 저장하므로 REST로는 LOCATION 저장 가능하나, 위치 데이터 검증이 전혀 없음

### Material 모델 (`app/models/material.py:36-38`)
- `location_address`, `location_lat`, `location_lng` 필드가 이미 존재
- `@property location` 메서드가 `{"address": ..., "lat": ..., "lng": ...}` 딕셔너리 반환
- **자재의 위치 정보 구조가 이미 패턴으로 확립되어 있음 -- LOCATION 메시지도 이와 동일한 구조 활용 권장**

### 스키마 (`app/schemas/chat_response.py`)
- `Message` 스키마: `content: str` -- LOCATION일 때의 별도 직렬화 없음
- `MessageCreate` 스키마: content 검증 없음 (빈 문자열도 가능)

---

## 2. 지도 연동 설계

### 2.1 LOCATION 메시지 데이터 포맷

LOCATION 메시지의 `content` 필드에 JSON 문자열로 위치 데이터를 저장:

```json
{
  "latitude": 37.5665,
  "longitude": 126.9780,
  "address": "서울특별시 중구 세종대로 110",
  "title": "서울시청"
}
```

**근거:**
- 기존 `content: Text` 컬럼을 재활용하여 DB 마이그레이션 불필요
- Material 모델의 위치 패턴(lat/lng/address)과 일관성 유지
- `title`은 선택적 -- 사용자가 장소명을 지정할 수 있음
- JSON 직렬화/역직렬화는 서버 측에서 검증 후 저장

### 2.2 WebSocket 전송 방식

클라이언트 -> 서버:
```json
{
  "type": "location",
  "content": {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "address": "서울특별시 중구 세종대로 110",
    "title": "서울시청"
  }
}
```

서버 -> 클라이언트 (broadcast):
```json
{
  "type": "message",
  "data": {
    "id": 123,
    "content": "{\"latitude\":37.5665,\"longitude\":126.9780,\"address\":\"서울특별시 중구 세종대로 110\",\"title\":\"서울시청\"}",
    "messageType": "LOCATION",
    "senderId": 1,
    "senderName": "홍길동",
    "isRead": false,
    "createdAt": "2026-02-22T10:00:00+00:00"
  }
}
```

**설계 결정:**
- 클라이언트는 `content`를 JSON 객체로 전송
- 서버가 검증 후 JSON **문자열**로 직렬화하여 DB 저장
- 응답의 `content`는 JSON 문자열 -- 클라이언트가 `messageType === "LOCATION"`일 때 파싱
- 이 방식은 기존 `content: Text` 컬럼 구조를 깨지 않음

### 2.3 REST API 전송 방식

`POST /chats/rooms/{room_id}/messages`:
```json
{
  "content": "{\"latitude\":37.5665,\"longitude\":126.9780,\"address\":\"서울특별시 중구 세종대로 110\"}",
  "messageType": "LOCATION"
}
```

서버 측에서 `messageType == "LOCATION"`일 때 `content`가 올바른 위치 JSON인지 검증.

### 2.4 외부 지도 API 필요 여부

**불필요.** 이유:
- 위치 데이터(lat/lng/address)는 클라이언트(모바일 앱)에서 디바이스 GPS 또는 지도 SDK(네이버/카카오)를 통해 직접 제공
- 서버는 위치 데이터를 **저장/전달**만 하면 됨
- 역지오코딩(좌표->주소 변환)은 클라이언트 앱에서 처리
- 지도 렌더링도 클라이언트 앱의 지도 SDK가 처리

향후 필요 시 추가할 수 있는 선택적 기능:
- 서버 측 역지오코딩 (주소 없이 좌표만 올 때) -- 현 단계에서는 YAGNI

### 2.5 위치 검증 유틸리티

```python
# app/utils/location.py
import json
from typing import Optional

class LocationData:
    """위치 데이터 검증 및 직렬화"""

    def __init__(self, latitude: float, longitude: float,
                 address: Optional[str] = None, title: Optional[str] = None):
        if not (-90 <= latitude <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("longitude must be between -180 and 180")
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.title = title

    def to_json_string(self) -> str:
        data = {"latitude": self.latitude, "longitude": self.longitude}
        if self.address:
            data["address"] = self.address
        if self.title:
            data["title"] = self.title
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "LocationData":
        lat = data.get("latitude")
        lng = data.get("longitude")
        if lat is None or lng is None:
            raise ValueError("latitude and longitude are required")
        return cls(
            latitude=float(lat),
            longitude=float(lng),
            address=data.get("address"),
            title=data.get("title"),
        )

    @classmethod
    def from_json_string(cls, s: str) -> "LocationData":
        return cls.from_dict(json.loads(s))
```

---

## 3. 동시성 테스트 시나리오

### 시나리오 A: 10개 WebSocket 클라이언트 동시 LOCATION 전송 -- 순서 보장 테스트

```python
# app/tests/api/test_location_concurrency.py
import asyncio
import json
import time
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.core.ws_manager import ConnectionManager, manager
from app.models.chat import ChatRoom, Message
from app.tests.conftest import TestingSessionLocal


class TestLocationConcurrency:
    """LOCATION 메시지 동시 전송 시 순서 보장 테스트"""

    @pytest.fixture(autouse=True)
    def cleanup_manager(self):
        manager.active_connections.clear()
        manager.connection_user_map.clear()
        manager._user_connection_count.clear()
        manager._total_connections = 0
        for task in list(manager._heartbeat_tasks.values()):
            if not task.done():
                task.cancel()
        manager._heartbeat_tasks.clear()
        manager._last_pong.clear()
        yield
        manager.active_connections.clear()
        manager.connection_user_map.clear()
        manager._user_connection_count.clear()
        manager._total_connections = 0
        for task in list(manager._heartbeat_tasks.values()):
            if not task.done():
                task.cancel()
        manager._heartbeat_tasks.clear()
        manager._last_pong.clear()

    @pytest.fixture()
    def test_room(self, test_user, test_user2):
        db = TestingSessionLocal()
        try:
            room = ChatRoom(buyer_id=test_user.id, seller_id=test_user2.id)
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
        finally:
            db.close()

    def test_sequential_location_messages_maintain_order(
        self, client: TestClient, test_room, test_user, test_user2
    ):
        """10개의 LOCATION 메시지를 순차 전송 후, DB에 created_at 순서대로 저장되는지 검증."""
        token1 = create_access_token(subject=test_user.id)
        token2 = create_access_token(subject=test_user2.id)

        locations = [
            {"latitude": 37.0 + i * 0.01, "longitude": 127.0 + i * 0.01,
             "address": f"위치 {i}"}
            for i in range(10)
        ]

        with patch("app.api.endpoints.ws.get_db_session",
                    side_effect=lambda: TestingSessionLocal()), \
             patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"), \
             patch("app.core.push.send_chat_notification"):

            with client.websocket_connect(
                f"/ws/chat/{test_room.id}?token={token1}"
            ) as ws1:
                with client.websocket_connect(
                    f"/ws/chat/{test_room.id}?token={token2}"
                ) as ws2:
                    # 10개 위치 메시지 순차 전송
                    for loc in locations:
                        ws1.send_json({"type": "location", "content": loc})
                        # ws2가 수신 확인
                        data = ws2.receive_json()
                        assert data["type"] == "message"
                        assert data["data"]["messageType"] == "LOCATION"
                        # ws1 자신도 수신 확인
                        data1 = ws1.receive_json()
                        assert data1["type"] == "message"

        # DB 순서 검증
        db = TestingSessionLocal()
        try:
            msgs = (
                db.query(Message)
                .filter(
                    Message.chat_room_id == test_room.id,
                    Message.message_type == "LOCATION",
                )
                .order_by(Message.id)
                .all()
            )
            assert len(msgs) == 10
            for i, msg in enumerate(msgs):
                parsed = json.loads(msg.content)
                assert abs(parsed["latitude"] - (37.0 + i * 0.01)) < 0.001
                assert parsed["address"] == f"위치 {i}"
        finally:
            db.close()

    def test_concurrent_rest_location_messages(
        self, client: TestClient, test_room, test_user, auth_headers
    ):
        """REST API로 여러 LOCATION 메시지를 빠르게 전송해도 모두 정상 저장."""
        for i in range(5):
            loc_content = json.dumps({
                "latitude": 35.0 + i * 0.1,
                "longitude": 129.0 + i * 0.1,
                "address": f"REST 위치 {i}",
            })
            resp = client.post(
                f"/api/v1/chats/rooms/{test_room.id}/messages",
                json={"content": loc_content, "messageType": "LOCATION"},
                headers=auth_headers,
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["data"]["messageType"] == "LOCATION"

        # DB 검증
        db = TestingSessionLocal()
        try:
            msgs = (
                db.query(Message)
                .filter(
                    Message.chat_room_id == test_room.id,
                    Message.message_type == "LOCATION",
                )
                .all()
            )
            assert len(msgs) == 5
        finally:
            db.close()
```

### 시나리오 B: 위치 데이터 형식 검증 실패 시 에러 처리

```python
class TestLocationValidation:
    """LOCATION 메시지 데이터 형식 검증 실패 테스트"""

    @pytest.fixture(autouse=True)
    def cleanup_manager(self):
        manager.active_connections.clear()
        manager.connection_user_map.clear()
        manager._user_connection_count.clear()
        manager._total_connections = 0
        for task in list(manager._heartbeat_tasks.values()):
            if not task.done():
                task.cancel()
        manager._heartbeat_tasks.clear()
        manager._last_pong.clear()
        yield
        manager.active_connections.clear()
        manager.connection_user_map.clear()

    @pytest.fixture()
    def test_room(self, test_user, test_user2):
        db = TestingSessionLocal()
        try:
            room = ChatRoom(buyer_id=test_user.id, seller_id=test_user2.id)
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
        finally:
            db.close()

    def test_location_missing_latitude(
        self, client: TestClient, test_room, test_user
    ):
        """latitude 누락 시 에러 응답."""
        token = create_access_token(subject=test_user.id)

        with patch("app.api.endpoints.ws.get_db_session",
                    side_effect=lambda: TestingSessionLocal()), \
             patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"), \
             patch("app.core.push.send_chat_notification"):

            with client.websocket_connect(
                f"/ws/chat/{test_room.id}?token={token}"
            ) as ws:
                ws.send_json({
                    "type": "location",
                    "content": {"longitude": 126.978}  # latitude 누락
                })
                data = ws.receive_json()
                assert data["type"] == "error"
                assert "latitude" in data["data"]["detail"].lower()

    def test_location_invalid_latitude_range(
        self, client: TestClient, test_room, test_user
    ):
        """latitude 범위 초과 시 에러 응답."""
        token = create_access_token(subject=test_user.id)

        with patch("app.api.endpoints.ws.get_db_session",
                    side_effect=lambda: TestingSessionLocal()), \
             patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"), \
             patch("app.core.push.send_chat_notification"):

            with client.websocket_connect(
                f"/ws/chat/{test_room.id}?token={token}"
            ) as ws:
                ws.send_json({
                    "type": "location",
                    "content": {"latitude": 999.0, "longitude": 126.978}
                })
                data = ws.receive_json()
                assert data["type"] == "error"

    def test_location_non_numeric_coordinates(
        self, client: TestClient, test_room, test_user
    ):
        """좌표가 숫자가 아닌 경우 에러 응답."""
        token = create_access_token(subject=test_user.id)

        with patch("app.api.endpoints.ws.get_db_session",
                    side_effect=lambda: TestingSessionLocal()), \
             patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"), \
             patch("app.core.push.send_chat_notification"):

            with client.websocket_connect(
                f"/ws/chat/{test_room.id}?token={token}"
            ) as ws:
                ws.send_json({
                    "type": "location",
                    "content": {"latitude": "invalid", "longitude": "bad"}
                })
                data = ws.receive_json()
                assert data["type"] == "error"

    def test_location_content_not_dict(
        self, client: TestClient, test_room, test_user
    ):
        """content가 딕셔너리가 아닌 경우 에러 응답."""
        token = create_access_token(subject=test_user.id)

        with patch("app.api.endpoints.ws.get_db_session",
                    side_effect=lambda: TestingSessionLocal()), \
             patch("app.core.ws_manager.ConnectionManager._heartbeat_loop"), \
             patch("app.core.push.send_chat_notification"):

            with client.websocket_connect(
                f"/ws/chat/{test_room.id}?token={token}"
            ) as ws:
                ws.send_json({
                    "type": "location",
                    "content": "not a dict"
                })
                data = ws.receive_json()
                assert data["type"] == "error"

    def test_rest_location_invalid_json_content(
        self, client: TestClient, test_room, auth_headers
    ):
        """REST API에서 LOCATION 타입인데 content가 유효한 위치 JSON이 아닌 경우 422."""
        resp = client.post(
            f"/api/v1/chats/rooms/{test_room.id}/messages",
            json={"content": "not valid json", "messageType": "LOCATION"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
```

---

## 4. 가정 목록

| # | 가정 | 근거 |
|---|------|------|
| 1 | DB 마이그레이션 불필요 | `content: Text` 컬럼에 JSON 문자열 저장. `message_type` 이미 `LOCATION` 지원 |
| 2 | 외부 지도 API 불필요 | 위치 데이터는 클라이언트가 제공. 서버는 저장/전달만 |
| 3 | `address`와 `title`은 선택적 | 클라이언트가 GPS 좌표만 보낼 수도 있음 |
| 4 | conftest.py에 `test_user`, `test_user2`, `auth_headers`, `auth_headers2` fixture 존재 | test_chats.py, test_websocket.py에서 사용 중인 것 확인 |
| 5 | Material 위치의 공유는 별도 기능 | "자재 위치 공유" 기능(채팅에서 Material 위치를 빠르게 전송)은 이 단계에서 미구현 |

---

## 5. 파일 수정 계획

| # | 파일 | 변경 내용 |
|---|------|-----------|
| 1 | `app/utils/location.py` | **신규 생성** -- `LocationData` 클래스 (검증 + 직렬화) |
| 2 | `app/api/endpoints/ws.py` | `"location"` 타입 핸들러 추가 (131번째 줄 부근, `text/image` 조건 옆에) |
| 3 | `app/api/endpoints/chats.py` | `create_message` 라우트에서 `messageType == "LOCATION"` 시 content 검증 로직 추가 |
| 4 | `app/tests/api/test_location.py` | **신규 생성** -- 동시성 테스트 + 검증 실패 테스트 |

### 변경하지 않는 파일:
- `app/models/chat.py` -- 스키마 변경 없음 (이미 LOCATION 지원)
- `app/schemas/chat_response.py` -- content는 문자열로 유지 (JSON 파싱은 클라이언트 책임)
- `app/crud/crud_chat.py` -- create_message 시그니처 변경 없음
- Alembic 마이그레이션 -- 테이블 변경 없음

### 세부 변경 사항:

#### `app/api/endpoints/ws.py` 수정 (핵심)

현재 (131줄):
```python
if msg_type in ("text", "image"):
```

변경 후:
```python
if msg_type in ("text", "image"):
    # ... 기존 로직 유지 ...

elif msg_type == "location":
    content_data = data.get("content")
    try:
        location = LocationData.from_dict(content_data)
        content = location.to_json_string()
    except (ValueError, TypeError, AttributeError) as e:
        await manager.send_personal(websocket, {
            "type": "error",
            "data": {"detail": f"Invalid location data: {e}"}
        })
        continue

    # DB 저장 및 브로드캐스트 (text/image와 동일 패턴)
    db = get_db_session()
    try:
        msg = crud_message.create_message(
            db, room_id=room_id, sender_id=user_id,
            content=content, message_type="LOCATION",
        )
        message_data = { ... }  # 기존 패턴과 동일
    finally:
        db.close()

    await manager.broadcast_to_room(room_id, message_data, exclude=websocket)
    await manager.send_personal(websocket, message_data)
```

#### `app/api/endpoints/chats.py` 수정

`create_message` 라우트에서 LOCATION 검증:
```python
if message_in.message_type == "LOCATION":
    try:
        location = LocationData.from_json_string(message_in.content)
        # 재직렬화하여 정규화된 JSON 저장
        validated_content = location.to_json_string()
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid location data: {e}")
    message_in_content = validated_content
else:
    message_in_content = message_in.content
```
