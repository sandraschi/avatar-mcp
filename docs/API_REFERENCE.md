# AvatarMCP API Reference

This document provides a comprehensive reference for the AvatarMCP API, which enables programmatic control over VRM avatars, animations, and related functionality.

## Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
   - [Models](#models)
   - [Animations](#animations)
   - [Avatars](#avatars)
   - [Real-time Updates](#real-time-updates)
5. [WebSocket API](#websocket-api)
6. [Examples](#examples)
7. [Rate Limiting](#rate-limiting)
8. [Versioning](#versioning)

## Base URL

All API endpoints are prefixed with `/api/v1/`.

```
http://localhost:8080/api/v1/
```

## Authentication

Authentication is handled via API keys in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field_name": "Additional error details"
    },
    "status": 400
  }
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 422 | VALIDATION_ERROR | Request validation failed |
| 429 | TOO_MANY_REQUESTS | Rate limit exceeded |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

## Endpoints

### Models

#### List Models

```http
GET /api/v1/models
```

**Response**

```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "id": "model_123",
        "name": "SampleModel",
        "file_path": "/path/to/model.vrm",
        "size_mb": 12.5,
        "load_time": 1.23,
        "last_accessed": "2025-08-19T10:00:00Z"
      }
    ],
    "count": 1
  }
}
```

#### Upload Model

```http
POST /api/v1/models
Content-Type: multipart/form-data

file=@model.vrm
```

**Response**

```json
{
  "status": "success",
  "data": {
    "model_id": "model_123",
    "name": "SampleModel",
    "version": "1.0",
    "bones_count": 56,
    "materials_count": 12
  }
}
```

#### Get Model Details

```http
GET /api/v1/models/{model_id}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "id": "model_123",
    "name": "SampleModel",
    "version": "1.0",
    "bones": [
      {"name": "Hips", "parent": null},
      {"name": "Spine", "parent": "Hips"}
    ],
    "materials": [
      {"name": "Body"},
      {"name": "Eyes"}
    ],
    "metadata": {
      "title": "Sample VRM Model",
      "author": "Artist Name"
    }
  }
}
```

#### Delete Model

```http
DELETE /api/v1/models/{model_id}
```

**Response**

```json
{
  "status": "success"
}
```

### Avatars

#### List Avatars

```http
GET /api/v1/avatars
```

**Response**

```json
{
  "status": "success",
  "data": {
    "avatars": [
      {
        "id": "avatar_123",
        "model_id": "model_123",
        "position": [0, 0, 0],
        "rotation": [0, 0, 0, 1],
        "scale": [1, 1, 1]
      }
    ],
    "count": 1
  }
}
```

#### Create Avatar

```http
POST /api/v1/avatars
Content-Type: application/json

{
  "model_id": "model_123",
  "position": [0, 0, 0],
  "rotation": [0, 0, 0, 1],
  "scale": [1, 1, 1]
}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "avatar_id": "avatar_123",
    "model_id": "model_123",
    "created_at": "2025-08-19T10:00:00Z"
  }
}
```

#### Get Avatar Details

```http
GET /api/v1/avatars/{avatar_id}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "id": "avatar_123",
    "model_id": "model_123",
    "position": [0, 0, 0],
    "rotation": [0, 0, 0, 1],
    "scale": [1, 1, 1],
    "blend_shapes": {
      "blink": 0.0,
      "smile": 0.5
    },
    "animation": {
      "active_animations": [
        {
          "name": "idle",
          "time": 1.23,
          "weight": 1.0,
          "loop": true,
          "speed": 1.0
        }
      ]
    },
    "created_at": "2025-08-19T10:00:00Z",
    "updated_at": "2025-08-19T10:05:00Z"
  }
}
```

#### Update Avatar

```http
PUT /api/v1/avatars/{avatar_id}
Content-Type: application/json

{
  "position": [1, 2, 3],
  "rotation": [0, 0.707, 0, 0.707],
  "scale": [1, 1, 1],
  "blend_shapes": {
    "blink": 1.0
  }
}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "id": "avatar_123",
    "updated": true
  }
}
```

#### Delete Avatar

```http
DELETE /api/v1/avatars/{avatar_id}
```

**Response**

```json
{
  "status": "success"
}
```

### Animation Control

#### Play Animation

```http
POST /api/v1/avatars/{avatar_id}/play
Content-Type: application/json

{
  "animation": "wave",
  "loop": true,
  "fade_time": 0.2
}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "avatar_id": "avatar_123",
    "animation": "wave",
    "loop": true,
    "fade_time": 0.2
  }
}
```

#### Stop Animation

```http
POST /api/v1/avatars/{avatar_id}/stop
```

**Response**

```json
{
  "status": "success",
  "data": {
    "avatar_id": "avatar_123",
    "stopped": true
  }
}
```

#### Set Blend Shape

```http
POST /api/v1/avatars/{avatar_id}/blend-shape
Content-Type: application/json

{
  "name": "blink",
  "value": 1.0
}
```

**Response**

```json
{
  "status": "success",
  "data": {
    "avatar_id": "avatar_123",
    "blend_shape": "blink",
    "value": 1.0
  }
}
```

## WebSocket API

Connect to the WebSocket endpoint for real-time updates:

```
ws://localhost:8080/ws
```

### Message Format

All WebSocket messages are JSON-encoded objects with a `type` field:

```json
{
  "type": "message_type",
  "data": {}
}
```

### Subscribing to Updates

Send a subscription message:

```json
{
  "type": "subscribe",
  "resource": "avatar_updates",
  "id": "avatar_123"
}
```

### Receiving Updates

Example update message:

```json
{
  "type": "avatar_updated",
  "data": {
    "id": "avatar_123",
    "position": [0, 0, 0],
    "rotation": [0, 0, 0, 1],
    "blend_shapes": {
      "blink": 0.0
    }
  }
}
```

## Examples

### Python Client Example

```python
import asyncio
import aiohttp
import json

async def main():
    base_url = "http://localhost:8080/api/v1"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # List models
        async with session.get(f"{base_url}/models") as resp:
            models = await resp.json()
            print("Available models:", models)
        
        # Create an avatar
        async with session.post(
            f"{base_url}/avatars",
            json={"model_id": "model_123"}
        ) as resp:
            avatar = await resp.json()
            avatar_id = avatar["data"]["avatar_id"]
            print(f"Created avatar: {avatar_id}")
        
        # Play an animation
        async with session.post(
            f"{base_url}/avatars/{avatar_id}/play",
            json={"animation": "wave", "loop": True}
        ) as resp:
            print("Playing animation:", await resp.json())
        
        # Set a blend shape
        async with session.post(
            f"{base_url}/avatars/{avatar_id}/blend-shape",
            json={"name": "smile", "value": 0.8}
        ) as resp:
            print("Set blend shape:", await resp.json())

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript Client Example

```javascript
const API_BASE = 'http://localhost:8080/api/v1';
const API_KEY = 'YOUR_API_KEY';

async function fetchWithAuth(url, options = {}) {
  const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Request failed');
  }

  return response.json();
}

// Example usage
async function createAndAnimateAvatar() {
  try {
    // Create an avatar
    const { data: avatar } = await fetchWithAuth('/avatars', {
      method: 'POST',
      body: JSON.stringify({ model_id: 'model_123' }),
    });

    console.log('Created avatar:', avatar.avatar_id);

    // Play an animation
    await fetchWithAuth(`/avatars/${avatar.avatar_id}/play`, {
      method: 'POST',
      body: JSON.stringify({ animation: 'wave', loop: true }),
    });

    console.log('Animation started');
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. The following limits apply:

- 60 requests per minute per IP address
- 1000 requests per hour per API key

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1632000000
```

## Versioning

The API follows semantic versioning (SemVer). The current API version is `v1`.

To request a specific version, include it in the `Accept` header:

```
Accept: application/vnd.avatarmcp.v1+json
```

Or as a query parameter:

```
/api/v1/models?api-version=1
```

## Web Interface

A web-based interface is available at:

```
http://localhost:8080/
```

This provides a graphical interface for managing models, avatars, and animations.
