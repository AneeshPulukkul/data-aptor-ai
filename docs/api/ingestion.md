# Ingestion Service API

The Ingestion Service handles dataset uploads, parsing, validation, and metadata extraction.

## Overview

- **Base URL**: `http://localhost:8002` (direct) or `http://localhost:8000/api/ingestion` (via gateway)
- **Purpose**: Dataset intake and preprocessing

## Endpoints

### Health Check

```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime": 3600.5,
  "database_connection": true,
  "storage_connection": true
}
```

### Upload Dataset

Upload a new dataset file.

```
POST /upload
```

**Headers**:
```
Content-Type: multipart/form-data
```

**Form Data**:
- `file`: The dataset file (required)

**Supported File Types**:
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- JSON (`.json`)
- Parquet (`.parquet`)
- XML (`.xml`)
- Images (`.jpg`, `.jpeg`, `.png`)
- Audio (`.wav`, `.mp3`)

**Size Limits**:
- Maximum file size: 500 MB
- Maximum rows (CSV/Excel): 10 million

**Response**:
```json
{
  "id": 1,
  "name": "dataset.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "file_path": "datasets/1/dataset.csv",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "rows": 10000,
    "columns": 15,
    "column_names": ["id", "name", "value", "..."],
    "column_types": {
      "id": "integer",
      "name": "string",
      "value": "float"
    },
    "file_hash": "sha256:abc123..."
  }
}
```

**Error Responses**:

413 - File too large:
```json
{
  "detail": "File too large. Maximum size is 500MB"
}
```

415 - Unsupported file type:
```json
{
  "detail": "Unsupported file type. Supported types: csv, xlsx, json, parquet, xml, jpg, png, wav, mp3"
}
```

### List Datasets

Get a paginated list of all datasets.

```
GET /datasets
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Records to skip |
| limit | integer | 10 | Max records (1-100) |

**Response**:
```json
{
  "datasets": [
    {
      "id": 1,
      "name": "dataset1.csv",
      "file_type": "csv",
      "file_size": 1024000,
      "file_path": "datasets/1/dataset1.csv",
      "created_at": "2024-01-15T10:30:00Z",
      "metadata": {...}
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10
}
```

### Get Dataset

Get details of a specific dataset.

```
GET /datasets/{dataset_id}
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Response**:
```json
{
  "id": 1,
  "name": "dataset.csv",
  "file_type": "csv",
  "file_size": 1024000,
  "file_path": "datasets/1/dataset.csv",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "rows": 10000,
    "columns": 15,
    "column_names": ["id", "name", "value"],
    "column_types": {
      "id": "integer",
      "name": "string",
      "value": "float"
    },
    "missing_values": {
      "name": 50,
      "value": 100
    },
    "file_hash": "sha256:abc123..."
  }
}
```

**Error Response** (404):
```json
{
  "detail": "Dataset with ID 1 not found"
}
```

### Get Dataset Data

Retrieve the actual data records from a dataset.

```
GET /api/ingestion/datasets/{dataset_id}/data
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Response**:
```json
{
  "dataset_id": 1,
  "records": [
    {"id": 1, "name": "Item 1", "value": 100.5},
    {"id": 2, "name": "Item 2", "value": 200.3}
  ],
  "total_records": 10000,
  "truncated": true
}
```

**Notes**:
- Returns up to 10,000 records for performance
- `truncated` indicates if full dataset exceeds limit

### Delete Dataset

Delete a dataset and its associated file.

```
DELETE /datasets/{dataset_id}
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Response**:
```json
{
  "message": "Dataset with ID 1 successfully deleted"
}
```

## Metadata Extraction

The Ingestion Service automatically extracts metadata based on file type:

### CSV/Excel Metadata

```json
{
  "rows": 10000,
  "columns": 15,
  "column_names": ["col1", "col2", "..."],
  "column_types": {
    "col1": "integer",
    "col2": "string",
    "col3": "float",
    "col4": "datetime"
  },
  "missing_values": {
    "col2": 50,
    "col3": 100
  },
  "encoding": "utf-8",
  "delimiter": ","
}
```

### JSON Metadata

```json
{
  "records": 5000,
  "schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"}
      }
    }
  },
  "nested_depth": 2
}
```

### Image Metadata

```json
{
  "image_count": 1000,
  "formats": {"jpg": 800, "png": 200},
  "resolutions": {
    "1920x1080": 500,
    "1280x720": 300,
    "other": 200
  },
  "color_modes": {"RGB": 900, "RGBA": 100},
  "total_size_bytes": 500000000
}
```

### Audio Metadata

```json
{
  "audio_count": 500,
  "formats": {"wav": 300, "mp3": 200},
  "total_duration_seconds": 36000,
  "sample_rates": {"44100": 400, "48000": 100},
  "channels": {"mono": 200, "stereo": 300}
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Dataset doesn't exist |
| 413 | Payload Too Large - File exceeds limit |
| 415 | Unsupported Media Type - Invalid format |
| 500 | Internal Server Error |

## See Also

- [API Gateway](api-gateway.md)
- [Assessment API](assessment.md)
- [Dataset Assessment Guide](../user-guides/dataset-assessment.md)
