# Alembic 마이그레이션 실행 및 검증 계획서

## 작성자: migration-agent
## 대상: chatroom_unique_constraint.py (revision: chatroom_uq_001)

---

## 1. 현재 DB 상태 분석

### 확인 방법
```bash
cd /Users/jeongseongchae/dev/owner/surplus-hub-api-v3
source .venv/bin/activate
alembic current   # 현재 적용된 revision 확인
alembic history   # 전체 마이그레이션 히스토리 확인
alembic heads     # 최신 head revision 확인
```

### 현재 상태 (코드 기반 분석)
- **현재 HEAD (코드 상)**: `chatroom_uq_001` (chatroom_unique_constraint.py)
- **DB HEAD (예상)**: `ai_pgvector_001` (마이그레이션 미실행 상태로 명시됨)
- **마이그레이션 체인**: `chat_improve_001` -> `ai_pgvector_001` -> `chatroom_uq_001`

### SQLAlchemy 모델 현황
- `app/models/chat.py`의 `ChatRoom` 모델에는 이미 `UniqueConstraint("material_id", "buyer_id", "seller_id", name="uq_chatroom_material_buyer_seller")`가 선언되어 있음
- 즉, **모델은 이미 UNIQUE 제약조건을 선언하고 있으나, DB에는 아직 적용되지 않은 상태**

---

## 2. 실행 계획

### 단계 1: 사전 확인
```bash
# DB 연결 확인
alembic current

# 기존 데이터에 중복이 있는지 확인 (중복이 있으면 마이그레이션 실패)
psql $DATABASE_URL -c "
  SELECT material_id, buyer_id, seller_id, COUNT(*)
  FROM chat_rooms
  GROUP BY material_id, buyer_id, seller_id
  HAVING COUNT(*) > 1;
"
```

### 단계 2: 마이그레이션 실행
```bash
alembic upgrade head
```

### 단계 3: 적용 확인
```bash
alembic current  # chatroom_uq_001 확인

# 제약조건 확인
psql $DATABASE_URL -c "
  SELECT conname, contype
  FROM pg_constraint
  WHERE conrelid = 'chat_rooms'::regclass AND contype = 'u';
"
```

### 단계 4: 테스트 실행
```bash
pytest app/tests/api/test_chats.py -v
pytest app/tests/api/test_concurrency.py -v
pytest app/tests/api/test_chatroom_unique.py -v  # 새로 작성할 테스트
```

---

## 3. 동시성 테스트 시나리오

### 시나리오 A: 두 요청이 동시에 동일 (material_id=1, buyer_id=2, seller_id=3)으로 ChatRoom 생성 시도

**기대 결과:**
- 하나의 요청만 INSERT 성공, 다른 요청은 `IntegrityError` 발생
- `crud_chat.py`의 `get_or_create()` 메서드가 `IntegrityError`를 catch하고 rollback 후 기존 레코드를 SELECT하여 반환
- 결과적으로 **두 요청 모두 200 OK**를 반환하며, **동일한 room_id**를 반환

**현재 코드 분석 (`crud_chat.py:40-73`):**
```python
def get_or_create(self, db, *, material_id, buyer_id, seller_id):
    existing = db.query(ChatRoom).filter(...).first()
    if existing:
        return existing, False

    db_obj = ChatRoom(...)
    db.add(db_obj)
    try:
        db.commit()
        return db_obj, True
    except IntegrityError:
        db.rollback()
        existing = db.query(ChatRoom).filter(...).first()
        return existing, False
```

**Race condition 흐름:**
```
Thread A: SELECT -> NULL (없음)
Thread B: SELECT -> NULL (없음)
Thread A: INSERT -> 성공 (COMMIT)
Thread B: INSERT -> IntegrityError (UNIQUE 위반)
Thread B: ROLLBACK -> SELECT -> 기존 레코드 반환
```

이 패턴은 올바른 "check-then-create with retry" 패턴이며, DB-level UNIQUE 제약조건이 race condition의 최후 방어선 역할을 합니다.

