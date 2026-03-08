# 커뮤니티 화면 API 명세서 (Community Screen API Specification)

`flutter-view`로 구현된 커뮤니티 화면(`CommunityPage`)에서 사용되는 API 명세서입니다.
이 문서는 게시글 목록 조회, 카테고리 필터링, 그리고 게시글 상세 정보와 관련된 API를 정의합니다.

## 1. 커뮤니티 게시글 목록 조회 (Get Community Posts)

커뮤니티 피드에 표시될 게시글 목록을 조회합니다. 카테고리 필터링과 페이징을 지원합니다.

- **Endpoint**: `GET /api/v1/community/posts`
- **목적**: 게시판 피드 구성 및 카테고리별 필터링
- **인증**: 불필요 (비로그인 상태에서도 조회 가능)

### 요청 파라미터 (Query Parameters)
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | Integer | No | 페이지 번호 (기본값: 1) |
| `limit` | Integer | No | 페이지 당 항목 수 (기본값: 20) |
| `category` | String | No | 카테고리 필터 (예: 'Q&A', 'Know-how', 'Safety', 'Info') |
| `sort` | String | No | 정렬 기준 (`LATEST`, `POPULAR`, `VIEWS`) |

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `data` | Array | 게시글 아이템 리스트 |
| `data[].id` | String | 게시글 고유 ID |
| `data[].title` | String | 게시글 제목 |
| `data[].author` | String | 작성자 닉네임 |
| `data[].userAvatarUrl` | String | 작성자 프로필 이미지 URL |
| `data[].timeAgo` | String | 작성 시간 (상대 시간) |
| `data[].category` | String | 게시글 카테고리 |
| `data[].content` | String | 게시글 본문 (일부 미리보기) |
| `data[].likes` | Integer | 좋아요 수 |
| `data[].comments` | Integer | 댓글 수 |
| `data[].views` | Integer | 조회수 |
| `data[].imageUrl` | String | 첨부 이미지 URL (있는 경우) |
| `meta` | Object | 페이징 메타 정보 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": [
    {
      "id": "post_1",
      "title": "남은 시멘트 포대 보관 노하우 공유합니다",
      "author": "김반장",
      "userAvatarUrl": "https://api.surplushub.com/profiles/kim.jpg",
      "timeAgo": "2시간 전",
      "category": "Know-how",
      "content": "현장에서 쓰고 남은 시멘트 50포대가 있는데...",
      "likes": 15,
      "comments": 4,
      "views": 124,
      "imageUrl": null
    },
    {
      "id": "post_3",
      "title": "안전고리 점검 필수입니다",
      "author": "이안전",
      "userAvatarUrl": "https://api.surplushub.com/profiles/lee.jpg",
      "timeAgo": "1일 전",
      "category": "Safety",
      "content": "오늘 아침 점검 중에 발견한 크랙입니다. 6개월밖에 안 된 장비인데...",
      "likes": 89,
      "comments": 24,
      "views": 1200,
      "imageUrl": "https://api.surplushub.com/posts/safety_crack.jpg"
    }
  ],
  "meta": {
    "totalCount": 150,
    "page": 1,
    "limit": 20,
    "hasNextPage": true
  }
}
```

---

## 2. 게시글 상세 조회 (Get Post Detail)

특정 게시글의 상세 내용을 조회합니다.

- **Endpoint**: `GET /api/v1/community/posts/{postId}`
- **목적**: 게시글 상세 화면 표시
- **인증**: 불필요

### 응답 스펙 (Response Specification)
| Field | Type | Description |
|-------|------|-------------|
| `id` | String | 게시글 ID |
| `title` | String | 제목 |
| `content` | String | 본문 전체 |
| `author` | Object | 작성자 정보 (id, name, avatarUrl, role) |
| `createdAt` | String | 작성 일시 (ISO 8601) |
| `images` | Array | 첨부 이미지 URL 리스트 |
| `stats` | Object | 통계 (likes, comments, views) |
| `isLiked` | Boolean | 현재 사용자의 좋아요 여부 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "post_3",
    "title": "안전고리 점검 필수입니다",
    "content": "오늘 아침 점검 중에 발견한 크랙입니다...",
    "author": {
      "id": "user_999",
      "name": "이안전",
      "avatarUrl": "https://api.surplushub.com/profiles/lee.jpg",
      "role": "Safety Manager"
    },
    "createdAt": "2024-05-19T09:00:00Z",
    "images": ["https://api.surplushub.com/posts/safety_crack.jpg"],
    "stats": {
      "likes": 89,
      "comments": 24,
      "views": 1200
    },
    "isLiked": false
  }
}
```

---

## 3. 게시글 작성 (Create Post)

새로운 게시글을 작성합니다.

- **Endpoint**: `POST /api/v1/community/posts`
- **목적**: 새 게시글 등록
- **인증**: Bearer Token 필요

### 요청 바디 (Request Body)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | String | Yes | 게시글 제목 |
| `content` | String | Yes | 게시글 본문 |
| `category` | String | Yes | 카테고리 코드 (QnA, KnowHow, Safety, Info) |
| `imageIds` | Array | No | 업로드된 이미지 ID 리스트 |

### 응답 예시 (Example Response)
```json
{
  "status": "success",
  "data": {
    "id": "post_new_123",
    "createdAt": "2024-05-20T15:00:00Z"
  }
}
```
