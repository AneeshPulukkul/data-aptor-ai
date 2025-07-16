# MVP Development Guide

This guide outlines the specific steps for implementing the Phase 1 MVP of DataAptor AI. It provides detailed technical guidance and implementation priorities for developers.

## MVP Scope

The MVP will focus on:

1. Core assessment capabilities for structured data (CSV, JSON)
2. Basic Web UI and CLI interface
3. Fundamental scoring and reporting
4. Local deployment capability

## Service Implementation Priorities

### 1. Ingestion Service

#### Priority Features
- CSV and JSON file parsing
- Basic validation (file integrity, format correctness)
- Metadata extraction (column types, statistics)
- Storage of datasets in temporary storage

#### Implementation Steps
1. Create file upload endpoint in FastAPI
2. Implement parsers for CSV using pandas
3. Implement parsers for JSON using Python's json module
4. Add validation rules for file structure
5. Develop metadata extraction functions
6. Connect to S3 (MinIO) for temporary storage

#### Technical Requirements
```python
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
pandas==2.0.1
python-multipart==0.0.6
boto3==1.26.129
pydantic==1.10.7
```

### 2. Assessment Service - Data Quality Module

#### Priority Features
- Completeness assessment (missing values)
- Accuracy assessment (outlier detection, type consistency)
- Consistency assessment (format uniformity)
- Timeliness assessment (if timestamp data available)

#### Implementation Steps
1. Create assessment API endpoints in FastAPI
2. Implement completeness checking algorithm
3. Develop basic accuracy validation
4. Build consistency evaluation logic
5. Add timeliness assessment for datasets with time components
6. Store assessment results in PostgreSQL

#### Technical Requirements
```python
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
pandas==2.0.1
numpy==1.24.3
scikit-learn==1.2.2
sqlalchemy==2.0.12
psycopg2-binary==2.9.6
pydantic==1.10.7
```

### 3. Assessment Service - Accessibility Module

#### Priority Features
- Availability assessment (format compatibility)
- Volume assessment (sample size adequacy)

#### Implementation Steps
1. Create accessibility API endpoints
2. Implement format compatibility checking
3. Develop sample size evaluation logic
4. Store assessment results in PostgreSQL

### 4. Scoring Service

#### Priority Features
- Weight-based scoring algorithm
- Default weights for assessment criteria
- Custom weight configuration
- Overall readiness score calculation

#### Implementation Steps
1. Create scoring API endpoints
2. Implement weighted scoring algorithm
3. Add support for custom weights
4. Develop overall score calculation
5. Store scoring results in PostgreSQL

#### Technical Requirements
```python
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
numpy==1.24.3
sqlalchemy==2.0.12
psycopg2-binary==2.9.6
pydantic==1.10.7
```

### 5. Reporting Service

#### Priority Features
- Score breakdown report
- Basic visualizations (bar charts, pie charts)
- Actionable recommendations
- Report export (JSON format)

#### Implementation Steps
1. Create reporting API endpoints
2. Implement report generation logic
3. Develop basic visualization generator
4. Add recommendation engine based on scores
5. Create JSON export functionality
6. Store reports in PostgreSQL and S3

#### Technical Requirements
```python
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
matplotlib==3.7.1
jinja2==3.1.2
sqlalchemy==2.0.12
psycopg2-binary==2.9.6
boto3==1.26.129
pydantic==1.10.7
```

### 6. API Gateway

#### Priority Features
- Service routing
- Basic authentication
- Request validation
- Error handling

#### Implementation Steps
1. Create gateway API endpoints
2. Implement routing to appropriate services
3. Add basic authentication (API key)
4. Develop request validation
5. Implement unified error handling

#### Technical Requirements
```python
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
httpx==0.24.0
python-jose==3.3.0
pydantic==1.10.7
```

### 7. Web UI

#### Priority Features
- Dataset upload interface
- Assessment configuration
- Results dashboard
- Basic visualizations

#### Implementation Steps
1. Create React application structure
2. Implement upload component
3. Develop configuration form
4. Build results dashboard with visualizations
5. Add API integration

#### Technical Requirements
```json
// package.json dependencies
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.11.1",
    "axios": "^1.4.0",
    "chart.js": "^4.3.0",
    "react-chartjs-2": "^5.2.0",
    "tailwindcss": "^3.3.2"
  }
}
```

### 8. CLI Tool

#### Priority Features
- Dataset upload command
- Assessment trigger command
- Results display
- Report export

#### Implementation Steps
1. Create CLI structure with Click
2. Implement upload command
3. Add assessment trigger command
4. Develop results display logic
5. Implement report export functionality

#### Technical Requirements
```python
# requirements.txt
click==8.1.3
requests==2.29.0
tabulate==0.9.0
rich==13.3.5
```

## Database Schema

### Core Tables

#### datasets
```sql
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

#### assessments
```sql
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    module VARCHAR(50) NOT NULL,
    criterion VARCHAR(50) NOT NULL,
    score NUMERIC(3,1) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### scores
```sql
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    total_score NUMERIC(5,2) NOT NULL,
    quality_score NUMERIC(5,2),
    accessibility_score NUMERIC(5,2),
    weights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### reports
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    score_id INTEGER REFERENCES scores(id),
    report_path VARCHAR(512),
    visualizations JSONB,
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Contracts

### Ingestion Service

```
POST /api/ingestion/upload
- Accepts multipart/form-data with file
- Returns dataset metadata and ID

GET /api/ingestion/datasets/{dataset_id}
- Returns dataset details
```

### Assessment Service

```
POST /api/assessment/quality/{dataset_id}
- Triggers quality assessment
- Returns assessment results

POST /api/assessment/accessibility/{dataset_id}
- Triggers accessibility assessment
- Returns assessment results
```

### Scoring Service

```
POST /api/scoring/{dataset_id}
- Accepts optional weights JSON
- Returns calculated scores
```

### Reporting Service

```
POST /api/reporting/{dataset_id}
- Generates report for dataset
- Returns report details and visualizations
```

## Development Milestones

### Week 1-2: Foundation
- Set up development environment
- Initialize service skeletons
- Create database schema

### Week 3-4: Core Services
- Implement basic Ingestion Service
- Develop Data Quality Module
- Create database connectors

### Week 5-6: Scoring & Reporting
- Implement Scoring Service
- Develop basic Reporting Service
- Create simple visualizations

### Week 7-8: API & Integration
- Implement API Gateway
- Integrate services
- Add basic authentication

### Week 9-10: Frontend
- Develop basic Web UI
- Implement CLI tool
- Integrate with backend services

### Week 11-12: Testing & Refinement
- Write unit and integration tests
- Fix bugs and issues
- Improve performance

## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Achieve >80% code coverage

### Integration Tests
- Test service interactions
- Verify database operations
- Validate workflow sequences

### End-to-End Tests
- Test complete assessment process
- Verify UI functionality
- Validate report generation

## Initial Development Tasks

For the first sprint, focus on:

1. Setting up the development environment
2. Implementing basic CSV file ingestion
3. Creating simple data quality assessment
4. Setting up the database schema
5. Building a minimal API for testing

This will establish the foundation for the MVP and allow for early testing of core functionality.
