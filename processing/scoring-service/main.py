"""
Scoring Service for DataAptor AI

This service calculates weighted AI readiness scores based on assessment results.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

app = FastAPI(
    title="DataAptor AI Scoring Service",
    description="Scoring service for calculating AI readiness scores",
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

# Default weights for assessment modules
DEFAULT_WEIGHTS = {
    "quality": 0.40,
    "accessibility": 0.20,
    "governance": 0.15,
    "ai_compatibility": 0.20,
    "diversity": 0.05
}

# Readiness level thresholds
READINESS_LEVELS = {
    "high": {"min": 80, "max": 100, "description": "Ready for AI/ML applications"},
    "moderate": {"min": 60, "max": 79, "description": "Minor improvements needed"},
    "low": {"min": 40, "max": 59, "description": "Significant work required"},
    "not_ready": {"min": 0, "max": 39, "description": "Major issues to address"}
}


class ScoringRequest(BaseModel):
    assessment_results: Dict[str, Any]
    weights: Optional[Dict[str, float]] = None


class ScoreBreakdown(BaseModel):
    module: str
    raw_score: float
    max_score: float
    normalized_score: float
    weight: float
    weighted_score: float


class ScoringResponse(BaseModel):
    overall_score: float
    readiness_level: str
    readiness_description: str
    module_scores: List[ScoreBreakdown]
    weights_used: Dict[str, float]
    timestamp: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "scoring-service"}


def normalize_score(raw_score: float, max_score: float) -> float:
    """Normalize a score to 0-100 scale."""
    if max_score <= 0:
        return 0
    return (raw_score / max_score) * 100


def get_readiness_level(score: float) -> tuple:
    """Get readiness level based on score."""
    for level, thresholds in READINESS_LEVELS.items():
        if thresholds["min"] <= score <= thresholds["max"]:
            return level, thresholds["description"]
    return "not_ready", READINESS_LEVELS["not_ready"]["description"]


def calculate_weighted_score(
    assessment_results: Dict[str, Any],
    weights: Dict[str, float]
) -> tuple:
    """Calculate weighted overall score from assessment results."""
    module_scores = []
    total_weighted_score = 0
    total_weight = 0
    
    for module, weight in weights.items():
        if module in assessment_results:
            result = assessment_results[module]
            
            # Handle different result formats
            if isinstance(result, dict):
                raw_score = result.get("score", 0)
                max_score = result.get("max_score", 1)
            else:
                raw_score = float(result) if result else 0
                max_score = 100
            
            normalized = normalize_score(raw_score, max_score)
            weighted = normalized * weight
            
            module_scores.append(ScoreBreakdown(
                module=module,
                raw_score=raw_score,
                max_score=max_score,
                normalized_score=round(normalized, 2),
                weight=weight,
                weighted_score=round(weighted, 2)
            ))
            
            total_weighted_score += weighted
            total_weight += weight
    
    # Normalize if weights don't sum to 1
    if total_weight > 0 and total_weight != 1:
        total_weighted_score = total_weighted_score / total_weight
    
    return round(total_weighted_score, 2), module_scores


@app.post("/api/scoring/{dataset_id}", response_model=ScoringResponse)
async def calculate_score(dataset_id: int, request: ScoringRequest):
    """
    Calculate AI readiness score for a dataset based on assessment results.
    
    The score is calculated as a weighted sum of normalized module scores:
    - Quality: 40% (default)
    - Accessibility: 20% (default)
    - Governance: 15% (default)
    - AI Compatibility: 20% (default)
    - Diversity: 5% (default)
    
    Custom weights can be provided in the request.
    """
    # Use custom weights if provided, otherwise use defaults
    weights = request.weights if request.weights else DEFAULT_WEIGHTS
    
    # Validate weights
    if not weights:
        raise HTTPException(status_code=400, detail="No weights provided")
    
    # Calculate weighted score
    overall_score, module_scores = calculate_weighted_score(
        request.assessment_results,
        weights
    )
    
    # Determine readiness level
    readiness_level, readiness_description = get_readiness_level(overall_score)
    
    return ScoringResponse(
        overall_score=overall_score,
        readiness_level=readiness_level,
        readiness_description=readiness_description,
        module_scores=module_scores,
        weights_used=weights,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/scoring/weights")
async def get_default_weights():
    """Get the default scoring weights."""
    return {
        "weights": DEFAULT_WEIGHTS,
        "description": {
            "quality": "Data quality assessment (completeness, accuracy, consistency, timeliness)",
            "accessibility": "Data accessibility (format compatibility, volume adequacy)",
            "governance": "Data governance (privacy, licensing)",
            "ai_compatibility": "AI compatibility (relevance, labeling, features, preprocessing)",
            "diversity": "Diversity and bias assessment"
        }
    }


@app.get("/api/scoring/levels")
async def get_readiness_levels():
    """Get the readiness level definitions."""
    return {"levels": READINESS_LEVELS}


@app.post("/api/scoring/custom")
async def calculate_custom_score(
    assessment_results: Dict[str, Any],
    weights: Dict[str, float]
):
    """
    Calculate score with fully custom weights.
    
    This endpoint allows complete flexibility in weight assignment.
    """
    # Validate that weights sum to approximately 1
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        # Normalize weights
        weights = {k: v / weight_sum for k, v in weights.items()}
    
    overall_score, module_scores = calculate_weighted_score(
        assessment_results,
        weights
    )
    
    readiness_level, readiness_description = get_readiness_level(overall_score)
    
    return {
        "overall_score": overall_score,
        "readiness_level": readiness_level,
        "readiness_description": readiness_description,
        "module_scores": [s.dict() for s in module_scores],
        "weights_used": weights,
        "weights_normalized": True,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
