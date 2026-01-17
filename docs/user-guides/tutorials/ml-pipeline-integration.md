# Tutorial: ML Pipeline Integration

This tutorial shows how to integrate DataAptor AI into your machine learning pipelines for automated data validation.

## Prerequisites

- DataAptor AI running (see [Installation Guide](../installation.md))
- Python 3.9+
- ML framework (TensorFlow, PyTorch, or scikit-learn)

## Overview

Integrating DataAptor AI into your ML pipeline ensures:
- Data quality is validated before training
- Issues are caught early in the pipeline
- Training only proceeds with quality data
- Data quality metrics are tracked over time

## Installation

Install the DataAptor Python client:

```bash
pip install dataaptor-client
```

Or install from source:

```bash
cd client/cli
pip install -e .
```

## Basic Integration

### Simple Validation Before Training

```python
from dataaptor import DataAptorClient
import pandas as pd

# Initialize client
client = DataAptorClient(api_url="http://localhost:8000")

def validate_and_train(data_path, min_score=70):
    """Validate data quality before training."""
    
    # Step 1: Upload and assess
    print("Uploading dataset...")
    dataset_id = client.upload(data_path)
    
    print("Running assessment...")
    assessment = client.assess(dataset_id, wait=True)
    
    # Step 2: Check quality threshold
    if assessment.overall_score < min_score:
        print(f"Data quality too low: {assessment.overall_score}/100")
        print("Issues found:")
        for finding in assessment.findings:
            print(f"  - [{finding['severity']}] {finding['description']}")
        raise ValueError("Data quality below threshold")
    
    print(f"Data quality passed: {assessment.overall_score}/100")
    
    # Step 3: Proceed with training
    df = pd.read_csv(data_path)
    # ... your training code here ...
    
    return assessment

# Usage
assessment = validate_and_train("training_data.csv", min_score=75)
```

## TensorFlow Integration

### Custom Data Validation Layer

```python
import tensorflow as tf
from dataaptor import DataAptorClient

class DataAptorValidator:
    """Validates data quality before TensorFlow training."""
    
    def __init__(self, api_url="http://localhost:8000", min_score=70):
        self.client = DataAptorClient(api_url=api_url)
        self.min_score = min_score
        self.last_assessment = None
    
    def validate(self, data_path):
        """Validate dataset and return assessment."""
        dataset_id = self.client.upload(data_path)
        self.last_assessment = self.client.assess(dataset_id, wait=True)
        
        if self.last_assessment.overall_score < self.min_score:
            raise ValueError(
                f"Data quality {self.last_assessment.overall_score} "
                f"below threshold {self.min_score}"
            )
        
        return self.last_assessment
    
    def get_quality_metrics(self):
        """Get metrics for TensorBoard logging."""
        if not self.last_assessment:
            return {}
        
        return {
            "data_quality/overall": self.last_assessment.overall_score,
            "data_quality/quality": self.last_assessment.module_scores.get("quality", 0),
            "data_quality/accessibility": self.last_assessment.module_scores.get("accessibility", 0),
            "data_quality/governance": self.last_assessment.module_scores.get("governance", 0),
            "data_quality/ai_compatibility": self.last_assessment.module_scores.get("ai_compatibility", 0),
            "data_quality/diversity": self.last_assessment.module_scores.get("diversity", 0),
        }


# Usage in training script
validator = DataAptorValidator(min_score=75)

# Validate training data
print("Validating training data...")
assessment = validator.validate("train.csv")
print(f"Training data score: {assessment.overall_score}")

# Validate validation data
print("Validating validation data...")
val_assessment = validator.validate("val.csv")
print(f"Validation data score: {val_assessment.overall_score}")

# Log metrics to TensorBoard
file_writer = tf.summary.create_file_writer("logs/data_quality")
with file_writer.as_default():
    for name, value in validator.get_quality_metrics().items():
        tf.summary.scalar(name, value, step=0)

# Proceed with training
model = tf.keras.Sequential([...])
model.compile(...)
model.fit(train_dataset, validation_data=val_dataset, ...)
```

