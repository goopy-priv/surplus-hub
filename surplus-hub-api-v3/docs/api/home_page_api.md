# 홈 화면 (자재 목록) API 명세서

이 문서는 홈 화면(`HomePage`)을 구현하기 위해 필요한 서버 API 명세를 정의합니다.
자재 목록 조회(검색/필터/정렬 포함) 및 카테고리 정보 조회 API를 포함합니다.

## 1. 자재 목록 조회 (검색 및 필터링)
조건에 맞는 자재 목록을 페이징하여 조회합니다.

- **Endpoint**: `GET /api/v1/materials`
- **용도**: 홈 화면의 자재 그리드(Grid) 표시, 검색, 카테고리 필터링, 정렬 적용
- **인증**: 선택 (비로그인 사용자도 조회 가능할 수 있음, 단 '거리순' 정렬 시 위치 정보 필요)

### 요청 파라미터 (Query Parameters)
| 파라미터명 | 타입 | 필수 여부 | 기본값 | 설명 |
|---|---|---|---|---|
| `q` | String | 선택 | - | 검색 키워드 (예: "시멘트") |
| `category` | String | 선택 | "전체" | 카테고리 필터 (예: "Wood", "Metal") |
| `sort` | String | 선택 | "latest" | 정렬 기준 (`latest`: 최신순, `distance`: 거리순, `popular`: 인기순) |
| `page` | Integer | 선택 | 1 | 페이지 번호 |
| `limit` | Integer | 선택 | 20 | 페이지당 항목 수 |
| `lat` | Double | 선택 | - | 사용자 위도 (거리순 정렬 시 필수) |
| `lng` | Double | 선택 | - | 사용자 경도 (거리순 정렬 시 필수) |

### 응답 스펙 (Response)
| 필드명 | 타입 | 설명 |
|---|---|---|
| `data` | Array | 자재 아이템 리스트 |
| `meta` | Object | 페이징 정보 (totalCount, currentPage, totalPages) |

#### 자재 아이템 (`data` 요소)
| 필드명 | 타입 | 설명 |
|---|---|---|
| `id` | String | 자재 고유 ID |
| `title` | String | 제목 |
| `price` | String | 가격 (포맷팅된 문자열, 예: "150,000원") |
| `location` | String | 판매 지역 |
| `seller` | String | 판매자 닉네임 |
| `imageUrl` | String | 썸네일 이미지 URL |
| `likes` | Integer | 좋아요 수 |
| `chats` | Integer | 채팅 수 |
| `category` | String | 카테고리 식별자 |
| `categoryPath` | Array<String> | 카테고리 경로 (예: ["자재", "목재"]) |
| `isNew` | Boolean | 신규 등록 여부 (배지 표시용) |

### 예시 (Example)
**요청**
`GET /api/v1/materials?category=Wood&sort=popular&page=1&limit=10`

**응답**
```json
{
  "status": "success",
  "data": [
    {
      "id": "mat_101",
      "title": "미사용 구조목 2x4 팝니다",
      "price": "50,000원",
      "location": "서울 강남구",
      "seller": "김목수",
      "imageUrl": "https://example.com/images/wood_1.jpg",
      "likes": 15,
      "chats": 3,
      "category": "Wood",
      "categoryPath": ["건축자재", "목재"],
      "isNew": true
    },
    {
      "id": "mat_102",
      "title": "합판 자투리 일괄",
      "price": "무료",
      "location": "경기 성남시",
      "seller": "박반장",
      "imageUrl": "https://example.com/images/wood_2.jpg",
      "likes": 42,
      "chats": 10,
      "category": "Wood",
      "categoryPath": ["건축자재", "목재", "합판"],
      "isNew": false
    }
  ],
  "meta": {
    "totalCount": 45,
    "currentPage": 1,
    "totalPages": 5
  }
}
```

---

## 2. 카테고리 목록 조회
홈 화면 상단 필터에 사용할 카테고리 목록을 조회합니다.

- **Endpoint**: `GET /api/v1/categories`
- **용도**: 카테고리 필터 탭 렌더링

### 응답 스펙 (Response)
| 필드명 | 타입 | 설명 |
|---|---|---|
| `id` | String | 카테고리 ID |
| `name` | String | 표시할 카테고리 명 (예: "목재", "금속") |
| `slug` | String | API 요청용 식별자 |

### 예시 (Example)
```json
{
  "status": "success",
  "data": [
    { "id": "cat_all", "name": "전체", "slug": "all" },
    { "id": "cat_wood", "name": "목재", "slug": "wood" },
    { "id": "cat_metal", "name": "금속", "slug": "metal" },
    { "id": "cat_concrete", "name": "콘크리트", "slug": "concrete" }
  ]
}
```
