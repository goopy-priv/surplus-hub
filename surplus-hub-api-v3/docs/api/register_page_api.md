# 자재 등록 화면 API 명세서 (Register Screen API Specification)

`flutter-view`로 구현된 자재 등록 화면(`RegisterPage`)에서 사용되는 API 명세서입니다.
이 문서는 자재 판매/나눔을 위한 게시글 등록(Create)과 이미지 업로드 API를 정의합니다.

## 1. 자재 등록 (Register Material)

새로운 잉여 자재 판매/나눔 게시글을 등록합니다.

- **Endpoint**: `POST /api/v1/materials`
- **목적**: 판매할 자재 정보(제목, 가격, 설명, 사진 등) 저장
- **인증**: Bearer Token 필요
- **Content-Type**: `application/json`

### 요청 바디 (Request Body)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | String | Yes | 자재 제목 |
| `description` | String | Yes | 자재 상세 설명 |
| `price` | Number | Yes | 가격 (0이면 무료나눔) |
| `quantity` | Integer | Yes | 수량 |
| `quantityUnit` | String | Yes | 수량 단위 (예: '개', 'kg', '포대', '박스') |
| `tradeMethod` | String | Yes | 거래 방식 (`DIRECT`: 직거래, `DELIVERY`: 택배, `BOTH`: 무관) |
| `location` | Object | Yes | 거래 희망 지역 정보 |
| `location.address` | String | Yes | 주소 문자열 (예: "서울 강남구 역삼동") |
| `location.lat` | Double | No | 위도 |
| `location.lng` | Double | No | 경도 |
| `photoUrls` | Array<String> | No | 업로드된 이미지 URL 리스트 |
| `category` | String | No | 카테고리 코드 (자동 분류가 아닐 경우 필수) |

### 요청 예시 (Example Request)
```json
{
  "title": "남은 방부목 데크재 팝니다",
  "description": "공사하고 남은 방부목입니다. 상태 A급이고 실내 보관 중입니다.",
  "price": 50000,
  "quantity": 10,
  "quantityUnit": "개",
  "tradeMethod": "DIRECT",
  "location": {
    "address": "서울 강남구 역삼동",
    "lat": 37.5000,
    "lng": 127.0300
  },
  "photoUrls": [
    "https://api.surplushub.com/temp/image1.jpg",
    "https://api.surplushub.com/temp/image2.jpg"
  ],
  "category": "WOOD"
}
```

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `id` | String | 생성된 자재 게시글 ID |
| `createdAt` | String | 등록 일시 (ISO 8601) |
| `status` | String | 게시글 상태 (`ACTIVE`, `REVIEWING`) |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "mat_new_12345",
    "createdAt": "2024-05-20T15:30:00Z",
    "status": "ACTIVE"
  }
}
```

---

## 2. 이미지 업로드 (Upload Images)

게시글에 첨부할 자재 사진을 업로드합니다. 다중 파일 업로드를 지원합니다.

- **Endpoint**: `POST /api/v1/upload/images`
- **목적**: 자재 사진을 서버(또는 스토리지)에 저장하고 접근 가능한 URL 획득
- **인증**: Bearer Token 필요
- **Content-Type**: `multipart/form-data`

### 요청 파라미터 (Form Data)
| Key | Type | Description |
|-----|------|-------------|
| `files` | File[] | 업로드할 이미지 파일들 (최대 10장) |
| `type` | String | 이미지 용도 (예: `MATERIAL`) |

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `urls` | Array<String> | 업로드된 이미지의 URL 리스트 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "urls": [
      "https://api.surplushub.com/materials/2024/05/20/img_001.jpg",
      "https://api.surplushub.com/materials/2024/05/20/img_002.jpg"
    ]
  }
}
```

---

## 3. 주소 검색 (Search Location) - Optional

사용자가 거래 희망 지역을 입력할 때 검색을 돕는 API입니다.

- **Endpoint**: `GET /api/v1/locations/search`
- **목적**: 키워드로 주소/지역 검색
- **인증**: 불필요

### 요청 파라미터 (Query Parameters)
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keyword` | String | Yes | 검색할 주소 키워드 (예: "역삼동") |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": [
    {
      "addressName": "서울 강남구 역삼동",
      "lat": 37.5006,
      "lng": 127.0364
    },
    {
      "addressName": "경기 용인시 처인구 역삼동",
      "lat": 37.2409,
      "lng": 127.1780
    }
  ]
}
```
