"""
DataAptor AI CLI - API Client module

This module provides a client for interacting with the DataAptor AI API.
"""

import requests
import os
import json
from pathlib import Path


class DataAptorClient:
    """Client for interacting with the DataAptor AI API"""
    
    def __init__(self, api_url=None):
        """Initialize the client with the API URL"""
        self.api_url = api_url or os.environ.get("DATAAPTOR_API_URL", "http://localhost:8000")
    
    def upload_dataset(self, file_path):
        """Upload a dataset file for assessment"""
        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            files = {'file': (file_name, f)}
            
            response = requests.post(f"{self.api_url}/api/ingestion/upload", files=files)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            
            return response.json()
    
    def list_datasets(self, skip=0, limit=10):
        """List all uploaded datasets"""
        response = requests.get(f"{self.api_url}/api/ingestion/datasets?skip={skip}&limit={limit}")
        response.raise_for_status()
        
        return response.json()
    
    def get_dataset(self, dataset_id):
        """Get details of a specific dataset"""
        response = requests.get(f"{self.api_url}/api/ingestion/datasets/{dataset_id}")
        response.raise_for_status()
        
        return response.json()
    
    def delete_dataset(self, dataset_id):
        """Delete a dataset"""
        response = requests.delete(f"{self.api_url}/api/ingestion/datasets/{dataset_id}")
        response.raise_for_status()
        
        return response.json()
    
    def trigger_assessment(self, dataset_id, modules=None):
        """Trigger assessment for a dataset"""
        data = {'dataset_id': dataset_id}
        if modules:
            data['modules'] = modules
        
        response = requests.post(f"{self.api_url}/api/assessment/trigger", json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_assessment_status(self, assessment_id):
        """Check the status of an assessment"""
        response = requests.get(f"{self.api_url}/api/assessment/{assessment_id}/status")
        response.raise_for_status()
        
        return response.json()
    
    def get_assessment_report(self, assessment_id):
        """Get the detailed assessment report"""
        response = requests.get(f"{self.api_url}/api/assessment/{assessment_id}/report")
        response.raise_for_status()
        
        return response.json()
    
    def export_assessment_report(self, assessment_id, format='pdf'):
        """Export the assessment report"""
        response = requests.get(f"{self.api_url}/api/assessment/{assessment_id}/export?format={format}")
        response.raise_for_status()
        
        return response.content
    
    def list_assessments(self, dataset_id=None, skip=0, limit=10):
        """List all assessments"""
        url = f"{self.api_url}/api/assessment/list?skip={skip}&limit={limit}"
        if dataset_id:
            url += f"&dataset_id={dataset_id}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
