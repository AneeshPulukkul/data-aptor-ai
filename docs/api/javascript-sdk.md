# JavaScript SDK

The DataAptor JavaScript SDK provides a convenient way to interact with the DataAptor AI API from JavaScript and TypeScript applications.

## Installation

```bash
npm install dataaptor-client
```

Or with yarn:

```bash
yarn add dataaptor-client
```

## Quick Start

```javascript
import { DataAptorClient } from 'dataaptor-client';

// Initialize client
const client = new DataAptorClient({
  apiUrl: 'http://localhost:8000'
});

// Login
await client.login('user@example.com', 'password');

// Upload a dataset
const datasetId = await client.upload('./data.csv');

// Run assessment
const assessment = await client.assess(datasetId, { wait: true });

// View results
console.log(`Score: ${assessment.overallScore}`);
console.log(`Level: ${assessment.readinessLevel}`);
```

## TypeScript Support

The SDK is written in TypeScript and includes full type definitions:

```typescript
import { 
  DataAptorClient, 
  Dataset, 
  Assessment, 
  Report,
  AssessmentOptions 
} from 'dataaptor-client';

const client = new DataAptorClient({
  apiUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

const options: AssessmentOptions = {
  modules: ['quality', 'accessibility'],
  weights: { quality: 0.6, accessibility: 0.4 },
  wait: true
};

const assessment: Assessment = await client.assess(1, options);
```

## Client Configuration

### Constructor Options

```typescript
interface ClientOptions {
  apiUrl: string;
  apiKey?: string;
  timeout?: number;  // Default: 30000ms
  retries?: number;  // Default: 3
}

const client = new DataAptorClient({
  apiUrl: 'http://localhost:8000',
  apiKey: 'your-api-key',
  timeout: 60000,
  retries: 5
});
```

### Environment Variables

```javascript
// Uses DATAAPTOR_API_URL and DATAAPTOR_API_KEY
const client = new DataAptorClient();
```

## API Reference

### Authentication

#### login()

Authenticate with username and password.

```typescript
async login(username: string, password: string): Promise<TokenResponse>
```

**Example**:
```javascript
const token = await client.login('user@example.com', 'password');
console.log(`Token expires in: ${token.expiresIn} seconds`);
```

#### refreshToken()

Refresh the current authentication token.

```typescript
async refreshToken(): Promise<TokenResponse>
```

### Dataset Methods

#### upload()

Upload a dataset file.

```typescript
async upload(
  file: string | File | Buffer,
  options?: UploadOptions
): Promise<number>

interface UploadOptions {
  name?: string;
  metadata?: Record<string, any>;
  onProgress?: (progress: number) => void;
}
```

**Examples**:

```javascript
// Node.js - from file path
const datasetId = await client.upload('./data.csv', {
  name: 'Customer Data'
});

// Browser - from File object
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];
const datasetId = await client.upload(file, {
  onProgress: (progress) => console.log(`${progress}% uploaded`)
});

// From Buffer
const buffer = fs.readFileSync('./data.csv');
const datasetId = await client.upload(buffer, {
  name: 'data.csv'
});
```

#### listDatasets()

List all datasets.

```typescript
async listDatasets(options?: ListOptions): Promise<DatasetList>

interface ListOptions {
  skip?: number;
  limit?: number;
}
```

**Example**:
```javascript
const { datasets, total } = await client.listDatasets({ limit: 50 });
datasets.forEach(ds => {
  console.log(`${ds.id}: ${ds.name} (${ds.fileType})`);
});
```

#### getDataset()

Get details of a specific dataset.

```typescript
async getDataset(datasetId: number): Promise<Dataset>
```

#### deleteDataset()

Delete a dataset.

```typescript
async deleteDataset(datasetId: number): Promise<boolean>
```

### Assessment Methods

#### assess()

Start an assessment for a dataset.

```typescript
async assess(
  datasetId: number,
  options?: AssessmentOptions
): Promise<Assessment>

interface AssessmentOptions {
  modules?: string[];
  weights?: Record<string, number>;
  wait?: boolean;
  pollInterval?: number;  // Default: 5000ms
  timeout?: number;       // Default: 300000ms
}
```

**Example**:
```javascript
const assessment = await client.assess(1, {
  modules: ['quality', 'accessibility', 'governance'],
  weights: {
    quality: 0.5,
    accessibility: 0.3,
    governance: 0.2
  },
  wait: true
});

console.log(`Score: ${assessment.overallScore}`);
console.log(`Level: ${assessment.readinessLevel}`);
```

#### getAssessmentStatus()

Check the status of an assessment.

```typescript
async getAssessmentStatus(assessmentId: number): Promise<AssessmentStatus>
```

**Example**:
```javascript
const status = await client.getAssessmentStatus(1);
console.log(`Status: ${status.status}`);
console.log(`Progress: ${status.progress}%`);
```

#### waitForAssessment()

Wait for an assessment to complete.

```typescript
async waitForAssessment(
  assessmentId: number,
  options?: WaitOptions
): Promise<Assessment>

interface WaitOptions {
  timeout?: number;
  pollInterval?: number;
  onProgress?: (status: AssessmentStatus) => void;
}
```

