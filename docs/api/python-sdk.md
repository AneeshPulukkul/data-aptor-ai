# Python SDK

The DataAptor Python SDK provides a convenient way to interact with the DataAptor AI API from Python applications.

## Installation

```bash
pip install dataaptor-client
```

Or install from source:

```bash
cd client/cli
pip install -e .
```

## Quick Start

```python
from dataaptor import DataAptorClient

# Initialize client
client = DataAptorClient(api_url="http://localhost:8000")

# Login (or use API key)
client.login(username="user@example.com", password="your_password")

# Upload a dataset
dataset_id = client.upload("data.csv")

# Run assessment
assessment = client.assess(dataset_id, wait=True)

# View results
print(f"Score: {assessment.overall_score}")
print(f"Level: {assessment.readiness_level}")
```

## Client Configuration

### Using Environment Variables

```python
import os
os.environ["DATAAPTOR_API_URL"] = "http://localhost:8000"
os.environ["DATAAPTOR_API_KEY"] = "your-api-key"

from dataaptor import DataAptorClient
client = DataAptorClient()  # Reads from environment
```

### Using Constructor Arguments

```python
from dataaptor import DataAptorClient

# With API key
client = DataAptorClient(
    api_url="http://localhost:8000",
    api_key="your-api-key"
)

# With username/password
client = DataAptorClient(api_url="http://localhost:8000")
client.login(username="user@example.com", password="password")
```

### Configuration File

Create `~/.dataaptor/config.yaml`:

```yaml
api_url: http://localhost:8000
api_key: your-api-key
timeout: 30
```

```python
from dataaptor import DataAptorClient
client = DataAptorClient()  # Reads from config file
```

## API Reference

### DataAptorClient

The main client class for interacting with the API.

#### Constructor

```python
DataAptorClient(
    api_url: str = None,
    api_key: str = None,
    timeout: int = 30
)
```

**Parameters**:
- `api_url`: Base URL of the DataAptor API
- `api_key`: API key for authentication
- `timeout`: Request timeout in seconds

### Authentication Methods

#### login()

Authenticate with username and password.

```python
client.login(username: str, password: str) -> TokenResponse
```

**Example**:
```python
token = client.login("user@example.com", "password")
print(f"Token expires in: {token.expires_in} seconds")
```

#### refresh_token()

Refresh the current authentication token.

```python
client.refresh_token() -> TokenResponse
```

### Dataset Methods

#### upload()

Upload a dataset file.

```python
client.upload(
    file_path: str,
    name: str = None,
    metadata: dict = None
) -> int
```

**Parameters**:
- `file_path`: Path to the dataset file
- `name`: Optional name for the dataset
- `metadata`: Optional metadata dictionary

**Returns**: Dataset ID

**Example**:
```python
dataset_id = client.upload(
    "data.csv",
    name="Customer Data",
    metadata={"source": "CRM", "version": "2.0"}
)
```

#### list_datasets()

List all datasets.

```python
client.list_datasets(
    skip: int = 0,
    limit: int = 10
) -> DatasetList
```

**Example**:
```python
datasets = client.list_datasets(limit=50)
for ds in datasets.datasets:
    print(f"{ds.id}: {ds.name} ({ds.file_type})")
```

#### get_dataset()

Get details of a specific dataset.

```python
client.get_dataset(dataset_id: int) -> Dataset
```

**Example**:
```python
dataset = client.get_dataset(1)
print(f"Rows: {dataset.metadata.get('rows')}")
print(f"Columns: {dataset.metadata.get('columns')}")
```

#### delete_dataset()

Delete a dataset.

```python
client.delete_dataset(dataset_id: int) -> bool
```

### Assessment Methods

#### assess()

Start an assessment for a dataset.

```python
client.assess(
    dataset_id: int,
    modules: List[str] = None,
    weights: Dict[str, float] = None,
    wait: bool = False
) -> Assessment
```

**Parameters**:
- `dataset_id`: ID of the dataset to assess
- `modules`: List of modules to run (default: all)
- `weights`: Custom weights for scoring
- `wait`: If True, wait for assessment to complete

