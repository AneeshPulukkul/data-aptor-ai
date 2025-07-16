import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setFileName(droppedFile.name);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    // Check file type
    const fileExt = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'json', 'txt'].includes(fileExt)) {
      setError('Unsupported file type. Please upload CSV, JSON, or TXT files.');
      return;
    }

    // Check file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
      setError('File size exceeds 100MB limit.');
      return;
    }

    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/ingestion/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });

      // After successful upload, navigate to assessment page
      navigate(`/assessment/${response.data.id}`);
    } catch (err) {
      console.error('Upload error:', err);
      setError(
        err.response?.data?.detail || 'An error occurred during upload. Please try again.'
      );
      setUploading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Upload Dataset</h1>

      <div className="card max-w-2xl mx-auto">
        <form onSubmit={handleSubmit}>
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 mb-6 text-center cursor-pointer hover:border-primary-500 transition-colors"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <input
              id="fileInput"
              type="file"
              className="hidden"
              onChange={handleFileChange}
              accept=".csv,.json,.txt"
            />
            <div className="mb-4">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                ></path>
              </svg>
            </div>
            <p className="text-sm text-gray-600 mb-1">
              {fileName ? (
                <span className="font-medium text-primary-600">{fileName}</span>
              ) : (
                <>
                  <span className="font-medium">Click to upload</span> or drag and drop
                </>
              )}
            </p>
            <p className="text-xs text-gray-500">CSV, JSON, or TXT (max 100MB)</p>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {uploading && (
            <div className="mb-6">
              <div className="h-2 bg-gray-200 rounded-full mb-2">
                <div
                  className="h-full bg-primary-600 rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 text-center">{progress}% uploaded</p>
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={uploading || !file}
            >
              {uploading ? 'Uploading...' : 'Upload Dataset'}
            </button>
          </div>
        </form>
      </div>

      <div className="card max-w-2xl mx-auto mt-8">
        <h2 className="text-lg font-semibold mb-4">Supported Formats</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border rounded-lg">
            <div className="flex items-center mb-2">
              <svg className="h-6 w-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 className="font-medium">CSV</h3>
            </div>
            <p className="text-sm text-gray-600">
              Comma-separated values with header row
            </p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center mb-2">
              <svg className="h-6 w-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 className="font-medium">JSON</h3>
            </div>
            <p className="text-sm text-gray-600">
              Array of objects or single object
            </p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center mb-2">
              <svg className="h-6 w-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 className="font-medium">TXT</h3>
            </div>
            <p className="text-sm text-gray-600">
              Plain text files with line breaks
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
