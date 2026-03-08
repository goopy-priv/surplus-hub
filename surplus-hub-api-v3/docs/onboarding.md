# Surplus Hub API - Onboarding Guide

## 1. Project Overview

건설 잉여자재 거래 마켓플레이스 플랫폼의 백엔드 API입니다.

| 항목 | 값 |
|------|------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy |
| Auth | JWT (PyJWT + passlib/bcrypt) |
| Admin | SQLAdmin |
| Storage | AWS S3 (boto3) |
| Push | Firebase Admin |
| Rate Limit | slowapi |
| Deployment | Docker + Docker Compose |

## 2. Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) & Docker Compose
- [Python 3.11+](https://www.python.org/downloads/) (로컬 개발 시)

## 3. Getting Started

### Docker로 실행 (권장)

```bash
# 1. 저장소 클론
git clone <repository-url>
cd surplus-hub-api-v3

# 2. 컨테이너 빌드 및 실행
docker-compose up --build
```

실행되면:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5433

### 로컬 실행 (Docker 없이)

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env 파일 확인)
# DATABASE_URL이 로컬 PostgreSQL을 가리키는지 확인

# 4. DB 마이그레이션 실행
alembic upgrade head

# 5. 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Environment Variables

`.env` 파일에 다음 변수들이 필요합니다:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=apppass
DATABASE_URL=postgresql://appuser:apppass@localhost:5432/appdb

# JWT Auth
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Clerk Auth (선택)
CLERK_PEM_PUBLIC_KEY=<clerk-public-key>
```

## 5. Project Structure

```text
surplus-hub-api-v3/
├── app/
│   ├── main.py              # FastAPI 앱 엔트리포인트, CORS, Admin, 라우터 등록
│   ├── admin_views.py       # SQLAdmin 관리자 뷰
│   ├── core/                # 설정, 인증, 보안 및 공통 모듈 (push, ws_manager 등)
│   ├── db/                  # 데이터베이스 설정 및 연결
│   ├── models/              # SQLAlchemy ORM 모델
│   │   ├── category.py, chat.py, community.py, event.py, like.py, material.py, notification.py, review.py, subscription.py, transaction.py, user.py 등
│   ├── schemas/             # Pydantic 스키마 (camelCase alias 지원)
│   ├── api/                 # API 라우터
│   │   ├── api.py           # 라우터 통합 (/api/v1 prefix)
│   │   ├── deps.py          # 의존성 주입 (get_db, get_current_user 등)
│   │   └── endpoints/       # 도메인별 API 핸들러
│   │       ├── admin_api.py, auth.py, categories.py, chats.py, community.py, events.py, materials.py, notifications.py, reviews.py, transactions.py, upload.py, users.py, ws.py
│   ├── crud/                # DB 데이터 조작용 도메인별 CRUD 구현체
│   └── tests/               # pytest 테스트 (API, Health, DB)
├── alembic/                 # DB 마이그레이션 도구 패키지
├── docs/                    # 프로젝트 문서
├── alembic.ini              # Alembic 설정
├── .env                     # 환경 변수
├── Dockerfile               # API 서버 컨테이너 빌드 설정
├── docker-compose.yml       # 인프라(DB) 컨테이너 실행 구성 
├── requirements.txt         # 파이썬 패키지 의존성 목록
└── create_test_user.py      # 테스트 사용자 생성 유틸리티
```

## 6. Development Workflow

### DB 마이그레이션

```bash
# 모델 변경 후 마이그레이션 자동 생성
docker-compose exec web alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
docker-compose exec web alembic upgrade head

# 마이그레이션 롤백
docker-compose exec web alembic downgrade -1
```

### 테스트 실행

```bash
# Docker 환경
docker-compose exec web pytest

# 로컬 환경
pytest app/tests/
```

### 테스트 사용자 생성

```bash
python create_test_user.py
```

### 새 의존성 추가

```bash
# 1. requirements.txt에 패키지 추가
# 2. 컨테이너 재빌드
docker-compose up --build
```

## 7. API Modules

| 모듈 | Prefix | 주요 기능 |
|------|--------|-----------|
| **Auth** | `/api/v1/auth` | 로그인, JWT 토큰 발급 |
| **Users** | `/api/v1/users` | 사용자 목록 (관리자), 내 프로필 조회 |
| **Materials** | `/api/v1/materials` | 자재 CRUD, 검색, 필터링, 정렬 |
| **Chats** | `/api/v1/chats` | 채팅방 목록/생성, 메시지 조회/전송 |
| **Community** | `/api/v1/community` | 게시글 목록/작성, 커멘트 |
| **Notifications** | `/api/v1/notifications` | 알림 목록, 확인 및 디바이스 토큰 등록 |
| **Reviews** | `/api/v1/reviews` | 거래 후기 및 평점 |
| **Transactions** | `/api/v1/transactions` | 자재 거래 매칭 및 확정 프로세스 |
| **Upload** | `/api/v1/upload` | AWS S3 파일 업로드 및 Presigned URL |
| **Events** | `/api/v1/events` | 이벤트(배너/프로모션) 조회 |
| **Categories** | `/api/v1/categories` | 자재 품목 카테고리 목록 |

상세 엔드포인트는 [API 레퍼런스](api_guide.md)를 참고하세요.

## 8. Coding Standards

- **PEP 8** 스타일 가이드 준수
- **Type Hints** 모든 함수 인자와 반환 타입에 적용
- 새 엔드포인트는 반드시 **Pydantic 스키마** 정의
- 응답은 **StandardResponse** 래퍼 사용
- 스키마 필드명은 **camelCase alias** 지원 (프론트엔드 호환)
- 새 기능은 **테스트** 작성 필수

---

*Last Updated: 2026-02-20*
