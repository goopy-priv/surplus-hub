# Surplus Hub API (Backend) - 신입 개발자 온보딩 가이드

환영합니다! 👋
이 문서는 **Surplus Hub API (Backend)** 프로젝트에 처음 합류한 개발자를 위한 종합 가이드입니다. 서버 구조를 이해하고, 개발 환경을 설정하며, 안정적으로 서비스를 운영하는 방법을 단계별로 설명합니다.

---

## 1. 프로젝트 개요

**Surplus Hub API**는 잉여 자재 직거래 플랫폼의 백엔드 서비스를 담당합니다. RESTful API를 제공하며, 사용자 인증, 자재 관리, 실시간 채팅, 커뮤니티 기능을 지원합니다.

### 기술 스택
*   **Language**: Python 3.10+
*   **Web Framework**: FastAPI (High performance, Easy-to-use)
*   **Server**: Uvicorn (ASGI)
*   **Database**: PostgreSQL (Production), SQLite (Dev option)
*   **ORM**: SQLAlchemy (Core & ORM)
*   **Migration**: Alembic
*   **Validation**: Pydantic v2
*   **Authentication**: JWT (JSON Web Tokens)
*   **Admin Panel**: SQLAdmin

### 프로젝트 구조 (`surplus-hub-api-v3/`)
```
app/
├── api/                # API 라우터 및 엔드포인트 정의
│   ├── endpoints/      # 기능별 API (auth, users, materials 등)
│   └── api.py          # 라우터 통합
├── core/               # 핵심 설정 (Config, Security)
├── db/                 # 데이터베이스 연결 및 세션 관리
├── models/             # SQLAlchemy DB 모델 정의 (Table Schema)
├── schemas/            # Pydantic DTO 스키마 (Request/Response)
├── tests/              # Pytest 테스트 코드
├── admin_views.py      # 관리자 페이지 뷰 설정
└── main.py             # 앱 진입점 (FastAPI 인스턴스 생성)
alembic/                # DB 마이그레이션 스크립트
requirements.txt        # 의존성 패키지 목록
.env                    # 환경 변수 (Git 제외)
```

---

## 2. 개발 환경 설정 (Setup)

### 필수 요구사항
*   **Python**: 3.10 이상
*   **Database**: PostgreSQL (권장) 또는 로컬 개발용 SQLite

### 로컬 환경 구축 단계
1.  **저장소 클론 및 이동**:
    ```bash
    git clone <repository-url>
    cd surplus-hub-api-v3
    ```

2.  **가상환경 생성 및 활성화**:
    ```bash
    # 가상환경 생성
    python3 -m venv .venv

    # 활성화 (macOS/Linux)
    source .venv/bin/activate
    # 활성화 (Windows)
    .venv\Scripts\activate
    ```

3.  **의존성 설치**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정**:
    `.env` 파일을 생성하고 아래 내용을 작성하세요. (DB URL은 로컬 환경에 맞게 수정)
    ```ini
    PROJECT_NAME="Surplus Hub API"
    # SQLite 사용 시 (간편 설정)
    DATABASE_URL="sqlite:///./surplushub.db"
    # PostgreSQL 사용 시
    # DATABASE_URL="postgresql://user:password@localhost:5432/surplushub"
    SECRET_KEY="your-secret-key-here"
    ```

5.  **DB 마이그레이션 적용**:
    ```bash
    alembic upgrade head
    ```

6.  **서버 실행**:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   Swagger UI: `http://localhost:8000/docs`
    *   Admin Panel: `http://localhost:8000/admin`

---

## 3. 코드베이스 이해 & 컨벤션

### 주요 모듈
*   **`models/` vs `schemas/`**:
    *   `models`: DB 테이블과 1:1 매핑되는 SQLAlchemy 클래스입니다. 비즈니스 로직에서 데이터를 저장/조회할 때 사용합니다.
    *   `schemas`: API 요청/응답의 형태를 정의하는 Pydantic 클래스입니다. 데이터 검증(Validation)과 직렬화(Serialization)를 담당합니다.
