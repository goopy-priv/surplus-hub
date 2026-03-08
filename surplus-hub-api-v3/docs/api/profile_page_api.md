# 프로필 화면 API 명세서 (Profile Screen API Specification)

`flutter-view`로 구현된 프로필 화면(`ProfilePage`)에서 사용되는 API 명세서입니다.
이 문서는 사용자 정보 조회, 진행 중인 거래 요약, 그리고 메뉴의 배지(Badge) 정보를 불러오기 위한 API를 정의합니다.

## 1. 내 프로필 정보 조회 (Get User Profile)

로그인된 사용자의 상세 프로필 정보를 조회합니다. 프로필 헤더와 사용자 통계(신뢰도, 매너온도 등)를 렌더링하는 데 사용됩니다.

- **Endpoint**: `GET /api/v1/users/me`
- **목적**: 프로필 상단의 사용자 정보 및 활동 통계 표시
- **인증**: Bearer Token 필요

### 요청 헤더 (Request Headers)
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | 인증 토큰 |

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `id` | String | 사용자 고유 ID |
| `name` | String | 사용자 닉네임 |
| `profileImageUrl` | String | 프로필 이미지 URL |
| `location` | String | 활동 지역 |
| `trustLevel` | Integer | 신뢰 등급 (1-10) |
| `mannerTemperature` | Double | 매너 온도 (예: 36.5) |
| `stats` | Object | 활동 통계 객체 |
| `stats.salesCount` | Integer | 판매 내역 수 |
| `stats.purchaseCount` | Integer | 구매 내역 수 |
| `stats.reviewCount` | Integer | 받은 후기 수 |
| `isPremium` | Boolean | 프리미엄 멤버십 여부 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "usr_20240520",
    "name": "김철수",
    "profileImageUrl": "https://api.surplushub.com/images/profiles/usr_20240520.jpg",
    "location": "서울 강남구",
    "trustLevel": 3,
    "mannerTemperature": 42.5,
    "stats": {
      "salesCount": 15,
      "purchaseCount": 8,
      "reviewCount": 23
    },
    "isPremium": false
  }
}
```

---

## 2. 진행 중인 거래 요약 (Get Ongoing Trades Summary)

사용자의 현재 진행 중인 거래 상태를 요약하여 반환합니다. "진행중인 거래" 위젯에 표시될 텍스트와 상태를 제공합니다.

- **Endpoint**: `GET /api/v1/trades/ongoing/summary`
- **목적**: 대시보드 형태의 거래 현황 요약 카드 표시
- **인증**: Bearer Token 필요

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `activeTradeCount` | Integer | 진행 중인 총 거래 수 |
| `summaryMessage` | String | 사용자에게 보여줄 요약 메시지 |
| `highlightStatus` | String | 강조할 거래 상태 (예: `WAITING_APPROVAL`, `IN_PROGRESS`) |
| `actionUrl` | String | '자세히 보기' 버튼 클릭 시 이동할 딥링크 또는 경로 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "activeTradeCount": 1,
    "summaryMessage": "1건의 거래가 승인 대기 중입니다",
    "highlightStatus": "WAITING_APPROVAL",
    "actionUrl": "/trades/ongoing"
  }
}
```

---

## 3. 사용자 활동 배지 조회 (Get User Activity Badges)

메뉴 리스트에 표시할 "신규" 알림이나 카운트 배지 정보를 조회합니다.

- **Endpoint**: `GET /api/v1/users/me/badges`
- **목적**: '관심 목록', '공지사항' 등의 메뉴 아이템 옆에 신규 알림 표시
- **인증**: Bearer Token 필요

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `newFavoritesCount` | Integer | 새로운 관심 목록 아이템 수 (0이면 배지 숨김) |
| `unreadNoticesCount` | Integer | 읽지 않은 공지사항 수 |
| `newReviewsCount` | Integer | 확인하지 않은 새 후기 수 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "newFavoritesCount": 3,
    "unreadNoticesCount": 0,
    "newReviewsCount": 1
  }
}
```

---

## 4. 프로필 정보 수정 (Update User Profile)

사용자의 프로필 정보를 수정합니다.

- **Endpoint**: `PUT /api/v1/users/me`
- **목적**: 닉네임, 프로필 사진, 지역 정보 수정
- **인증**: Bearer Token 필요

### 요청 바디 (Request Body)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | No | 변경할 닉네임 |
| `profileImageUrl` | String | No | 변경할 프로필 이미지 URL |
| `location` | String | No | 변경할 지역 정보 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "usr_20240520",
    "name": "김철수_수정",
    "profileImageUrl": "https://api.surplushub.com/images/profiles/new_image.jpg",
    "location": "서울 서초구",
    "updatedAt": "2024-12-19T10:00:00Z"
  }
}
```
