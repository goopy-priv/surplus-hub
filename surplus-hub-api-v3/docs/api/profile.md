# Profile Page API Specification

This document outlines the API endpoints required to implement the Profile Page functionality in the Flutter application.

## Base URL
`https://api.surplushub.com/api/v1`

## Authentication
All endpoints require a valid Bearer Token in the `Authorization` header.
`Authorization: Bearer <token>`

---

## 1. User Profile

### Get My Profile
Retrieves the detailed profile information of the currently authenticated user, including statistics and membership status.

- **Endpoint**: `/users/me`
- **Method**: `GET`
- **Description**: Fetches the current user's profile data to be displayed in the Profile Header and User Stats sections.

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "id": "user_12345",
    "name": "Alex Builder",
    "email": "alex@example.com",
    "profileImageUrl": "https://lh3.googleusercontent.com/...",
    "location": "New York, NY",
    "role": "Site Manager",
    "trustLevel": 5,
    "mannerTemperature": 98.6,
    "stats": {
      "salesCount": 12,
      "purchaseCount": 5,
      "reviewCount": 20
    },
    "isPremium": false,
    "createdAt": "2023-01-15T10:30:00Z"
  }
}
```

### Update My Profile
Updates the current user's profile information.

- **Endpoint**: `/users/me`
- **Method**: `PATCH`
- **Description**: Allows the user to update editable profile fields.

#### Request Body
```json
{
  "name": "Alex B.",
  "location": "San Francisco, CA",
  "profileImageUrl": "https://new-image-url.com/avatar.jpg"
}
```

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "id": "user_12345",
    "name": "Alex B.",
    "location": "San Francisco, CA",
    // ... updated fields
  }
}
```

---

## 2. Trade Summary

### Get Ongoing Trade Summary
Retrieves a summary of the user's ongoing trade activities.

- **Endpoint**: `/trades/my-summary`
- **Method**: `GET`
- **Description**: Provides data for the "Ongoing Trades" widget, including the count of active trades and the status of the most urgent item.

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "ongoingCount": 3,
    "pendingApprovalCount": 1,
    "latestActionItem": {
      "tradeId": "trade_987",
      "title": "Excavator Rental",
      "status": "WAITING_APPROVAL",
      "description": "1 transaction is waiting for approval"
    }
  }
}
```

---

## 3. Membership

### Get Premium Status (Optional)
If not included in the main profile, this endpoint checks the user's membership status.

- **Endpoint**: `/users/me/membership`
- **Method**: `GET`

#### Response Example
**Status**: 200 OK
```json
{
  "success": true,
  "data": {
    "isPremium": true,
    "plan": "PRO_YEARLY",
    "expiryDate": "2024-12-31T23:59:59Z"
  }
}
```
