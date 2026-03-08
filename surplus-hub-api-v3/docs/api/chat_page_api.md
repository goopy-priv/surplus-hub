# 채팅 화면 API 명세서 (Chat Screen API Specification)

`flutter-view`로 구현된 채팅 화면(`ChatPage`)에서 사용되는 API 명세서입니다.
이 문서는 채팅방 목록 조회, 검색, 필터링을 위한 API를 정의합니다.

## 1. 채팅방 목록 조회 (Get Chat Rooms)

사용자의 채팅방 목록을 조회합니다. 검색어, 상태 필터(구매중, 판매중, 안읽음 등)를 지원합니다.

- **Endpoint**: `GET /api/v1/chat/rooms`
- **목적**: 메시지 탭의 채팅방 리스트 구성
- **인증**: Bearer Token 필요

### 요청 파라미터 (Query Parameters)
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | Integer | No | 페이지 번호 (기본값: 1) |
| `limit` | Integer | No | 페이지 당 항목 수 (기본값: 20) |
| `keyword` | String | No | 검색어 (상대방 이름, 자재명, 대화 내용 검색) |
| `filter` | String | No | 필터 (`ALL`, `BUYING`, `SELLING`, `UNREAD`) |

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `data` | Array | 채팅방 리스트 |
| `data[].id` | String | 채팅방 고유 ID |
| `data[].otherUser` | Object | 상대방 사용자 정보 |
| `data[].otherUser.name` | String | 상대방 닉네임 |
| `data[].otherUser.profileUrl` | String | 상대방 프로필 이미지 URL |
| `data[].otherUser.isOnline` | Boolean | 상대방 접속 여부 |
| `data[].product` | Object | 관련 자재 정보 (선택) |
| `data[].product.title` | String | 자재 제목 (예: "Regarding: 50 Bags...") |
| `data[].lastMessage` | String | 마지막 대화 내용 |
| `data[].lastMessageTime` | String | 마지막 대화 시간 (ISO 8601) |
| `data[].unreadCount` | Integer | 읽지 않은 메시지 수 |
| `meta` | Object | 페이징 메타 정보 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": [
    {
      "id": "room_123",
      "otherUser": {
        "id": "user_456",
        "name": "BuildCorp Supply",
        "profileUrl": "https://api.surplushub.com/profiles/buildcorp.jpg",
        "isOnline": true
      },
      "product": {
        "id": "prod_789",
        "title": "시멘트 50포대 일괄 판매"
      },
      "lastMessage": "오늘 픽업 가능하신가요?",
      "lastMessageTime": "2024-05-20T14:30:00Z",
      "unreadCount": 1
    },
    {
      "id": "room_124",
      "otherUser": {
        "id": "user_789",
        "name": "김반장",
        "profileUrl": null,
        "isOnline": false
      },
      "product": {
        "id": "prod_101",
        "title": "철근 자투리 나눔"
      },
      "lastMessage": "감사합니다. 내일 뵙겠습니다.",
      "lastMessageTime": "2024-05-19T09:15:00Z",
      "unreadCount": 0
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

---

## 2. 채팅방 상세 조회 (Get Chat Room Detail) - Optional

특정 채팅방의 메시지 내역과 상세 정보를 조회합니다. (채팅방 입장 시 호출)

- **Endpoint**: `GET /api/v1/chat/rooms/{roomId}/messages`
- **목적**: 채팅방 내부 대화 내역 로드
- **인증**: Bearer Token 필요

### 요청 파라미터 (Query Parameters)
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `before` | String | No | 특정 시간(Cursor) 이전의 메시지 조회 (페이징용) |
| `limit` | Integer | No | 가져올 메시지 수 (기본값: 50) |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": [
    {
      "id": "msg_999",
      "senderId": "user_456",
      "content": "오늘 픽업 가능하신가요?",
      "type": "TEXT",
      "createdAt": "2024-05-20T14:30:00Z",
      "isRead": false
    },
    {
      "id": "msg_998",
      "senderId": "user_me",
      "content": "네, 오후 3시에 가겠습니다.",
      "type": "TEXT",
      "createdAt": "2024-05-20T14:28:00Z",
      "isRead": true
    }
  ]
}
```

---

## 3. 메시지 전송 (Send Message)

채팅방에 메시지를 전송합니다.

- **Endpoint**: `POST /api/v1/chat/rooms/{roomId}/messages`
- **목적**: 텍스트 또는 이미지 메시지 전송
- **인증**: Bearer Token 필요

### 요청 바디 (Request Body)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | String | Yes | 메시지 내용 |
| `type` | String | Yes | 메시지 타입 (`TEXT`, `IMAGE`, `LOCATION`) |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "msg_1000",
    "createdAt": "2024-05-20T14:31:00Z"
  }
}
```
