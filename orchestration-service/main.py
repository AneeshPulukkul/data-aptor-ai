"""
Orchestration Service for DataAptor AI

This service coordinates workflow management between services,
handling user configurations and service coordination.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import os
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="DataAptor AI Orchestration Service",
    description="Orchestration service for coordinating assessment workflows",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8002")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:8003")
SCORING_SERVICE_URL = os.getenv("SCORING_SERVICE_URL", "http://localhost:8004")
REPORTING_SERVICE_URL = os.getenv("REPORTING_SERVICE_URL", "http://localhost:8005")


class AssessmentStatus(str, Enum):
    PENDING = "pending"
    INGESTING = "ingesting"
    ASSESSING = "assessing"
    SCORING = "scoring"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class AssessmentRequest(BaseModel):
    dataset_id: int
    modules: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None


class AssessmentResponse(BaseModel):
    id: int
    dataset_id: int
    status: str
    started_at: str
    modules: List[str]


# In-memory storage for MVP (use database in production)
datasets_store: Dict[int, Dict[str, Any]] = {}
assessments_store: Dict[int, Dict[str, Any]] = {}
dataset_counter = 0
assessment_counter = 0


# Default assessment modules
DEFAULT_MODULES = ["quality", "accessibility", "governance", "ai_compatibility", "diversity"]

# Default weights
DEFAULT_WEIGHTS = {
    "quality": 0.40,
    "accessibility": 0.20,
    "governance": 0.15,
    "ai_compatibility": 0.20,
    "diversity": 0.05
}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orchestration-service"}


# Dataset endpoints
@app.post("/api/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None)
):
    """Upload a dataset and forward to ingestion service."""
    global dataset_counter
    
    async with httpx.AsyncClient() as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            data = {"name": name} if name else {}
            response = await client.post(
                f"{INGESTION_SERVICE_URL}/api/ingestion/upload",
                files=files,
                data=data,
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Store dataset info
            dataset_counter += 1
            datasets_store[result.get("id", dataset_counter)] = result
            
            return result
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ingestion service error: {str(e)}")


@app.get("/api/datasets")
async def list_datasets(skip: int = 0, limit: int = 100):
    """List all datasets."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INGESTION_SERVICE_URL}/api/ingestion/datasets",
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ingestion service error: {str(e)}")


@app.get("/api/datasets/{dataset_id}")
async def get_dataset(dataset_id: int):
    """Get details for a specific dataset."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INGESTION_SERVICE_URL}/api/ingestion/datasets/{dataset_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ingestion service error: {str(e)}")


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int):
    """Delete a dataset."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{INGESTION_SERVICE_URL}/api/ingestion/datasets/{dataset_id}"
            )
            response.raise_for_status()
            
            # Remove from local store
            if dataset_id in datasets_store:
                del datasets_store[dataset_id]
            
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ingestion service error: {str(e)}")


# Assessment endpoints
@app.post("/api/assessments")
async def start_assessment(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks
):
    """Start an assessment workflow for a dataset."""
    global assessment_counter
    
    assessment_counter += 1
    assessment_id = assessment_counter
    
    modules = request.modules or DEFAULT_MODULES
    weights = request.weights or DEFAULT_WEIGHTS
    
    assessment = {
        "id": assessment_id,
        "dataset_id": request.dataset_id,
        "status": AssessmentStatus.PENDING.value,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "modules": modules,
        "weights": weights,
        "results": {},
        "scores": {},
        "report": None
    }
    
    assessments_store[assessment_id] = assessment
    
    # Start assessment workflow in background
    background_tasks.add_task(
        run_assessment_workflow,
        assessment_id,
        request.dataset_id,
        modules,
        weights
    )
    
    return AssessmentResponse(
        id=assessment_id,
        dataset_id=request.dataset_id,
        status=assessment["status"],
        started_at=assessment["started_at"],
        modules=modules
    )


