# Profile Page API Specification

This document describes the API endpoints required to implement the Profile screen functionality.

## Overview

- **Base URL**: `https://api.surplushub.com/v1`
- **Authentication**: All endpoints require a Bearer Token in the `Authorization` header.
- **Content-Type**: `application/json`

---

## 1. Get User Profile

Fetches the current user's profile information, including statistics and trust scores.

- **Endpoint**: `GET /users/me`
- **Purpose**: To display user information in the Profile Header and User Stats sections.

### Response

```json
{
  "status": "success",
  "data": {
    "id": "user_12345",
    "name": "Alex Builder",
    "profileImageUrl": "https://example.com/profiles/user_123.jpg",
    "location": "New York, NY",
    "role": "Site Manager",
    "trustLevel": 5,
    "mannerTemperature": 98.6,
    "stats": {
      "salesCount": 12,
      "purchaseCount": 5,
      "reviewCount": 20
    }
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique user identifier |
| `name` | String | User display name |
| `profileImageUrl` | String | URL to the user's profile image |
| `location` | String | User's location (City, State) |
| `role` | String | User's job title or role |
| `trustLevel` | Integer | User's trust level (1-5) |
| `mannerTemperature` | Double | User's manner temperature score |
| `stats.salesCount` | Integer | Total number of sales |
| `stats.purchaseCount` | Integer | Total number of purchases |
| `stats.reviewCount` | Integer | Total number of reviews received |

---

## 2. Update User Profile

Updates the current user's profile information.

- **Endpoint**: `PUT /users/me`
- **Purpose**: To allow users to edit their profile details.

### Request Body

```json
{
  "name": "Alex Builder Updated",
  "location": "San Francisco, CA",
  "role": "Senior Site Manager"
}
```

### Response

```json
{
  "status": "success",
  "data": {
    "id": "user_12345",
    "name": "Alex Builder Updated",
    "profileImageUrl": "https://example.com/profiles/user_123.jpg",
    "location": "San Francisco, CA",
    "role": "Senior Site Manager",
    "trustLevel": 5,
    "mannerTemperature": 98.6,
    "stats": {
      "salesCount": 12,
      "purchaseCount": 5,
      "reviewCount": 20
    }
  }
}
```

---

## 3. Get Ongoing Trades Summary

Fetches a summary of ongoing trades to display in the "Ongoing Trades" widget.

- **Endpoint**: `GET /trades/ongoing/summary`
- **Purpose**: To show the "1건의 거래가 승인 대기 중입니다" message.

### Response

```json
{
  "status": "success",
  "data": {
    "totalOngoingCount": 3,
    "pendingApprovalCount": 1,
    "inProgressCount": 2,
    "summaryMessage": "1 transaction pending approval"
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `totalOngoingCount` | Integer | Total number of active trades |
| `pendingApprovalCount` | Integer | Number of trades waiting for approval |
| `summaryMessage` | String | localized summary message to display directly in UI |

---

## 4. Get User Menu Badges

Fetches notification counts and badges for the user menu items.

- **Endpoint**: `GET /users/me/badges`
- **Purpose**: To display badges like "3 New" in the "Favorites" menu item.

### Response

```json
{
  "status": "success",
  "data": {
    "newFavoritesCount": 3,
    "unreadNotificationsCount": 5,
    "newReviewsCount": 0
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `newFavoritesCount` | Integer | Number of new favorite items since last check |
| `unreadNotificationsCount` | Integer | Total unread system notifications |

---

## 5. Upload Profile Image

Uploads a new profile image.

- **Endpoint**: `POST /upload/profile-image`
- **Content-Type**: `multipart/form-data`

### Request

- `file`: Binary image file (jpg, png)

### Response

```json
{
  "status": "success",
  "data": {
    "imageUrl": "https://example.com/profiles/new_image_url.jpg"
  }
}
```
