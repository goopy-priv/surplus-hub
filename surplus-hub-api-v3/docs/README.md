# Surplus Hub API v3 - Documentation

Surplus Hub 백엔드 API 프로젝트 문서입니다. 건설 자재 마켓플레이스 플랫폼의 REST API를 제공합니다.

## Quick Links

- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **Admin 패널**: http://localhost:8000/admin

## Backend API 문서

| 문서 | 설명 |
|------|------|
| [온보딩 가이드](onboarding.md) | 개발 환경 설정 및 프로젝트 시작 |
| [시스템 아키텍처](architecture.md) | 레이어 구조, ER 다이어그램, 기술 스택 |
| [API 레퍼런스](api_guide.md) | 전체 엔드포인트 명세 및 스키마 |
| [DB 테스트 리포트](db_test_report.md) | 데이터베이스 연결 및 성능 테스트 결과 |
| [API 테스트 리포트](test_report.md) | 엔드포인트 기능 및 스키마 검증 결과 |

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (PyJWT + passlib/bcrypt) |
| Admin | SQLAdmin |
| Storage | AWS S3 (boto3) |
| Push | Firebase Admin |
| Rate Limit | slowapi |
| Deployment | Docker + Docker Compose |

## 프로젝트 구조

```text
surplus-hub-api-v3/
├── app/
│   ├── main.py                 # FastAPI 앱 엔트리포인트
│   ├── admin_views.py          # SQLAdmin 관리자 뷰
│   ├── core/                   # 설정, 인증, 보안 및 공통 모듈
│   │   ├── admin_auth.py       # 관리자 인증
│   │   ├── config.py           # 환경 설정 (Settings)
│   │   ├── push.py             # 푸시 알림
│   │   ├── rate_limit.py       # 요청 제한(Rate Limit)
│   │   ├── security.py         # JWT 토큰, 비밀번호 해싱
│   │   ├── storage.py          # 파일 저장소 (S3 등)
│   │   └── ws_manager.py       # 웹소켓 연결 관리
│   ├── db/                     # 데이터베이스 설정 및 연결
│   │   ├── base.py             # SQLAlchemy Base 모델
│   │   ├── database.py         # Async DB 연결
│   │   └── session.py          # Sync DB 세션 팩토리
│   ├── models/                 # SQLAlchemy 모델 정의 (DB 테이블)
│   │   ├── category.py, chat.py, community.py, event.py, like.py, material.py, notification.py, review.py, subscription.py, transaction.py, user.py 등
│   ├── schemas/                # Pydantic 스키마 (데이터 검증/DTO)
│   │   ├── (models와 대응하는 스키마 파일들)
│   ├── api/                    # API 라우터 (Endpoints)
│   │   ├── api.py              # 전체 앱 라우터 통합
│   │   ├── deps.py             # FastAPI 의존성 (DB, 인증)
│   │   └── endpoints/          # 도메인별 API 핸들러
│   │       ├── admin_api.py, auth.py, categories.py, chats.py, community.py, events.py, materials.py, notifications.py, reviews.py, transactions.py, upload.py, users.py, ws.py
│   ├── crud/                   # CRUD 패턴 인터페이스 (DB 데이터 로직)
│   │   ├── base.py             # 기본 CRUD 제네릭 구현
│   │   └── crud_*.py           # 도메인별 CRUD 구현체 (crud_category, crud_user 등)
│   └── tests/                  # 테스트 코드(Pytest)
│       ├── api/                # 엔드포인트 테스트
│       ├── conftest.py         # DB, 의존성 픽스처
│       └── test_health.py      # HealthCheck 테스트
├── alembic/                    # DB 마이그레이션 도구 패키지
├── docs/                       # 프로젝트 개발/명세 문서
├── alembic.ini                 # Alembic 구성 파일
├── Dockerfile                  # API 서버 컨테이너 빌드 설정
├── docker-compose.yml          # 인프라(DB) 컨테이너 실행 구성 
├── requirements.txt            # 파이썬 패키지 의존성 목록
├── create_test_user.py         # 테스트 사용자 생성 스크립트
└── .env                        # 환경 변수
```

## 빠른 시작

```bash
# 1. Docker로 실행
docker-compose up --build

# 2. API 문서 확인
open http://localhost:8000/docs

# 3. 테스트 실행
docker-compose exec web pytest
```

자세한 내용은 [온보딩 가이드](onboarding.md)를 참고하세요.

---

## Flutter 모바일 앱 문서 (참고용)

아래 문서들은 Surplus Hub Flutter 모바일 앱 프로젝트의 개발 가이드입니다.

<details>
<summary>Flutter 문서 목록 (클릭하여 펼치기)</summary>

- [프로젝트 개요](01-project-overview.md)
- [기술 스택](02-tech-stack.md)
- [개발 환경 설정](03-development-setup.md)
- [프로젝트 설정](04-project-setup.md)
- [폴더 구조](05-project-structure.md)
- [코딩 컨벤션](06-coding-conventions.md)
- [기능 개발 가이드](07-feature-development.md)
- [상태 관리 (BLoC)](08-state-management.md)
- [FAQ](15-faq.md)
- [트러블슈팅](16-troubleshooting.md)

</details>

---

*Last Updated: 2026-02-20*
