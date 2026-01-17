"""
Assessment Service for DataAptor AI

This service evaluates datasets across multiple dimensions:
- Data Quality (completeness, accuracy, consistency, timeliness)
- Accessibility (availability, volume)
- Governance (privacy, licensing)
- AI Compatibility (relevance, labeling, feature richness, preprocessing)
- Diversity/Bias (representativeness, diversity)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import httpx
from datetime import datetime

from config import settings
from database import get_db_connection
from modules.quality import assess_quality
from modules.accessibility import assess_accessibility
from modules.governance import assess_governance
from modules.ai_compatibility import assess_ai_compatibility
from modules.diversity import assess_diversity

app = FastAPI(
    title="DataAptor AI Assessment Service",
    description="Assessment service for evaluating dataset AI readiness",
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


class AssessmentResult(BaseModel):
    module: str
    score: float
    max_score: float
    details: Dict[str, Any]
    criteria: List[Dict[str, Any]]
    timestamp: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "assessment-service"}


async def get_dataset_data(dataset_id: int) -> Dict[str, Any]:
    """Fetch dataset data from ingestion service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INGESTION_SERVICE_URL}/api/ingestion/datasets/{dataset_id}/data",
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch dataset data: {str(e)}"
            )


async def get_dataset_metadata(dataset_id: int) -> Dict[str, Any]:
    """Fetch dataset metadata from ingestion service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{INGESTION_SERVICE_URL}/api/ingestion/datasets/{dataset_id}",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch dataset metadata: {str(e)}"
            )


@app.post("/api/assessment/quality/{dataset_id}")
async def assess_data_quality(dataset_id: int) -> AssessmentResult:
    """
    Assess data quality for a dataset.
    
    Evaluates:
    - Completeness: Missing value detection
    - Accuracy: Outlier detection, type consistency
    - Consistency: Format uniformity
    - Timeliness: Data freshness
    """
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        result = assess_quality(data, metadata)
        
        return AssessmentResult(
            module="quality",
            score=result["score"],
            max_score=result["max_score"],
            details=result["details"],
            criteria=result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/assessment/accessibility/{dataset_id}")
async def assess_data_accessibility(dataset_id: int) -> AssessmentResult:
    """
    Assess data accessibility for a dataset.
    
    Evaluates:
    - Availability: Format compatibility
    - Volume: Sample size adequacy
    """
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        result = assess_accessibility(data, metadata)
        
        return AssessmentResult(
            module="accessibility",
            score=result["score"],
            max_score=result["max_score"],
            details=result["details"],
            criteria=result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/assessment/governance/{dataset_id}")
async def assess_data_governance(dataset_id: int) -> AssessmentResult:
    """
    Assess data governance for a dataset.
    
    Evaluates:
    - Privacy: PII detection
    - Licensing: Usage rights validation
    """
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        result = assess_governance(data, metadata)
        
        return AssessmentResult(
            module="governance",
            score=result["score"],
            max_score=result["max_score"],
            details=result["details"],
            criteria=result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/assessment/ai_compatibility/{dataset_id}")
async def assess_ai_compatibility_endpoint(dataset_id: int) -> AssessmentResult:
    """
    Assess AI compatibility for a dataset.
    
    Evaluates:
    - Relevance: Task alignment
    - Labeling: Label quality
    - Feature Richness: Feature variability
    - Preprocessing Needs: Transformation requirements
    """
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        result = assess_ai_compatibility(data, metadata)
        
        return AssessmentResult(
            module="ai_compatibility",
            score=result["score"],
            max_score=result["max_score"],
            details=result["details"],
            criteria=result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/assessment/diversity/{dataset_id}")
async def assess_data_diversity(dataset_id: int) -> AssessmentResult:
    """
    Assess data diversity for a dataset.
    
    Evaluates:
    - Representativeness: Sample diversity
    - Bias Detection: Fairness metrics
    """
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        result = assess_diversity(data, metadata)
        
        return AssessmentResult(
            module="diversity",
            score=result["score"],
            max_score=result["max_score"],
            details=result["details"],
            criteria=result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/assessment/full/{dataset_id}")
async def run_full_assessment(dataset_id: int) -> Dict[str, AssessmentResult]:
    """Run all assessment modules for a dataset."""
    results = {}
    
    try:
        metadata = await get_dataset_metadata(dataset_id)
        data = await get_dataset_data(dataset_id)
        
        # Run all assessments
        quality_result = assess_quality(data, metadata)
        results["quality"] = AssessmentResult(
            module="quality",
            score=quality_result["score"],
            max_score=quality_result["max_score"],
            details=quality_result["details"],
            criteria=quality_result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        accessibility_result = assess_accessibility(data, metadata)
        results["accessibility"] = AssessmentResult(
            module="accessibility",
            score=accessibility_result["score"],
            max_score=accessibility_result["max_score"],
            details=accessibility_result["details"],
            criteria=accessibility_result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        governance_result = assess_governance(data, metadata)
        results["governance"] = AssessmentResult(
            module="governance",
            score=governance_result["score"],
            max_score=governance_result["max_score"],
            details=governance_result["details"],
            criteria=governance_result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        ai_compat_result = assess_ai_compatibility(data, metadata)
        results["ai_compatibility"] = AssessmentResult(
            module="ai_compatibility",
            score=ai_compat_result["score"],
            max_score=ai_compat_result["max_score"],
            details=ai_compat_result["details"],
            criteria=ai_compat_result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        diversity_result = assess_diversity(data, metadata)
        results["diversity"] = AssessmentResult(
            module="diversity",
            score=diversity_result["score"],
            max_score=diversity_result["max_score"],
            details=diversity_result["details"],
            criteria=diversity_result["criteria"],
            timestamp=datetime.utcnow().isoformat()
        )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full assessment failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
