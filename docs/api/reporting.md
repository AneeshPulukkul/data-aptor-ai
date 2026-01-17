# Reporting Service API

The Reporting Service generates comprehensive reports and visualizations from assessment results.

## Overview

- **Base URL**: `http://localhost:8005` (direct) or `http://localhost:8000/api/reporting` (via gateway)
- **Purpose**: Generate reports, recommendations, and export in multiple formats

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

### Generate Report

Generate a comprehensive report for a dataset assessment.

```
POST /api/reporting/{dataset_id}
```

**Path Parameters**:
- `dataset_id`: Integer ID of the dataset

**Response**:
```json
{
  "id": 1,
  "dataset_id": 1,
  "assessment_id": 1,
  "overall_score": 78.5,
  "readiness_level": "moderate",
  "summary": {
    "total_criteria_assessed": 14,
    "criteria_passed": 10,
    "criteria_warning": 3,
    "criteria_failed": 1,
    "key_strengths": [
      "High data completeness (97.5%)",
      "Consistent data formats",
      "Compatible file format (CSV)"
    ],
    "key_issues": [
      "PII detected in 2 columns",
      "Class imbalance in target variable",
      "Below recommended sample size"
    ]
  },
  "module_scores": {
    "quality": 87.5,
    "accessibility": 75.0,
    "governance": 62.5,
    "ai_compatibility": 75.0,
    "diversity": 62.5
  },
  "findings": [...],
  "recommendations": [...],
  "created_at": "2024-01-15T10:40:00Z"
}
```

### Get Report

Retrieve an existing report.

```
GET /api/reporting/{assessment_id}
```

**Path Parameters**:
- `assessment_id`: Integer ID of the assessment

**Response**:
```json
{
  "id": 1,
  "dataset_id": 1,
  "assessment_id": 1,
  "overall_score": 78.5,
  "readiness_level": "moderate",
  "summary": {...},
  "module_scores": {...},
  "findings": [
    {
      "id": 1,
      "type": "pii_detected",
      "severity": "high",
      "module": "governance",
      "description": "Email addresses detected in 'customer_email' column",
      "affected_columns": ["customer_email"],
      "affected_rows": 10000,
      "recommendation": "Anonymize or remove email addresses before AI/ML use"
    },
    {
      "id": 2,
      "type": "class_imbalance",
      "severity": "medium",
      "module": "ai_compatibility",
      "description": "Target variable has 60/40 class imbalance",
      "affected_columns": ["target"],
      "details": {
        "class_0": 6000,
        "class_1": 4000,
        "imbalance_ratio": 1.5
      },
      "recommendation": "Consider oversampling minority class or using class weights"
    }
  ],
  "recommendations": [
    {
      "id": 1,
      "priority": "critical",
      "category": "governance",
      "issue": "PII detected",
      "action": "Anonymize email addresses in 'customer_email' column",
      "impact": "Required for compliance and privacy",
      "effort": "low"
    },
    {
      "id": 2,
      "priority": "high",
      "category": "accessibility",
      "issue": "Insufficient sample size",
      "action": "Collect additional data samples to reach 10,000 records",
      "impact": "Improves model training reliability",
      "effort": "high"
    },
    {
      "id": 3,
      "priority": "medium",
      "category": "ai_compatibility",
      "issue": "Class imbalance",
      "action": "Apply SMOTE or other oversampling techniques",
      "impact": "Improves model performance on minority class",
      "effort": "medium"
    }
  ],
  "created_at": "2024-01-15T10:40:00Z"
}
```

### Export Report

Export the report in various formats.

```
GET /api/reporting/{assessment_id}/export
```

**Path Parameters**:
- `assessment_id`: Integer ID of the assessment

**Query Parameters**:
- `format`: Export format (json, csv, html, pdf)

**Response by Format**:

#### JSON Format
```json
{
  "report": {...},
  "exported_at": "2024-01-15T10:45:00Z",
  "format": "json"
}
```

#### CSV Format
Returns a CSV file with findings and recommendations:
```csv
type,severity,module,description,recommendation
pii_detected,high,governance,"Email addresses detected","Anonymize emails"
class_imbalance,medium,ai_compatibility,"60/40 imbalance","Apply oversampling"
```

#### HTML Format
Returns an HTML document with:
- Executive summary
- Score visualizations (charts)
- Detailed findings table
- Prioritized recommendations
- Styling for printing

#### PDF Format
Returns a PDF document with the same content as HTML, formatted for professional reports.

### List Reports

List all reports for a dataset.

```
GET /api/reporting?dataset_id={dataset_id}
```

**Query Parameters**:
- `dataset_id`: Filter by dataset ID
- `skip`: Records to skip (default: 0)
- `limit`: Max records (default: 10)

**Response**:
```json
{
  "reports": [
    {
      "id": 1,
      "dataset_id": 1,
      "assessment_id": 1,
      "overall_score": 78.5,
      "readiness_level": "moderate",
      "created_at": "2024-01-15T10:40:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 10
}
```

## Findings Structure

Each finding includes:

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique finding ID |
| type | string | Finding type (e.g., pii_detected, missing_values) |
| severity | string | critical, high, medium, low |
| module | string | Assessment module that detected it |
| description | string | Human-readable description |
| affected_columns | array | Columns involved |
| affected_rows | integer | Number of rows affected |
| details | object | Additional details |
| recommendation | string | Suggested action |

### Finding Types

| Type | Module | Description |
|------|--------|-------------|
| missing_values | quality | Missing data detected |
| outliers | quality | Statistical outliers found |
| format_inconsistency | quality | Inconsistent data formats |
| stale_data | quality | Data is outdated |
| unsupported_format | accessibility | File format issues |
| insufficient_volume | accessibility | Not enough samples |
| pii_detected | governance | Personal information found |
| unclear_licensing | governance | Usage rights unclear |
| class_imbalance | ai_compatibility | Unbalanced target classes |
| missing_labels | ai_compatibility | Unlabeled records |
| low_feature_diversity | ai_compatibility | Limited feature variety |
| bias_detected | diversity | Potential bias found |
| underrepresentation | diversity | Groups underrepresented |

## Recommendations Structure

Each recommendation includes:

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique recommendation ID |
| priority | string | critical, high, medium, low |
| category | string | Assessment module category |
| issue | string | Brief issue description |
| action | string | Recommended action |
| impact | string | Expected impact of action |
| effort | string | Estimated effort (low, medium, high) |

### Priority Levels

| Priority | Description | Action Required |
|----------|-------------|-----------------|
| critical | Blocks AI/ML use | Must fix immediately |
| high | Significant impact | Should fix before use |
| medium | Moderate impact | Plan to address |
| low | Minor impact | Nice to have |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid format or parameters |
| 404 | Not Found - Assessment or report not found |
| 500 | Internal Server Error |

## See Also

- [Assessment API](assessment.md)
- [Scoring API](scoring.md)
- [Report Interpretation Guide](../user-guides/report-interpretation.md)