**Example**:
```python
# Start and wait for completion
assessment = client.assess(
    dataset_id=1,
    modules=["quality", "accessibility", "governance"],
    weights={"quality": 0.5, "accessibility": 0.3, "governance": 0.2},
    wait=True
)

print(f"Score: {assessment.overall_score}")
```

#### get_assessment_status()

Check the status of an assessment.

```python
client.get_assessment_status(assessment_id: int) -> AssessmentStatus
```

**Example**:
```python
status = client.get_assessment_status(1)
print(f"Status: {status.status}")
print(f"Progress: {status.progress}%")
```

#### wait_for_assessment()

Wait for an assessment to complete.

```python
client.wait_for_assessment(
    assessment_id: int,
    timeout: int = 300,
    poll_interval: int = 5
) -> Assessment
```

### Report Methods

#### get_report()

Get the assessment report.

```python
client.get_report(assessment_id: int) -> Report
```

**Example**:
```python
report = client.get_report(1)
print(f"Overall Score: {report.overall_score}")
print(f"Readiness Level: {report.readiness_level}")

for finding in report.findings:
    print(f"[{finding.severity}] {finding.description}")

for rec in report.recommendations:
    print(f"[{rec.priority}] {rec.action}")
```

#### export_report()

Export the report to a file.

```python
client.export_report(
    assessment_id: int,
    format: str = "json",
    output_path: str = None
) -> str
```

**Parameters**:
- `assessment_id`: Assessment ID
- `format`: Export format (json, csv, html, pdf)
- `output_path`: Path to save the file (optional)

**Returns**: File path or content string

**Example**:
```python
# Export to file
path = client.export_report(1, format="html", output_path="report.html")

# Get content as string
content = client.export_report(1, format="json")
```

## Data Classes

### Dataset

```python
@dataclass
class Dataset:
    id: int
    name: str
    file_type: str
    file_size: int
    file_path: str
    created_at: datetime
    metadata: dict
```

### Assessment

```python
@dataclass
class Assessment:
    id: int
    dataset_id: int
    status: str
    overall_score: float
    readiness_level: str
    module_scores: Dict[str, float]
    created_at: datetime
    completed_at: datetime
```

### Report

```python
@dataclass
class Report:
    id: int
    assessment_id: int
    overall_score: float
    readiness_level: str
    summary: dict
    module_scores: Dict[str, float]
    findings: List[Finding]
    recommendations: List[Recommendation]
    created_at: datetime
```

### Finding

```python
@dataclass
class Finding:
    id: int
    type: str
    severity: str  # critical, high, medium, low
    module: str
    description: str
    affected_columns: List[str]
    recommendation: str
```

### Recommendation

```python
@dataclass
class Recommendation:
    id: int
    priority: str  # critical, high, medium, low
    category: str
    issue: str
    action: str
    impact: str
    effort: str  # low, medium, high
```

## Error Handling

```python
from dataaptor import DataAptorClient
from dataaptor.exceptions import (
    DataAptorError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError
)

client = DataAptorClient()

try:
    dataset = client.get_dataset(999)
except NotFoundError as e:
    print(f"Dataset not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after} seconds")
except DataAptorError as e:
    print(f"API error: {e}")
```

## Async Support

```python
import asyncio
from dataaptor import AsyncDataAptorClient

async def main():
    client = AsyncDataAptorClient(api_url="http://localhost:8000")
    await client.login("user@example.com", "password")
    
    # Upload multiple datasets concurrently
    tasks = [
        client.upload(f"data_{i}.csv")
        for i in range(5)
    ]
    dataset_ids = await asyncio.gather(*tasks)
    
    # Assess all datasets
    assessments = await asyncio.gather(*[
        client.assess(ds_id, wait=True)
        for ds_id in dataset_ids
    ])
    
    for assessment in assessments:
        print(f"Dataset {assessment.dataset_id}: {assessment.overall_score}")

asyncio.run(main())
```

## See Also

- [API Gateway Documentation](api-gateway.md)
- [Authentication Guide](authentication.md)
- [JavaScript SDK](javascript-sdk.md)
