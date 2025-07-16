import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import Alert from '../components/Alert';
import Card from '../components/Card';
import Button from '../components/Button';
import { formatBytes, formatDate } from '../utils/helpers';
import { datasetService, assessmentService } from '../services/api';

const Assessment = () => {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [assessmentStatus, setAssessmentStatus] = useState('not_started');
  const [assessmentId, setAssessmentId] = useState(null);
  const [modules, setModules] = useState(['quality', 'accessibility']);
  const [selectedModules, setSelectedModules] = useState(['quality', 'accessibility']);
  const [progress, setProgress] = useState(0);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Fetch dataset details when component mounts
  useEffect(() => {
    const fetchDataset = async () => {
      try {
        setIsLoading(true);
        const response = await datasetService.getDatasetById(datasetId);
        setDataset(response.data);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching dataset:', err);
        setError('Failed to fetch dataset details. Please try again.');
        setIsLoading(false);
      }
    };

    fetchDataset();
  }, [datasetId]);

  // Function to start assessment
  const startAssessment = async () => {
    try {
      setAssessmentStatus('in_progress');
      // API call to start assessment
      const response = await assessmentService.startAssessment({
        dataset_id: datasetId,
        modules: selectedModules
      });
      
      setAssessmentId(response.data.assessment_id);
      
      // Start polling for assessment status
      const interval = setInterval(checkAssessmentStatus, 2000, response.data.assessment_id);
      setPollingInterval(interval);
    } catch (err) {
      console.error('Error starting assessment:', err);
      setError('Failed to start assessment. Please try again.');
      setAssessmentStatus('failed');
    }
  };

  // Function to check assessment status
  const checkAssessmentStatus = async (id) => {
    try {
      const response = await assessmentService.getAssessmentStatus(id);
      const status = response.data;
      
      // Update progress
      if (status.progress) {
        setProgress(status.progress.percentage || 0);
      }
      
      // Check if assessment is complete
      if (status.status === 'completed') {
        clearInterval(pollingInterval);
        setAssessmentStatus('completed');
        setAssessment(status);
      } else if (status.status === 'failed') {
        clearInterval(pollingInterval);
        setAssessmentStatus('failed');
        setError(status.error || 'Assessment failed for unknown reason');
      }
    } catch (err) {
      console.error('Error checking assessment status:', err);
      clearInterval(pollingInterval);
      setAssessmentStatus('failed');
      setError('Failed to check assessment status. Please try again.');
    }
  };

  // Function to handle module selection
  const handleModuleSelection = (module) => {
    if (selectedModules.includes(module)) {
      setSelectedModules(selectedModules.filter(m => m !== module));
    } else {
      setSelectedModules([...selectedModules, module]);
    }
  };

  // Function to view detailed report
  const viewReport = () => {
    navigate(`/reports/${datasetId}?assessmentId=${assessmentId}`);
  };

  // Clean up interval on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" message="Loading dataset details..." />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message={error} />;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Dataset Assessment</h1>
      
      {dataset && (
        <Card title="Dataset Details" className="mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Name</p>
              <p className="font-medium">{dataset.name}</p>
            </div>
            <div>
              <p className="text-gray-600">Type</p>
              <p className="font-medium">{dataset.file_type}</p>
            </div>
            <div>
              <p className="text-gray-600">Size</p>
              <p className="font-medium">{formatBytes(dataset.file_size)}</p>
            </div>
            <div>
              <p className="text-gray-600">Uploaded</p>
              <p className="font-medium">{formatDate(dataset.created_at)}</p>
            </div>
          </div>
        </Card>
      )}

      {assessmentStatus === 'not_started' && (
        <Card title="Assessment Configuration" className="mb-6">
          <div className="mb-4">
            <p className="text-gray-600 mb-2">Select Assessment Modules:</p>
            <div className="flex flex-wrap gap-2">
              {modules.map(module => (
                <div
                  key={module}
                  className={`px-4 py-2 rounded-full cursor-pointer text-sm ${
                    selectedModules.includes(module)
                      ? 'bg-primary-100 text-primary-800 border border-primary-300'
                      : 'bg-gray-100 text-gray-800 border border-gray-300'
                  }`}
                  onClick={() => handleModuleSelection(module)}
                >
                  {module.charAt(0).toUpperCase() + module.slice(1)}
                </div>
              ))}
            </div>
          </div>
          <Button 
            onClick={startAssessment}
            disabled={selectedModules.length === 0}
            variant="primary"
          >
            Start Assessment
          </Button>
        </Card>
      )}

      {assessmentStatus === 'in_progress' && (
        <Card title="Assessment in Progress" className="mb-6">
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-right text-sm text-gray-600 mt-1">{progress.toFixed(1)}%</p>
          </div>
          <p className="text-gray-600">Please wait while we assess your dataset. This may take a few minutes.</p>
        </Card>
      )}

      {assessmentStatus === 'completed' && assessment && (
        <Card title="Assessment Complete" className="mb-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600">Overall Score:</span>
              <span className="text-2xl font-bold text-primary-600">
                {assessment.overall_score ? `${assessment.overall_score}/100` : 'N/A'}
              </span>
            </div>

            {assessment.module_scores && (
              <div className="mt-4">
                <h3 className="text-lg font-medium mb-2">Module Scores</h3>
                <div className="space-y-2">
                  {assessment.module_scores.map(module => (
                    <div key={module.name} className="flex items-center">
                      <div className="w-32 text-gray-600">
                        {module.name.charAt(0).toUpperCase() + module.name.slice(1)}:
                      </div>
                      <div className="flex-1">
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div
                            className="bg-primary-600 h-2.5 rounded-full"
                            style={{ width: `${module.score}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-16 text-right font-medium">{module.score}/100</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="flex justify-end">
            <Button
              onClick={viewReport}
              variant="primary"
            >
              View Detailed Report
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Assessment;
