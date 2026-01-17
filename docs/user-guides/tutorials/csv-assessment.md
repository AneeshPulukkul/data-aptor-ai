# Tutorial: Assessing CSV Datasets

This tutorial walks you through assessing a CSV dataset using DataAptor AI.

## Prerequisites

- DataAptor AI running (see [Installation Guide](../installation.md))
- A CSV file to assess
- CLI tool installed or access to Web UI

## Sample Dataset

For this tutorial, we'll use a sample customer dataset. Create a file called `customers.csv`:

```csv
customer_id,name,email,age,signup_date,total_purchases,churn_label
1,John Smith,john.smith@email.com,35,2023-01-15,1250.50,0
2,Jane Doe,jane.doe@email.com,28,2023-02-20,890.25,0
3,Bob Johnson,bob.j@email.com,45,2022-11-10,2100.00,1
4,Alice Brown,,32,2023-03-05,450.75,0
5,Charlie Wilson,charlie@email.com,55,2022-08-22,3200.00,0
6,Diana Lee,diana.lee@email.com,29,2023-04-18,125.00,1
7,Edward Kim,edward.k@email.com,41,2023-01-30,1800.50,0
8,Fiona Garcia,fiona.g@email.com,38,2022-12-15,2500.25,0
9,George Taylor,george.t@email.com,52,2022-09-08,4100.00,0
10,Helen Martinez,,47,2023-02-28,950.00,1
```

## Step 1: Upload the Dataset

### Using the CLI

```bash
# Navigate to CLI directory
cd client/cli

# Upload the dataset
python dataaptor.py upload customers.csv

# Expected output:
# Dataset uploaded successfully!
# Dataset ID: 1
# Name: customers.csv
# Size: 892 bytes
# Type: csv
```

### Using the Web UI

1. Open http://localhost:3000
2. Click "Upload" in the navigation
3. Drag and drop `customers.csv` or click to browse
4. Wait for upload confirmation

### Using the API

```bash
curl -X POST http://localhost:8000/api/datasets/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@customers.csv" \
  -F "name=Customer Churn Dataset"
```

## Step 2: Start the Assessment

### Using the CLI

```bash
# Start assessment with all modules
python dataaptor.py assess 1

# Expected output:
# Assessment started!
# Assessment ID: 1
# Modules: quality, accessibility, governance, ai_compatibility, diversity
# Status: pending
```

### Using the Web UI

1. Go to the Dashboard
2. Find your dataset in the list
3. Click "Assess"
4. Select modules (all selected by default)
5. Click "Start Assessment"

### Using the API

```bash
curl -X POST http://localhost:8000/api/assessments \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1}'
```

## Step 3: Monitor Progress

### Using the CLI

```bash
# Check status
python dataaptor.py status 1

# Expected output (while running):
# Assessment ID: 1
# Status: assessing
# Progress: 60%
# Current Module: governance

# Expected output (when complete):
# Assessment ID: 1
# Status: completed
# Duration: 45 seconds
```

### Using the Web UI

The progress bar updates automatically. You'll see:
- Current module being processed
- Percentage complete
- Estimated time remaining

## Step 4: View the Report

### Using the CLI

```bash
# View the report
python dataaptor.py report 1

# Expected output:
# ================================
# DataAptor AI Assessment Report
# ================================
# Dataset: customers.csv
# Assessment ID: 1
# 
# Overall Score: 72/100
# Readiness Level: MODERATE
# 
# Module Scores:
# - Quality:          14/16 (87.5%)
# - Accessibility:     6/8  (75.0%)
# - Governance:        5/8  (62.5%)
# - AI Compatibility: 12/16 (75.0%)
# - Diversity:         5/8  (62.5%)
# 
# Key Findings:
# - 2 missing values detected in 'email' column
# - PII detected: email addresses
# - Class imbalance in 'churn_label' (70/30 split)
# 
# Top Recommendations:
# 1. [HIGH] Anonymize email addresses before AI/ML use
# 2. [MEDIUM] Fill missing email values or remove rows
# 3. [MEDIUM] Apply oversampling to balance churn labels
```

### Using the Web UI

1. Click on the completed assessment
2. View the interactive dashboard with:
   - Radar chart showing module scores
   - Bar chart showing criteria scores
   - Detailed findings list
   - Prioritized recommendations

## Step 5: Export the Report

### Using the CLI

```bash
# Export as JSON
python dataaptor.py export 1 --format json --output report.json

# Export as HTML
python dataaptor.py export 1 --format html --output report.html

# Export as CSV
python dataaptor.py export 1 --format csv --output report.csv
```

### Using the Web UI

1. Click "Export" button on the report page
2. Select format (JSON, HTML, CSV, PDF)
3. Download the file

## Understanding the Results

### Quality Score (14/16)

Our dataset scored well on quality:
- **Completeness**: 2 missing emails out of 10 records (80% complete)
- **Accuracy**: No outliers detected
- **Consistency**: Dates and numbers are consistent
- **Timeliness**: Data is recent (within 1 year)

### Accessibility Score (6/8)

- **Format**: CSV is fully compatible (4/4)
- **Volume**: 10 records is below minimum for ML (2/4)

### Governance Score (5/8)

- **Privacy**: PII detected (email addresses) (1/4)
- **Licensing**: No license info provided (4/4 assumed internal)

### AI Compatibility Score (12/16)

- **Relevance**: Good for classification task (4/4)
- **Labeling**: Labels present but imbalanced (3/4)
- **Features**: Good feature variety (3/4)
- **Preprocessing**: Minimal preprocessing needed (2/4)

### Diversity Score (5/8)

- **Representativeness**: Limited sample diversity (2/4)
- **Bias**: Minor class imbalance detected (3/4)

## Improving the Score

Based on the recommendations, let's improve our dataset:

```python
import pandas as pd
import hashlib

# Load data
df = pd.read_csv('customers.csv')

# 1. Anonymize emails
df['email_hash'] = df['email'].apply(
    lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:12] if pd.notna(x) else None
)
df = df.drop(columns=['email'])

# 2. Handle missing values
df['email_hash'].fillna('unknown', inplace=True)

# 3. Add more samples (in real scenario, collect more data)
# For now, we'll note this as a limitation

# Save improved dataset
df.to_csv('customers_improved.csv', index=False)
```

Re-run the assessment:

```bash
python dataaptor.py upload customers_improved.csv
python dataaptor.py assess 2
python dataaptor.py report 2

# Expected improvement:
# Overall Score: 82/100 (up from 72)
# - Governance score improved (no PII)
# - Quality score improved (no missing values)
```

## Next Steps

- Try the [Image Assessment Tutorial](image-assessment.md)
- Learn about [ML Pipeline Integration](ml-pipeline-integration.md)
- Review [Customizing Weights](../customizing-weights.md)
