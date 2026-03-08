# AI API 엔드포인트 문서

건설 잉여자재 마켓플레이스 Surplus Hub API v3의 AI 기능 엔드포인트입니다.

## 개요

이 문서는 Surplus Hub API의 7개 AI 엔드포인트를 정의합니다. 모든 AI 기능은 OpenAI GPT-4o 및 Google Gemini Vision AI를 활용하여 자재 등록, 검색, 채팅, 커뮤니티 기능을 지원합니다.

### 엔드포인트 요약

| 메서드 | 경로 | 설명 | 인증 | Rate Limit |
|--------|------|------|------|------------|
| `GET` | `/api/v1/ai/search` | 하이브리드 시맨틱 검색 | 불필요 | 30회/분 |
| `POST` | `/api/v1/ai/analyze-image` | 자재 이미지 분석 | 필수 | 10회/분 |
| `POST` | `/api/v1/ai/generate-description` | 자재 설명 자동 생성 | 필수 | 10회/분 |
| `POST` | `/api/v1/ai/suggest-price` | 자재 가격 제안 | 필수 | 10회/분 |
| `POST` | `/api/v1/ai/chat-suggestions` | 채팅 답변 제안 | 필수 | 20회/분 |
| `POST` | `/api/v1/ai/community-answer` | 커뮤니티 질문 AI 답변 | 필수 | 5회/분 |
| `POST` | `/api/v1/ai/summarize-discussion` | 커뮤니티 토론 요약 | 필수 | 5회/분 |

---

## 공통 사항

### 인증 (Authentication)

인증이 필요한 엔드포인트는 Bearer 토큰을 사용합니다.

```http
Authorization: Bearer <JWT_TOKEN>
```

**인증 흐름**:
1. `/api/v1/auth/login` 엔드포인트에서 JWT 토큰 발급
2. `deps.get_current_active_user` 의존성을 통해 사용자 검증 (PyJWT 기반)
3. 활성 사용자만 AI 기능 사용 가능

### Rate Limiting

Rate Limiting은 `slowapi` 라이브러리를 사용하여 IP 기반으로 적용됩니다.

| 제한 방식 | 설명 |
|----------|------|
| **IP 기반** | 각 클라이언트 IP 주소당 제한 |
| **분 단위** | 제한은 1분 단위로 재설정 |
| **429 응답** | 제한 초과 시 `429 Too Many Requests` 반환 |

### 응답 형식

모든 AI 엔드포인트는 camelCase 응답 규칙을 따릅니다 (Pydantic `alias` 사용).

**성공 응답**:
```json
{
  "status": "success",
  "data": { ... }
}
```

**에러 응답**:
```json
{
  "detail": "Error message"
}
```

### 공통 에러 응답

| 상태 코드 | 설명 | 응답 예시 |
|----------|------|----------|
| `401 Unauthorized` | 인증 토큰 없음 또는 만료 | `{"detail": "Not authenticated"}` |
| `422 Unprocessable Entity` | 요청 스키마 검증 실패 | `{"detail": [{"loc": ["body", "imageUrl"], "msg": "field required"}]}` |
| `502 Bad Gateway` | AI 서비스 (OpenAI/Gemini) 장애 | `{"detail": "Vision AI service unavailable"}` |

---

## 1. 하이브리드 시맨틱 검색

자연어 쿼리를 사용하여 자재를 검색합니다. 키워드 매칭과 벡터 유사도를 결합한 하이브리드 검색을 제공합니다.

### 엔드포인트

```
GET /api/v1/ai/search
```

### 인증

불필요

### Rate Limit

30회/분

### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `q` | string | ✅ | - | 검색 쿼리 (예: "각목 10개") |
| `page` | integer | ❌ | 1 | 페이지 번호 |
| `limit` | integer | ❌ | 20 | 페이지당 항목 수 (최대 100) |
| `category` | string | ❌ | null | 카테고리 필터 (예: "목재") |

### 요청 예시

```http
GET /api/v1/ai/search?q=각목+10개&page=1&limit=20&category=목재
```

### 응답 스키마

```typescript
{
  status: "success",
  data: Array<{
    id: number;
    title: string;
    description: string;
    price: number;
    category: string | null;
    thumbnailUrl: string | null;
    score: number;              // 종합 점수 (0.0 ~ 1.0)
    vectorSimilarity: number;   // 벡터 유사도 (0.0 ~ 1.0)
    keywordScore: number;       // 키워드 매칭 점수 (0.0 ~ 1.0)
  }>,
  meta: {
    totalCount: number;
    page: number;
    limit: number;
    hasNextPage: boolean;
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": [
    {
      "id": 42,
      "title": "각목 10개 세트 (3m)",
      "description": "건축용 각목 10개입니다. 상태 양호하며 약간의 긁힘이 있습니다.",
      "price": 50000,
      "category": "목재",
      "thumbnailUrl": "https://s3.amazonaws.com/surplus-hub/materials/42/thumb.jpg",
      "score": 0.89,
      "vectorSimilarity": 0.92,
      "keywordScore": 0.86
    }
  ],
  "meta": {
    "totalCount": 15,
    "page": 1,
    "limit": 20,
    "hasNextPage": false
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `422` | `q` 파라미터 누락 |
| `429` | Rate limit 초과 (30회/분) |

---

## 2. 자재 이미지 분석

Vision AI를 사용하여 자재 이미지를 분석하고 카테고리, 태그, 제목, 상태를 자동으로 추출합니다.

### 엔드포인트

```
POST /api/v1/ai/analyze-image
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

