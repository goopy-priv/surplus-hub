# 외부 API 통합 문서

Surplus Hub API v3에서 사용하는 모든 외부 AI 서비스에 대한 통합 문서입니다.

---

## 1. Google Gemini API (Vision)

### 기본 정보

| 항목 | 내용 |
|------|------|
| **SDK** | `google-genai >= 1.0.0` |
| **모델** | `gemini-2.5-flash-lite` |
| **용도** | 자재 이미지 분석 (카테고리, 태그, 제목 제안, 상태, 자재종류, 확신도) |
| **클라이언트 위치** | `app/ai/clients/gemini.py` |

### 클라이언트 구조

**싱글톤 패턴**: Thread-safe double-check locking

```python
_client = None
_lock = threading.Lock()

def _get_client():
    """Thread-safe singleton for google.genai.Client."""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from google import genai
                _client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)
    return _client
```

### 인증

- **환경변수**: `GOOGLE_AI_API_KEY`
- **설정 위치**: `app/core/config.py` (Optional[str] = None)
- **키 누락 시**: 기능 비활성화 (HTTPException 502 반환)

### 호출 흐름

```
ai_assist.py (엔드포인트)
    ↓
registration.py:analyze_material_image()
    ↓
gemini.py:analyze_image(image_url)
    ↓
google.genai.Client.models.generate_content()
    ↓
JSON 응답 파싱 (markdown fence 제거)
```

#### 세부 호출 과정

1. **엔드포인트**: `POST /api/v1/ai-assist/analyze-image`
   - Rate Limit: 10/분 (slowapi)
   - 인증: JWT 토큰 필수 (현재 활성 사용자)

2. **서비스 계층**: `registration.py:analyze_material_image(image_url)`
   - 카테고리 힌트 생성 (선택사항)
   - Gemini 클라이언트 호출

3. **클라이언트 계층**: `gemini.py:analyze_image(image_url, categories)`
   - 프롬프트 + 이미지 URL 전송
   - 응답 JSON 파싱

### 프롬프트

**위치**: `app/ai/prompts/material.py:IMAGE_ANALYSIS_PROMPT`

```python
"""
당신은 건설 잉여자재 전문 분석가입니다.
주어진 이미지를 분석하여 아래 JSON 형식으로 정확히 응답하세요.

{
  "category": "자재 카테고리 (예: 철근, 시멘트, 목재, 배관, 전기, 타일, 페인트, 기타)",
  "tags": ["관련 태그 3~5개"],
  "title_suggestion": "추천 상품명 (20자 이내)",
  "condition": "상태 (새제품/양호/보통/사용감있음)",
  "material_type": "구체적 자재 종류 (예: H빔, PVC파이프, 포틀랜드시멘트)",
  "confidence": 0.0~1.0
}
"""
```

### 응답 파싱

```python
# Markdown code fence 제거
if text.startswith("```"):
    text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text[:-3].strip()

# JSON 파싱
try:
    result = json.loads(text)
except json.JSONDecodeError:
    # 실패 시 빈 결과 반환
    result = {
        "category": None,
        "tags": [],
        "title_suggestion": None,
        "condition": None,
        "material_type": None,
        "confidence": 0.0,
    }
```

### 에러 처리

```python
try:
    result = registration_service.analyze_material_image(body.image_url)
except Exception:
    raise HTTPException(status_code=502, detail="Vision AI service unavailable")
```

### 비용

- **모델**: Gemini 2.5 Flash-Lite
- **특징**: Gemini 모델 중 가장 저렴한 모델
- **최적화**: Vision 작업에 특화, 빠른 응답 속도

### Rate Limiting

- **서버측 제한**: 10/분 (slowapi)
- **용도**: 이미지 분석 남용 방지

---

## 2. OpenAI API (Text Generation)

### 기본 정보

| 항목 | 내용 |
|------|------|
| **SDK** | `openai >= 1.30.0` |
| **모델** | `gpt-5-nano` (기본), `gpt-5-mini` (추론) |
| **클라이언트 위치** | `app/ai/clients/openai_client.py` |

### 모델 선택

| 모델 | 변수명 | 용도 |
|------|--------|------|
| `gpt-5-nano` | `DEFAULT_MODEL` | 기본 텍스트 생성 (설명, 가격 제안, 채팅 추천, 요약) |
| `gpt-5-mini` | `REASONING_MODEL` | 복잡한 추론 (긴 게시글, Safety 카테고리 답변) |

### 클라이언트 구조

**싱글톤 패턴**: Thread-safe double-check locking

```python
_client = None
_lock = threading.Lock()

