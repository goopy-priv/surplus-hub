# AI 기술 스택

Surplus Hub API v3의 AI 통합 기술 스택 문서입니다.

## 1. Embedding 모델: BAAI/bge-m3

### 기본 정보
- **라이브러리**: `sentence-transformers >= 3.0.0`
- **모델**: BAAI/bge-m3 (다국어 임베딩 모델)
- **차원**: 1024
- **메모리**: 약 2.4GB (모델 로딩 시)
- **정규화**: `normalize_embeddings=True` (코사인 유사도 최적화)

### 구현 패턴
```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    _instance = None
    _model = None
    _lock = threading.Lock()

    @classmethod
    def get_model(cls):
        if cls._model is None:
            with cls._lock:
                if cls._model is None:  # double-check locking
                    cls._model = SentenceTransformer('BAAI/bge-m3')
        return cls._model
```

### 최적화 전략
- **싱글톤 패턴**: Thread-safe double-check locking으로 메모리 절약
- **Lazy Loading**: 첫 호출 시에만 모델 로딩
- **Gunicorn Preload**: `gunicorn --preload`로 워커 간 모델 공유

### 사용 목적
- 자재 검색 (semantic search)
- 유사 자재 추천
- 가격 제안 시 유사 자재 매칭

---

## 2. Vision AI: Gemini 2.5 Flash-Lite

### 기본 정보
- **SDK**: `google-genai >= 1.0.0`
- **모델**: gemini-2.5-flash-lite
- **용도**: 자재 이미지 분석 (카테고리, 상태, 자재 종류 식별)
- **응답 형식**: JSON (프롬프트에서 강제)
- **비용**: Flash-Lite는 가장 저렴한 Gemini 모델

### API 사용 예시
```python
import google.genai as genai

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        genai.types.Part(
            file_data=genai.types.FileData(
                file_uri=image_url,
                mime_type="image/jpeg"
            )
        ),
        "이미지를 분석하여 건설 자재의 카테고리, 상태, 종류를 JSON 형식으로 반환하세요."
    ]
)
```

### 사용 목적
- 자재 등록 시 이미지 자동 분석
- 카테고리 자동 분류
- 자재 상태 평가 (양호, 보통, 손상)
- 제목 제안

---

## 3. Text Generation: GPT-5 Nano / Mini

### 기본 정보
- **SDK**: `openai >= 1.30.0`
- **모델**:
  - `gpt-5-nano`: 기본 모델 (설명 생성, 채팅 답장, 요약)
  - `gpt-5-mini`: 복잡한 추론 (긴 안전 관련 QA)

### 모델 선택 기준
```python
def select_model(post_content: str, category: str) -> str:
    # Safety 카테고리는 Mini 사용 (정확성 중요)
    if category == "Safety":
        return "gpt-5-mini"

    # 긴 컨텐츠(500자 이상)는 Mini 사용
    if len(post_content) > 500:
        return "gpt-5-mini"

    # 그 외는 Nano 사용 (비용 절감)
    return "gpt-5-nano"
```

### API 사용 예시
```python
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": "건설 자재 마켓플레이스의 AI 어시스턴트입니다."},
        {"role": "user", "content": f"다음 자재에 대한 설명을 생성하세요: {title}"}
    ],
    temperature=0.7
)
```

### 사용 목적
- **GPT-5 Nano**:
  - 자재 설명 자동 생성
  - 채팅 답장 제안 (3개)
  - 짧은 커뮤니티 답변 생성

- **GPT-5 Mini**:
  - 안전 관련 커뮤니티 질문 답변
  - 긴 토론 요약 (핵심 포인트 추출)
  - 복잡한 자재 추천 이유 설명

---

## 4. Vector DB: PostgreSQL + pgvector

### 기본 정보
- **Docker 이미지**: `pgvector/pgvector:pg15`
- **확장**: pgvector
- **인덱스**: HNSW (Hierarchical Navigable Small World)
- **연산자**: `<=>` (cosine distance)
- **SQLAlchemy 통합**: `pgvector >= 0.3.0`

