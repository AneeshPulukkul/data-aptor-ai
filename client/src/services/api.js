import axios from 'axios';
import mockDatasets from '../mocks/datasets.json';
import mockAssessments from '../mocks/assessments.json';

// Get API base URL from environment variable or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const isDevelopment = process.env.NODE_ENV === 'development';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage if it exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error status codes
    if (error.response) {
      const { status } = error.response;
      
      // Unauthorized - clear localStorage and redirect to login
      if (status === 401) {
        localStorage.removeItem('token');
        // Redirect logic can be added here
      }
      
      // Service unavailable - server might be down
      if (status === 503) {
        console.error('Service unavailable. Please try again later.');
      }
    }
    
    return Promise.reject(error);
  }
);

// Dataset services
const datasetService = {
  // Get all datasets
  getAllDatasets: () => {
    if (isDevelopment) {
      return Promise.resolve({ data: mockDatasets });
    }
    return api.get('/ingestion/datasets');
  },
  
  // Get dataset by ID
  getDatasetById: (id) => {
    if (isDevelopment) {
      const dataset = mockDatasets.find(d => d.id === parseInt(id));
      return Promise.resolve({ data: dataset });
    }
    return api.get(`/ingestion/datasets/${id}`);
  },
  
  // Upload new dataset
  uploadDataset: (formData) => {
    if (isDevelopment) {
      // Simulate upload delay
      return new Promise(resolve => {
        setTimeout(() => {
          const newDataset = {
            id: mockDatasets.length + 1,
            name: formData.get('name') || 'New Dataset',
            file_type: 'CSV',
            file_size: Math.floor(Math.random() * 10000000),
            created_at: new Date().toISOString(),
            metadata: {
              rows: Math.floor(Math.random() * 10000),
              columns: Math.floor(Math.random() * 20),
              has_header: true
            }
          };
          resolve({ data: newDataset });
        }, 1500);
      });
    }
    return api.post('/ingestion/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // Delete dataset
  deleteDataset: (id) => {
    if (isDevelopment) {
      return Promise.resolve({ data: { success: true }});
    }
    return api.delete(`/ingestion/datasets/${id}`);
  }
};

// Assessment services
const assessmentService = {
  // Trigger assessment
  startAssessment: (data) => {
    if (isDevelopment) {
      return new Promise(resolve => {
        setTimeout(() => {
          const newAssessment = {
            id: mockAssessments.length + 1,
            dataset_id: data.dataset_id,
            module: data.module || 'quality',
            created_at: new Date().toISOString(),
            status: 'in_progress'
          };
          resolve({ data: newAssessment });
        }, 1000);
      });
    }
    return api.post('/assessment/trigger', data);
  },
  
  // Get assessment status
  getAssessmentStatus: (id) => {
    if (isDevelopment) {
      const assessment = mockAssessments.find(a => a.id === parseInt(id));
      if (assessment) {
        return Promise.resolve({ data: assessment });
      }
      return Promise.reject(new Error('Assessment not found'));
    }
    return api.get(`/assessment/status/${id}`);
  },
  
  // Get assessment report
  getAssessmentReport: (id) => {
    if (isDevelopment) {
      const assessment = mockAssessments.find(a => a.id === parseInt(id));
      if (!assessment) {
        return Promise.reject(new Error('Assessment not found'));
      }
      
      // Simulate a full report with more details
      const report = {
        ...assessment,
        recommendations: [
          "Consider cleaning missing values in the dataset",
          "Address outliers in numeric columns",
          "Standardize date formats across the dataset"
        ],
        impact_analysis: {
          training_impact: "Medium",
          inference_impact: "Low",
          bias_potential: "Low to Medium"
        }
      };
      
      return Promise.resolve({ data: report });
    }
    return api.get(`/assessment/report/${id}`);
  },
  
  // Get assessments for a dataset
  getDatasetAssessments: (datasetId) => {
    if (isDevelopment) {
      const filteredAssessments = mockAssessments.filter(
        a => a.dataset_id === parseInt(datasetId)
      );
      return Promise.resolve({ data: filteredAssessments });
    }
    return api.get(`/assessment/dataset/${datasetId}`);
  },
  
  // Export assessment report
  exportReport: (id, format = 'pdf') => {
    if (isDevelopment) {
      return Promise.resolve({ 
        data: new Blob(['Mock PDF data'], { type: 'application/pdf' }),
        headers: { 'content-disposition': `attachment; filename="assessment-${id}.${format}"` }
      });
    }
    return api.get(`/assessment/export/${id}?format=${format}`, {
      responseType: 'blob'
    });
  }
};

// User services (for future authentication)
const userService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => {
    localStorage.removeItem('token');
    return Promise.resolve();
  }
};

export {
  api as default,
  datasetService,
  assessmentService,
  userService
};
