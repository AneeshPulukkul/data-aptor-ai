# Preparing Datasets for Assessment

This guide provides best practices for preparing your datasets before running DataAptor AI assessments.

## Overview

Proper data preparation can significantly improve your AI readiness scores and make the assessment results more actionable. This guide covers:

1. Data cleaning and formatting
2. Metadata preparation
3. File format considerations
4. Size and sampling guidelines

## Data Cleaning

### Remove Test Data

Before assessment, ensure your dataset contains only production-quality data:

```python
import pandas as pd

# Load your data
df = pd.read_csv("raw_data.csv")

# Remove test records
df = df[~df['email'].str.contains('test|example|dummy', case=False, na=False)]

# Remove placeholder values
df = df.replace(['N/A', 'TBD', 'PLACEHOLDER', ''], pd.NA)

# Save cleaned data
df.to_csv("cleaned_data.csv", index=False)
```

### Handle Missing Values

Document your missing value strategy:

```python
# Option 1: Remove rows with too many missing values
threshold = 0.5  # 50% threshold
df = df.dropna(thresh=int(len(df.columns) * threshold))

# Option 2: Fill with appropriate values
df['numeric_column'].fillna(df['numeric_column'].median(), inplace=True)
df['category_column'].fillna('Unknown', inplace=True)

# Option 3: Keep missing values but document them
missing_report = df.isnull().sum()
missing_report.to_csv("missing_values_report.csv")
```

### Standardize Formats

Ensure consistent formatting across your dataset:

```python
# Standardize date formats
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

# Standardize text case
df['category'] = df['category'].str.lower().str.strip()

# Standardize phone numbers
import re
df['phone'] = df['phone'].apply(
    lambda x: re.sub(r'[^\d]', '', str(x)) if pd.notna(x) else x
)
```

## Metadata Preparation

### Include Licensing Information

Add licensing metadata to help with governance assessment:

```json
{
  "license": "MIT",
  "source": "Internal data collection",
  "usage_rights": "Approved for AI/ML training",
  "data_owner": "Data Science Team",
  "collection_date": "2024-01-15"
}
```

### Document Column Meanings

Create a data dictionary:

```csv
column_name,description,data_type,is_pii,is_label
customer_id,Unique customer identifier,integer,false,false
email,Customer email address,string,true,false
purchase_amount,Transaction value in USD,float,false,false
churn_label,Whether customer churned,boolean,false,true
```

### Specify AI Task Type

Include the intended AI task in metadata:

```json
{
  "ai_task": "classification",
  "target_column": "churn_label",
  "feature_columns": ["age", "tenure", "purchase_amount"],
  "description": "Customer churn prediction dataset"
}
```

## File Format Guidelines

### CSV Files

Best practices for CSV:

```python
# Use UTF-8 encoding
df.to_csv("data.csv", index=False, encoding='utf-8')

# Include headers
# Avoid special characters in column names
df.columns = df.columns.str.replace(r'[^\w]', '_', regex=True)

# Use consistent delimiters (comma preferred)
df.to_csv("data.csv", sep=',', index=False)
```

### JSON Files

Structure JSON for optimal assessment:

```json
{
  "metadata": {
    "version": "1.0",
    "created_at": "2024-01-15T10:00:00Z",
    "record_count": 10000,
    "schema": {
      "id": "integer",
      "name": "string",
      "value": "float"
    }
  },
  "records": [
    {"id": 1, "name": "Item 1", "value": 100.5},
    {"id": 2, "name": "Item 2", "value": 200.3}
  ]
}
```

### Excel Files

Prepare Excel files properly:

- Use the first sheet for data
- Include headers in the first row
- Avoid merged cells
- Remove formatting (colors, fonts) that might cause parsing issues
- Save as `.xlsx` (not `.xls`)

## Size and Sampling

### Minimum Sample Sizes

Recommended minimum samples by AI task:

| Task Type | Minimum Samples | Recommended |
|-----------|-----------------|-------------|
| Classification | 1,000 | 10,000+ |
| Regression | 500 | 5,000+ |
| NLP | 10,000 | 100,000+ |
| Computer Vision | 5,000 | 50,000+ |
| Audio | 1,000 | 10,000+ |

### Sampling Strategies

If your dataset is too large, create a representative sample:

```python
# Random sampling
sample = df.sample(n=10000, random_state=42)

# Stratified sampling (for classification)
from sklearn.model_selection import train_test_split
sample, _ = train_test_split(
    df, 
    train_size=10000, 
    stratify=df['label'],
    random_state=42
)

# Time-based sampling (for time series)
sample = df.sort_values('date').tail(10000)
```

### Large File Handling

For files larger than 1GB:

1. **Split into chunks**: Create multiple smaller files
2. **Sample first**: Assess a representative sample
3. **Use streaming**: Process data in batches

```python
# Split large CSV into chunks
chunk_size = 100000
for i, chunk in enumerate(pd.read_csv("large_file.csv", chunksize=chunk_size)):
    chunk.to_csv(f"chunk_{i}.csv", index=False)
```

## PII Handling

### Identify PII Columns

Common PII types to look for:

- Names (first_name, last_name, full_name)
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Addresses
- Dates of birth
- IP addresses

### Anonymization Techniques

```python
import hashlib

# Hash identifiers
df['customer_id_hash'] = df['customer_id'].apply(
    lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16]
)

# Mask email addresses
df['email_masked'] = df['email'].apply(
    lambda x: x.split('@')[0][:2] + '***@' + x.split('@')[1] if pd.notna(x) else x
)

# Generalize dates (keep only year-month)
df['birth_month'] = pd.to_datetime(df['birth_date']).dt.to_period('M')

# Remove original PII columns
df = df.drop(columns=['customer_id', 'email', 'birth_date'])
```

## Pre-Assessment Checklist

Before running an assessment, verify:

- [ ] Test/dummy data removed
- [ ] Missing values documented or handled
- [ ] Formats standardized (dates, text, numbers)
- [ ] Column headers are descriptive
- [ ] File encoding is UTF-8
- [ ] Metadata includes licensing information
- [ ] PII is anonymized or documented
- [ ] Sample size meets minimum requirements
- [ ] File size is under 1GB (or sampled)

## Next Steps

- Run your assessment following the [Dataset Assessment Guide](dataset-assessment.md)
- Learn about [Improving Readiness](improving-readiness.md)
- Review [Security Practices](security-practices.md)
