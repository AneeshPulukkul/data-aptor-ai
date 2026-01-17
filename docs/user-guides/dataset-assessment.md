# Dataset Assessment Guide

This guide explains how to assess your datasets for AI readiness using DataAptor AI.

## Overview

DataAptor AI evaluates datasets across five key dimensions to determine their suitability for AI/ML applications:

1. **Data Quality** (40% weight)
2. **Accessibility** (20% weight)
3. **Governance** (15% weight)
4. **AI Compatibility** (20% weight)
5. **Diversity/Bias** (5% weight)

## Supported File Formats

DataAptor AI supports a wide range of file formats:

### Structured Data
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- JSON (`.json`)
- Parquet (`.parquet`)

### Semi-Structured Data
- XML (`.xml`)
- YAML (`.yaml`, `.yml`)

### Unstructured Data
- Text files (`.txt`)
- PDF documents (`.pdf`)
- Images (`.jpg`, `.jpeg`, `.png`)
- Audio files (`.wav`, `.mp3`)

## Starting an Assessment

### Using the Web UI

1. **Navigate to the Dashboard**
   - Open http://localhost:3000 in your browser

2. **Upload Your Dataset**
   - Click the "Upload" button
   - Drag and drop your file or click to browse
   - Wait for the upload to complete

3. **Configure Assessment**
   - Select which modules to run (all are selected by default)
   - Optionally customize weights for each module
   - Click "Start Assessment"

4. **Monitor Progress**
   - Watch the progress bar as each module completes
   - Assessment typically takes 1-5 minutes depending on dataset size

5. **View Results**
   - Once complete, you'll see your overall score
   - Click on individual modules for detailed breakdowns

### Using the CLI

```bash
# Upload a dataset
python dataaptor.py upload your_data.csv
# Output: Dataset uploaded successfully. ID: 1

# Start assessment with default settings
python dataaptor.py assess 1
# Output: Assessment started. ID: 1

# Start assessment with specific modules
python dataaptor.py assess 1 --modules quality,accessibility,governance

# Check assessment status
python dataaptor.py status 1
# Output: Status: completed

# View the report
python dataaptor.py report 1
```

### Using the API

```bash
# Upload dataset
curl -X POST http://localhost:8000/api/datasets/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@your_data.csv"

# Start assessment
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1}'

# Check status
curl http://localhost:8000/api/assessments/1/status \
  -H "Authorization: Bearer <token>"

# Get report
curl http://localhost:8000/api/reports/1 \
  -H "Authorization: Bearer <token>"
```

## Assessment Modules

### Data Quality Module

Evaluates the fundamental quality of your data:

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| Completeness | Missing value detection | 0-4 based on % missing |
| Accuracy | Outlier detection, type consistency | 0-4 based on issues found |
| Consistency | Format uniformity | 0-4 based on format issues |
| Timeliness | Data freshness | 0-4 based on data age |

### Accessibility Module

Assesses how easily the data can be used:

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| Availability | Format compatibility for AI/ML | 0-4 based on format |
| Volume | Sample size adequacy | 0-4 based on record count |

### Governance Module

Checks compliance and legal aspects:

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| Privacy | PII detection (email, phone, SSN, etc.) | 0-4 based on PII found |
| Licensing | Usage rights validation | 0-4 based on license clarity |

### AI Compatibility Module

Evaluates suitability for specific AI tasks:

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| Relevance | Task alignment | 0-4 based on indicators |
| Labeling | Label quality and coverage | 0-4 based on label analysis |
| Feature Richness | Feature variability | 0-4 based on feature diversity |
| Preprocessing | Transformation requirements | 0-4 based on effort needed |

### Diversity/Bias Module

Assesses fairness and representation:

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| Representativeness | Sample diversity | 0-4 based on entropy |
| Bias Detection | Fairness metrics | 0-4 based on bias indicators |

## Customizing Weights

You can customize the weight of each module based on your priorities:

### Via Web UI

1. Go to Assessment Configuration
2. Adjust the sliders for each module
3. Weights will automatically normalize to 100%

### Via CLI

```bash
python dataaptor.py assess 1 \
  --weight-quality 0.5 \
  --weight-accessibility 0.2 \
  --weight-governance 0.1 \
  --weight-ai-compatibility 0.15 \
  --weight-diversity 0.05
```

### Via API

```bash
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "weights": {
      "quality": 0.5,
      "accessibility": 0.2,
      "governance": 0.1,
      "ai_compatibility": 0.15,
      "diversity": 0.05
    }
  }'
```

## Best Practices

1. **Prepare Your Data**
   - Remove any test or dummy records
   - Ensure column headers are descriptive
   - Include metadata about licensing if available

2. **Choose Appropriate Modules**
   - For quick checks, run only Quality and Accessibility
   - For compliance-sensitive data, prioritize Governance
   - For ML projects, include AI Compatibility

3. **Interpret Results Carefully**
   - Low scores indicate areas for improvement, not failure
   - Review detailed findings for actionable insights
   - Consider your specific use case when evaluating scores

## Next Steps

- Learn to [Interpret Reports](report-interpretation.md)
- Explore [Customizing Weights](customizing-weights.md)
- See [Tutorials](tutorials/) for hands-on examples