### 시나리오 B: UNIQUE 제약 위반 시 API 레이어 에러 처리

**현재 동작:**
- `IntegrityError`는 CRUD 레이어에서 잡힘 (`crud_chat.py:62`)
- API 엔드포인트(`chats.py:87-96`)는 `get_or_create`의 반환값만 받으므로, 에러가 API 레벨까지 전파되지 않음
- 사용자는 항상 `{"status": "success", "data": {"id": <room_id>}}`를 받음

**잠재적 Edge Case:**
- `IntegrityError` 후 rollback 후 SELECT에서도 레코드를 못 찾는 경우 (삭제된 경우) -> `None` 반환 -> API에서 `None.id` 접근 시 `AttributeError` -> 500 에러
- 이 케이스는 실제로는 거의 발생하지 않음 (ChatRoom 삭제 기능이 없으므로)

### pytest 테스트 코드 초안

```python
"""TC-CONC-UQ: ChatRoom UNIQUE constraint concurrency tests.

이 테스트는 SQLite 환경에서 실행되므로 진정한 멀티스레드 동시성은 불가.
대신 CRUD 레이어의 IntegrityError 처리 로직을 직접 검증.
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.core.config import settings
from app.crud.crud_chat import crud_chat_room

API = settings.API_V1_STR


class TestChatRoomUniqueConstraint:
    """UNIQUE(material_id, buyer_id, seller_id) 제약조건 검증."""

    def test_same_params_return_same_room(
        self, client: TestClient, auth_headers, test_user2
    ):
        """동일 파라미터로 두 번 생성 요청 -> 같은 room_id 반환."""
        payload = {"sellerId": test_user2.id}
        resp1 = client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)
        resp2 = client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["data"]["id"] == resp2.json()["data"]["id"]

    def test_different_material_creates_different_room(
        self, client: TestClient, auth_headers, test_user2
    ):
        """다른 material_id -> 다른 채팅방 생성."""
        # material_id=None (기본)
        resp1 = client.post(
            f"{API}/chats/rooms",
            json={"sellerId": test_user2.id},
            headers=auth_headers,
        )
        # material_id가 다른 경우는 별도 채팅방
        # (materialId 필드가 있는 경우)
        assert resp1.status_code == 200

    def test_integrity_error_handled_gracefully(self, db, test_user, test_user2):
        """CRUD get_or_create가 IntegrityError를 gracefully 처리하는지 검증."""
        # 첫 번째 생성
        room1, created1 = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        assert room1 is not None

        # 같은 파라미터로 재생성 -> existing 반환
        room2, created2 = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        assert room2 is not None
        assert room1.id == room2.id
        assert created2 is False

    def test_rapid_creation_all_return_same_id(
        self, client: TestClient, auth_headers, test_user2
    ):
        """10회 연속 생성 요청 -> 모두 동일 room_id."""
        payload = {"sellerId": test_user2.id}
        results = [
            client.post(f"{API}/chats/rooms", json=payload, headers=auth_headers)
            for _ in range(10)
        ]
        assert all(r.status_code == 200 for r in results)
        room_ids = {r.json()["data"]["id"] for r in results}
        assert len(room_ids) == 1, f"Expected 1 unique room, got {room_ids}"


class TestChatRoomUniqueConstraintCRUD:
    """CRUD 레벨에서 IntegrityError 시뮬레이션."""

    def test_simulated_race_condition(self, db, test_user, test_user2):
        """
        Race condition 시뮬레이션:
        첫 SELECT -> None, INSERT -> IntegrityError, 재SELECT -> 기존 레코드
        """
        # 먼저 정상적으로 하나 생성
        room, _ = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        original_id = room.id

        # get_or_create의 IntegrityError 경로 테스트:
        # 실제 DB에 이미 존재하는 레코드와 동일한 값으로 재호출
        room2, created = crud_chat_room.get_or_create(
            db, material_id=None, buyer_id=test_user.id, seller_id=test_user2.id
        )
        assert room2.id == original_id
        assert created is False
```