10회/분

### 요청 스키마

```typescript
{
  imageUrl: string;  // HTTPS URL (S3, Cloudinary 등)
}
```

### 요청 예시

```json
{
  "imageUrl": "https://s3.amazonaws.com/surplus-hub/upload/temp/abc123.jpg"
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    category: string | null;       // 추출된 카테고리 (예: "목재", "철근")
    tags: string[];                // 추출된 태그 배열
    titleSuggestion: string | null; // 제안된 제목
    condition: string | null;      // 상태 (예: "상", "중", "하")
    materialType: string | null;   // 자재 유형 (예: "각목", "H빔")
    confidence: number;            // 신뢰도 (0.0 ~ 1.0)
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "category": "목재",
    "tags": ["각목", "건축자재", "원목"],
    "titleSuggestion": "건축용 각목 10개 세트",
    "condition": "상",
    "materialType": "각목",
    "confidence": 0.94
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `imageUrl` 필드 누락 또는 형식 오류 |
| `502` | Gemini Vision AI 서비스 장애 |
| `429` | Rate limit 초과 (10회/분) |

---

## 3. 자재 설명 자동 생성

LLM을 사용하여 자재 제목과 메타데이터를 기반으로 설명을 자동 생성합니다.

### 엔드포인트

```
POST /api/v1/ai/generate-description
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

10회/분

### 요청 스키마

```typescript
{
  title: string;             // 필수: 자재 제목
  tags?: string[];           // 선택: 태그 배열
  category?: string | null;  // 선택: 카테고리
  condition?: string | null; // 선택: 상태 (예: "상", "중", "하")
  quantity?: number | null;  // 선택: 수량
  quantityUnit?: string | null; // 선택: 수량 단위 (예: "개", "톤")
}
```

### 요청 예시

```json
{
  "title": "건축용 각목 10개 세트",
  "tags": ["각목", "원목"],
  "category": "목재",
  "condition": "상",
  "quantity": 10,
  "quantityUnit": "개"
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    description: string;  // 생성된 설명
    modelUsed: string;    // 사용된 모델 이름 (예: "gpt-4o")
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "description": "건축용으로 사용된 각목 10개 세트입니다. 길이 3m, 단면 10cm x 10cm 규격이며 상태가 양호합니다. 일부 긁힘이 있으나 구조적 문제는 없습니다. 건축 현장, DIY 프로젝트에 적합합니다.",
    "modelUsed": "gpt-4o"
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `title` 필드 누락 |
| `502` | OpenAI LLM 서비스 장애 |
| `429` | Rate limit 초과 (10회/분) |

---

## 4. 자재 가격 제안

유사한 자재 데이터를 기반으로 적정 가격을 제안합니다.

### 엔드포인트

```
POST /api/v1/ai/suggest-price
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

10회/분

### 요청 스키마

```typescript
{
  title: string;             // 필수: 자재 제목
  category?: string | null;  // 선택: 카테고리
  condition?: string | null; // 선택: 상태 (예: "상", "중", "하")
  quantity?: number | null;  // 선택: 수량
}
```

### 요청 예시

```json
{
  "title": "건축용 각목 10개 세트",
  "category": "목재",
  "condition": "상",
  "quantity": 10
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    suggestedPrice: number;    // 제안 가격 (원)
    priceRangeLow: number;     // 가격 범위 하한 (원)
    priceRangeHigh: number;    // 가격 범위 상한 (원)
    reasoning: string;         // 가격 산정 근거
    similarCount: number;      // 참고한 유사 자재 개수
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "suggestedPrice": 50000,
    "priceRangeLow": 40000,
    "priceRangeHigh": 60000,
    "reasoning": "유사한 각목 자재 12건의 평균 가격(50,000원)을 기준으로 산정했습니다. 상태가 '상'이므로 평균 가격을 제안합니다.",
    "similarCount": 12
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `title` 필드 누락 |
| `502` | 가격 제안 서비스 장애 |
| `429` | Rate limit 초과 (10회/분) |

---

## 5. 채팅 답변 제안

채팅방의 대화 컨텍스트를 분석하여 빠른 답변 제안을 생성합니다.

### 엔드포인트

```
POST /api/v1/ai/chat-suggestions
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

20회/분

### 요청 스키마

```typescript
{
  roomId: number;  // 필수: 채팅방 ID
}
```

### 요청 예시