async def run_assessment_workflow(
    assessment_id: int,
    dataset_id: int,
    modules: List[str],
    weights: Dict[str, float]
):
    """Run the complete assessment workflow."""
    assessment = assessments_store[assessment_id]
    
    try:
        # Step 1: Run assessments
        assessment["status"] = AssessmentStatus.ASSESSING.value
        
        async with httpx.AsyncClient() as client:
            # Call assessment service for each module
            for module in modules:
                try:
                    response = await client.post(
                        f"{ASSESSMENT_SERVICE_URL}/api/assessment/{module}/{dataset_id}",
                        timeout=300.0
                    )
                    if response.status_code == 200:
                        assessment["results"][module] = response.json()
                except httpx.HTTPError:
                    assessment["results"][module] = {"error": "Assessment failed"}
            
            # Step 2: Calculate scores
            assessment["status"] = AssessmentStatus.SCORING.value
            
            try:
                response = await client.post(
                    f"{SCORING_SERVICE_URL}/api/scoring/{dataset_id}",
                    json={
                        "assessment_results": assessment["results"],
                        "weights": weights
                    },
                    timeout=60.0
                )
                if response.status_code == 200:
                    assessment["scores"] = response.json()
            except httpx.HTTPError:
                assessment["scores"] = {"error": "Scoring failed"}
            
            # Step 3: Generate report
            assessment["status"] = AssessmentStatus.REPORTING.value
            
            try:
                response = await client.post(
                    f"{REPORTING_SERVICE_URL}/api/reporting/{dataset_id}",
                    json={
                        "assessment_id": assessment_id,
                        "results": assessment["results"],
                        "scores": assessment["scores"]
                    },
                    timeout=60.0
                )
                if response.status_code == 200:
                    assessment["report"] = response.json()
            except httpx.HTTPError:
                assessment["report"] = {"error": "Report generation failed"}
            
            # Mark as completed
            assessment["status"] = AssessmentStatus.COMPLETED.value
            assessment["completed_at"] = datetime.utcnow().isoformat()
            
    except Exception as e:
        assessment["status"] = AssessmentStatus.FAILED.value
        assessment["error"] = str(e)


@app.get("/api/assessments")
async def list_assessments(
    dataset_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """List all assessments."""
    assessments = list(assessments_store.values())
    
    if dataset_id:
        assessments = [a for a in assessments if a["dataset_id"] == dataset_id]
    
    return assessments[skip:skip + limit]


@app.get("/api/assessments/{assessment_id}")
async def get_assessment(assessment_id: int):
    """Get details for a specific assessment."""
    if assessment_id not in assessments_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessments_store[assessment_id]


@app.get("/api/assessments/{assessment_id}/status")
async def get_assessment_status(assessment_id: int):
    """Get the status of an assessment."""
    if assessment_id not in assessments_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_store[assessment_id]
    return {
        "id": assessment_id,
        "status": assessment["status"],
        "started_at": assessment["started_at"],
        "completed_at": assessment.get("completed_at")
    }


# Report endpoints
@app.get("/api/reports/{assessment_id}")
async def get_report(assessment_id: int):
    """Get the report for an assessment."""
    if assessment_id not in assessments_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_store[assessment_id]
    
    if assessment["status"] != AssessmentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Assessment not completed. Current status: {assessment['status']}"
        )
    
    return {
        "assessment_id": assessment_id,
        "dataset_id": assessment["dataset_id"],
        "results": assessment["results"],
        "scores": assessment["scores"],
        "report": assessment["report"]
    }


@app.get("/api/reports/{assessment_id}/export")
async def export_report(assessment_id: int, format: str = "json"):
    """Export the report in the specified format."""
    if assessment_id not in assessments_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_store[assessment_id]
    
    if assessment["status"] != AssessmentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Assessment not completed. Current status: {assessment['status']}"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{REPORTING_SERVICE_URL}/api/reporting/{assessment_id}/export",
                params={"format": format}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Return basic export if reporting service fails
            return {
                "format": format,
                "assessment_id": assessment_id,
                "data": assessment
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
