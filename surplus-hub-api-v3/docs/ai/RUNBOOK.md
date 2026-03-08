# AI 기능 운영 가이드

Surplus Hub API v3의 AI 기능(이미지 분석, 자재 설명 생성, 가격 제안, 시맨틱 검색, 채팅 추천, QA, 요약)을 운영하기 위한 가이드입니다.

---

## 목차

1. [초기 설정 가이드](#1-초기-설정-가이드)
2. [일상 운영](#2-일상-운영)
3. [장애 대응](#3-장애-대응)
4. [스케일링 가이드](#4-스케일링-가이드)
5. [배포 체크리스트](#5-배포-체크리스트)
6. [롤백 절차](#6-롤백-절차)
7. [트러블슈팅 가이드](#7-트러블슈팅-가이드)
8. [모니터링 대시보드](#8-모니터링-대시보드-선택사항)
9. [연락처 및 지원](#9-연락처-및-지원)
10. [체크리스트 요약](#10-체크리스트-요약)

---

## 1. 초기 설정 가이드

### 1.1. 환경변수 설정

`.env` 파일에 다음 환경변수를 설정하세요:

```bash
# Gemini API (이미지 분석)
GOOGLE_AI_API_KEY=your-gemini-api-key

# OpenAI API (텍스트 생성, 채팅 추천, QA, 요약)
OPENAI_API_KEY=your-openai-api-key

# 임베딩 모델 설정 (기본값 권장, 변경 시 전체 재생성 필요)
EMBEDDING_MODEL_NAME=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
```

**환경변수 확인**:

```bash
# .env 파일이 올바른지 확인
grep -E "GOOGLE_AI_API_KEY|OPENAI_API_KEY" .env

# API 키가 유효한지 간단 테스트
python -c "import os; print('GOOGLE_AI_API_KEY:', os.getenv('GOOGLE_AI_API_KEY')[:10] if os.getenv('GOOGLE_AI_API_KEY') else 'NOT SET')"
python -c "import os; print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### 1.2. Docker 이미지

`docker-compose.yml`에서 **pgvector 내장 PostgreSQL 이미지**를 사용하세요:

```yaml
# docker-compose.yml
services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: surplus_hub
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**Docker 컨테이너 시작**:

```bash
docker-compose up -d db
```

### 1.3. 마이그레이션 실행

데이터베이스 스키마를 최신 버전으로 업데이트:

```bash
# Alembic 마이그레이션 실행
alembic upgrade head

# 마이그레이션 버전 확인
alembic current
```

**pgvector 확장 활성화 확인**:

```bash
# PostgreSQL에 접속하여 확인
psql -h localhost -U postgres -d surplus_hub -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

# 결과 예시:
#  extname | extversion
# ---------+------------
#  vector  | 0.5.1
```

**materials 테이블의 embedding_vector 컬럼 확인**:

```bash
psql -h localhost -U postgres -d surplus_hub -c "\d materials" | grep embedding_vector

# 결과 예시:
#  embedding_vector | vector(1024) |  |  |
```

### 1.4. 임베딩 백필 (기존 데이터)

이미 등록된 자재 데이터에 대해 임베딩 벡터를 생성:

```bash
# 백필 스크립트 실행
python scripts/backfill_embeddings.py

# 진행 상황 확인 (별도 터미널)
watch -n 5 "psql -h localhost -U postgres -d surplus_hub -c \"SELECT COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding, COUNT(*) AS total FROM materials;\""
```

**백필 완료 확인**:

```bash
psql -h localhost -U postgres -d surplus_hub -c "
SELECT
    COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding,
    COUNT(*) FILTER (WHERE embedding_vector IS NULL) AS without_embedding,
    ROUND(
        COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS percentage
FROM materials
WHERE status = 'ACTIVE';
"

# 결과 예시:
#  with_embedding | without_embedding | percentage
# ----------------+-------------------+------------
#             450 |                 5 |      98.90
```

**목표**: 95% 이상의 활성 자재에 임베딩 벡터가 생성되어야 합니다.

---

## 2. 일상 운영

### 2.1. 로그 모니터링

AI 관련 로그는 `app.ai.*` 네임스페이스에서 확인할 수 있습니다.

**주요 경고 로그 패턴**:

| 로그 메시지 | 의미 | 영향 범위 |
|-----------|------|---------|
| `"Gemini returned non-JSON response"` | Vision AI 응답 파싱 실패 | 이미지 분석 실패 |
| `"Chat suggestion LLM returned non-JSON"` | 채팅 추천 응답 파싱 실패 | 채팅 추천 기능 불가 |
| `"Price suggestion LLM returned non-JSON"` | 가격 제안 응답 파싱 실패 | 가격 제안 기능 불가 |
| `"Summarize LLM returned non-JSON"` | 요약 응답 파싱 실패 | 요약 기능 불가 |
| `"Failed to generate query embedding"` | 임베딩 생성 실패 | 시맨틱 검색 불가 |
| `"Failed to update embedding for material"` | 자재 임베딩 업데이트 실패 | 신규 자재 검색 불가 |

**로그 확인 방법**:

```bash
# 최근 AI 관련 에러 로그 확인
docker logs surplus-hub-api | grep -i "error" | grep "app.ai"

# 특정 시간대의 로그 확인
docker logs surplus-hub-api --since "2026-02-21T10:00:00" | grep "app.ai"

# 실시간 로그 모니터링
docker logs -f surplus-hub-api | grep "app.ai"
```

### 2.2. 임베딩 비율 체크

정기적으로 임베딩 생성 비율을 확인하여 시맨틱 검색 품질을 유지하세요.

**일일 체크 쿼리**:

```sql
SELECT
    COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding,
    COUNT(*) FILTER (WHERE embedding_vector IS NULL) AS without_embedding,
    ROUND(
        COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS percentage
FROM materials
WHERE status = 'ACTIVE';
```

**목표**: 95% 이상 유지

**임베딩 비율이 낮을 경우**:

1. 최근 추가된 자재 중 임베딩이 없는 항목 확인:
   ```sql
   SELECT id, title, created_at
   FROM materials
   WHERE status = 'ACTIVE'
     AND embedding_vector IS NULL
   ORDER BY created_at DESC
   LIMIT 10;
   ```

2. 임베딩 서비스 로그 확인:
   ```bash
   docker logs surplus-hub-api | grep "Failed to update embedding"
   ```

3. 필요 시 수동으로 백필 재실행:
   ```bash
   python scripts/backfill_embeddings.py --missing-only
   ```

### 2.3. 인덱스 상태 확인

pgvector HNSW 인덱스의 크기와 상태를 모니터링:

```sql
-- 인덱스 크기 확인
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    pg_relation_size(indexrelid) AS size_bytes
FROM pg_stat_user_indexes
WHERE indexname = 'idx_materials_embedding_hnsw';

-- 인덱스 사용 통계
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname = 'idx_materials_embedding_hnsw';
```

**인덱스 크기 증가율 확인**:

```bash
# 주간 스냅샷 저장
psql -h localhost -U postgres -d surplus_hub -c "
SELECT
    NOW() AS snapshot_time,
    pg_relation_size('idx_materials_embedding_hnsw') AS index_size_bytes
" >> /var/log/surplus-hub/index_size_history.log
```

### 2.4. API 사용량 모니터링

외부 AI 서비스(Gemini, OpenAI)의 사용량과 비용을 추적:

**Rate Limit 로그 확인**:

```bash
# Rate limit 초과 로그
docker logs surplus-hub-api | grep "429" | grep "/ai/"

# 시간대별 AI 요청 수
docker logs surplus-hub-api | grep "POST /api/v1/ai/" | awk '{print $1}' | cut -d'T' -f1 | sort | uniq -c
```

**비용 추정**:

| 엔드포인트 | 사용 모델 | 예상 비용/1000요청 |
|----------|---------|------------------|
| `/ai/analyze-image` | Gemini Pro Vision | $0.25 (이미지당) |
| `/ai/generate-description` | GPT-4o-mini | $0.60 |
| `/ai/suggest-price` | GPT-4o-mini | $0.40 |
| `/ai/chat-suggestions` | GPT-4o-mini | $0.30 |
| `/ai/qa` | GPT-4o-mini | $0.50 |
| `/ai/summarize` | GPT-4o-mini | $0.40 |
| Embedding 생성 | bge-m3 (로컬) | 무료 |

---

## 3. 장애 대응

### 3.1. Gemini API 장애

**증상**:
- `POST /api/v1/ai/analyze-image` 엔드포인트에서 502 응답 다수 발생
- 로그에 `"Gemini returned non-JSON response"` 또는 API 에러 메시지

**확인**:

```bash
# 테스트 요청 실행
curl -X POST http://localhost:8000/api/v1/ai/analyze-image \
  -H "Authorization: Bearer {valid_token}" \
  -H "Content-Type: application/json" \
  -d '{"imageUrl":"https://example.com/test-image.jpg"}' \
  -w "\nStatus: %{http_code}\n"

# 결과가 502/500이면 장애 확인
```

**대응**:

1. **Google AI Studio 상태 확인**:
   - https://status.cloud.google.com/ 접속
   - Generative AI 서비스 상태 확인

2. **API 키 유효성 확인**:
   ```bash
   # 환경변수 확인
   echo $GOOGLE_AI_API_KEY

   # API 키 테스트 (간단한 요청)
   curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_AI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
   ```

3. **API 사용량 한도 확인**:
   - Google Cloud Console → API & Services → Quotas
   - Generative Language API 할당량 확인

4. **임시 우회**:
   - 이미지 분석 기능만 영향을 받음
   - 다른 AI 기능(설명 생성, 가격 제안 등)은 정상 동작
   - 필요 시 프론트엔드에서 이미지 업로드 버튼 비활성화

**영향 범위**: 이미지 분석만 불가, 다른 기능 정상

### 3.2. OpenAI API 장애

**증상**:
- 설명 생성, 가격 제안, 채팅 추천, QA, 요약 모두 502 응답
- 로그에 `"OpenAI API error"` 또는 `"LLM returned non-JSON"` 다수 발생

**확인**:

```bash
# 502 응답 급증 확인
docker logs surplus-hub-api --since "10m" | grep "POST /api/v1/ai/" | grep "502" | wc -l

# OpenAI API 직접 테스트
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

**대응**:

1. **OpenAI 상태 페이지 확인**:
   - https://status.openai.com/ 접속
   - API 서비스 상태 확인

2. **API 키 유효성 확인**:
   ```bash
   # 환경변수 확인
   echo $OPENAI_API_KEY

   # API 키 테스트
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **API 사용량/과금 한도 확인**:
   - OpenAI Platform → Usage (https://platform.openai.com/usage)
   - Rate limits 및 billing limits 확인

4. **임시 우회**:
   - 텍스트 생성 기능 전체가 영향을 받음
   - 시맨틱 검색은 정상 동작 (임베딩은 로컬 모델 사용)
   - 필요 시 프론트엔드에서 "AI 기능 일시 중단" 안내

**영향 범위**: 텍스트 생성 전체 불가, 검색은 정상

### 3.3. 임베딩 서비스 장애

**증상**:
- 시맨틱 검색 결과가 비어있음
- 신규 자재 등록 시 임베딩이 생성되지 않음
- 로그에 `"Failed to generate query embedding"` 또는 `"Failed to update embedding for material"` 발생

**확인**:

```bash
# 임베딩 생성 실패 로그 확인
docker logs surplus-hub-api | grep "Failed to generate.*embedding"

# 최근 등록된 자재의 임베딩 상태 확인
psql -h localhost -U postgres -d surplus_hub -c "
SELECT id, title, embedding_vector IS NOT NULL AS has_embedding
FROM materials
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 10;
"
```

**대응**:

1. **서버 메모리 확인**:
   ```bash
   # 사용 가능한 메모리 확인 (bge-m3는 약 2.4GB 필요)
   free -h

   # Docker 컨테이너 메모리 사용량
   docker stats surplus-hub-api --no-stream
   ```

   메모리 부족 시:
   - Docker 메모리 제한 증가 (docker-compose.yml의 `mem_limit`)
   - 서버 메모리 증설 검토

2. **디스크 공간 확인**:
   ```bash
   # Hugging Face 모델 캐시 위치 확인
   du -sh ~/.cache/huggingface/

   # 디스크 여유 공간 확인
   df -h ~/.cache/huggingface/
   ```

   디스크 부족 시:
   - 불필요한 캐시 정리
   - 디스크 공간 확보

3. **서버 재시작으로 모델 재로딩**:
   ```bash
   # API 서버 재시작
   docker-compose restart api

   # 로그에서 모델 로딩 확인
   docker logs surplus-hub-api | grep "Loading embedding model"
   ```

4. **모델 파일 무결성 확인**:
   ```bash
   # 캐시 삭제 후 재다운로드
   rm -rf ~/.cache/huggingface/hub/models--BAAI--bge-m3
   docker-compose restart api
   ```

**영향 범위**: 시맨틱 검색 전체 불가, 가격 제안(유사 매물 매칭) 불가

### 3.4. pgvector 관련 이슈

**증상**: `different vector dimensions` 에러 발생

**원인**: 임베딩 모델 변경 시 기존 벡터와 차원이 불일치

**대응**:

1. **현재 설정 확인**:
   ```bash
   # 환경변수에서 차원 확인
   grep EMBEDDING_DIMENSION .env

   # 데이터베이스에서 컬럼 차원 확인
   psql -h localhost -U postgres -d surplus_hub -c "\d materials" | grep embedding_vector
   ```

2. **모델 변경 시 전체 임베딩 재생성**:
   ```bash
   # 1. 기존 임베딩 벡터 초기화
   psql -h localhost -U postgres -d surplus_hub -c "UPDATE materials SET embedding_vector = NULL;"

   # 2. 인덱스 재생성
   psql -h localhost -U postgres -d surplus_hub -c "
   DROP INDEX IF EXISTS idx_materials_embedding_hnsw;
   CREATE INDEX idx_materials_embedding_hnsw
   ON materials USING hnsw (embedding_vector vector_cosine_ops)
   WITH (m = 16, ef_construction = 64);
   "

   # 3. 백필 재실행
   python scripts/backfill_embeddings.py
   ```

**주의**: 임베딩 모델 변경은 전체 데이터 재생성이 필요하므로, 변경 전에 충분히 검토하세요.

---

## 4. 스케일링 가이드

### 4.1. 자재 10만건 이상

자재 데이터가 10만건을 초과하면 HNSW 인덱스 파라미터를 조정하여 검색 성능을 최적화하세요.

**HNSW 파라미터 튜닝**:

```sql
-- 기존 인덱스 삭제
DROP INDEX IF EXISTS idx_materials_embedding_hnsw;

-- 성능 최적화된 파라미터로 재생성
CREATE INDEX idx_materials_embedding_hnsw
ON materials USING hnsw (embedding_vector vector_cosine_ops)
WITH (m = 24, ef_construction = 128);

-- 인덱스 생성 진행 상황 확인 (별도 터미널)
-- PostgreSQL 12+에서는 CREATE INDEX CONCURRENTLY 사용 가능
SELECT
    phase,
    blocks_done,
    blocks_total,
    ROUND(100.0 * blocks_done / NULLIF(blocks_total, 0), 2) AS progress_pct
FROM pg_stat_progress_create_index
WHERE relid = 'materials'::regclass;
```

**파라미터 설명**:

| 파라미터 | 기본값 | 10만건+ 권장값 | 효과 |
|---------|-------|-------------|------|
| `m` | 16 | 24 | 그래프 연결 수 증가 → 검색 정확도 향상 |
| `ef_construction` | 64 | 128 | 인덱스 구축 시 탐색 범위 증가 → 품질 향상 |

**트레이드오프**:
- 장점: 검색 정확도 향상 (Recall 증가)
- 단점: 인덱스 크기 증가 (~30%), 구축 시간 증가 (~2배)

**검색 시 파라미터 조정**:

```python
# app/services/ai/embedding_service.py 수정

async def search_similar_materials(
    self,
    query_embedding: List[float],
    limit: int = 10,
    ef_search: int = 100  # 기본값 40 → 100으로 증가
) -> List[Material]:
    # ef_search: 검색 시 탐색 범위 (높을수록 정확도 향상, 속도 저하)
    result = await self.db.execute(
        text(f"SET hnsw.ef_search = {ef_search}")
    )
    # 검색 쿼리 실행...
```

### 4.2. 트래픽 증가 대응

#### 4.2.1. Gunicorn 워커 수 조정

**현재 설정 확인**:

```bash
# 실행 중인 워커 수 확인
ps aux | grep gunicorn | grep -v grep | wc -l
```

**권장 워커 수**:

```
워커 수 = (CPU 코어 수 × 2) + 1
```

**메모리 고려사항**:
- 임베딩 모델(bge-m3)은 워커당 최소 1GB 추가 메모리 필요
- 예: 4코어 서버 → 워커 9개 → 최소 9GB RAM 필요

**설정 변경**:

```bash
# docker-compose.yml 또는 gunicorn 설정 파일
# 예: 4코어 서버의 경우
gunicorn app.main:app \
  --workers 9 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 4.2.2. Rate Limit 값 조정

**현재 설정 확인**:

```python
# app/api/endpoints/ai_assist.py
# 기본값: 분당 10회, 시간당 100회
```

**트래픽 패턴에 따른 조정**:

| 사용자 규모 | 분당 제한 | 시간당 제한 |
|-----------|---------|-----------|
| 소규모 (~1,000명) | 10 | 100 |
| 중규모 (~10,000명) | 20 | 200 |
| 대규모 (10,000명+) | 30 | 300 |

**설정 변경**:

```python
# app/api/endpoints/ai_assist.py

# 이미지 분석 (비용 높음)
@router.post("/analyze-image")
@limiter.limit("20/minute;200/hour")  # 기본값에서 2배 증가
async def analyze_image(...):
    ...

# 텍스트 생성 (비용 중간)
@router.post("/generate-description")
@limiter.limit("30/minute;300/hour")  # 기본값에서 3배 증가
async def generate_description(...):
    ...

# 검색 (비용 낮음, 로컬 모델)
@router.get("/search")
@limiter.limit("60/minute;600/hour")  # 기본값에서 6배 증가
async def semantic_search(...):
    ...
```

#### 4.2.3. Redis 캐싱 도입 고려

반복적인 요청에 대해 캐싱을 적용하여 외부 API 호출을 줄입니다.

**캐싱 대상**:

| 엔드포인트 | 캐시 키 | TTL | 이유 |
|----------|--------|-----|------|
| `/ai/generate-description` | `desc:{title}:{category_id}` | 1시간 | 동일 제목 반복 요청 가능 |
| `/ai/suggest-price` | `price:{material_id}` | 30분 | 동일 자재 가격 재요청 가능 |
| `/ai/search` | `search:{query}:{limit}` | 10분 | 인기 검색어 반복 |

**구현 예시**:

```python
# app/services/ai/text_generation_service.py
import aioredis

class TextGenerationService:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def generate_description(
        self,
        title: str,
        category_id: int
    ) -> str:
        # 캐시 확인
        cache_key = f"desc:{title}:{category_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            return cached.decode("utf-8")

        # 캐시 미스: LLM 호출
        description = await self._call_llm(title, category_id)

        # 캐시 저장 (1시간)
        await self.redis.setex(cache_key, 3600, description)

        return description
```

---

## 5. 배포 체크리스트

새로운 버전을 배포하기 전에 다음 항목을 확인하세요.

### 5.1. 배포 전 확인사항

- [ ] **환경변수 설정 확인**
  ```bash
  grep -E "GOOGLE_AI_API_KEY|OPENAI_API_KEY|EMBEDDING_MODEL_NAME|EMBEDDING_DIMENSION" .env
  ```

- [ ] **Docker 이미지 확인**
  ```bash
  docker-compose config | grep "image:" | grep "pgvector/pgvector:pg15"
  ```

- [ ] **마이그레이션 실행**
  ```bash
  alembic upgrade head
  alembic current
  ```

- [ ] **pgvector 확장 활성화 확인**
  ```bash
  psql -h localhost -U postgres -d surplus_hub -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
  ```

- [ ] **임베딩 백필 완료 확인**
  ```bash
  psql -h localhost -U postgres -d surplus_hub -c "
  SELECT
      COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding,
      COUNT(*) AS total,
      ROUND(COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) * 100.0 / NULLIF(COUNT(*), 0), 2) AS percentage
  FROM materials WHERE status = 'ACTIVE';
  "
  # 목표: percentage >= 95.00
  ```

- [ ] **테스트 통과 확인**
  ```bash
  pytest app/tests/api/test_ai_assist.py -v
  pytest app/tests/api/test_ai_analyze.py -v
  pytest app/tests/api/test_ai_chat.py -v
  pytest app/tests/api/test_ai_qa.py -v
  ```

- [ ] **Rate Limit 설정 확인**
  ```bash
  grep -r "@limiter.limit" app/api/endpoints/ai_assist.py
  ```

- [ ] **로그 레벨 확인** (프로덕션: INFO 이상)
  ```bash
  grep "LOG_LEVEL" .env
  # 결과: LOG_LEVEL=INFO
  ```

### 5.2. 배포 후 확인사항

- [ ] **API 헬스체크**
  ```bash
  curl http://localhost:8000/health
  # 결과: {"status":"ok"}
  ```

- [ ] **AI 엔드포인트 동작 확인**
  ```bash
  # 이미지 분석
  curl -X POST http://localhost:8000/api/v1/ai/analyze-image \
    -H "Authorization: Bearer {valid_token}" \
    -H "Content-Type: application/json" \
    -d '{"imageUrl":"https://example.com/test.jpg"}' \
    -w "\nStatus: %{http_code}\n"

  # 시맨틱 검색
  curl "http://localhost:8000/api/v1/ai/search?q=철근&limit=5" \
    -H "Authorization: Bearer {valid_token}" \
    -w "\nStatus: %{http_code}\n"
  ```

- [ ] **로그 모니터링** (10분간)
  ```bash
  docker logs -f surplus-hub-api | grep -E "ERROR|WARN|app.ai"
  # 이상 없는지 확인
  ```

- [ ] **인덱스 상태 확인**
  ```bash
  psql -h localhost -U postgres -d surplus_hub -c "
  SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
  FROM pg_stat_user_indexes
  WHERE indexname = 'idx_materials_embedding_hnsw';
  "
  ```

---

## 6. 롤백 절차

AI 기능 배포 후 문제가 발생하면 다음 절차로 롤백하세요.

### 6.1. 긴급 롤백 (AI 기능 전체 비활성화)

**1. AI 라우터 비활성화**:

```python
# app/api/api.py 수정
from app.api.endpoints import (
    auth,
    users,
    materials,
    # ai_assist,  # ← 주석 처리
    categories,
    # ...
)

# Router 등록 부분
# api_router.include_router(ai_assist.router, prefix="/ai", tags=["ai"])  # ← 주석 처리
```

**2. 서버 재시작**:

```bash
docker-compose restart api
```

**3. 확인**:

```bash
# AI 엔드포인트가 404를 반환하는지 확인
curl http://localhost:8000/api/v1/ai/search?q=test
# 결과: {"detail":"Not Found"} (404)
```

### 6.2. 부분 롤백 (특정 기능만 비활성화)

**이미지 분석만 비활성화**:

```python
# app/api/endpoints/ai_assist.py 수정

@router.post("/analyze-image")
async def analyze_image(...):
    # 임시로 503 반환
    raise HTTPException(
        status_code=503,
        detail="Image analysis is temporarily unavailable"
    )
    # 기존 코드는 주석 처리
```

**텍스트 생성만 비활성화**:

```python
# app/api/endpoints/ai_assist.py 수정

@router.post("/generate-description")
async def generate_description(...):
    raise HTTPException(
        status_code=503,
        detail="Description generation is temporarily unavailable"
    )
```

### 6.3. 데이터베이스 마이그레이션 롤백

AI 기능 관련 마이그레이션을 롤백해야 하는 경우:

```bash
# 1. 현재 마이그레이션 버전 확인
alembic current

# 2. 마이그레이션 히스토리 확인
alembic history

# 3. AI 기능 추가 이전 버전으로 롤백
# 예: revision abc123이 AI 기능 추가 마이그레이션이라면
alembic downgrade abc123^

# 4. 확인
alembic current
psql -h localhost -U postgres -d surplus_hub -c "\d materials" | grep embedding_vector
# embedding_vector 컬럼이 없어야 함
```

### 6.4. 임베딩 데이터 정리 (필요 시)

롤백 후 임베딩 데이터를 완전히 제거하려면:

```bash
# 1. 임베딩 벡터 초기화
psql -h localhost -U postgres -d surplus_hub -c "UPDATE materials SET embedding_vector = NULL;"

# 2. HNSW 인덱스 삭제
psql -h localhost -U postgres -d surplus_hub -c "DROP INDEX IF EXISTS idx_materials_embedding_hnsw;"

# 3. 확인
psql -h localhost -U postgres -d surplus_hub -c "
SELECT COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding
FROM materials;
"
# 결과: with_embedding = 0
```

### 6.5. 롤백 후 복구

문제 해결 후 AI 기능을 다시 활성화하려면:

```bash
# 1. 코드 수정 원복 (주석 제거)
# app/api/api.py, app/api/endpoints/ai_assist.py 수정

# 2. 마이그레이션 재실행
alembic upgrade head

# 3. 임베딩 백필 재실행
python scripts/backfill_embeddings.py

# 4. 서버 재시작
docker-compose restart api

# 5. 동작 확인
curl http://localhost:8000/api/v1/ai/search?q=test -H "Authorization: Bearer {token}"
```

---

## 7. 트러블슈팅 가이드

### 7.1. 자주 발생하는 문제

#### 문제 1: "Model loading failed" 에러

**증상**:
```
ERROR: Failed to load embedding model BAAI/bge-m3
```

**원인**: Hugging Face 모델 다운로드 실패 또는 메모리 부족

**해결**:

1. 인터넷 연결 확인
2. Hugging Face Hub 접근 가능 여부 확인:
   ```bash
   curl https://huggingface.co/BAAI/bge-m3
   ```
3. 메모리 확인:
   ```bash
   free -h
   # 최소 4GB 이상 여유 필요
   ```
4. 캐시 삭제 후 재시도:
   ```bash
   rm -rf ~/.cache/huggingface/hub/models--BAAI--bge-m3
   docker-compose restart api
   ```

#### 문제 2: Rate Limit 초과

**증상**:
```
429 Too Many Requests: Rate limit exceeded
```

**원인**: slowapi Rate Limiter 설정값 초과

**해결**:

1. 현재 설정 확인:
   ```python
   # app/api/endpoints/ai_assist.py
   @limiter.limit("10/minute;100/hour")
   ```

2. 설정 조정 (섹션 4.2.2 참조)

3. 또는 특정 IP/사용자 화이트리스트 추가:
   ```python
   # app/core/rate_limit.py

   def is_whitelisted(request: Request) -> bool:
       # 관리자 IP 화이트리스트
       whitelist_ips = ["192.168.1.100", "10.0.0.1"]
       client_ip = request.client.host
       return client_ip in whitelist_ips

   # 엔드포인트에서 사용
   @router.post("/analyze-image")
   async def analyze_image(request: Request, ...):
       if not is_whitelisted(request):
           # Rate limit 적용
           ...
   ```

#### 문제 3: 검색 결과가 비어있음

**증상**: 시맨틱 검색 시 결과가 항상 빈 배열

**원인**:
1. 임베딩 벡터가 생성되지 않음
2. HNSW 인덱스가 손상됨
3. 쿼리 임베딩 생성 실패

**해결**:

1. 임베딩 생성 상태 확인:
   ```sql
   SELECT COUNT(*) FILTER (WHERE embedding_vector IS NOT NULL) AS with_embedding
   FROM materials WHERE status = 'ACTIVE';
   ```

2. 인덱스 상태 확인:
   ```sql
   SELECT indexname FROM pg_indexes WHERE tablename = 'materials' AND indexname = 'idx_materials_embedding_hnsw';
   ```

3. 쿼리 임베딩 로그 확인:
   ```bash
   docker logs surplus-hub-api | grep "Failed to generate query embedding"
   ```

4. 필요 시 인덱스 재생성:
   ```sql
   DROP INDEX idx_materials_embedding_hnsw;
   CREATE INDEX idx_materials_embedding_hnsw
   ON materials USING hnsw (embedding_vector vector_cosine_ops)
   WITH (m = 16, ef_construction = 64);
   ```

### 7.2. 성능 이슈

#### 검색 속도가 느림 (>1초)

**원인**: HNSW 파라미터가 최적화되지 않음

**해결**: 섹션 4.1 참조 (HNSW 파라미터 튜닝)

#### 메모리 사용량 급증

**원인**: 임베딩 모델이 워커마다 로딩됨

**해결**:

1. 워커 수 줄이기 (섹션 4.2.1)
2. 또는 모델 공유 메커니즘 도입 (고급):
   ```python
   # app/services/ai/embedding_service.py

   # 싱글톤 패턴으로 모델 로딩
   _model = None

   def get_embedding_model():
       global _model
       if _model is None:
           _model = SentenceTransformer("BAAI/bge-m3")
       return _model
   ```

---

## 8. 모니터링 대시보드 (선택사항)

### 8.1. Prometheus + Grafana 통합

AI 기능 메트릭을 시각화하려면 Prometheus와 Grafana를 연동할 수 있습니다.

**주요 메트릭**:

| 메트릭 | 설명 | 타입 |
|-------|------|------|
| `ai_requests_total` | AI 엔드포인트 요청 수 | Counter |
| `ai_request_duration_seconds` | 요청 처리 시간 | Histogram |
| `ai_errors_total` | AI 에러 발생 수 | Counter |
| `embedding_generation_duration_seconds` | 임베딩 생성 시간 | Histogram |
| `materials_with_embedding_total` | 임베딩이 있는 자재 수 | Gauge |

**구현 예시**:

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

ai_requests_total = Counter(
    "ai_requests_total",
    "Total AI requests",
    ["endpoint", "status"]
)

ai_request_duration = Histogram(
    "ai_request_duration_seconds",
    "AI request duration",
    ["endpoint"]
)

# app/api/endpoints/ai_assist.py에서 사용
@router.post("/analyze-image")
async def analyze_image(...):
    with ai_request_duration.labels(endpoint="analyze_image").time():
        try:
            result = await vision_service.analyze(...)
            ai_requests_total.labels(endpoint="analyze_image", status="success").inc()
            return result
        except Exception as e:
            ai_requests_total.labels(endpoint="analyze_image", status="error").inc()
            raise
```

---

## 9. 연락처 및 지원

문제 해결이 어려운 경우:

1. **기술 문서**:
   - `/docs/ai/AI_FEATURES_GUIDE.md`: 기능 상세 가이드
   - `/docs/ai/ARCHITECTURE.md`: 아키텍처 설계 문서

2. **로그 수집**:
   ```bash
   # 지원팀에 전달할 로그 수집
   docker logs surplus-hub-api --since "1h" > ai_logs_$(date +%Y%m%d_%H%M%S).log
   ```

3. **디버그 모드 활성화**:
   ```bash
   # .env
   LOG_LEVEL=DEBUG

   # 재시작
   docker-compose restart api
   ```

---

## 10. 체크리스트 요약

### 일일 점검

- [ ] 임베딩 비율 체크 (목표: 95% 이상)
- [ ] AI 엔드포인트 에러 로그 확인
- [ ] Rate limit 초과 여부 확인

### 주간 점검

- [ ] 인덱스 크기 증가율 확인
- [ ] API 사용량 및 비용 확인
- [ ] 백필 스크립트 실행 (신규 자재 대상)

### 월간 점검

- [ ] HNSW 인덱스 최적화 검토
- [ ] Rate Limit 설정 조정 검토
- [ ] 캐싱 전략 도입 검토
- [ ] 로그 아카이빙

---

**문서 버전**: v1.0.0
**최종 업데이트**: 2026-02-21
**담당자**: AI 기능 운영팀