```json
{
  "roomId": 123
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    suggestions: string[];  // 제안된 답변 배열 (최대 3개)
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "suggestions": [
      "네, 가능합니다. 언제 방문하실 수 있으신가요?",
      "현재 재고가 10개 남아있습니다.",
      "가격은 협의 가능합니다. 직접 통화하시겠습니까?"
    ]
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `roomId` 필드 누락 또는 형식 오류 |
| `404` | 채팅방이 존재하지 않거나 접근 권한 없음 |
| `502` | Chat AI 서비스 장애 |
| `429` | Rate limit 초과 (20회/분) |

---

## 6. 커뮤니티 질문 AI 답변

커뮤니티 게시글을 분석하여 AI 기반 답변을 생성합니다.

### 엔드포인트

```
POST /api/v1/ai/community-answer
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

5회/분

### 요청 스키마

```typescript
{
  postId: number;  // 필수: 커뮤니티 게시글 ID
}
```

### 요청 예시

```json
{
  "postId": 456
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    answer: string;      // 생성된 AI 답변
    modelUsed: string;   // 사용된 모델 이름 (예: "gpt-4o")
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "answer": "각목을 보관할 때는 직사광선을 피하고 통풍이 잘 되는 그늘진 곳에 보관하는 것이 좋습니다. 습기에 노출되면 뒤틀림이 발생할 수 있으므로 바닥과의 간격을 두고 보관하세요. 장기 보관 시에는 방부제 처리를 권장합니다.",
    "modelUsed": "gpt-4o"
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `postId` 필드 누락 또는 형식 오류 |
| `404` | 게시글이 존재하지 않음 |
| `502` | QA bot 서비스 장애 |
| `429` | Rate limit 초과 (5회/분) |

---

## 7. 커뮤니티 토론 요약

커뮤니티 게시글과 댓글을 분석하여 토론 내용을 요약합니다.

### 엔드포인트

```
POST /api/v1/ai/summarize-discussion
```

### 인증

필수 (Bearer 토큰)

### Rate Limit

5회/분

### 요청 스키마

```typescript
{
  postId: number;  // 필수: 커뮤니티 게시글 ID
}
```

### 요청 예시

```json
{
  "postId": 789
}
```

### 응답 스키마

```typescript
{
  status: "success",
  data: {
    summary: string;       // 전체 토론 요약
    keyPoints: string[];   // 핵심 포인트 배열
  }
}
```

### 응답 예시

```json
{
  "status": "success",
  "data": {
    "summary": "이 토론은 건축 현장에서 잉여 자재를 효율적으로 관리하는 방법에 대한 논의입니다. 참여자들은 보관 방법, 재판매 전략, 법적 제약사항 등을 공유했습니다.",
    "keyPoints": [
      "잉여 자재는 현장별로 분류하여 보관",
      "재판매 시 품질 검증 필수",
      "건축폐기물 관리법 준수 필요",
      "온라인 플랫폼 활용 권장"
    ]
  }
}
```

### 에러 응답

| 상태 코드 | 설명 |
|----------|------|
| `401` | 인증 토큰 없음 또는 만료 |
| `422` | `postId` 필드 누락 또는 형식 오류 |
| `404` | 게시글이 존재하지 않음 |
| `502` | Summarization 서비스 장애 |
| `429` | Rate limit 초과 (5회/분) |

---

## 기술 스택

| 컴포넌트 | 기술 |
|---------|------|
| **LLM** | OpenAI GPT-4o |
| **Vision AI** | Google Gemini 1.5 Pro (Vision) |
| **벡터 DB** | PostgreSQL + pgvector |
| **임베딩** | OpenAI text-embedding-3-small |
| **Rate Limiting** | slowapi (IP 기반) |
| **인증** | PyJWT (Bearer Token) |
| **스키마 검증** | Pydantic v2 (camelCase aliases) |

---

## 참고 사항

### Pydantic 스키마 규칙

모든 AI 스키마는 `app/schemas/ai_schemas.py`에 정의되어 있으며 다음 규칙을 따릅니다:

```python
class Config:
    from_attributes = True
    populate_by_name = True  # snake_case와 camelCase 모두 허용
```

### camelCase 응답 규칙

응답은 `model_dump(by_alias=True)`를 사용하여 camelCase로 변환됩니다:

```python
# 내부 필드: thumbnail_url
# 응답 JSON: thumbnailUrl
```

### 비동기 처리

일부 AI 기능 (임베딩 생성)은 non-blocking 방식으로 처리됩니다:

```python
# materials.py
update_material_embedding(db, db_obj)  # 실패해도 자재 등록은 성공
```

### 에러 처리

AI 서비스 장애 시 502 응답을 반환하며, 재시도 로직은 클라이언트에서 구현해야 합니다.

---

## 버전 정보

- **API Version**: v3
- **문서 업데이트**: 2026-02-21
- **FastAPI**: 0.115+
- **Pydantic**: v2
- **Python**: 3.12+
