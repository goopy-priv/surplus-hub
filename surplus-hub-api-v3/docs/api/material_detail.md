# Material Detail API Specification

This document outlines the API endpoints required to implement the Material Detail Page.

## Base URL
`https://api.surplushub.com/api/v1`

## Authentication
Required for actions like "Like" or "Start Chat". Optional for viewing details.
`Authorization: Bearer <token>`

---

## 1. Material Information

### Get Material Details
Retrieves full details for a specific material listing, including AI analysis and seller info.

- **Endpoint**: `/materials/:id`
- **Method**: `GET`
- **Description**: Populates the Material Detail page.

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "id": "mat_123",
    "title": "Unused Cement Bags",
    "description": "5 bags of unused Portland cement. Leftover from a project.",
    "price": "Free",
    "category": {
      "id": "cat_concrete",
      "name": "Concrete"
    },
    "images": [
      "https://example.com/img1.jpg",
      "https://example.com/img2.jpg"
    ],
    "hashtags": ["#cement", "#diy", "#construction"],
    "location": {
      "address": "Mapo-gu, Seoul",
      "lat": 37.556,
      "lng": 126.924
    },
    "seller": {
      "id": "user_55",
      "name": "Construction Pro",
      "profileImageUrl": "https://example.com/avatar.jpg",
      "trustLevel": 4,
      "mannerTemperature": 99.0
    },
    "aiAnalysis": {
      "condition": "Excellent",
      "estimatedValue": "$50",
      "sustainabilityScore": 95,
      "usageSuggestions": ["Foundation repair", "Small walkway"]
    },
    "stats": {
      "likes": 24,
      "views": 300,
      "chats": 5
    },
    "isLiked": false,
    "createdAt": "2023-10-20T14:30:00Z"
  }
}
```

---

## 2. User Actions

### Toggle Like
Adds or removes the material from the user's wishlist.

- **Endpoint**: `/materials/:id/like`
- **Method**: `POST`
- **Description**: Toggles the like status.

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "isLiked": true,
    "totalLikes": 25
  }
}
```

### Start Chat (Create Room)
Initiates a chat session with the seller regarding this material.

- **Endpoint**: `/chats`
- **Method**: `POST`
- **Description**: Creates a new chat room or returns the existing one if it already exists.

#### Request Body
```json
{
  "materialId": "mat_123",
  "sellerId": "user_55"
}
```

#### Response Example
**Status**: 201 Created
```json
{
  "success": true,
  "data": {
    "chatRoomId": "room_999",
    "createdAt": "2023-10-26T09:00:00Z"
  }
}
```