*   **`core/config.py`**: `pydantic-settings`를 사용하여 환경 변수를 로드하고 앱 설정을 관리합니다.

### 코드 컨벤션
*   **Style**: PEP 8을 준수합니다.
*   **Type Hinting**: 모든 함수 인자와 반환값에 타입 힌트를 명시합니다.
    ```python
    def get_user(db: Session, user_id: int) -> Optional[User]: ...
    ```
*   **API 문서**: FastAPI가 Docstring과 Pydantic 스키마를 기반으로 자동 생성합니다. 엔드포인트 작성 시 `summary`, `description`, `response_model`을 명시해주세요.

---

## 4. 유지보수 및 작업 절차

### 버그 수정 프로세스
1.  **이슈 확인**: 에러 로그(Sentry 등)나 사용자 리포트를 확인합니다.
2.  **테스트 작성**: 버그를 재현하는 테스트 케이스를 `tests/` 폴더에 작성합니다.
3.  **수정 및 검증**: 코드를 수정하고 테스트(`pytest`)가 통과하는지 확인합니다.

### 기능 추가 (새로운 API 개발)
1.  **모델링**: `app/models`에 DB 모델 추가 -> `alembic revision --autogenerate` -> `alembic upgrade head`.
2.  **스키마 정의**: `app/schemas`에 Request/Response DTO 정의.
3.  **엔드포인트 구현**: `app/api/endpoints`에 라우터 구현.
4.  **라우터 등록**: `app/api/api.py`에 라우터 추가.

### 코드 리뷰 체크리스트
*   [ ] 불필요한 DB 쿼리(N+1 문제 등)가 없는가?
*   [ ] 입력값 검증(Validation)이 적절한가?
*   [ ] 적절한 예외 처리(HTTPException)가 되어 있는가?
*   [ ] 민감한 정보가 로그에 남지 않는가?

---

## 5. 문제 해결 (Troubleshooting)

### 자주 발생하는 오류
*   **`ImportError`**: 가상환경(`source .venv/bin/activate`)이 활성화되었는지 확인하세요.
*   **DB 연결 오류**: `.env` 파일의 `DATABASE_URL`이 올바른지, DB 서버가 실행 중인지 확인하세요.
*   **Alembic 충돌**: 여러 개발자가 동시에 마이그레이션을 생성했을 때 발생합니다. `alembic merge heads`로 해결하거나 순서를 조정해야 합니다.

### 디버깅
*   `print()` 대신 로깅을 사용하세요. (FastAPI 기본 로거 사용)
*   VS Code의 디버거를 연결하여 중단점(Breakpoint)을 활용하세요.

---

## 6. 배포 및 운영

### 배포 파이프라인 (CI/CD)
*   현재는 수동 배포 또는 간단한 스크립트 기반 배포를 가정합니다.
*   **Production 실행**:
    ```bash
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
    ```
    `gunicorn`을 사용하여 멀티 워커 프로세스로 실행하는 것을 권장합니다.

### 모니터링
*   **Health Check**: `GET /` 엔드포인트를 통해 서버 상태를 확인할 수 있습니다.
*   **로그**: `stdout`/`stderr`로 출력되는 로그를 수집하여 모니터링합니다.

---

## 7. 추가 학습 자료

*   **FastAPI**: [공식 문서 (한글)](https://fastapi.tiangolo.com/ko/) - 튜토리얼이 매우 훌륭합니다.
*   **SQLAlchemy**: [공식 튜토리얼](https://docs.sqlalchemy.org/en/14/tutorial/)
*   **Pydantic**: [공식 문서](https://docs.pydantic.dev/latest/)

질문이 있다면 언제든 팀 채널에 물어봐 주세요. 함께 성장해 봅시다! 🚀