---

## 4. 가정 목록

| # | 가정 | 확인 필요 여부 |
|---|------|---------------|
| 1 | PostgreSQL DB가 실행 중이고 접근 가능하다 | **확인 필요** — `alembic current`로 확인 |
| 2 | `ai_pgvector_001`까지의 모든 마이그레이션이 이미 적용되어 있다 | **확인 필요** — `alembic current`로 확인 |
| 3 | `chat_rooms` 테이블에 (material_id, buyer_id, seller_id) 중복 데이터가 없다 | **확인 필요** — SQL 쿼리로 확인. 중복이 있으면 마이그레이션 실패 |
| 4 | 테스트 환경은 SQLite in-memory를 사용한다 (conftest.py 확인 완료) | 확인 완료 |
| 5 | ChatRoom 삭제 기능이 없으므로 `IntegrityError` 후 재SELECT 시 `None` 반환은 발생하지 않는다 | 코드 기반 확인 완료 |
| 6 | `material_id`가 `nullable=True`이므로 NULL 값도 UNIQUE 제약조건에 포함된다. PostgreSQL에서 NULL != NULL이므로 material_id=NULL인 동일 buyer/seller 쌍은 **여러 개 생성 가능** | **주의 필요** — 이 동작이 의도된 것인지 확인 필요 |

### 가정 #6에 대한 상세 분석 (중요)

PostgreSQL의 UNIQUE 제약조건은 NULL 값에 대해 `NULL != NULL`로 평가합니다. 즉:

```sql
-- 이 두 행은 UNIQUE 위반이 아님 (PostgreSQL)
INSERT INTO chat_rooms (material_id, buyer_id, seller_id) VALUES (NULL, 1, 2);
INSERT INTO chat_rooms (material_id, buyer_id, seller_id) VALUES (NULL, 1, 2);
```

**영향**: `material_id=None`으로 채팅방을 생성할 때, UNIQUE 제약조건이 race condition을 방어하지 못합니다. 하지만 현재 `get_or_create`의 application-level SELECT 체크가 1차 방어선 역할을 하므로 대부분의 경우 문제 없습니다.

**개선 방안** (이번 스코프 외, 향후 고려):
- `UNIQUE NULLS NOT DISTINCT` (PostgreSQL 15+) 사용
- 또는 `COALESCE(material_id, 0)` 기반의 partial unique index 생성

---

## 5. 롤백 전략

### 마이그레이션 롤백
```bash
# chatroom_uq_001만 되돌리기
alembic downgrade ai_pgvector_001
```

### downgrade 함수 검증
```python
def downgrade() -> None:
    op.drop_constraint("uq_chatroom_material_buyer_seller", "chat_rooms", type_="unique")
```
- 제약조건만 제거하므로 데이터 손실 없음
- 안전하게 롤백 가능

### 롤백이 필요한 상황
1. 마이그레이션 실행 중 중복 데이터로 인한 실패 -> 중복 데이터 정리 후 재실행
2. 제약조건 적용 후 기존 기능에서 예상치 못한 에러 발생
3. NULL material_id 관련 동작이 기대와 다른 경우

### 긴급 롤백 절차
```bash
alembic downgrade ai_pgvector_001
# 테스트 실행하여 이전 상태 확인
pytest app/tests/api/test_chats.py -v
```

---

## 요약

| 항목 | 내용 |
|------|------|
| 마이그레이션 파일 | `alembic/versions/chatroom_unique_constraint.py` |
| Revision | `chatroom_uq_001` |
| 변경 내용 | `chat_rooms` 테이블에 `UNIQUE(material_id, buyer_id, seller_id)` 추가 |
| 위험도 | **낮음** — 제약조건 추가만, 데이터/스키마 변경 없음 |
| 핵심 보호 장치 | CRUD의 `get_or_create` + DB UNIQUE 제약조건 (이중 방어) |
| 주요 리스크 | NULL material_id 시 UNIQUE 미적용 (PostgreSQL NULL != NULL) |