def _get_client():
    """Thread-safe singleton for openai.OpenAI."""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                import openai
                _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client
```

### 인증

- **환경변수**: `OPENAI_API_KEY`
- **설정 위치**: `app/core/config.py` (Optional[str] = None)
- **키 누락 시**: 기능 비활성화 (HTTPException 502 반환)

### 호출 패턴

#### 패턴 1: 단일 메시지 (generate_text)

```python
def generate_text(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    client = _get_client()
    model = model or DEFAULT_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content or ""
```

#### 패턴 2: 대화 히스토리 포함 (generate_text_with_history)

```python
def generate_text_with_history(
    system_prompt: str,
    messages: List[dict],
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    client = _get_client()
    model = model or DEFAULT_MODEL

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content or ""
```

### 사용처

#### 1. 설명 생성 (Description Generation)

- **파일**: `registration.py:generate_material_description()`
- **모델**: `gpt-5-nano`
- **Temperature**: 0.7 (창의적)
- **Max Tokens**: 512
- **Rate Limit**: 10/분

**호출 흐름**:
```
POST /api/v1/ai-assist/generate-description
    ↓
registration.py:generate_material_description()
    ↓
openai_client.py:generate_text()
    ↓
프롬프트: DESCRIPTION_GENERATION_PROMPT
```

**프롬프트 특징**:
```python
"""
당신은 건설 잉여자재 마켓플레이스의 상품 설명 작성 전문가입니다.

규칙:
- 200자 내외로 간결하게 작성
- 자재의 특성, 상태, 활용 가능성을 포함
- 건설 전문 용어를 적절히 사용하되 이해하기 쉽게
- 과장 없이 사실에 기반
"""
```

#### 2. 가격 제안 (Price Suggestion)

- **파일**: `registration.py:suggest_material_price()`
- **모델**: `gpt-5-nano`
- **Temperature**: 0.3 (일관적)
- **Max Tokens**: 256
- **Rate Limit**: 10/분

**호출 흐름**:
```
POST /api/v1/ai-assist/suggest-price
    ↓
registration.py:suggest_material_price()
    ↓
search.py:vector_search_only() (유사 자재 검색)
    ↓
openai_client.py:generate_text()
    ↓
JSON 응답 파싱 → PriceSuggestResponse
```

**응답 형식**:
```json
{
  "suggested_price": 150000,
  "price_range_low": 120000,
  "price_range_high": 180000,
  "reasoning": "유사 매물 평균가 기준 ±20% 범위"
}
```

#### 3. 채팅 추천 (Chat Suggestions)

- **파일**: `qa_bot.py:generate_chat_suggestions()`
- **모델**: `gpt-5-nano`
- **Temperature**: 0.8 (다양성)
- **Max Tokens**: 256
- **Rate Limit**: 20/분
- **패턴**: `generate_text_with_history` (대화 히스토리 포함)

**호출 흐름**:
```
POST /api/v1/ai-assist/chat-suggestions
    ↓
qa_bot.py:generate_chat_suggestions()
    ↓
최근 메시지 10개 조회 + 자재 정보 추가
    ↓
openai_client.py:generate_text_with_history()
    ↓
JSON 배열 파싱 → ["답장1", "답장2", "답장3"]
```

**응답 형식**:
```json
["확인했습니다.", "가격 협상 가능할까요?", "언제 거래 가능하신가요?"]
```

#### 4. 커뮤니티 답변 (Community Answer)

- **파일**: `qa_bot.py:generate_community_answer()`
- **모델**: 조건부 선택
  - `gpt-5-nano`: 기본 (게시글 길이 ≤ 500자, 일반 카테고리)
  - `gpt-5-mini`: 복잡한 추론 필요 (게시글 길이 > 500자 또는 Safety 카테고리)
- **Temperature**: 0.5 (균형)
- **Max Tokens**: 1024
- **Rate Limit**: 5/분

**모델 선택 로직**:
```python
use_reasoning = len(post.content) > 500 or (
    post.category and post.category.lower() in ("safety", "안전")
)
model = REASONING_MODEL if use_reasoning else DEFAULT_MODEL
```

**프롬프트 특징**:
```python
"""
당신은 건설 현장 안전 및 자재 전문가입니다.

규칙:
- 200~300자 내외로 작성
- 안전 관련 질문은 반드시 관련 규정/기준을 언급
- 실무 경험에 기반한 실용적 조언 포함
- 불확실한 정보는 "전문가 확인 필요"로 명시
"""
```

#### 5. 토론 요약 (Discussion Summarize)

- **파일**: `qa_bot.py:summarize_discussion()`
- **모델**: `gpt-5-nano`
- **Temperature**: 0.3 (일관적)
- **Max Tokens**: 512
- **Rate Limit**: 5/분

**호출 흐름**:
```
POST /api/v1/ai-assist/summarize-discussion
    ↓
qa_bot.py:summarize_discussion()
    ↓
게시글 + 댓글 최대 100개 조회
    ↓
openai_client.py:generate_text()
    ↓
JSON 응답 파싱 → SummarizeResponse
```

**응답 형식**:
```json
{
  "summary": "3줄 이내 요약",
  "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"]
}
```

### JSON 응답 파싱 (공통 로직)

```python
# Markdown code fence 제거
text = raw.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text[:-3].strip()

# JSON 파싱
try:
    data = json.loads(text)
except json.JSONDecodeError:
    logger.warning("LLM returned non-JSON: %s", text[:200])
    # 기본값 반환
```

### 에러 처리 (공통)

```python
try:
    result = service_function(...)
except Exception:
    raise HTTPException(status_code=502, detail="LLM service unavailable")
```

---

## 3. Sentence-Transformers (로컬 임베딩)

### 기본 정보

| 항목 | 내용 |
|------|------|
| **라이브러리** | `sentence-transformers >= 3.0.0` |
| **모델** | `BAAI/bge-m3` (다국어, 1024차원) |
| **위치** | `app/ai/clients/embeddings.py` |
| **외부 API 호출** | **없음** (로컬 실행) |

### 클라이언트 구조

**싱글톤 패턴**: Thread-safe double-check locking

```python
_model = None
_lock = threading.Lock()

def _get_model():
    """Thread-safe singleton for SentenceTransformer."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                logger.info("Embedding model loaded successfully")
    return _model
```

### 설정

- **환경변수**: `EMBEDDING_MODEL_NAME` (기본값: `BAAI/bge-m3`)
- **차원**: `EMBEDDING_DIMENSION=1024` (config.py)
- **외부 API 키**: 불필요 (로컬 모델)

### 모델 특징

| 항목 | 내용 |
|------|------|
| **모델명** | BAAI/bge-m3 |
| **타입** | 다국어 임베딩 모델 |
| **차원** | 1024 (고정) |
| **정규화** | `normalize_embeddings=True` |
| **메모리** | ~2.4GB (모델 로딩 시) |

### 메모리 최적화

**gunicorn 프리로드 모드**:
```bash
gunicorn --preload app.main:app
```

- 모델을 부모 프로세스에서 한 번만 로드
- 자식 프로세스들이 메모리 공유 (CoW, Copy-on-Write)
- 메모리 절약: 워커 N개 × 2.4GB → 1회만 로드

### 검색 텍스트 빌드

```python
def build_search_text(
    title: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
) -> str:
    """자재 필드를 하나의 검색 텍스트로 결합."""
    parts = [title]
    if category:
        parts.append(f"카테고리: {category}")
    if description:
        parts.append(description[:500])  # 최대 500자
    return " ".join(parts)
```

### 임베딩 생성

#### 단일 벡터 생성

```python
def generate_embedding(text: str) -> List[float]:
    """단일 임베딩 벡터 생성."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
```

#### 배치 벡터 생성

```python
def generate_embeddings_batch(
    texts: List[str], batch_size: int = 32
) -> List[List[float]]:
    """여러 텍스트의 임베딩을 배치로 생성."""
    model = _get_model()
    vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
```

### 사용처

#### 1. 자재 등록/수정 시 자동 생성 (Embedding Hook)

**파일**: `app/ai/services/embedding_hook.py:update_material_embedding()`

```python
def update_material_embedding(db: Session, material: Material) -> bool:
    """자재 임베딩을 생성하고 저장. 실패 시에도 메인 흐름을 방해하지 않음."""
    try:
        search_text = build_search_text(
            title=material.title,
            description=material.description,
            category=material.category,
        )
        embedding = generate_embedding(search_text)
        material.embedding_vector = embedding
        db.commit()
        return True
    except Exception:
        logger.exception("Failed to update embedding for material %d", material.id)
        db.rollback()
        return False
```

**실패 안전성**:
- try/except로 래핑
- 임베딩 실패 시에도 자재 등록은 성공
- 로그 기록 후 rollback

#### 2. 하이브리드 검색 (Semantic + Keyword)

**파일**: `app/ai/services/search.py`

**벡터 유사도 검색**:
```python
def vector_search_only(db: Session, query: str, limit: int = 20):
    """벡터 유사도 검색 (코사인 유사도)."""
    query_vector = generate_embedding(query)

    # pgvector 코사인 유사도 (<=> 연산자)
    results = db.execute(
        text("""
            SELECT id, title, description, price, category,
                   1 - (embedding_vector <=> :query_vector) AS similarity
            FROM materials
            WHERE embedding_vector IS NOT NULL
            ORDER BY embedding_vector <=> :query_vector
            LIMIT :limit
        """),
        {"query_vector": query_vector, "limit": limit}
    )
    return results
```

**하이브리드 검색** (벡터 + 키워드):
```python
def hybrid_search(db: Session, query: str, page: int, limit: int):
    """벡터 유사도 + 키워드 매칭 결합 검색."""
    # 1. 벡터 검색
    vector_results = vector_search_only(db, query, limit * 2)

    # 2. 키워드 검색 (LIKE)
    keyword_results = keyword_search(db, query, limit * 2)

    # 3. 점수 결합 (vector_similarity * 0.7 + keyword_score * 0.3)
    combined = combine_scores(vector_results, keyword_results)

    # 4. 페이지네이션
    return paginate(combined, page, limit)
```

#### 3. 가격 제안 시 유사 자재 검색

**파일**: `registration.py:suggest_material_price()`

```python
# 유사 자재 10개 조회 (벡터 검색)
similar = vector_search_only(db, query=title, limit=10)

# 유사 자재 가격 정보를 LLM에 전달
similar_info = []
for material, similarity in similar:
    similar_info.append(
        f"- {material.title}: {material.price:,}원 (유사도: {similarity:.2f})"
    )
```

### 배치 백필 (Batch Backfill)

**스크립트**: `scripts/backfill_embeddings.py`

기존 자재에 대해 임베딩을 일괄 생성:

```python
# 임베딩이 없는 자재 조회
materials_without_embeddings = db.query(Material).filter(
    Material.embedding_vector.is_(None)
).all()

# 배치로 임베딩 생성
texts = [build_search_text(m.title, m.description, m.category) for m in materials]
embeddings = generate_embeddings_batch(texts, batch_size=32)

# DB 업데이트
for material, embedding in zip(materials, embeddings):
    material.embedding_vector = embedding
db.commit()
```

---

## 4. API 키 관리

### 환경변수 설정

**파일**: `app/core/config.py`

```python
class Settings(BaseSettings):
    # AI Services
    GOOGLE_AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024
```

### .env.example 문서화

**파일**: `.env.example`

```bash
# ===== AI Services =====
# Google Gemini API Key (for image analysis)
# GOOGLE_AI_API_KEY=your-google-ai-api-key
# OpenAI API Key (for text generation)
# OPENAI_API_KEY=your-openai-api-key
# Embedding model (default: BAAI/bge-m3)
EMBEDDING_MODEL_NAME=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
```

### 키 없을 때의 동작

| 서비스 | 환경변수 | 키 누락 시 동작 |
|--------|---------|---------------|
| **Gemini Vision** | `GOOGLE_AI_API_KEY` | HTTPException 502 ("Vision AI service unavailable") |
| **OpenAI GPT** | `OPENAI_API_KEY` | HTTPException 502 ("LLM service unavailable") |
| **Embeddings** | 불필요 (로컬) | 정상 작동 |

### 보안 고려사항

1. **환경변수 보관**:
   - `.env` 파일에 저장
   - `.gitignore`에 등록하여 버전 관리 제외

2. **프로덕션 배포**:
   - Docker secrets 또는 클라우드 Secret Manager 사용 권장
   - 환경변수로 주입

3. **API 키 검증**:
   - 애플리케이션 시작 시 로그로 키 존재 여부 확인
   - 키 없이도 서버 시작은 가능 (해당 기능만 비활성화)

---

## 5. 장애 대응

### 에러 처리 전략

모든 외부 API 호출은 try/except로 래핑하여 실패 시에도 서비스 전체가 중단되지 않도록 처리합니다.

#### 1. Vision AI 실패

```python
try:
    result = registration_service.analyze_material_image(body.image_url)
except Exception:
    raise HTTPException(status_code=502, detail="Vision AI service unavailable")
```

**클라이언트 응답**:
```json
{
  "status": "error",
  "detail": "Vision AI service unavailable"
}
```

**복구 방법**:
- API 키 확인
- Google AI API 상태 확인
- Rate limit 확인

#### 2. LLM 서비스 실패

```python
try:
    result = registration_service.generate_material_description(...)
except Exception:
    raise HTTPException(status_code=502, detail="LLM service unavailable")
```

**클라이언트 응답**:
```json
{
  "status": "error",
  "detail": "LLM service unavailable"
}
```

**복구 방법**:
- API 키 확인
- OpenAI API 상태 확인
- Rate limit 확인

#### 3. 임베딩 생성 실패

**특수 처리**: 임베딩 실패 시에도 자재 등록은 성공

```python
def update_material_embedding(db: Session, material: Material) -> bool:
    try:
        embedding = generate_embedding(search_text)
        material.embedding_vector = embedding
        db.commit()
        return True
    except Exception:
        logger.exception("Failed to update embedding for material %d", material.id)
        db.rollback()
        return False
```

**결과**:
- 자재는 정상 등록
- `embedding_vector` 필드만 NULL
- 검색 시 해당 자재는 키워드 검색에만 포함 (벡터 검색 제외)

**복구 방법**:
- 배치 백필 스크립트 실행: `python scripts/backfill_embeddings.py`
- 모델 다운로드 확인: Hugging Face Hub 연결 상태

### 장애 모니터링

#### 로그 분석

```python
logger.warning("Gemini returned non-JSON response: %s", text[:200])
logger.warning("Price suggestion LLM returned non-JSON: %s", text[:200])
logger.exception("Failed to update embedding for material %d", material.id)
```

**모니터링 포인트**:
- JSON 파싱 실패 빈도
- HTTPException 502 발생 빈도
- 임베딩 생성 실패율

#### 헬스체크 엔드포인트 (향후 추가 권장)

```python
@router.get("/ai-health")
def ai_health_check():
    """AI 서비스 상태 확인."""
    status = {
        "gemini": check_gemini_available(),
        "openai": check_openai_available(),
        "embeddings": check_embeddings_model_loaded(),
    }
    return {"status": "healthy", "services": status}
```

---

## 6. 비용 최적화

### 모델 선택 전략

| 서비스 | 모델 | 이유 |
|--------|------|------|
| **이미지 분석** | Gemini 2.5 Flash-Lite | Vision 모델 중 가장 저렴 |
| **텍스트 생성** | GPT-5 Nano (우선) | 기본 작업에 충분, 저렴 |
| **복잡한 추론** | GPT-5 Mini (조건부) | 긴 게시글, Safety 카테고리만 |
| **임베딩** | BAAI/bge-m3 (로컬) | **API 비용 0원** |

### Rate Limiting으로 과도한 호출 방지

**slowapi를 통한 제한**:

| 엔드포인트 | Rate Limit | 이유 |
|-----------|-----------|------|
| `/ai-assist/search` | 30/분 | 검색은 비교적 가벼움 |
| `/ai-assist/analyze-image` | 10/분 | Vision API 비용 높음 |
| `/ai-assist/generate-description` | 10/분 | LLM 비용 관리 |
| `/ai-assist/suggest-price` | 10/분 | 벡터 검색 + LLM 결합 |
| `/ai-assist/chat-suggestions` | 20/분 | 실시간 채팅 보조 |
| `/ai-assist/community-answer` | 5/분 | 추론 모델 사용 가능성 |
| `/ai-assist/summarize-discussion` | 5/분 | 댓글 100개까지 처리 |

### 비용 절감 팁

1. **임베딩은 로컬 모델 사용**:
   - OpenAI Embeddings API를 사용하지 않음
   - 초기 메모리 ~2.4GB 필요하지만 API 비용 0원

2. **GPT-5 Nano 우선 사용**:
   - 긴 게시글/Safety 카테고리만 Mini 사용
   - 대부분의 텍스트 생성은 Nano로 충분

3. **토큰 제한**:
   - 설명 생성: max_tokens=512 (과도한 장문 방지)
   - 가격 제안: max_tokens=256 (JSON만 필요)
   - 채팅 추천: max_tokens=256 (짧은 답장만)

4. **입력 길이 제한**:
   - 설명 텍스트: 최대 500자로 truncate
   - 댓글 요약: 최대 100개 댓글까지만

5. **캐싱 전략 (향후 추가 권장)**:
   - 동일한 이미지 분석 결과 캐싱 (Redis)
   - 유사한 가격 제안 요청 캐싱

---

## 7. 성능 최적화

### 싱글톤 패턴으로 클라이언트 재사용

모든 AI 클라이언트는 Thread-safe 싱글톤으로 구현하여 재초기화 방지:

```python
# Gemini
_client = None
_lock = threading.Lock()

# OpenAI
_client = None
_lock = threading.Lock()

# Embeddings
_model = None
_lock = threading.Lock()
```

### gunicorn 프리로드로 메모리 절약

```bash
gunicorn --preload --workers 4 app.main:app
```

**효과**:
- 임베딩 모델 (~2.4GB)을 부모 프로세스에서 1회만 로드
- 자식 워커들이 Copy-on-Write로 메모리 공유
- 메모리 사용량: 4워커 × 2.4GB = 9.6GB → **약 2.4GB로 감소**

### 비동기 처리 (향후 개선 권장)

현재는 동기식 호출이지만, 향후 개선 시:

```python
# 현재 (동기)
result = registration_service.analyze_material_image(image_url)

# 향후 (비동기 - 백그라운드 태스크)
task_id = background_tasks.add_task(analyze_and_notify, image_url)
return {"task_id": task_id, "status": "processing"}
```

---

## 8. 의존성

### requirements.txt

```txt
# AI
sentence-transformers>=3.0.0
pgvector>=0.3.0
numpy>=1.24.0
google-genai>=1.0.0
openai>=1.30.0
```

### 추가 시스템 의존성

- **PostgreSQL + pgvector 확장**:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

- **Hugging Face 모델 다운로드**:
  - 첫 실행 시 `BAAI/bge-m3` 모델 자동 다운로드 (~2GB)
  - 캐시 위치: `~/.cache/huggingface/hub/`

---

## 9. 테스트

### 단위 테스트 (향후 추가 권장)

```python
# tests/ai/test_gemini.py
def test_analyze_image_success(mocker):
    mocker.patch("app.ai.clients.gemini.analyze_image")
    result = analyze_material_image("https://example.com/image.jpg")
    assert result.category is not None

# tests/ai/test_openai_client.py
def test_generate_text_success(mocker):
    mocker.patch("openai.OpenAI.chat.completions.create")
    result = generate_text("system", "user")
    assert isinstance(result, str)

# tests/ai/test_embeddings.py
def test_generate_embedding():
    embedding = generate_embedding("테스트 자재")
    assert len(embedding) == 1024
    assert all(isinstance(x, float) for x in embedding)
```

### 통합 테스트

```python
# tests/api/test_ai_assist.py
def test_analyze_image_endpoint(client, test_user):
    response = client.post(
        "/api/v1/ai-assist/analyze-image",
        json={"imageUrl": "https://example.com/test.jpg"},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    assert "category" in response.json()["data"]
```

---

## 10. 문제 해결 (Troubleshooting)

### Q1. "Vision AI service unavailable" 에러

**원인**:
1. `GOOGLE_AI_API_KEY` 환경변수 미설정
2. API 키 만료 또는 잘못된 키
3. Google AI API 서비스 장애
4. Rate limit 초과

**해결**:
```bash
# .env 파일 확인
cat .env | grep GOOGLE_AI_API_KEY

# API 키 유효성 테스트
curl -H "Authorization: Bearer $GOOGLE_AI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

### Q2. "LLM service unavailable" 에러

**원인**:
1. `OPENAI_API_KEY` 환경변수 미설정
2. API 키 만료 또는 잘못된 키
3. OpenAI API 서비스 장애
4. Rate limit 초과

**해결**:
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# API 키 유효성 테스트
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Q3. 임베딩 생성 실패

**원인**:
1. 임베딩 모델 미다운로드
2. Hugging Face Hub 연결 실패
3. 메모리 부족 (~2.4GB 필요)

**해결**:
```bash
# 모델 수동 다운로드
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# 메모리 확인
free -h

# 배치 백필로 재시도
python scripts/backfill_embeddings.py
```

### Q4. JSON 파싱 실패 경고 로그

**로그**:
```
WARNING: Gemini returned non-JSON response: ...
WARNING: Price suggestion LLM returned non-JSON: ...
```

**원인**:
- LLM이 markdown code fence로 JSON을 감쌈
- LLM이 JSON 외 텍스트 포함

**해결**:
- 코드에서 자동으로 code fence 제거 처리
- 파싱 실패 시 기본값 반환 (서비스 계속 동작)

### Q5. Rate limit 초과

**에러**:
```
429 Too Many Requests
```

**해결**:
1. **서버측 Rate Limit (slowapi)**:
   - 1분 후 재시도
   - 클라이언트에 429 응답

2. **외부 API Rate Limit**:
   - Google/OpenAI 대시보드에서 한도 확인
   - 유료 플랜 업그레이드 고려

---

## 11. 향후 개선 사항

### 1. 비동기 AI 처리

```python
from fastapi import BackgroundTasks

@router.post("/analyze-image-async")
async def analyze_image_async(
    background_tasks: BackgroundTasks,
    body: ImageAnalysisRequest,
):
    task_id = create_task_id()
    background_tasks.add_task(process_image_analysis, task_id, body.image_url)
    return {"task_id": task_id, "status": "processing"}
```

### 2. 응답 캐싱 (Redis)

```python
@router.post("/analyze-image")
@cache(expire=3600)  # 1시간 캐싱
def analyze_image(body: ImageAnalysisRequest):
    # 동일한 image_url에 대해 캐시된 결과 반환
    pass
```

### 3. AI 서비스 헬스체크

```python
@router.get("/ai-health")
def ai_health():
    return {
        "gemini": {"status": "healthy", "latency_ms": 120},
        "openai": {"status": "healthy", "latency_ms": 85},
        "embeddings": {"status": "healthy", "model_loaded": True},
    }
```

### 4. 모니터링 및 메트릭

```python
from prometheus_client import Counter, Histogram

ai_requests = Counter("ai_requests_total", "Total AI requests", ["service"])
ai_latency = Histogram("ai_latency_seconds", "AI request latency", ["service"])
```

### 5. A/B 테스트를 통한 모델 비교

```python
# Gemini vs GPT Vision 비교
if user_id % 2 == 0:
    result = gemini_analyze(image_url)
else:
    result = openai_vision_analyze(image_url)
```

---

## 참고 자료

- [Google Gemini API 문서](https://ai.google.dev/docs)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Sentence-Transformers 문서](https://www.sbert.net/)
- [pgvector 문서](https://github.com/pgvector/pgvector)
- [BAAI/bge-m3 모델](https://huggingface.co/BAAI/bge-m3)

---

*Last Updated: 2026-02-21*
