"""
Accessibility Assessment Module

Evaluates:
- Availability: Format compatibility
- Volume: Sample size adequacy
"""

from typing import Dict, Any, List


# Supported formats for AI/ML tasks
SUPPORTED_FORMATS = {
    "csv": {"compatibility": 4, "description": "Fully compatible"},
    "json": {"compatibility": 4, "description": "Fully compatible"},
    "parquet": {"compatibility": 4, "description": "Fully compatible"},
    "xlsx": {"compatibility": 3, "description": "Compatible with conversion"},
    "xls": {"compatibility": 3, "description": "Compatible with conversion"},
    "xml": {"compatibility": 2, "description": "Requires parsing"},
    "txt": {"compatibility": 2, "description": "Requires parsing"},
    "pdf": {"compatibility": 1, "description": "Requires extraction"},
    "jpeg": {"compatibility": 4, "description": "Fully compatible for vision tasks"},
    "jpg": {"compatibility": 4, "description": "Fully compatible for vision tasks"},
    "png": {"compatibility": 4, "description": "Fully compatible for vision tasks"},
    "wav": {"compatibility": 4, "description": "Fully compatible for audio tasks"},
    "mp3": {"compatibility": 3, "description": "Compatible with conversion"},
}

# Minimum sample sizes for different AI tasks
MIN_SAMPLES = {
    "classification": 1000,
    "regression": 500,
    "nlp": 10000,
    "computer_vision": 5000,
    "audio": 1000,
    "default": 1000
}


def assess_availability(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data availability and format compatibility."""
    file_type = metadata.get("file_type", "").lower().replace(".", "")
    
    if file_type in SUPPORTED_FORMATS:
        format_info = SUPPORTED_FORMATS[file_type]
        score = format_info["compatibility"]
        description = format_info["description"]
    else:
        score = 1
        description = "Unknown format - may require custom processing"
    
    return {
        "score": score,
        "max_score": 4,
        "file_type": file_type,
        "compatibility": description,
        "supported_formats": list(SUPPORTED_FORMATS.keys())
    }


def assess_volume(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data volume and sample size adequacy."""
    records = data.get("records", [])
    record_count = len(records)
    
    # Get AI task type from metadata if available
    ai_task = metadata.get("ai_task", "default")
    min_samples = MIN_SAMPLES.get(ai_task, MIN_SAMPLES["default"])
    
    # Calculate score based on sample size relative to minimum
    ratio = record_count / min_samples if min_samples > 0 else 0
    
    if ratio >= 10:
        score = 4  # Excellent - 10x minimum
    elif ratio >= 5:
        score = 3  # Good - 5x minimum
    elif ratio >= 1:
        score = 2  # Adequate - meets minimum
    elif ratio >= 0.5:
        score = 1  # Below minimum but usable
    else:
        score = 0  # Insufficient
    
    return {
        "score": score,
        "max_score": 4,
        "record_count": record_count,
        "minimum_recommended": min_samples,
        "ai_task": ai_task,
        "ratio": round(ratio, 2),
        "recommendation": get_volume_recommendation(ratio, min_samples)
    }


def get_volume_recommendation(ratio: float, min_samples: int) -> str:
    """Get recommendation based on volume ratio."""
    if ratio >= 10:
        return "Excellent sample size for AI/ML tasks"
    elif ratio >= 5:
        return "Good sample size for most AI/ML tasks"
    elif ratio >= 1:
        return "Adequate sample size - consider augmentation for better results"
    elif ratio >= 0.5:
        return f"Below recommended minimum of {min_samples} samples - collect more data"
    else:
        return f"Insufficient data - need at least {min_samples} samples for reliable results"


def assess_accessibility(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run all accessibility assessments and aggregate results."""
    availability = assess_availability(data, metadata)
    volume = assess_volume(data, metadata)
    
    # Calculate total score
    total_score = availability["score"] + volume["score"]
    max_score = 8  # 2 criteria * 4 points each
    
    return {
        "score": total_score,
        "max_score": max_score,
        "details": {
            "availability": availability,
            "volume": volume
        },
        "criteria": [
            {
                "name": "availability",
                "score": availability["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Format compatibility for AI/ML tasks"
            },
            {
                "name": "volume",
                "score": volume["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Sample size adequacy"
            }
        ]
    }
