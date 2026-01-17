# API Gateway Documentation

The API Gateway is the single entry point for all client requests to DataAptor AI. It handles routing, authentication, rate limiting, and request validation.

## Overview

- **Base URL**: `http://localhost:8000`
- **Protocol**: HTTP/HTTPS
- **Authentication**: JWT Bearer tokens
- **Rate Limiting**: 100 requests/minute per user

## Endpoints

### Health Check

Check the health status of the API Gateway.

```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime": 3600.5
}
```

### Authentication

#### Login

Authenticate and receive a JWT token.

```
POST /api/auth/login
```

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Refresh Token

Refresh an expiring token.

```
POST /api/auth/refresh
```

**Headers**:
```
Authorization: Bearer <current_token>
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Dataset Operations

All dataset endpoints require authentication.

#### Upload Dataset

Upload a new dataset for assessment.

```
POST /api/datasets/upload
```

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data**:
- `file`: The dataset file (required)
- `name`: Optional name for the dataset

**Response**:
```json
{
  "id": 1,
  "name": "my_dataset.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "rows": 10000,
    "columns": 15
  }
}
```

#### List Datasets

Get a paginated list of datasets.

```
GET /api/datasets
```

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 10, max: 100)

**Response**:
```json
{
  "datasets": [
    {
      "id": 1,
      "name": "dataset1.csv",
      "file_type": "csv",
      "file_size": 1024000,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10
}
```

#### Get Dataset

Get details of a specific dataset.

```
GET /api/datasets/{dataset_id}
```

**Response**:
```json
{
  "id": 1,
  "name": "my_dataset.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "file_path": "datasets/1/my_dataset.csv",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "rows": 10000,
    "columns": 15,
    "column_types": {
      "id": "integer",
      "name": "string",
      "value": "float"
    }
  }
}
```

#### Delete Dataset

Delete a dataset and its associated data.

```
DELETE /api/datasets/{dataset_id}
```

**Response**:
```json
{
  "message": "Dataset 1 successfully deleted"
}
```

### Assessment Operations

#### Start Assessment

Start a new assessment for a dataset.

```
POST /api/assessments
```

**Request Body**:
```json
{
  "dataset_id": 1,
  "modules": ["quality", "accessibility", "governance", "ai_compatibility", "diversity"],
  "weights": {
    "quality": 0.40,
    "accessibility": 0.20,
    "governance": 0.15,
    "ai_compatibility": 0.20,
    "diversity": 0.05
  }
}
```

**Response**:
```json
{
  "id": 1,
  "dataset_id": 1,
  "status": "pending",
  "modules": ["quality", "accessibility", "governance", "ai_compatibility", "diversity"],
  "created_at": "2024-01-15T10:35:00Z"
}
```

#### Get Assessment Status

Check the status of an assessment.

```
GET /api/assessments/{assessment_id}/status
```

**Response**:
```json
{
  "id": 1,
  "status": "completed",
  "progress": 100,
  "current_module": null,
  "started_at": "2024-01-15T10:35:00Z",
  "completed_at": "2024-01-15T10:36:30Z"
}
```

#### List Assessments

Get assessments for a dataset.

```
GET /api/assessments?dataset_id={dataset_id}
```

**Response**:
```json
{
  "assessments": [
    {
      "id": 1,
      "dataset_id": 1,
      "status": "completed",
      "overall_score": 85,
      "created_at": "2024-01-15T10:35:00Z"
    }
  ],
  "total": 5
}
```

### Report Operations

#### Get Report

Get the assessment report.

```
GET /api/reports/{assessment_id}
```

**Response**:
```json
{
  "id": 1,
  "assessment_id": 1,
  "overall_score": 85,
  "readiness_level": "high",
  "module_scores": {
    "quality": 90,
    "accessibility": 80,
    "governance": 85,
    "ai_compatibility": 82,
    "diversity": 78
  },
  "findings": [...],
  "recommendations": [...],
  "created_at": "2024-01-15T10:36:30Z"
}
```

#### Export Report

Export the report in various formats.

```
GET /api/reports/{assessment_id}/export?format={format}
```

**Query Parameters**:
- `format`: Export format (json, csv, html, pdf)

**Response**: File download or JSON depending on format.

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File exceeds size limit |
| 415 | Unsupported Media Type - Invalid file format |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

The API Gateway enforces rate limits:

- **Default**: 100 requests/minute per user
- **Upload**: 10 uploads/minute per user
- **Assessment**: 5 assessments/minute per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

## CORS

The API Gateway supports CORS for browser-based clients:

- Allowed origins: Configurable (default: *)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: Authorization, Content-Type

## Versioning

The API uses URL path versioning. The current version is v1 (implicit in the base path).

Future versions will be available at `/api/v2/...`

## See Also

- [Authentication Guide](authentication.md)
- [Ingestion API](ingestion.md)
- [Assessment API](assessment.md)
- [Scoring API](scoring.md)
- [Reporting API](reporting.md)
