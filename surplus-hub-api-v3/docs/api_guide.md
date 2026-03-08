# Surplus Hub API v3 - API Guide

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

Get a token via `POST /api/v1/auth/login/access-token`.

## Response Format
All responses follow this structure:
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "totalCount": 100,
    "page": 1,
    "limit": 20,
    "hasNextPage": true,
    "totalPages": 5
  }
}
```

---

## Auth (`/auth`)

### POST `/auth/login/access-token`
Login and get JWT token. Rate limited: 5/minute.
- **Auth**: None
- **Body**: `application/x-www-form-urlencoded` — `username` (email), `password`
- **Response**: `{ "access_token": "...", "token_type": "bearer" }`

### POST `/auth/refresh-token`
Get a fresh access token using current valid token.
- **Auth**: Required
- **Response**: `{ "status": "success", "data": { "accessToken": "...", "tokenType": "bearer" } }`

---

## Users (`/users`)

### GET `/users/`
List all users. Admin only.
- **Auth**: Superuser

### GET `/users/me`
Get current user profile with stats.
- **Auth**: Required
- **Response**: UserData with stats (salesCount, purchaseCount, reviewCount), isPremium

### PUT `/users/me`
Update current user profile.
- **Auth**: Required
- **Body**: `{ "name": "...", "profile_image_url": "...", "location": "..." }`

### GET `/users/me/wishlist`
Get liked materials list.
- **Auth**: Required
- **Query**: `page`, `limit`

### GET `/users/me/subscription`
Get subscription status.
- **Auth**: Required

### POST `/users/me/subscription/verify`
Verify IAP receipt for premium.
- **Auth**: Required
- **Body**: `{ "receiptId": "...", "platform": "ios" }`

---

## Materials (`/materials`)

### GET `/materials/`
List materials with advanced filtering.
- **Auth**: None
- **Query**: `page`, `limit`, `category`, `keyword`, `sort` (latest|price_asc|price_desc|distance|popular), `lat`, `lng`, `radius` (km), `priceMin`, `priceMax`, `tradeMethod` (DIRECT|DELIVERY|BOTH)

### POST `/materials/`
Create a new material listing.
- **Auth**: Required
- **Body**: MaterialCreate (title, description, price, quantity, quantityUnit, tradeMethod, location, category, photoUrls[])

### GET `/materials/{id}`
Get material detail.
- **Auth**: None

### PUT `/materials/{id}`
Update material. Owner only.
- **Auth**: Required (owner)

### DELETE `/materials/{id}`
Soft-delete material. Owner only.
- **Auth**: Required (owner)

### PATCH `/materials/{id}/status`
Update material status. Owner or admin.
- **Auth**: Required
- **Query**: `status` (ACTIVE|REVIEWING|SOLD|HIDDEN)

### POST `/materials/{id}/like`
Toggle like on material.
- **Auth**: Required
- **Response**: `{ "isLiked": true, "likesCount": 5 }`

### GET `/materials/{id}/like`
Check if current user liked this material.
- **Auth**: Required

---

## Chats (`/chats`)

### GET `/chats/rooms`
List user's chat rooms. Sorted by **last message time** (most recent first).
- **Auth**: Required
- **Query**: `page`, `limit`

### POST `/chats/rooms`
Create or get existing chat room.
- **Auth**: Required
- **Body**: `{ "materialId": 1, "sellerId": 2 }`

### GET `/chats/rooms/{room_id}/messages`
List messages in a room. Automatically marks unread messages as read on retrieval.
- **Auth**: Required (participant)
- **Query**: `page`, `limit`

### POST `/chats/rooms/{room_id}/messages`
Send a message. The message is saved to the database and simultaneously broadcast via WebSocket to the chat room. If the recipient is offline, an FCM push notification and an in-app notification (stored in the `notifications` table) are automatically created.
- **Auth**: Required (participant)
- **Body**: `{ "content": "...", "messageType": "TEXT" }`

---

## WebSocket (`/ws`)

### WS `/ws/chat/{room_id}?token={jwt}`
Real-time chat connection.
- **Auth**: JWT via query parameter. Supports both **Clerk RS256 tokens** and **local HS256 tokens**. Clerk token verification is attempted first; on failure, falls back to HS256 verification.

**Client → Server:**
- `{ "type": "text", "content": "hello" }`
- `{ "type": "image", "content": "https://..." }`
- `{ "type": "read" }` — explicitly mark messages as read (required; automatic read-on-receive has been removed)
- `{ "type": "typing" }` — typing indicator

**Server → Client:**
- `{ "type": "message", "data": { ... } }` — new message (sent only to the other participant; the sender receives a separate confirmation via `send_personal`)
- `{ "type": "read_receipt", "data": { "userId": 1, "readAt": "..." } }`
- `{ "type": "typing", "data": { "userId": 1, "userName": "..." } }`
- `{ "type": "error", "data": { "detail": "..." } }`

**Push Notifications:**
When a message is sent via WebSocket and the recipient is not connected, the server automatically:
1. Sends an **FCM push notification** to the recipient's registered device(s).
2. Creates an **in-app notification** record in the `notifications` table.

**DB Indexes:**
The `messages` table has indexes on `chat_room_id`, `sender_id`, and `is_read` for optimized query performance.

---

## Community (`/community`)

### GET `/community/posts`
List community posts.
- **Auth**: None
- **Query**: `page`, `limit`, `category` (QnA|KnowHow|Safety|Info)

### POST `/community/posts`
Create a post.
- **Auth**: Required
- **Body**: `{ "title": "...", "content": "...", "category": "QnA", "imageUrl": "..." }`

### GET `/community/posts/{id}`
Get post detail (increments view count).
- **Auth**: None

### PUT `/community/posts/{id}`
Update post. Author only.
- **Auth**: Required (author)

### DELETE `/community/posts/{id}`
Delete post. Author only.
- **Auth**: Required (author)

### POST `/community/posts/{id}/like`
Toggle like on post.
- **Auth**: Required

### GET `/community/posts/{id}/comments`
List comments on a post.
- **Auth**: None
- **Query**: `page`, `limit`

### POST `/community/posts/{id}/comments`
Create a comment.
- **Auth**: Required
- **Body**: `{ "content": "..." }`

### PUT `/community/posts/{post_id}/comments/{comment_id}`
Update comment. Author only.
- **Auth**: Required (author)
- **Body**: `{ "content": "..." }`

### DELETE `/community/posts/{post_id}/comments/{comment_id}`
Delete comment. Author only.
- **Auth**: Required (author)

---

## Notifications (`/notifications`)

### POST `/notifications/device-token`
Register FCM device token.
- **Auth**: Required
- **Body**: `{ "token": "fcm-token", "platform": "ios" }`

### DELETE `/notifications/device-token`
Deactivate device token.
- **Auth**: Required
- **Body**: `{ "token": "fcm-token", "platform": "ios" }`

### GET `/notifications/`
List notifications.
- **Auth**: Required
- **Query**: `page`, `limit`

### PATCH `/notifications/{id}/read`
Mark notification as read.
- **Auth**: Required

### PATCH `/notifications/read-all`
Mark all notifications as read.
- **Auth**: Required

### GET `/notifications/unread-count`
Get unread notification count.
- **Auth**: Required

---

## Reviews (`/reviews`)

### POST `/reviews/`
Create a review for another user.
- **Auth**: Required
- **Body**: `{ "targetUserId": 2, "materialId": 1, "rating": 5, "content": "Great seller!" }`
- **Rules**: Cannot review yourself. Rating 1-5. Updates target user's manner temperature.

### GET `/reviews/{review_id}`
Get review detail.
- **Auth**: None

### GET `/reviews/user/{user_id}`
Get all reviews for a user.
- **Auth**: None
- **Query**: `page`, `limit`
- **Meta** includes: `averageRating`, `mannerTemperature`

---

## Transactions (`/transactions`)

### POST `/transactions/`
Create a transaction (buyer action).
- **Auth**: Required
- **Body**: `{ "materialId": 1, "note": "..." }`
- **Rules**: Cannot buy own material. Material must be ACTIVE.

### GET `/transactions/`
List current user's transactions.
- **Auth**: Required
- **Query**: `page`, `limit`

### GET `/transactions/{id}`
Get transaction detail. Participants only.
- **Auth**: Required (buyer or seller)

### PATCH `/transactions/{id}/confirm`
Seller confirms the transaction.
- **Auth**: Required (seller)
- **Rules**: Status must be PENDING.

### PATCH `/transactions/{id}/complete`
Complete the transaction. Material status changes to SOLD.
- **Auth**: Required (buyer or seller)
- **Rules**: Status must be CONFIRMED.

---

## Events (`/events`)

### GET `/events/`
List active events/promotions.
- **Auth**: None
- **Query**: `page`, `limit`

### GET `/events/{id}`
Get event detail.
- **Auth**: None

---

## Upload (`/upload`)

### POST `/upload/image`
Upload image directly (multipart/form-data). Rate limited: 20/minute.
- **Auth**: Required
- **Body**: `file` (image/jpeg, image/png, image/webp, image/heic, max 10MB)
- **Response**: `{ "url": "https://s3..." }`

### POST `/upload/presigned-url`
Get S3 presigned URL for direct client upload.
- **Auth**: Required
- **Body**: `{ "filename": "photo.jpg", "contentType": "image/jpeg", "folder": "materials" }`
- **Response**: `{ "uploadUrl": "...", "publicUrl": "...", "key": "...", "expiresIn": 3600 }`

---

## Categories (`/categories`)

### GET `/categories/`
Get all active categories (auto-seeds 10 construction categories if empty).
- **Auth**: None

---

## Admin (`/admin`)

### PATCH `/admin/materials/{id}/review`
Approve or reject a material listing. Superuser only.
- **Auth**: Superuser
- **Body**: `{ "action": "approve", "note": "Looks good" }`
- **Actions**: `approve` (→ ACTIVE), `reject` (→ HIDDEN)

### Admin Panel
Access the SQLAdmin interface at `/admin`. Requires superuser login.

---

## Health

### GET `/`
Basic health check.
- **Response**: `{ "status": "ok", "version": "3.0.0", ... }`

### GET `/health`
Detailed health check with DB connectivity.
- **Response**: `{ "status": "ok", "checks": { "api": "ok", "database": "ok" } }`

---

## Error Responses

```json
{
  "status": "error",
  "detail": "Error message"
}
```

| Status Code | Description |
|------------|-------------|
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## Database Tables (19)

| Table | Description |
|-------|-------------|
| users | User accounts |
| materials | Material listings |
| material_images | Material photos |
| material_likes | Material likes/wishlist |
| categories | Material categories |
| chat_rooms | Chat rooms |
| messages | Chat messages |
| posts | Community posts |
| comments | Post comments |
| post_likes | Post likes |
| notifications | User notifications |
| device_tokens | FCM push tokens |
| reviews | User reviews |
| transactions | Purchase transactions |
| events | Events/promotions |
| subscriptions | Premium subscriptions |