### Keras Callback for Continuous Validation

```python
import tensorflow as tf
from dataaptor import DataAptorClient

class DataQualityCallback(tf.keras.callbacks.Callback):
    """Keras callback to log data quality metrics."""
    
    def __init__(self, validator, log_dir="logs"):
        super().__init__()
        self.validator = validator
        self.file_writer = tf.summary.create_file_writer(f"{log_dir}/data_quality")
    
    def on_train_begin(self, logs=None):
        """Log data quality metrics at training start."""
        with self.file_writer.as_default():
            for name, value in self.validator.get_quality_metrics().items():
                tf.summary.scalar(name, value, step=0)

# Usage
validator = DataAptorValidator()
validator.validate("train.csv")

model.fit(
    train_dataset,
    callbacks=[
        DataQualityCallback(validator),
        tf.keras.callbacks.TensorBoard(log_dir="logs")
    ]
)
```

## PyTorch Integration

### Custom Dataset with Validation

```python
import torch
from torch.utils.data import Dataset, DataLoader
from dataaptor import DataAptorClient
import pandas as pd

class ValidatedDataset(Dataset):
    """PyTorch Dataset with built-in data quality validation."""
    
    def __init__(self, data_path, min_score=70, validate=True):
        self.data_path = data_path
        
        if validate:
            self._validate(min_score)
        
        self.data = pd.read_csv(data_path)
        self.features = self.data.drop(columns=['label']).values
        self.labels = self.data['label'].values
    
    def _validate(self, min_score):
        """Validate data quality before loading."""
        client = DataAptorClient()
        dataset_id = client.upload(self.data_path)
        assessment = client.assess(dataset_id, wait=True)
        
        self.assessment = assessment
        
        if assessment.overall_score < min_score:
            raise ValueError(
                f"Data quality {assessment.overall_score} below threshold {min_score}"
            )
        
        print(f"Data quality validated: {assessment.overall_score}/100")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return (
            torch.tensor(self.features[idx], dtype=torch.float32),
            torch.tensor(self.labels[idx], dtype=torch.long)
        )


# Usage
train_dataset = ValidatedDataset("train.csv", min_score=75)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Access assessment results
print(f"Quality score: {train_dataset.assessment.module_scores['quality']}")
```

### PyTorch Lightning Integration

```python
import pytorch_lightning as pl
from dataaptor import DataAptorClient

class DataQualityModule(pl.LightningModule):
    """Lightning module with data quality logging."""
    
    def __init__(self, model, data_assessment):
        super().__init__()
        self.model = model
        self.data_assessment = data_assessment
        
        # Log data quality as hyperparameters
        self.save_hyperparameters({
            "data_quality_score": data_assessment.overall_score,
            "data_quality_level": data_assessment.readiness_level,
        })
    
    def on_train_start(self):
        """Log data quality metrics at training start."""
        self.logger.log_metrics({
            "data_quality/overall": self.data_assessment.overall_score,
            "data_quality/quality": self.data_assessment.module_scores.get("quality", 0),
            "data_quality/accessibility": self.data_assessment.module_scores.get("accessibility", 0),
        })


# Usage
client = DataAptorClient()
dataset_id = client.upload("train.csv")
assessment = client.assess(dataset_id, wait=True)

model = YourModel()
lightning_module = DataQualityModule(model, assessment)

trainer = pl.Trainer(...)
trainer.fit(lightning_module, train_loader)
```

## scikit-learn Integration

### Pipeline with Validation Step

