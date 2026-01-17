# Improving AI Readiness

This guide provides actionable strategies for improving your dataset's AI readiness score based on assessment results.

## Overview

After receiving your assessment report, you'll have specific findings and recommendations. This guide helps you address common issues and improve your scores across all five assessment modules.

## Improving Data Quality Score

### Addressing Missing Values

**Issue**: High percentage of missing values

**Solutions**:

1. **Mean/Median Imputation** (for numeric data):
```python
import pandas as pd
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='median')
df['numeric_col'] = imputer.fit_transform(df[['numeric_col']])
```

2. **Mode Imputation** (for categorical data):
```python
df['category_col'].fillna(df['category_col'].mode()[0], inplace=True)
```

3. **Advanced Imputation** (using ML):
```python
from sklearn.impute import KNNImputer

imputer = KNNImputer(n_neighbors=5)
df_imputed = pd.DataFrame(
    imputer.fit_transform(df),
    columns=df.columns
)
```

4. **Collect Missing Data**: If possible, go back to the source

### Fixing Outliers

**Issue**: Outliers detected in numeric columns

**Solutions**:

1. **Remove Outliers** (if they're errors):
```python
from scipy import stats

z_scores = stats.zscore(df['numeric_col'])
df = df[(abs(z_scores) < 3)]
```

2. **Cap Outliers** (winsorization):
```python
lower = df['numeric_col'].quantile(0.01)
upper = df['numeric_col'].quantile(0.99)
df['numeric_col'] = df['numeric_col'].clip(lower, upper)
```

3. **Transform Data** (reduce skewness):
```python
import numpy as np
df['numeric_col_log'] = np.log1p(df['numeric_col'])
```

### Improving Consistency

**Issue**: Inconsistent formats detected

**Solutions**:

1. **Standardize Date Formats**:
```python
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
```

2. **Standardize Text Case**:
```python
df['category'] = df['category'].str.lower().str.strip()
```

3. **Create Validation Rules**:
```python
def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, str(email)))

df['email_valid'] = df['email'].apply(validate_email)
```

### Improving Timeliness

**Issue**: Data is stale or outdated

**Solutions**:

1. **Refresh Data**: Collect new samples
2. **Add Timestamps**: Include collection dates
3. **Filter Recent Data**:
```python
cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=365)
df = df[df['created_at'] >= cutoff_date]
```

## Improving Accessibility Score

### Format Compatibility

**Issue**: Unsupported or complex file format

**Solutions**:

1. **Convert to Standard Formats**:
```python
# From Excel to CSV
df = pd.read_excel('data.xlsx')
df.to_csv('data.csv', index=False)

# From XML to JSON
import xmltodict
import json

with open('data.xml') as f:
    data = xmltodict.parse(f.read())
with open('data.json', 'w') as f:
    json.dump(data, f)
```

2. **Use Parquet for Large Datasets**:
```python
df.to_parquet('data.parquet', index=False)
```

### Increasing Volume

**Issue**: Insufficient sample size

**Solutions**:

1. **Collect More Data**: Extend data collection period
2. **Data Augmentation** (for images):
```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)
```

3. **Synthetic Data Generation**:
```python
from sdv.tabular import GaussianCopula

model = GaussianCopula()
model.fit(df)
synthetic_data = model.sample(num_rows=5000)
```

4. **Combine Multiple Sources**: Merge related datasets

## Improving Governance Score

### Removing PII

**Issue**: PII detected in dataset

**Solutions**:

1. **Anonymization**:
```python
import hashlib

def anonymize(value, salt='secret'):
    return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()[:12]

df['customer_id'] = df['customer_id'].apply(anonymize)
```

2. **Pseudonymization**:
```python
from faker import Faker
fake = Faker()

name_map = {name: fake.name() for name in df['name'].unique()}
df['name'] = df['name'].map(name_map)
```

3. **Generalization**:
```python
# Age ranges instead of exact ages
df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100],
                         labels=['<18', '18-35', '35-50', '50-65', '65+'])

# Zip code prefix only
df['zip_prefix'] = df['zip_code'].str[:3]
```

4. **Suppression** (remove sensitive columns):
```python
df = df.drop(columns=['ssn', 'credit_card', 'phone'])
```

### Clarifying Licensing

**Issue**: Unclear usage rights

**Solutions**:

1. **Document Data Sources**: Create a data lineage document
2. **Obtain Explicit Permissions**: Get written approval for AI/ML use
3. **Add License Metadata**:
```python
metadata = {
    "license": "CC-BY-4.0",
    "source": "Internal collection",
    "usage_rights": "Approved for AI/ML training",
    "approved_by": "Legal Team",
    "approval_date": "2024-01-15"
}
```

## Improving AI Compatibility Score

### Improving Label Quality

**Issue**: Poor label quality or class imbalance

**Solutions**:

1. **Fix Class Imbalance**:
```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)
```

2. **Improve Label Coverage**:
```python
# Identify unlabeled records
unlabeled = df[df['label'].isna()]
print(f"Unlabeled records: {len(unlabeled)}")

# Manual labeling or active learning
```

3. **Validate Labels**:
```python
# Check for label consistency
label_counts = df.groupby(['feature1', 'feature2'])['label'].nunique()
inconsistent = label_counts[label_counts > 1]
```

### Enhancing Features

**Issue**: Low feature richness

**Solutions**:

1. **Feature Engineering**:
```python
# Create derived features
df['total_spend'] = df['quantity'] * df['price']
df['days_since_signup'] = (pd.Timestamp.now() - df['signup_date']).dt.days

# Interaction features
df['feature_interaction'] = df['feature1'] * df['feature2']
```

2. **Add External Data**:
```python
# Merge with external dataset
external_data = pd.read_csv('external_features.csv')
df = df.merge(external_data, on='id', how='left')
```

### Reducing Preprocessing Needs

**Issue**: Extensive preprocessing required

**Solutions**:

1. **Pre-encode Categorical Variables**:
```python
df = pd.get_dummies(df, columns=['category1', 'category2'])
```

2. **Pre-scale Numeric Features**:
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
```

## Improving Diversity Score

### Increasing Representativeness

**Issue**: Low sample diversity

**Solutions**:

1. **Stratified Sampling**:
```python
from sklearn.model_selection import train_test_split

# Ensure all groups are represented
stratified_sample = df.groupby('category', group_keys=False).apply(
    lambda x: x.sample(min(len(x), 1000))
)
```

2. **Targeted Data Collection**: Collect more samples from underrepresented groups

### Addressing Bias

**Issue**: Potential bias detected

**Solutions**:

1. **Rebalance Protected Attributes**:
```python
# Ensure equal representation
min_count = df['protected_attr'].value_counts().min()
balanced_df = df.groupby('protected_attr').apply(
    lambda x: x.sample(min_count)
).reset_index(drop=True)
```

2. **Apply Fairness Constraints**:
```python
from fairlearn.reductions import ExponentiatedGradient, DemographicParity

constraint = DemographicParity()
mitigator = ExponentiatedGradient(estimator, constraint)
mitigator.fit(X, y, sensitive_features=sensitive)
```

3. **Monitor Disparate Impact**:
```python
def disparate_impact_ratio(df, protected_col, outcome_col):
    groups = df.groupby(protected_col)[outcome_col].mean()
    return groups.min() / groups.max()

dir_ratio = disparate_impact_ratio(df, 'gender', 'approved')
print(f"Disparate Impact Ratio: {dir_ratio:.2f}")
# Should be >= 0.8 for fairness
```

## Iterative Improvement

1. **Run Initial Assessment**: Get baseline scores
2. **Prioritize Issues**: Focus on critical and high-priority findings
3. **Implement Fixes**: Apply relevant solutions
4. **Re-assess**: Run assessment again to measure improvement
5. **Repeat**: Continue until target score is reached

## Next Steps

- Review [Security Practices](security-practices.md)
- Explore [Integration Options](integrations.md)
- Check [Tutorials](tutorials/) for hands-on examples