### HNSW 인덱스 설정
```sql
CREATE INDEX idx_materials_embedding_hnsw
ON materials USING hnsw (embedding_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**파라미터 설명**:
- `m = 16`: 노드당 연결 수 (높을수록 정확하지만 메모리 증가)
- `ef_construction = 64`: 인덱스 빌드 시 탐색 범위 (높을수록 정확하지만 빌드 느림)

### SQLAlchemy 모델
```python
from pgvector.sqlalchemy import Vector

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding_vector = Column(Vector(1024), nullable=True)
```

### 쿼리 예시
```python
from sqlalchemy import text

# 코사인 유사도 검색 (거리가 가까울수록 유사)
query = text("""
    SELECT *, 1 - (embedding_vector <=> :query_vector) as similarity
    FROM materials
    WHERE status = 'ACTIVE'
      AND embedding_vector IS NOT NULL
    ORDER BY embedding_vector <=> :query_vector
    LIMIT 20
""")

results = db.execute(query, {"query_vector": query_vector})
```

---

## 의존성 관계

```
sentence-transformers >= 3.0.0
    └── torch (CPU-only 권장)
        └── numpy >= 1.24.0

google-genai >= 1.0.0
    └── google SDK 관련

openai >= 1.30.0
    └── httpx

pgvector >= 0.3.0
    └── psycopg2-binary (이미 설치됨)
```

---

## 버전 호환성 매트릭스

| 패키지 | 최소 버전 | 테스트된 버전 | 비고 |
|--------|-----------|-------------|------|
| sentence-transformers | 3.0.0 | 3.x | torch 자동 의존 |
| pgvector | 0.3.0 | 0.3.x | SQLAlchemy Vector 타입 지원 |
| numpy | 1.24.0 | 1.24+ | sentence-transformers 의존 |
| google-genai | 1.0.0 | 1.x | Gemini 2.5 API SDK |
| openai | 1.30.0 | 1.30+ | GPT-5 지원 필요 |
| torch | - | CPU-only | GPU 불필요 (임베딩만 사용) |

---

## 성능 최적화

### 1. 임베딩 모델 최적화
- **메모리 절약**: 싱글톤 패턴으로 1개 인스턴스만 로딩
- **시작 시간 단축**: gunicorn preload로 워커 시작 전 모델 로딩
- **배치 처리**: 여러 텍스트를 한번에 임베딩 생성 가능

### 2. Vector 검색 최적화
- **HNSW 인덱스**: IVFFlat보다 빠른 검색 (approximate nearest neighbor)
- **코사인 거리**: 정규화된 벡터로 내적 연산 최적화
- **필터링**: status='ACTIVE' 조건으로 검색 범위 축소

### 3. API 호출 최적화
- **Rate Limiting**: 엔드포인트별 분당 호출 제한 (5~30회)
- **Timeout**: 외부 API 호출 시 3초 타임아웃
- **에러 핸들링**: 502 에러로 일관된 장애 응답

---

## 메모리 사용량 추정

| 컴포넌트 | 메모리 사용량 | 비고 |
|---------|-------------|------|
| bge-m3 모델 | ~2.4GB | 첫 로딩 시 |
| 임베딩 캐시 (10k 자재) | ~40MB | 1024 dim × 4 bytes × 10k |
| PostgreSQL 버퍼 | 설정에 따라 | pgvector 인덱스 캐싱 |

**권장 서버 스펙**: 최소 4GB RAM (모델 + API 서버 + PostgreSQL)

---

## 비용 최적화 전략

### 1. Gemini Flash-Lite 사용
- 가장 저렴한 Gemini 모델 선택
- 이미지 분석 시에만 호출 (자재 등록 시)

### 2. GPT-5 Nano 우선 사용
- 단순 텍스트 생성은 Nano 사용
- Mini는 복잡한 추론에만 사용

### 3. 임베딩은 로컬 처리
- OpenAI Embeddings API 대신 로컬 모델 사용 (무료)
- 서버 리소스는 사용하지만 API 비용 0원

### 4. Rate Limiting
- 과도한 API 호출 방지
- 사용자당 제한으로 비용 예측 가능

---

*Last Updated: 2026-02-21*