```python
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from dataaptor import DataAptorClient
import pandas as pd
import tempfile

class DataQualityValidator(BaseEstimator, TransformerMixin):
    """scikit-learn transformer for data quality validation."""
    
    def __init__(self, min_score=70, api_url="http://localhost:8000"):
        self.min_score = min_score
        self.api_url = api_url
        self.assessment_ = None
    
    def fit(self, X, y=None):
        """Validate data quality during fit."""
        client = DataAptorClient(api_url=self.api_url)
        
        # Save data temporarily for upload
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            if isinstance(X, pd.DataFrame):
                X.to_csv(f.name, index=False)
            else:
                pd.DataFrame(X).to_csv(f.name, index=False)
            
            dataset_id = client.upload(f.name)
            self.assessment_ = client.assess(dataset_id, wait=True)
        
        if self.assessment_.overall_score < self.min_score:
            raise ValueError(
                f"Data quality {self.assessment_.overall_score} "
                f"below threshold {self.min_score}"
            )
        
        return self
    
    def transform(self, X):
        """Pass through data unchanged."""
        return X
    
    def get_quality_report(self):
        """Get the quality assessment report."""
        return self.assessment_


# Usage in pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipeline = Pipeline([
    ('validate', DataQualityValidator(min_score=75)),
    ('scale', StandardScaler()),
    ('classify', RandomForestClassifier())
])

# Fit pipeline (validation happens automatically)
pipeline.fit(X_train, y_train)

# Access quality report
quality_report = pipeline.named_steps['validate'].get_quality_report()
print(f"Data quality: {quality_report.overall_score}")
```

## MLflow Integration

### Logging Data Quality with Experiments

```python
import mlflow
from dataaptor import DataAptorClient

def train_with_mlflow(data_path, model_params):
    """Train model with MLflow tracking and data quality logging."""
    
    client = DataAptorClient()
    
    with mlflow.start_run():
        # Assess data quality
        print("Assessing data quality...")
        dataset_id = client.upload(data_path)
        assessment = client.assess(dataset_id, wait=True)
        
        # Log data quality metrics
        mlflow.log_metric("data_quality_score", assessment.overall_score)
        mlflow.log_metric("data_quality_level", 
                         {"high": 4, "moderate": 3, "low": 2, "not_ready": 1}
                         .get(assessment.readiness_level, 0))
        
        for module, score in assessment.module_scores.items():
            mlflow.log_metric(f"data_quality_{module}", score)
        
        # Log assessment report as artifact
        report_path = f"/tmp/assessment_{assessment.id}.json"
        assessment.export(report_path, format="json")
        mlflow.log_artifact(report_path)
        
        # Log data quality tags
        mlflow.set_tag("data_quality_level", assessment.readiness_level)
        
        # Check quality threshold
        if assessment.overall_score < 70:
            mlflow.set_tag("training_status", "skipped_low_quality")
            print(f"Skipping training: data quality too low ({assessment.overall_score})")
            return None
        
        # Proceed with training
        mlflow.log_params(model_params)
        
        # ... training code ...
        
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "model")
        
        return model

# Usage
model = train_with_mlflow("train.csv", {"n_estimators": 100})
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline with Data Validation

on:
  push:
    paths:
      - 'data/**'
      - 'models/**'

jobs:
  validate-and-train:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install dataaptor-client pandas scikit-learn
      
      - name: Validate Data Quality
        env:
          DATAAPTOR_API_URL: ${{ secrets.DATAAPTOR_API_URL }}
        run: |
          python -c "
          from dataaptor import DataAptorClient
          client = DataAptorClient()
          dataset_id = client.upload('data/train.csv')
          assessment = client.assess(dataset_id, wait=True)
          print(f'Data Quality Score: {assessment.overall_score}')
          if assessment.overall_score < 70:
              raise ValueError('Data quality below threshold')
          "
      
      - name: Train Model
        if: success()
        run: python train.py
      
      - name: Upload Model
        if: success()
        uses: actions/upload-artifact@v3
        with:
          name: trained-model
          path: models/
```

## Best Practices

1. **Set Appropriate Thresholds**: Start with 70, adjust based on your needs
2. **Log Quality Metrics**: Track data quality alongside model metrics
3. **Fail Fast**: Validate early in the pipeline to save resources
4. **Version Data Quality**: Track quality scores over time
5. **Automate Validation**: Include in CI/CD pipelines
6. **Handle Failures Gracefully**: Provide clear error messages

## Next Steps

- Review [Integrations Guide](../integrations.md) for more options
- Learn about [Customizing Weights](../customizing-weights.md)
- Check [API Documentation](../../api/README.md) for advanced usage