**Example**:
```javascript
const assessment = await client.waitForAssessment(1, {
  timeout: 600000,
  onProgress: (status) => {
    console.log(`${status.progress}% - ${status.currentModule}`);
  }
});
```

### Report Methods

#### getReport()

Get the assessment report.

```typescript
async getReport(assessmentId: number): Promise<Report>
```

**Example**:
```javascript
const report = await client.getReport(1);

console.log(`Overall Score: ${report.overallScore}`);
console.log(`Readiness Level: ${report.readinessLevel}`);

report.findings.forEach(finding => {
  console.log(`[${finding.severity}] ${finding.description}`);
});

report.recommendations.forEach(rec => {
  console.log(`[${rec.priority}] ${rec.action}`);
});
```

#### exportReport()

Export the report.

```typescript
async exportReport(
  assessmentId: number,
  format: 'json' | 'csv' | 'html' | 'pdf'
): Promise<string | Blob>
```

**Examples**:

```javascript
// Get as string (JSON, CSV, HTML)
const htmlContent = await client.exportReport(1, 'html');

// Get as Blob (PDF)
const pdfBlob = await client.exportReport(1, 'pdf');

// Download in browser
const url = URL.createObjectURL(pdfBlob);
const a = document.createElement('a');
a.href = url;
a.download = 'report.pdf';
a.click();

// Save in Node.js
const fs = require('fs');
const buffer = await pdfBlob.arrayBuffer();
fs.writeFileSync('report.pdf', Buffer.from(buffer));
```

## Type Definitions

### Dataset

```typescript
interface Dataset {
  id: number;
  name: string;
  fileType: string;
  fileSize: number;
  filePath: string;
  createdAt: Date;
  metadata: Record<string, any>;
}
```

### Assessment

```typescript
interface Assessment {
  id: number;
  datasetId: number;
  status: 'pending' | 'assessing' | 'completed' | 'failed';
  overallScore: number;
  readinessLevel: 'high' | 'moderate' | 'low' | 'not_ready';
  moduleScores: Record<string, number>;
  createdAt: Date;
  completedAt: Date | null;
}
```

### Report

```typescript
interface Report {
  id: number;
  assessmentId: number;
  overallScore: number;
  readinessLevel: string;
  summary: ReportSummary;
  moduleScores: Record<string, number>;
  findings: Finding[];
  recommendations: Recommendation[];
  createdAt: Date;
}

interface ReportSummary {
  totalCriteriaAssessed: number;
  criteriaPassed: number;
  criteriaWarning: number;
  criteriaFailed: number;
  keyStrengths: string[];
  keyIssues: string[];
}
```

### Finding

```typescript
interface Finding {
  id: number;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  module: string;
  description: string;
  affectedColumns: string[];
  recommendation: string;
}
```

### Recommendation

```typescript
interface Recommendation {
  id: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  issue: string;
  action: string;
  impact: string;
  effort: 'low' | 'medium' | 'high';
}
```

## Error Handling

```typescript
import { 
  DataAptorClient,
  DataAptorError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError
} from 'dataaptor-client';

const client = new DataAptorClient({ apiUrl: 'http://localhost:8000' });

try {
  const dataset = await client.getDataset(999);
} catch (error) {
  if (error instanceof NotFoundError) {
    console.log(`Dataset not found: ${error.message}`);
  } else if (error instanceof AuthenticationError) {
    console.log(`Authentication failed: ${error.message}`);
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limit exceeded. Retry after: ${error.retryAfter} seconds`);
  } else if (error instanceof DataAptorError) {
    console.log(`API error: ${error.message}`);
  }
}
```

## React Integration

```jsx
import React, { useState, useEffect } from 'react';
import { DataAptorClient } from 'dataaptor-client';

const client = new DataAptorClient({
  apiUrl: process.env.REACT_APP_API_URL
});

function DatasetAssessment({ datasetId }) {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function runAssessment() {
      try {
        setLoading(true);
        const result = await client.assess(datasetId, { wait: true });
        setAssessment(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    runAssessment();
  }, [datasetId]);

  if (loading) return <div>Assessing dataset...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Assessment Results</h2>
      <p>Score: {assessment.overallScore}</p>
      <p>Level: {assessment.readinessLevel}</p>
    </div>
  );
}
```

## Node.js Integration

```javascript
const { DataAptorClient } = require('dataaptor-client');
const fs = require('fs');

async function assessDataset(filePath) {
  const client = new DataAptorClient({
    apiUrl: process.env.DATAAPTOR_API_URL,
    apiKey: process.env.DATAAPTOR_API_KEY
  });

  // Upload dataset
  const datasetId = await client.upload(filePath);
  console.log(`Uploaded dataset: ${datasetId}`);

  // Run assessment
  const assessment = await client.assess(datasetId, { wait: true });
  console.log(`Score: ${assessment.overallScore}`);

  // Export report
  const report = await client.exportReport(assessment.id, 'json');
  fs.writeFileSync('report.json', report);

  return assessment;
}

assessDataset('./data.csv').catch(console.error);
```

## See Also

- [API Gateway Documentation](api-gateway.md)
- [Authentication Guide](authentication.md)
- [Python SDK](python-sdk.md)
