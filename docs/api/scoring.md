# Scoring Service API

The Scoring Service calculates weighted aggregate scores from assessment results.

## Overview

- **Base URL**: `http://localhost:8004` (direct) or `http://localhost:8000/api/scoring` (via gateway)
- **Purpose**: Calculate weighted AI readiness scores

## Default Weights

| Module | Default Weight |
|--------|----------------|
| quality | 0.40 (40%) |
| accessibility | 0.20 (20%) |
| governance | 0.15 (15%) |
| ai_compatibility | 0.20 (20%) |
| diversity | 0.05 (5%) |

## Readiness Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 80-100 | high | Ready for AI/ML applications |
| 60-79 | moderate | Minor improvements needed |
| 40-59 | low | Significant work required |
| 0-39 | not_ready | Major issues to address |

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
  "uptime": 3600.5
}
```

### Calculate Score

Calculate the weighted score for a dataset assessment.

```
POST /api/scoring/{dataset_id}
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Request Body** (optional):
```json
{
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
  "dataset_id": 1,
  "overall_score": 78.5,
  "readiness_level": "moderate",
  "readiness_description": "Dataset shows moderate AI readiness. Minor improvements recommended before production use.",
  "module_scores": {
    "quality": {
      "raw_score": 14,
      "max_score": 16,
      "normalized_score": 87.5,
      "weighted_contribution": 35.0
    },
    "accessibility": {
      "raw_score": 6,
      "max_score": 8,
      "normalized_score": 75.0,
      "weighted_contribution": 15.0
    },
    "governance": {
      "raw_score": 5,
      "max_score": 8,
      "normalized_score": 62.5,
      "weighted_contribution": 9.375
    },
    "ai_compatibility": {
      "raw_score": 12,
      "max_score": 16,
      "normalized_score": 75.0,
      "weighted_contribution": 15.0
    },
    "diversity": {
      "raw_score": 5,
      "max_score": 8,
      "normalized_score": 62.5,
      "weighted_contribution": 3.125
    }
  },
  "weights_used": {
    "quality": 0.40,
    "accessibility": 0.20,
    "governance": 0.15,
    "ai_compatibility": 0.20,
    "diversity": 0.05
  }
}
```

### Get Default Weights

Retrieve the default scoring weights.

```
GET /api/scoring/weights
```

**Response**:
```json
{
  "weights": {
    "quality": 0.40,
    "accessibility": 0.20,
    "governance": 0.15,
    "ai_compatibility": 0.20,
    "diversity": 0.05
  },
  "description": "Default weights optimized for general AI/ML use cases"
}
```

### Get Readiness Levels

Retrieve the readiness level definitions.

```
GET /api/scoring/levels
```

**Response**:
```json
{
  "levels": [
    {
      "level": "high",
      "min_score": 80,
      "max_score": 100,
      "description": "Dataset is ready for AI/ML applications with minimal preparation"
    },
    {
      "level": "moderate",
      "min_score": 60,
      "max_score": 79,
      "description": "Dataset shows moderate AI readiness. Minor improvements recommended before production use."
    },
    {
      "level": "low",
      "min_score": 40,
      "max_score": 59,
      "description": "Dataset requires significant improvements before AI/ML use"
    },
    {
      "level": "not_ready",
      "min_score": 0,
      "max_score": 39,
      "description": "Dataset has major issues that must be addressed before any AI/ML application"
    }
  ]
}
```

### Calculate Custom Score

Calculate score with custom weights and assessment results.

```
POST /api/scoring/custom
```

**Request Body**:
```json
{
  "assessment_results": {
    "quality": {
      "score": 14,
      "max_score": 16
    },
    "accessibility": {
      "score": 6,
      "max_score": 8
    },
    "governance": {
      "score": 5,
      "max_score": 8
    },
    "ai_compatibility": {
      "score": 12,
      "max_score": 16
    },
    "diversity": {
      "score": 5,
      "max_score": 8
    }
  },
  "weights": {
    "quality": 0.30,
    "accessibility": 0.25,
    "governance": 0.20,
    "ai_compatibility": 0.20,
    "diversity": 0.05
  }
}
```

**Response**:
```json
{
  "overall_score": 76.25,
  "readiness_level": "moderate",
  "readiness_description": "Dataset shows moderate AI readiness. Minor improvements recommended before production use.",
  "module_scores": {
    "quality": {
      "normalized_score": 87.5,
      "weighted_contribution": 26.25
    },
    "accessibility": {
      "normalized_score": 75.0,
      "weighted_contribution": 18.75
    },
    "governance": {
      "normalized_score": 62.5,
      "weighted_contribution": 12.5
    },
    "ai_compatibility": {
      "normalized_score": 75.0,
      "weighted_contribution": 15.0
    },
    "diversity": {
      "normalized_score": 62.5,
      "weighted_contribution": 3.125
    }
  },
  "weights_used": {
    "quality": 0.30,
    "accessibility": 0.25,
    "governance": 0.20,
    "ai_compatibility": 0.20,
    "diversity": 0.05
  }
}
```

## Score Calculation Algorithm

### Step 1: Normalize Module Scores

Each module score is normalized to 0-100:

```
normalized_score = (raw_score / max_score) * 100
```

### Step 2: Apply Weights

Each normalized score is multiplied by its weight:

```
weighted_contribution = normalized_score * weight
```

### Step 3: Calculate Overall Score

Sum all weighted contributions:

```
overall_score = sum(weighted_contributions)
```

### Step 4: Determine Readiness Level

Map overall score to readiness level:

```python
if overall_score >= 80:
    level = "high"
elif overall_score >= 60:
    level = "moderate"
elif overall_score >= 40:
    level = "low"
else:
    level = "not_ready"
```

## Weight Validation

Weights must:
- Sum to 1.0 (100%)
- Be non-negative
- Include all five modules

Invalid weights return a 400 error:

```json
{
  "detail": "Weights must sum to 1.0. Current sum: 0.95"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid weights or parameters |
| 404 | Not Found - Dataset or assessment not found |
| 500 | Internal Server Error |

## See Also

- [Assessment API](assessment.md)
- [Reporting API](reporting.md)
- [Customizing Weights Guide](../user-guides/customizing-weights.md)
