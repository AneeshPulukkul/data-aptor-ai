# Authentication Guide

This guide covers authentication and authorization for the DataAptor AI API.

## Overview

DataAptor AI uses JWT (JSON Web Tokens) for authentication. All API requests (except health checks and login) require a valid JWT token.

## Getting a Token

### Login Endpoint

```
POST /api/auth/login
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "your_password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA1MzE2NDAwfQ.abc123...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Using the Token

Include the token in the `Authorization` header for all authenticated requests:

```bash
curl http://localhost:8000/api/datasets \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Token Structure

The JWT token contains:

```json
{
  "sub": "user@example.com",
  "exp": 1705316400,
  "iat": 1705312800,
  "role": "analyst"
}
```

| Field | Description |
|-------|-------------|
| sub | Subject (username/email) |
| exp | Expiration timestamp |
| iat | Issued at timestamp |
| role | User role |

## Token Expiration

Tokens expire after 1 hour by default. Before expiration, refresh the token:

```
POST /api/auth/refresh
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer <current_token>"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Roles and Permissions

DataAptor AI supports role-based access control:

### Admin Role

Full access to all features:
- Manage users
- View all datasets
- Run assessments
- Export reports
- Configure system settings

### Analyst Role

Standard user access:
- Upload datasets
- Run assessments
- View own reports
- Export reports

### Viewer Role

Read-only access:
- View datasets
- View reports
- Cannot upload or run assessments

## Permission Matrix

| Action | Admin | Analyst | Viewer |
|--------|-------|---------|--------|
| Upload dataset | Yes | Yes | No |
| Delete dataset | Yes | Own only | No |
| Start assessment | Yes | Yes | No |
| View assessment | Yes | Own only | Own only |
| Export report | Yes | Yes | Yes |
| Manage users | Yes | No | No |

## API Key Authentication

For programmatic access, you can use API keys instead of JWT tokens:

### Creating an API Key

```bash
curl -X POST http://localhost:8000/api/auth/api-keys \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline",
    "expires_in_days": 365
  }'
```

**Response**:
```json
{
  "api_key": "dak_abc123xyz789...",
  "name": "CI/CD Pipeline",
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2025-01-15T10:00:00Z"
}
```

### Using an API Key

```bash
curl http://localhost:8000/api/datasets \
  -H "X-API-Key: dak_abc123xyz789..."
```

## CLI Authentication

### Configure API URL

```bash
python dataaptor.py config --set api_url --value http://localhost:8000
```

### Login

```bash
python dataaptor.py login
# Enter username and password when prompted
```

### Using API Key

```bash
python dataaptor.py config --set api_key --value dak_abc123xyz789...
```

### Environment Variables

```bash
export DATAAPTOR_API_URL=http://localhost:8000
export DATAAPTOR_API_KEY=dak_abc123xyz789...
```

## Python Client Authentication

```python
from dataaptor import DataAptorClient

# Using username/password
client = DataAptorClient(api_url="http://localhost:8000")
client.login(username="user@example.com", password="your_password")

# Using API key
client = DataAptorClient(
    api_url="http://localhost:8000",
    api_key="dak_abc123xyz789..."
)

# Using environment variables
client = DataAptorClient()  # Reads from DATAAPTOR_API_URL and DATAAPTOR_API_KEY
```

## Security Best Practices

1. **Never share tokens**: Tokens are sensitive credentials
2. **Use HTTPS**: Always use HTTPS in production
3. **Rotate API keys**: Regularly rotate long-lived API keys
4. **Minimal permissions**: Use the least privileged role needed
5. **Secure storage**: Store tokens securely, never in code
6. **Monitor usage**: Review API access logs regularly

## Error Handling

### Invalid Credentials

```json
{
  "detail": "Invalid username or password",
  "status_code": 401
}
```

### Expired Token

```json
{
  "detail": "Token has expired",
  "status_code": 401
}
```

### Invalid Token

```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### Insufficient Permissions

```json
{
  "detail": "Not enough permissions",
  "status_code": 403
}
```

## See Also

- [API Gateway Documentation](api-gateway.md)
- [Security Practices](../user-guides/security-practices.md)
