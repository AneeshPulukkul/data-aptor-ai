"""
Mock API server for testing the DataAptor CLI

This script creates a simple FastAPI server that responds to the endpoints
used by the DataAptor CLI, returning mock data for testing purposes.

To use:
1. Install dependencies: pip install fastapi uvicorn python-multipart
2. Run server: python mock_api_server.py
3. Test CLI commands against http://localhost:8000
"""

from fastapi import FastAPI, UploadFile, File, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import uvicorn
import random
import uuid
import datetime
import time
import os
from pathlib import Path

app = FastAPI(title="DataAptor Mock API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create mock data directory
MOCK_DATA_DIR = Path("./mock_data")
MOCK_DATA_DIR.mkdir(exist_ok=True)

# In-memory storage for mock data
datasets = []
assessments = []

@app.get("/")
async def root():
    return {"message": "DataAptor Mock API is running"}

# INGESTION SERVICE ENDPOINTS

@app.post("/api/ingestion/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Mock endpoint for uploading a dataset"""
    # Save the file to mock data directory
    file_path = MOCK_DATA_DIR / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create mock dataset record
    dataset_id = len(datasets) + 1
    created_at = datetime.datetime.now().isoformat()
    file_size = os.path.getsize(file_path)
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    file_type_map = {
        ".csv": "CSV",
        ".json": "JSON",
        ".txt": "TEXT",
        ".xml": "XML",
        ".xlsx": "EXCEL",
        ".jpg": "IMAGE",
        ".jpeg": "IMAGE",
        ".png": "IMAGE",
        ".wav": "AUDIO",
        ".mp3": "AUDIO"
    }
    
    file_type = file_type_map.get(file_extension, "UNKNOWN")
    
    # Mock metadata based on file type
    metadata = {
        "rows": random.randint(100, 1000) if file_type == "CSV" else None,
        "columns": random.randint(5, 20) if file_type == "CSV" else None,
        "format": file_type,
        "encoding": "UTF-8",
        "has_header": True if file_type == "CSV" else None,
        "file_hash": str(uuid.uuid4()),
    }
    
    dataset = {
        "id": dataset_id,
        "name": file.filename,
        "file_type": file_type,
        "file_size": file_size,
        "created_at": created_at,
        "metadata": metadata
    }
    
    datasets.append(dataset)
    return dataset

@app.get("/api/ingestion/datasets")
async def list_datasets(skip: int = 0, limit: int = 10):
    """Mock endpoint for listing datasets"""
    return {
        "datasets": datasets[skip:skip+limit],
        "total": len(datasets)
    }

@app.get("/api/ingestion/datasets/{dataset_id}")
async def get_dataset(dataset_id: int):
    """Mock endpoint for getting dataset details"""
    for dataset in datasets:
        if dataset["id"] == dataset_id:
            return dataset
    return {"error": "Dataset not found"}, 404

@app.delete("/api/ingestion/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int):
    """Mock endpoint for deleting a dataset"""
    global datasets
    original_length = len(datasets)
    datasets = [d for d in datasets if d["id"] != dataset_id]
    if len(datasets) < original_length:
        return {"message": "Dataset deleted successfully"}
    return {"error": "Dataset not found"}, 404

# ASSESSMENT SERVICE ENDPOINTS

@app.post("/api/assessment/trigger")
async def trigger_assessment(data: Dict[str, Any]):
    """Mock endpoint for triggering an assessment"""
    dataset_id = data.get("dataset_id")
    modules = data.get("modules", ["quality", "accessibility"])
    
    # Check if dataset exists
    dataset = None
    for d in datasets:
        if d["id"] == dataset_id:
            dataset = d
            break
    
    if not dataset:
        return {"error": "Dataset not found"}, 404
    
    # Create a mock assessment
    assessment_id = len(assessments) + 1
    created_at = datetime.datetime.now().isoformat()
    
    assessment = {
        "id": assessment_id,
        "dataset_id": dataset_id,
        "status": "in_progress",
        "created_at": created_at,
        "started_at": created_at,
        "modules": modules,
        "progress": {
            "percentage": 0,
            "current_module": modules[0] if modules else "quality",
            "modules_completed": 0,
            "total_modules": len(modules)
        }
    }
    
    assessments.append(assessment)
    
    # Simulate assessment processing in the background
    # In a real implementation, this would be a background task
    return {"assessment_id": assessment_id}

@app.get("/api/assessment/{assessment_id}/status")
async def get_assessment_status(assessment_id: int):
    """Mock endpoint for checking assessment status"""
    for assessment in assessments:
        if assessment["id"] == assessment_id:
            # Simulate progress based on time
            if assessment["status"] == "in_progress":
                elapsed = (datetime.datetime.now() - datetime.datetime.fromisoformat(assessment["started_at"])).total_seconds()
                
                # Progress increases over time (simulation)
                progress_pct = min(100, elapsed * 10)  # 10% per second
                
                modules = assessment.get("modules", ["quality", "accessibility"])
                total_modules = len(modules)
                modules_completed = int(progress_pct / (100 / total_modules))
                
                current_module_index = min(modules_completed, total_modules - 1)
                current_module = modules[current_module_index] if modules else "quality"
                
                assessment["progress"] = {
                    "percentage": progress_pct,
                    "current_module": current_module,
                    "modules_completed": modules_completed,
                    "total_modules": total_modules
                }
                
                # Mark as completed if progress reaches 100%
                if progress_pct >= 100:
                    assessment["status"] = "completed"
                    assessment["completed_at"] = datetime.datetime.now().isoformat()
                    assessment["duration_seconds"] = elapsed
                    
                    # Generate mock module scores
                    assessment["module_scores"] = [
                        {"name": "quality", "score": random.uniform(6.0, 9.5)},
                        {"name": "accessibility", "score": random.uniform(5.0, 9.0)}
                    ]
                    
                    # Calculate overall score (average of module scores)
                    assessment["overall_score"] = sum(m["score"] for m in assessment["module_scores"]) / len(assessment["module_scores"])
            
            return assessment
    
    return {"error": "Assessment not found"}, 404

@app.get("/api/assessment/{assessment_id}/report")
async def get_assessment_report(assessment_id: int):
    """Mock endpoint for getting assessment report"""
    for assessment in assessments:
        if assessment["id"] == assessment_id:
            if assessment["status"] != "completed":
                return {"error": "Assessment not yet completed"}, 400
            
            # Get dataset name
            dataset_name = "Unknown Dataset"
            for dataset in datasets:
                if dataset["id"] == assessment["dataset_id"]:
                    dataset_name = dataset["name"]
                    break
            
            # Generate mock report
            report = {
                "assessment_id": assessment_id,
                "dataset_id": assessment["dataset_id"],
                "dataset_name": dataset_name,
                "overall_score": assessment["overall_score"],
                "created_at": datetime.datetime.now().isoformat(),
                "module_scores": assessment["module_scores"],
                "findings": [
                    "Dataset contains 5% missing values",
                    "Column 'age' has 1 null value",
                    "Date formats are inconsistent in column 'created_date'",
                    "Potential outliers detected in column 'income'"
                ],
                "recommendations": [
                    "Fill missing values in the 'age' column",
                    "Standardize date formats across all columns",
                    "Review outliers in 'income' column to determine if they are valid",
                    "Consider normalizing numerical columns for better model performance"
                ]
            }
            
            return report
            
    return {"error": "Assessment not found"}, 404

@app.get("/api/assessment/{assessment_id}/export")
async def export_assessment_report(assessment_id: int, format: str = "pdf"):
    """Mock endpoint for exporting assessment report"""
    for assessment in assessments:
        if assessment["id"] == assessment_id:
            if assessment["status"] != "completed":
                return {"error": "Assessment not yet completed"}, 400
            
            # Generate mock file content based on format
            if format == "pdf":
                content = b"%PDF-1.5\nMock PDF content for assessment report"
            elif format == "html":
                content = b"<html><body><h1>Assessment Report</h1><p>Mock HTML content</p></body></html>"
            elif format == "json":
                content = b'{"assessment_id": ' + str(assessment_id).encode() + b', "mock": true}'
            elif format == "csv":
                content = b"module,score\nquality,8.5\naccessibility,7.2"
            else:
                return {"error": "Unsupported format"}, 400
            
            return content
            
    return {"error": "Assessment not found"}, 404

@app.get("/api/assessment/list")
async def list_assessments(dataset_id: Optional[int] = None, skip: int = 0, limit: int = 10):
    """Mock endpoint for listing assessments"""
    filtered_assessments = assessments
    if dataset_id:
        filtered_assessments = [a for a in assessments if a["dataset_id"] == dataset_id]
    
    return {
        "assessments": filtered_assessments[skip:skip+limit],
        "total": len(filtered_assessments)
    }

if __name__ == "__main__":
    print("Starting DataAptor Mock API Server...")
    print("Endpoints available at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
