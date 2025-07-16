import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { 
  Chart as ChartJS, 
  RadialLinearScale, 
  PointElement, 
  LineElement, 
  Filler, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ArcElement
} from 'chart.js';
import { Radar, Bar, Pie } from 'react-chartjs-2';
import LoadingSpinner from '../components/LoadingSpinner';
import Alert from '../components/Alert';
import Card from '../components/Card';
import Button from '../components/Button';
import { formatBytes, formatDate, formatScore } from '../utils/helpers';
import { datasetService, assessmentService } from '../services/api';

// Register ChartJS components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ArcElement
);

// Helper function to get URL parameters
function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const Reports = () => {
  const { datasetId } = useParams();
  const query = useQuery();
  const navigate = useNavigate();
  const assessmentId = query.get('assessmentId');
  const [dataset, setDataset] = useState(null);
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [exportFormat, setExportFormat] = useState('pdf');
  const [exportInProgress, setExportInProgress] = useState(false);

  // Fetch report data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch dataset details
        const datasetResponse = await datasetService.getDatasetById(datasetId);
        setDataset(datasetResponse.data);
        
        // Fetch report data
        const reportResponse = await assessmentService.getAssessmentReport(assessmentId);
        setReport(reportResponse.data);
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching report data:', err);
        setError('Failed to fetch report data. Please try again.');
        setIsLoading(false);
      }
    };

    if (datasetId && assessmentId) {
      fetchData();
    } else {
      setError('Missing dataset ID or assessment ID');
      setIsLoading(false);
    }
  }, [datasetId, assessmentId]);

  // Export report
  const exportReport = async () => {
    try {
      setExportInProgress(true);
      
      // Call export API
      const response = await assessmentService.exportReport(assessmentId, exportFormat);
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${assessmentId}.${exportFormat}`);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      setExportInProgress(false);
    } catch (err) {
      console.error('Error exporting report:', err);
      setError('Failed to export report. Please try again.');
      setExportInProgress(false);
    }
  };

  // Prepare chart data
  const prepareRadarData = () => {
    if (!report || !report.module_scores) return null;
    
    return {
      labels: report.module_scores.map(m => m.name.charAt(0).toUpperCase() + m.name.slice(1)),
      datasets: [
        {
          label: 'Module Scores',
          data: report.module_scores.map(m => m.score),
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
        }
      ]
    };
  };

  const prepareBarData = () => {
    if (!report || !report.criteria_scores) return null;
    
    return {
      labels: report.criteria_scores.map(c => c.name.charAt(0).toUpperCase() + c.name.slice(1)),
      datasets: [
        {
          label: 'Criteria Scores',
          data: report.criteria_scores.map(c => c.score),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }
      ]
    };
  };

  const preparePieData = () => {
    if (!report || !report.module_scores) return null;
    
    return {
      labels: report.module_scores.map(m => m.name.charAt(0).toUpperCase() + m.name.slice(1)),
      datasets: [
        {
          label: 'Score Distribution',
          data: report.module_scores.map(m => m.score),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
          ],
          borderWidth: 1
        }
      ]
    };
  };

  // Chart options
  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20
        }
      }
    }
  };

  const barOptions = {
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" message="Loading report data..." />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message={error} />;
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Assessment Report</h1>
        <div className="flex items-center space-x-2">
          <select
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
          >
            <option value="pdf">PDF</option>
            <option value="html">HTML</option>
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
          </select>
          <Button
            onClick={exportReport}
            disabled={exportInProgress}
            variant="primary"
          >
            {exportInProgress ? 'Exporting...' : 'Export Report'}
          </Button>
        </div>
      </div>

      {dataset && report && (
        <>
          <Card className="mb-6">
            <div className="flex justify-between">
              <div>
                <h2 className="text-xl font-semibold mb-2">{dataset.name}</h2>
                <p className="text-gray-600">
                  Type: {dataset.file_type.toUpperCase()} | Size: {formatBytes(dataset.file_size)} | 
                  Date: {formatDate(report.created_at)}
                </p>
              </div>
              <div className="text-center">
                <div className={`text-5xl font-bold ${formatScore(report.overall_score).colorClass}`}>
                  {report.overall_score}
                </div>
                <div className="text-gray-600">Overall Score</div>
              </div>
            </div>
          </Card>

          <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                <button
                  className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                    activeTab === 'overview'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveTab('overview')}
                >
                  Overview
                </button>
                <button
                  className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                    activeTab === 'details'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveTab('details')}
                >
                  Detailed Scores
                </button>
                <button
                  className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                    activeTab === 'recommendations'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveTab('recommendations')}
                >
                  Recommendations
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Score Distribution</h3>
                    <div className="h-80">
                      {prepareRadarData() && <Radar data={prepareRadarData()} options={radarOptions} />}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-4">Module Contribution</h3>
                    <div className="h-80">
                      {preparePieData() && <Pie data={preparePieData()} />}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'details' && (
                <div>
                  <h3 className="text-lg font-medium mb-4">Criteria Scores</h3>
                  <div className="h-96">
                    {prepareBarData() && <Bar data={prepareBarData()} options={barOptions} />}
                  </div>
                  {report.module_scores && (
                    <div className="mt-8">
                      <h3 className="text-lg font-medium mb-4">Module Breakdown</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {report.module_scores.map(module => (
                          <div key={module.name} className="bg-gray-50 p-4 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                              <h4 className="font-medium text-gray-800">
                                {module.name.charAt(0).toUpperCase() + module.name.slice(1)}
                              </h4>
                              <span className="text-lg font-bold text-primary-600">{module.score}/100</span>
                            </div>
                            <p className="text-sm text-gray-600">{module.description || 'No description available'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'recommendations' && (
                <div>
                  <h3 className="text-lg font-medium mb-4">Improvement Recommendations</h3>
                  {report.recommendations && report.recommendations.length > 0 ? (
                    <ul className="space-y-4">
                      {report.recommendations.map((recommendation, index) => (
                        <li key={index} className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                          <div className="flex">
                            <div className="flex-shrink-0">
                              <svg className="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                              </svg>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm text-blue-800">{recommendation}</p>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-600">No recommendations available for this assessment.</p>
                  )}

                  {report.findings && report.findings.length > 0 && (
                    <div className="mt-8">
                      <h3 className="text-lg font-medium mb-4">Key Findings</h3>
                      <ul className="space-y-4">
                        {report.findings.map((finding, index) => (
                          <li key={index} className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                            <div className="flex">
                              <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                              </div>
                              <div className="ml-3">
                                <p className="text-sm text-yellow-800">{finding}</p>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => navigate(`/assessment/${datasetId}`)}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Back to Assessment
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Return to Dashboard
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Reports;
