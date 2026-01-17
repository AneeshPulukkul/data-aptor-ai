# Integrations Guide

This guide explains how to integrate DataAptor AI with your existing data infrastructure and ML pipelines.

## Overview

DataAptor AI can integrate with:

- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob
- **Databases**: PostgreSQL, MySQL, MongoDB
- **ML Platforms**: TensorFlow, PyTorch, SageMaker, MLflow
- **CI/CD Pipelines**: GitHub Actions, GitLab CI, Jenkins
- **Data Catalogs**: Apache Atlas, AWS Glue, Databricks Unity Catalog

## Cloud Storage Integration

### AWS S3

Configure S3 as a data source:

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Configure DataAptor
python dataaptor.py config --set storage_type --value s3
python dataaptor.py config --set s3_bucket --value your-bucket-name
```

Upload directly from S3:

```bash
python dataaptor.py upload s3://your-bucket/path/to/data.csv
```

### Google Cloud Storage

```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Configure DataAptor
python dataaptor.py config --set storage_type --value gcs
python dataaptor.py config --set gcs_bucket --value your-bucket-name

# Upload from GCS
python dataaptor.py upload gs://your-bucket/path/to/data.csv
```

### Azure Blob Storage

```bash
# Set credentials
export AZURE_STORAGE_CONNECTION_STRING=your_connection_string

# Configure DataAptor
python dataaptor.py config --set storage_type --value azure
python dataaptor.py config --set azure_container --value your-container

# Upload from Azure
python dataaptor.py upload azure://your-container/path/to/data.csv
```

## Database Integration

### PostgreSQL

Connect to PostgreSQL and assess tables directly:

```bash
# Configure database connection
python dataaptor.py config --set db_type --value postgresql
python dataaptor.py config --set db_host --value localhost
python dataaptor.py config --set db_port --value 5432
python dataaptor.py config --set db_name --value your_database
python dataaptor.py config --set db_user --value your_user

# Assess a table
python dataaptor.py assess-table your_schema.your_table
```

### MySQL

```bash
python dataaptor.py config --set db_type --value mysql
python dataaptor.py config --set db_host --value localhost
python dataaptor.py config --set db_port --value 3306

python dataaptor.py assess-table your_database.your_table
```

### MongoDB

```bash
python dataaptor.py config --set db_type --value mongodb
python dataaptor.py config --set mongodb_uri --value mongodb://localhost:27017

python dataaptor.py assess-collection your_database.your_collection
```

## ML Pipeline Integration

### Pre-Training Validation

Add DataAptor AI as a validation step before model training:

```python
from dataaptor import DataAptorClient

client = DataAptorClient(api_url="http://localhost:8000")

# Upload and assess dataset
dataset_id = client.upload("training_data.csv")
assessment = client.assess(dataset_id)

# Check if data meets quality threshold
if assessment.overall_score < 70:
    raise ValueError(f"Data quality too low: {assessment.overall_score}")

# Proceed with training
model.fit(training_data)
```

### TensorFlow Integration

```python
import tensorflow as tf
from dataaptor import DataAptorClient

client = DataAptorClient()

def validate_dataset(dataset_path):
    """Validate dataset before TensorFlow training."""
    dataset_id = client.upload(dataset_path)
    result = client.assess(dataset_id, wait=True)
    
    if result.overall_score < 60:
        print(f"Warning: Low data quality score ({result.overall_score})")
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec['action']}")
    
    return result.overall_score >= 60

# Use in training pipeline
if validate_dataset("data/train.csv"):
    # Load and train
    dataset = tf.data.Dataset.from_tensor_slices(...)
    model.fit(dataset)
```

### PyTorch Integration

```python
import torch
from dataaptor import DataAptorClient

client = DataAptorClient()

class ValidatedDataset(torch.utils.data.Dataset):
    def __init__(self, data_path, min_score=60):
        # Validate data quality first
        dataset_id = client.upload(data_path)
        assessment = client.assess(dataset_id, wait=True)
        
        if assessment.overall_score < min_score:
            raise ValueError(
                f"Data quality score {assessment.overall_score} "
                f"below threshold {min_score}"
            )
        
        self.data = self._load_data(data_path)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]
```

### MLflow Integration

```python
import mlflow
from dataaptor import DataAptorClient

client = DataAptorClient()

with mlflow.start_run():
    # Assess training data
    assessment = client.assess_file("training_data.csv")
    
    # Log data quality metrics
    mlflow.log_metric("data_quality_score", assessment.overall_score)
    mlflow.log_metric("data_completeness", assessment.quality.completeness)
    mlflow.log_metric("data_accuracy", assessment.quality.accuracy)
    
    # Log assessment report as artifact
    mlflow.log_artifact(assessment.export("json"))
    
    # Train model
    model = train_model(...)
    mlflow.sklearn.log_model(model, "model")
```

## CI/CD Integration

### GitHub Actions

Add data validation to your CI/CD pipeline:

```yaml
# .github/workflows/data-validation.yml
name: Data Validation

on:
  push:
    paths:
      - 'data/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install DataAptor CLI
        run: pip install dataaptor-cli
      
      - name: Validate Data
        env:
          DATAAPTOR_API_URL: ${{ secrets.DATAAPTOR_API_URL }}
          DATAAPTOR_API_KEY: ${{ secrets.DATAAPTOR_API_KEY }}
        run: |
          dataaptor upload data/training.csv --assess --min-score 70
```

### GitLab CI

```yaml
# .gitlab-ci.yml
data-validation:
  stage: validate
  image: python:3.10
  script:
    - pip install dataaptor-cli
    - dataaptor config --set api_url --value $DATAAPTOR_API_URL
    - dataaptor upload data/training.csv --assess --min-score 70
  only:
    changes:
      - data/**
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Validate Data') {
            steps {
                sh '''
                    pip install dataaptor-cli
                    dataaptor config --set api_url --value ${DATAAPTOR_API_URL}
                    dataaptor upload data/training.csv --assess --min-score 70
                '''
            }
        }
        
        stage('Train Model') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh 'python train.py'
            }
        }
    }
}
```

## Webhook Integration

Configure webhooks to receive assessment notifications:

```bash
# Register a webhook
curl -X POST http://localhost:8000/api/webhooks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["assessment.completed", "assessment.failed"],
    "secret": "your_webhook_secret"
  }'
```

Webhook payload example:

```json
{
  "event": "assessment.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "assessment_id": 123,
    "dataset_id": 456,
    "overall_score": 85,
    "readiness_level": "high"
  }
}
```

## Next Steps

- Review [Security Practices](security-practices.md)
- Explore [Preparing Datasets](preparing-datasets.md)
- Check [API Documentation](../api/README.md)
