import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const [datasets, setDatasets] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch datasets and assessments
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch datasets
        const datasetsResponse = await axios.get('http://localhost:8000/api/ingestion/datasets');
        setDatasets(datasetsResponse.data);

        // Fetch assessments (mock data for now)
        // In a real implementation, you'd fetch from the API
        setAssessments([
          { id: 1, dataset_id: 1, module: 'quality', total_score: 85 },
          { id: 2, dataset_id: 2, module: 'quality', total_score: 72 },
          { id: 3, dataset_id: 3, module: 'quality', total_score: 93 },
          { id: 4, dataset_id: 1, module: 'accessibility', total_score: 78 },
          { id: 5, dataset_id: 2, module: 'accessibility', total_score: 65 },
          { id: 6, dataset_id: 3, module: 'accessibility', total_score: 88 },
        ]);

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data
  const barChartData = {
    labels: datasets.map(dataset => dataset.name),
    datasets: [
      {
        label: 'Quality Score',
        data: datasets.map(dataset => {
          const assessment = assessments.find(
            a => a.dataset_id === dataset.id && a.module === 'quality'
          );
          return assessment ? assessment.total_score : 0;
        }),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Accessibility Score',
        data: datasets.map(dataset => {
          const assessment = assessments.find(
            a => a.dataset_id === dataset.id && a.module === 'accessibility'
          );
          return assessment ? assessment.total_score : 0;
        }),
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
      },
    ],
  };

  const pieChartData = {
    labels: ['High Readiness', 'Medium Readiness', 'Low Readiness'],
    datasets: [
      {
        data: [
          assessments.filter(a => a.total_score >= 80).length,
          assessments.filter(a => a.total_score >= 60 && a.total_score < 80).length,
          assessments.filter(a => a.total_score < 60).length,
        ],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 99, 132, 0.6)',
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">AI Readiness Dashboard</h1>

      {datasets.length === 0 ? (
        <div className="card mb-6">
          <p>No datasets have been uploaded yet. Go to the Upload page to get started.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="card">
              <h2 className="text-lg font-semibold mb-2">Total Datasets</h2>
              <p className="text-4xl font-bold text-primary-600">{datasets.length}</p>
            </div>
            <div className="card">
              <h2 className="text-lg font-semibold mb-2">Assessed Datasets</h2>
              <p className="text-4xl font-bold text-secondary-600">
                {new Set(assessments.map(a => a.dataset_id)).size}
              </p>
            </div>
            <div className="card">
              <h2 className="text-lg font-semibold mb-2">Average Readiness</h2>
              <p className="text-4xl font-bold text-green-600">
                {assessments.length > 0
                  ? Math.round(
                      assessments.reduce((acc, curr) => acc + curr.total_score, 0) / assessments.length
                    )
                  : 0}
                %
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">Dataset Scores</h2>
              <div className="h-80">
                <Bar data={barChartData} options={{ maintainAspectRatio: false }} />
              </div>
            </div>
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">Readiness Distribution</h2>
              <div className="h-80 flex justify-center items-center">
                <Pie data={pieChartData} options={{ maintainAspectRatio: false }} />
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Recent Datasets</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Uploaded
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {datasets.slice(0, 5).map(dataset => (
                    <tr key={dataset.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{dataset.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{dataset.file_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {Math.round(dataset.file_size / 1024)} KB
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {new Date(dataset.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <a
                          href={`/assessment/${dataset.id}`}
                          className="text-primary-600 hover:text-primary-900 mr-3"
                        >
                          Assess
                        </a>
                        <a
                          href={`/reports/${dataset.id}`}
                          className="text-secondary-600 hover:text-secondary-900"
                        >
                          Report
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
