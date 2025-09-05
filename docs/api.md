# Metro Security System API Documentation

## Overview

The Metro Security System API provides endpoints for command classification, user management, security monitoring, and system administration. All endpoints require authentication except for health checks and user registration.

## Base URL

```
http://localhost:5000/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Health Check

#### GET /api/health

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "ai_model_loaded": true
}
```

### Authentication

#### POST /api/auth/register

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

**Status Codes:**
- `201` - User created successfully
- `400` - Invalid input
- `409` - Username already exists

#### POST /api/auth/login

Authenticate user and get access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "role": "operator"
  }
}
```

**Status Codes:**
- `200` - Login successful
- `401` - Invalid credentials
- `403` - Account deactivated

### Command Classification

#### POST /api/classify

Classify a command using AI and return security assessment.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "command": "string"
}
```

**Response:**
```json
{
  "command": "open_door",
  "classification": "Category = Valid, Type = Normal",
  "risk_score": 0.1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200` - Classification successful
- `400` - Invalid command
- `401` - Unauthorized
- `429` - Rate limit exceeded

**Rate Limits:**
- 100 requests per hour per user

### Command History

#### GET /api/commands/history

Get command history for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional) - Page number (default: 1)
- `per_page` (optional) - Items per page (default: 20, max: 100)
- `search` (optional) - Search term for commands

**Response:**
```json
{
  "commands": [
    {
      "id": 1,
      "command": "open_door",
      "classification": "Category = Valid, Type = Normal",
      "risk_score": 0.1,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "pages": 3,
  "current_page": 1
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

### Security Events (Admin Only)

#### GET /api/security/events

Get security events and alerts.

**Headers:**
```
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `page` (optional) - Page number (default: 1)
- `per_page` (optional) - Items per page (default: 50, max: 200)

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "event_type": "high_risk_command",
      "description": "High risk command detected: hack system",
      "severity": "high",
      "ip_address": "192.168.1.100",
      "timestamp": "2024-01-15T10:30:00Z",
      "resolved": false
    }
  ],
  "total": 25,
  "pages": 1,
  "current_page": 1
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Forbidden (not admin)

#### POST /api/security/events/{id}/resolve

Mark a security event as resolved.

**Headers:**
```
Authorization: Bearer <admin-token>
```

**Path Parameters:**
- `id` - Event ID

**Response:**
```json
{
  "message": "Event resolved successfully"
}
```

**Status Codes:**
- `200` - Success
- `404` - Event not found
- `403` - Forbidden (not admin)

### Metrics

#### GET /api/metrics

Get Prometheus metrics (Admin only).

**Headers:**
```
Authorization: Bearer <admin-token>
```

**Response:**
```
# HELP metro_commands_total Total commands processed
# TYPE metro_commands_total counter
metro_commands_total{classification="Valid - Normal"} 150
metro_commands_total{classification="Invalid - Malicious"} 5
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Forbidden (not admin)

## WebSocket Events

### Connection

Connect to WebSocket with JWT token:

```javascript
const socket = io('http://localhost:5000', {
  auth: {
    token: 'your-jwt-token'
  }
});
```

### Events

#### command_processed

Emitted when a command is processed.

**Data:**
```json
{
  "command": "open_door",
  "classification": "Category = Valid, Type = Normal",
  "risk_score": 0.1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### security_alert

Emitted when a security alert is triggered.

**Data:**
```json
{
  "type": "high_risk_command",
  "command": "hack system",
  "risk_score": 0.9,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional error details"
}
```

### Common Error Codes

- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `VALIDATION_ERROR` - Invalid input data
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **General API**: 1000 requests per hour
- **Login endpoint**: 10 requests per minute
- **Registration endpoint**: 5 requests per minute
- **Classify endpoint**: 100 requests per hour per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Security Considerations

### Input Validation

- All inputs are validated and sanitized
- XSS protection is enabled
- SQL injection prevention
- Command length limits (1000 characters)

### Authentication

- JWT tokens expire after 1 hour
- Refresh tokens expire after 30 days
- Passwords are hashed with bcrypt
- Session management with Redis

### Encryption

- All commands are encrypted before storage
- HTTPS is required in production
- Secure headers are enforced

## Examples

### Python Example

```python
import requests
import json

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123!'
})
token = response.json()['access_token']

# Classify command
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:5000/api/classify', 
                        json={'command': 'open_door'},
                        headers=headers)
result = response.json()
print(f"Classification: {result['classification']}")
```

### JavaScript Example

```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123!'
  })
});
const { access_token } = await loginResponse.json();

// Classify command
const classifyResponse = await fetch('http://localhost:5000/api/classify', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ command: 'open_door' })
});
const result = await classifyResponse.json();
console.log('Classification:', result.classification);
```

### cURL Examples

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123!"}'

# Classify command
curl -X POST http://localhost:5000/api/classify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "open_door"}'

# Get command history
curl -X GET http://localhost:5000/api/commands/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Changelog

### v2.0.0
- Added JWT authentication
- Implemented role-based access control
- Added WebSocket support for real-time updates
- Enhanced security with encryption and rate limiting
- Added comprehensive monitoring and logging
- Modernized frontend with React and Material-UI