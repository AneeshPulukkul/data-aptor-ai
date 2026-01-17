# Assessment Service API

The Assessment Service evaluates datasets across five modules to determine AI readiness.

## Overview

- **Base URL**: `http://localhost:8003` (direct) or `http://localhost:8000/api/assessment` (via gateway)
- **Purpose**: Run assessment modules on datasets

## Assessment Modules

| Module | Weight | Description |
|--------|--------|-------------|
| quality | 40% | Data quality (completeness, accuracy, consistency, timeliness) |
| accessibility | 20% | Format compatibility and volume adequacy |
| governance | 15% | Privacy (PII) and licensing |
| ai_compatibility | 20% | Task relevance, labeling, features, preprocessing |
| diversity | 5% | Representativeness and bias detection |

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

### Run Quality Assessment

Assess data quality for a dataset.

```
GET /api/assessment/quality/{dataset_id}
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Response**:
```json
{
  "module": "quality",
  "dataset_id": 1,
  "score": 14,
  "max_score": 16,
  "normalized_score": 87.5,
  "criteria": {
    "completeness": {
      "score": 4,
      "max_score": 4,
      "details": {
        "missing_percentage": 2.5,
        "columns_with_missing": ["email", "phone"]
      }
    },
    "accuracy": {
      "score": 3,
      "max_score": 4,
      "details": {
        "outlier_percentage": 5.2,
        "type_consistency": 95.0
      }
    },
    "consistency": {
      "score": 4,
      "max_score": 4,
      "details": {
        "format_issues": 0,
        "pattern_consistency": 100.0
      }
    },
    "timeliness": {
      "score": 3,
      "max_score": 4,
      "details": {
        "data_age_days": 180,
        "freshness_score": 75.0
      }
    }
  }
}
```

### Run Accessibility Assessment

Assess data accessibility.

```
GET /api/assessment/accessibility/{dataset_id}
```

**Response**:
```json
{
  "module": "accessibility",
  "dataset_id": 1,
  "score": 6,
  "max_score": 8,
  "normalized_score": 75.0,
  "criteria": {
    "availability": {
      "score": 4,
      "max_score": 4,
      "details": {
        "format": "csv",
        "format_compatibility": "high",
        "supported_frameworks": ["pandas", "tensorflow", "pytorch"]
      }
    },
    "volume": {
      "score": 2,
      "max_score": 4,
      "details": {
        "record_count": 5000,
        "recommended_minimum": 10000,
        "adequacy": "moderate"
      }
    }
  }
}
```

### Run Governance Assessment

Assess data governance (privacy and licensing).

```
GET /api/assessment/governance/{dataset_id}
```

**Response**:
```json
{
  "module": "governance",
  "dataset_id": 1,
  "score": 5,
  "max_score": 8,
  "normalized_score": 62.5,
  "criteria": {
    "privacy": {
      "score": 1,
      "max_score": 4,
      "details": {
        "pii_detected": true,
        "pii_types": ["email", "phone"],
        "pii_columns": ["customer_email", "contact_phone"],
        "pii_count": 10000
      }
    },
    "licensing": {
      "score": 4,
      "max_score": 4,
      "details": {
        "license_detected": "MIT",
        "ai_ml_compatible": true,
        "restrictions": []
      }
    }
  }
}
```

### Run AI Compatibility Assessment

Assess AI/ML compatibility.

```
GET /api/assessment/ai_compatibility/{dataset_id}
```

**Query Parameters**:
- `ai_task`: Optional AI task type (classification, regression, nlp, computer_vision)

**Response**:
```json
{
  "module": "ai_compatibility",
  "dataset_id": 1,
  "score": 12,
  "max_score": 16,
  "normalized_score": 75.0,
  "criteria": {
    "relevance": {
      "score": 4,
      "max_score": 4,
      "details": {
        "task_type": "classification",
        "task_alignment": "high",
        "relevant_features": 12
      }
    },
    "labeling": {
      "score": 3,
      "max_score": 4,
      "details": {
        "label_column": "target",
        "label_coverage": 98.5,
        "class_balance": {
          "class_0": 6000,
          "class_1": 4000
        },
        "imbalance_ratio": 1.5
      }
    },
    "feature_richness": {
      "score": 3,
      "max_score": 4,
      "details": {
        "feature_count": 15,
        "feature_types": {
          "numeric": 10,
          "categorical": 3,
          "text": 2
        },
        "variability_score": 78.0
      }
    },
    "preprocessing_needs": {
      "score": 2,
      "max_score": 4,
      "details": {
        "needs_scaling": true,
        "needs_encoding": true,
        "needs_imputation": true,
        "estimated_effort": "moderate"
      }
    }
  }
}
```

### Run Diversity Assessment

Assess data diversity and bias.

```
GET /api/assessment/diversity/{dataset_id}
```

**Response**:
```json
{
  "module": "diversity",
  "dataset_id": 1,
  "score": 5,
  "max_score": 8,
  "normalized_score": 62.5,
  "criteria": {
    "representativeness": {
      "score": 3,
      "max_score": 4,
      "details": {
        "entropy": 2.8,
        "normalized_entropy": 0.75,
        "category_distribution": {
          "category_a": 0.4,
          "category_b": 0.35,
          "category_c": 0.25
        }
      }
    },
    "bias": {
      "score": 2,
      "max_score": 4,
      "details": {
        "protected_attributes_detected": ["gender", "age_group"],
        "potential_bias": true,
        "disparate_impact_ratio": 0.72,
        "recommendations": ["Review gender distribution", "Check age group balance"]
      }
    }
  }
}
```

### Run Full Assessment

Run all assessment modules at once.

```
GET /api/assessment/full/{dataset_id}
```

**Query Parameters**:
- `modules`: Comma-separated list of modules (default: all)
- `ai_task`: Optional AI task type

**Response**:
```json
{
  "dataset_id": 1,
  "modules": {
    "quality": {...},
    "accessibility": {...},
    "governance": {...},
    "ai_compatibility": {...},
    "diversity": {...}
  },
  "summary": {
    "total_score": 42,
    "max_score": 56,
    "normalized_score": 75.0
  }
}
```

## Scoring Details

### Score Levels

Each criterion is scored 0-4:

| Score | Level | Description |
|-------|-------|-------------|
| 0 | Poor | Major issues, not suitable |
| 1 | Below Average | Significant issues |
| 2 | Moderate | Some issues to address |
| 3 | Good | Minor issues |
| 4 | Excellent | No significant issues |

### Module Score Calculation

Module score = Sum of criteria scores

Example for Quality (4 criteria):
- Completeness: 4
- Accuracy: 3
- Consistency: 4
- Timeliness: 3
- **Total**: 14/16 = 87.5%

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Dataset doesn't exist |
| 500 | Internal Server Error |

## See Also

- [Scoring API](scoring.md)
- [Reporting API](reporting.md)
- [Dataset Assessment Guide](../user-guides/dataset-assessment.md)
