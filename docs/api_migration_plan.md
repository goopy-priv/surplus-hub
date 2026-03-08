# API 마이그레이션 및 구현 계획

이 문서는 현재 클라이언트 앱(`surplus-hub-flutter`)에서 더미 데이터로 동작 중인 기능들을 백엔드 API(`surplus-hub-api-v3`)로 이관하기 위한 상세 분석 및 구현 계획을 담고 있습니다.

## 1. 백엔드 시스템 분석 (Backend Analysis)

### 1.1 기술 스택 및 환경
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM 사용)
- **Migration**: Alembic
- **API Spec**: OpenAPI (Swagger/ReDoc)
- **Authentication**: JWT (JSON Web Tokens) - `HS256` 알고리즘
- **Configuration**: Pydantic Settings (`.env` 파일 기반)

### 1.2 현재 API 구현 상태 (Current State)
백엔드 코드를 분석한 결과, 대부분의 엔드포인트가 **스켈레톤(Skeleton) 상태**이거나 **하드코딩된 더미 응답**을 반환하고 있습니다.

| 기능 | 엔드포인트 | 상태 | 문제점 |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST /auth/login/access-token` | ⚠️ Dummy | 고정된 토큰(`dummy_token`) 반환. 실제 인증 로직 부재. |
| **Materials** | `GET /materials/` | ⚠️ Mock | 빈 리스트(`[]`) 반환. DB 연동 없음. |
| **Materials** | `POST /materials/` | ⚠️ Mock | 요청 데이터를 그대로 반환(Echo). DB 저장 안 됨. |
| **Chats** | `GET /chats/rooms` | ⚠️ Mock | 빈 리스트(`[]`) 반환. DB 연동 없음. |
| **Community** | `GET /community/posts` | ⚠️ Mock | 빈 리스트(`[]`) 반환. DB 연동 없음. |
| **Users** | `GET /users/me` | ⚠️ Hardcoded | 고정된 사용자 정보('김철수') 반환. DB 연동 없음. |

### 1.3 데이터베이스 모델 (Database Models)
DB 모델(`app/models/`)은 정의되어 있으나, 실제 API 로직(`app/api/endpoints/`)에서 이를 활용하지 않고 있습니다.
- `User`: 기본 사용자 정보, 매너 온도, 신뢰도 등 포함.
- `Material`: 자재 정보, 위치(위도/경도), 판매자 관계 포함.
- `ChatRoom`, `Message`: 채팅방 및 메시지 모델 존재.
- `Post`, `Comment`: 커뮤니티 게시글 및 댓글 모델 존재.

---

## 2. 요구사항 정의 (Requirements)

클라이언트의 더미 데이터 기능을 대체하기 위해 다음 API들의 **실제 로직 구현**이 필요합니다.

### 2.1 Chat API (채팅)
- **목표**: 채팅방 목록 조회 및 메시지 송수신 기능 활성화.
- **구현 대상**:
  - `GET /chats/rooms`: 사용자별 채팅방 목록 조회 (DB `chat_rooms` 테이블 조인).
  - `GET /chats/rooms/{room_id}/messages`: 특정 채팅방의 메시지 내역 조회.
  - `POST /chats/rooms`: 자재 상세 페이지에서 채팅방 생성.
  - **Socket/Polling**: 실시간 메시징을 위한 WebSocket 엔드포인트 (`/ws/chats/{room_id}`) 필요.

### 2.2 Community API (커뮤니티)
- **목표**: 게시글 CRUD 및 카테고리 필터링.
- **구현 대상**:
  - `GET /community/posts`: 게시글 목록 조회 (페이지네이션, `category` 필터 지원).
  - `POST /community/posts`: 게시글 작성 (제목, 내용, 카테고리).
  - `GET /community/posts/{post_id}`: 게시글 상세 조회.

### 2.3 Profile API (프로필)
- **목표**: 실제 로그인한 사용자 정보 제공.
- **구현 대상**:
  - `GET /users/me`: `Authorization` 헤더의 JWT를 파싱하여 DB에서 해당 유저 정보 조회.
  - `PATCH /users/me`: 프로필 정보(이미지, 닉네임) 수정.

### 2.4 Register/Material API (자재)
- **목표**: 자재 등록 및 조회, 검색.
- **구현 대상**:
  - `POST /materials/`: 클라이언트 폼 데이터를 DB `materials` 테이블에 저장.
  - `GET /materials/`: 위치 기반(위도/경도) 거리순 정렬 및 검색어(`keyword`) 필터링 구현.
  - `GET /materials/{id}`: 자재 상세 정보 조회.

---

## 3. 구현 계획 (Implementation Roadmap)

### Phase 1: 데이터베이스 및 인증 기반 강화 (Priority: High)
1. **DB 마이그레이션**: `alembic`을 사용하여 정의된 모델(`models/*.py`)을 실제 DB 테이블로 생성.
2. **인증 로직 구현**:
   - `login_access_token`에서 실제 `User` 테이블 조회 및 패스워드 검증(`bcrypt`).
   - `create_access_token` 유틸리티 구현.
   - `get_current_user` 의존성(Dependency) 구현하여 보호된 라우트 처리.

### Phase 2: 핵심 기능 API 로직 구현 (Priority: High)
1. **Users**: `GET /users/me`를 실제 DB 데이터 반환하도록 수정.
2. **Materials**:
   - `POST /materials/`에 DB Insert 로직 추가.
   - `GET /materials/`에 SQLAlchemy Query 및 필터링 적용.
   - `GET /materials/{id}` 구현.

### Phase 3: 커뮤니티 및 채팅 기능 구현 (Priority: Medium)
1. **Community**: `Post` 모델 CRUD API 구현.
2. **Chat**:
   - 채팅방 생성/조회 API 구현.
   - (Optional) WebSocket 도입 전, HTTP Polling 방식의 메시지 조회 우선 구현.

### Phase 4: 이미지 업로드 처리 (Priority: Medium)
- 현재 클라이언트는 `via.placeholder.com`을 사용 중.
- **AWS S3** 또는 **로컬 파일 시스템**을 이용한 이미지 업로드 엔드포인트(`POST /upload/`) 구현 필요.

---

## 4. 검증 전략 (Verification Strategy)

### 4.1 개발 환경 검증
- **Swagger UI (`/docs`)**: 각 엔드포인트별 요청/응답 테스트.
- **Unit Test**: `tests/api/` 폴더 내의 테스트 케이스를 실제 로직에 맞게 수정 및 실행.
  - 예: `test_create_material`이 실제 DB에 데이터를 넣고 ID를 반환하는지 확인.

### 4.2 통합 테스트 (Integration Test)
- 클라이언트(`surplus-hub-flutter`)의 `api_endpoints.dart`가 실제 서버를 가리키도록 설정(`localhost:8000` or `10.0.2.2`).
- 앱 실행 후 로그인 -> 자재 등록 -> 홈 화면 노출 -> 상세 진입 -> 채팅방 생성 흐름이 끊기지 않는지 확인.

### 4.3 롤백 전략
- Git 브랜치 관리: 기능별 `feature/api-migration-*` 브랜치 사용.
- DB 백업: 마이그레이션 전 데이터 덤프.

---

## 5. 결론
현재 백엔드는 구조는 잘 잡혀 있으나 "껍데기" 상태입니다. 클라이언트가 더미 데이터를 걷어내려면 백엔드의 **DB 연동(Service Layer)**과 **인증(Auth)** 구현이 시급합니다. Phase 1과 Phase 2를 우선적으로 진행해야 합니다.
