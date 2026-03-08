# Home Page (Marketplace) API Specification

This document outlines the API endpoints required to implement the Home Page (Marketplace Feed) functionality.

## Base URL
`https://api.surplushub.com/api/v1`

## Authentication
Optional for viewing public listings, but required for personalized results (e.g., distance from user).
`Authorization: Bearer <token>`

---

## 1. Materials List

### Get Materials
Retrieves a paginated list of surplus materials based on search queries, categories, and sorting options.

- **Endpoint**: `/materials`
- **Method**: `GET`
- **Description**: Populates the main material grid on the Home Page.

#### Query Parameters
| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| `page` | int | No | Page number (default: 1) | `1` |
| `limit` | int | No | Items per page (default: 20) | `20` |
| `q` | string | No | Search query for title/description | `cement` |
| `category` | string | No | Filter by category slug | `wood`, `metal` |
| `sort` | string | No | Sort order: `latest`, `distance`, `popular` | `distance` |
| `lat` | double | No | User's latitude (required for `sort=distance`) | `37.5665` |
| `lng` | double | No | User's longitude (required for `sort=distance`) | `126.9780` |

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "mat_123",
        "title": "High Quality Wood Scraps",
        "price": "Free",
        "imageUrl": "https://example.com/image.jpg",
        "location": "Gangnam-gu, Seoul",
        "distance": "2.5km",
        "seller": {
          "id": "user_99",
          "name": "Builder Kim"
        },
        "stats": {
          "likes": 12,
          "chats": 3,
          "views": 150
        },
        "category": "Wood",
        "isNew": true,
        "createdAt": "2023-10-25T10:00:00Z"
      }
    ],
    "meta": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 98
    }
  }
}
```

---

## 2. Categories

### Get Categories
Retrieves the list of available material categories for the filter bar.

- **Endpoint**: `/categories`
- **Method**: `GET`
- **Description**: Populates the horizontal category scroll view.

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": [
    { "id": "cat_all", "slug": "all", "name": "전체" },
    { "id": "cat_wood", "slug": "wood", "name": "목재" },
    { "id": "cat_metal", "slug": "metal", "name": "금속" },
    { "id": "cat_concrete", "slug": "concrete", "name": "콘크리트" }
  ]
}
```
