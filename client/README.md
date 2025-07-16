# DataAptor AI - Web UI

This is the React-based frontend for the DataAptor AI platform, providing an intuitive interface for assessing datasets for AI readiness.

## Features

- **Dashboard**: Overview of datasets and assessment results with visualizations
- **Upload**: Dataset submission with drag-and-drop and validation
- **Assessment**: Configuration and triggering of dataset assessments
- **Reports**: Detailed assessment results with interactive visualizations

## Tech Stack

- **React.js**: Frontend library for building the user interface
- **React Router**: For client-side routing
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Chart.js**: For data visualization
- **Axios**: For API communication

## Project Structure

```
client/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Alert.js     # Alert component for notifications
│   │   ├── Button.js    # Button component with variants
│   │   ├── Card.js      # Container component
│   │   ├── LoadingSpinner.js # Loading indicator
│   │   └── Navbar.js    # Navigation header
│   │
│   ├── pages/           # Page components
│   │   ├── Dashboard.js # Main dashboard view
│   │   ├── Upload.js    # Dataset upload interface
│   │   ├── Assessment.js # Assessment configuration
│   │   ├── Reports.js   # Detailed assessment results
│   │   └── NotFound.js  # 404 page
│   │
│   ├── services/        # API service modules
│   │   └── api.js       # Centralized API service
│   │
│   ├── utils/           # Utility functions
│   │   └── helpers.js   # Formatting and display utilities
│   │
│   ├── App.js           # Main application component
│   └── index.js         # Application entry point
│
├── package.json         # Dependencies and scripts
└── tailwind.config.js   # Tailwind CSS configuration
```

## Getting Started

1. **Install dependencies**:
   ```
   npm install
   ```

2. **Start development server**:
   ```
   npm start
   ```

3. **Build for production**:
   ```
   npm run build
   ```

## Development Guidelines

### Component Structure

Components should follow this structure:

```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const ComponentName = ({ prop1, prop2 }) => {
  // State and hooks
  const [state, setState] = useState(initialState);

  // Effects
  useEffect(() => {
    // Side effects
  }, [dependencies]);

  // Event handlers
  const handleEvent = () => {
    // Handle events
  };

  // Render
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};

ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
};

ComponentName.defaultProps = {
  prop2: 0,
};

export default ComponentName;
```

### API Communication

Use the centralized API service for all API calls:

```jsx
import { datasetService } from '../services/api';

// In a component
const fetchData = async () => {
  try {
    const response = await datasetService.getAllDatasets();
    setDatasets(response.data);
  } catch (error) {
    setError('Failed to fetch datasets');
  }
};
```

### Error Handling

Always implement proper error handling for API calls and async operations:

```jsx
try {
  // Async operation
} catch (error) {
  console.error('Error:', error);
  setError('User-friendly error message');
} finally {
  setLoading(false);
}
```

### Loading States

Include loading states for better user experience:

```jsx
const [loading, setLoading] = useState(false);

// Before async operation
setLoading(true);

// In JSX
{loading ? <LoadingSpinner /> : <Content />}
```

## Component Documentation

### Alert

```jsx
<Alert 
  type="success" // success, error, warning, info
  message="Operation completed successfully" 
  onClose={() => setShowAlert(false)} 
/>
```

### Button

```jsx
<Button 
  variant="primary" // primary, secondary, danger, success
  size="md" // sm, md, lg
  disabled={false}
  onClick={handleClick}
>
  Button Text
</Button>
```

### Card

```jsx
<Card 
  title="Card Title" 
  subtitle="Optional subtitle"
  footer={<FooterComponent />}
>
  Card content goes here
</Card>
```

### LoadingSpinner

```jsx
<LoadingSpinner 
  size="md" // sm, md, lg
  color="blue" // Any Tailwind color
/>
```

## Utility Functions

### formatBytes

```jsx
import { formatBytes } from '../utils/helpers';

// Usage
<p>File size: {formatBytes(1024)}</p> // Output: "1 KB"
```

### formatDate

```jsx
import { formatDate } from '../utils/helpers';

// Usage
<p>Created: {formatDate(new Date())}</p>
```

### formatScore

```jsx
import { formatScore } from '../utils/helpers';

// Usage
const { score, colorClass } = formatScore(85);
<p className={colorClass}>{score}</p> // Renders in green
```

## API Integration

The Web UI communicates with the backend API using the services defined in `api.js`. Each service group (datasets, assessments, users) provides methods for interacting with the corresponding API endpoints.

### Example Usage

```jsx
import { datasetService, assessmentService } from '../services/api';

// Upload a dataset
const handleUpload = async (formData) => {
  try {
    const response = await datasetService.uploadDataset(formData);
    return response.data;
  } catch (error) {
    throw new Error('Upload failed');
  }
};

// Start an assessment
const startAssessment = async (datasetId, config) => {
  try {
    const response = await assessmentService.startAssessment({
      dataset_id: datasetId,
      ...config
    });
    return response.data;
  } catch (error) {
    throw new Error('Assessment failed to start');
  }
};
```
