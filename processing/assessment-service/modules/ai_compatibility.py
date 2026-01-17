"""
AI Compatibility Assessment Module

Evaluates:
- Relevance: Task alignment
- Labeling: Label quality
- Feature Richness: Feature variability
- Preprocessing Needs: Transformation requirements
"""

from typing import Dict, Any, List
import re


def assess_relevance(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data relevance for the specified AI task."""
    ai_task = metadata.get("ai_task", "general")
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 0,
            "max_score": 4,
            "ai_task": ai_task,
            "relevance_indicators": [],
            "recommendation": "No data available for relevance assessment"
        }
    
    columns = list(records[0].keys()) if records else []
    relevance_indicators = []
    
    # Task-specific relevance checks
    if ai_task in ["classification", "general"]:
        # Check for potential label columns
        label_columns = [c for c in columns if any(
            term in c.lower() for term in ["label", "class", "category", "target", "outcome", "type"]
        )]
        if label_columns:
            relevance_indicators.append({
                "indicator": "label_columns_found",
                "columns": label_columns,
                "positive": True
            })
        
        # Check for feature columns
        feature_columns = [c for c in columns if c not in label_columns]
        if len(feature_columns) >= 3:
            relevance_indicators.append({
                "indicator": "sufficient_features",
                "count": len(feature_columns),
                "positive": True
            })
    
    elif ai_task == "nlp":
        # Check for text columns
        text_columns = []
        for col in columns:
            sample_values = [str(r.get(col, "")) for r in records[:10] if r.get(col)]
            avg_length = sum(len(v) for v in sample_values) / len(sample_values) if sample_values else 0
            if avg_length > 50:  # Likely text content
                text_columns.append(col)
        
        if text_columns:
            relevance_indicators.append({
                "indicator": "text_columns_found",
                "columns": text_columns,
                "positive": True
            })
    
    elif ai_task == "regression":
        # Check for numeric target columns
        numeric_columns = []
        for col in columns:
            sample_values = [r.get(col) for r in records[:10] if r.get(col) is not None]
            if sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                numeric_columns.append(col)
        
        if numeric_columns:
            relevance_indicators.append({
                "indicator": "numeric_columns_found",
                "columns": numeric_columns,
                "positive": True
            })
    
    # Calculate score based on relevance indicators
    positive_indicators = sum(1 for i in relevance_indicators if i.get("positive", False))
    
    if positive_indicators >= 3:
        score = 4
    elif positive_indicators >= 2:
        score = 3
    elif positive_indicators >= 1:
        score = 2
    else:
        score = 1
    
    return {
        "score": score,
        "max_score": 4,
        "ai_task": ai_task,
        "relevance_indicators": relevance_indicators,
        "recommendation": get_relevance_recommendation(score, ai_task)
    }


def get_relevance_recommendation(score: int, ai_task: str) -> str:
    """Get relevance recommendation based on assessment."""
    if score >= 4:
        return f"Data appears highly relevant for {ai_task} tasks"
    elif score >= 3:
        return f"Data is suitable for {ai_task} tasks with minor adjustments"
    elif score >= 2:
        return f"Data may be usable for {ai_task} but requires review"
    else:
        return f"Data may not be well-suited for {ai_task} tasks - consider alternative approaches"


def assess_labeling(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess label quality and consistency."""
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 2,
            "max_score": 4,
            "label_column": None,
            "label_quality": "unknown",
            "details": {}
        }
    
    columns = list(records[0].keys()) if records else []
    
    # Find potential label columns
    label_columns = [c for c in columns if any(
        term in c.lower() for term in ["label", "class", "category", "target", "outcome"]
    )]
    
    if not label_columns:
        return {
            "score": 2,
            "max_score": 4,
            "label_column": None,
            "label_quality": "no_labels_found",
            "details": {"message": "No obvious label columns detected"}
        }
    
    # Analyze the first label column
    label_col = label_columns[0]
    labels = [r.get(label_col) for r in records if r.get(label_col) is not None]
    
    if not labels:
        return {
            "score": 1,
            "max_score": 4,
            "label_column": label_col,
            "label_quality": "empty",
            "details": {"message": "Label column is empty"}
        }
    
    # Calculate label statistics
    unique_labels = set(labels)
    label_counts = {}
    for label in labels:
        label_counts[str(label)] = label_counts.get(str(label), 0) + 1
    
    # Check for class imbalance
    if len(label_counts) > 1:
        counts = list(label_counts.values())
        max_count = max(counts)
        min_count = min(counts)
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    else:
        imbalance_ratio = 1
    
    # Calculate coverage (percentage of records with labels)
    coverage = len(labels) / len(records) * 100 if records else 0
    
    # Score based on label quality
    if coverage >= 99 and imbalance_ratio <= 3:
        score = 4  # Excellent
    elif coverage >= 95 and imbalance_ratio <= 5:
        score = 3  # Good
    elif coverage >= 80 and imbalance_ratio <= 10:
        score = 2  # Moderate
    elif coverage >= 50:
        score = 1  # Poor
    else:
        score = 0  # Very poor
    
    return {
        "score": score,
        "max_score": 4,
        "label_column": label_col,
        "label_quality": "assessed",
        "details": {
            "unique_labels": len(unique_labels),
            "label_distribution": dict(list(label_counts.items())[:10]),  # Top 10
            "coverage_percentage": round(coverage, 2),
            "imbalance_ratio": round(imbalance_ratio, 2)
        }
    }


def assess_feature_richness(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess feature richness and variability."""
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 0,
            "max_score": 4,
            "feature_count": 0,
            "feature_types": {},
            "variability_score": 0
        }
    
    columns = list(records[0].keys()) if records else []
    
    # Analyze feature types
    feature_types = {
        "numeric": [],
        "categorical": [],
        "text": [],
        "datetime": [],
        "boolean": []
    }
    
    for col in columns:
        sample_values = [r.get(col) for r in records[:100] if r.get(col) is not None]
        if not sample_values:
            continue
        
        # Determine feature type
        if all(isinstance(v, bool) for v in sample_values):
            feature_types["boolean"].append(col)
        elif all(isinstance(v, (int, float)) for v in sample_values):
            feature_types["numeric"].append(col)
        elif all(isinstance(v, str) for v in sample_values):
            avg_length = sum(len(v) for v in sample_values) / len(sample_values)
            unique_ratio = len(set(sample_values)) / len(sample_values)
            
            if avg_length > 100:
                feature_types["text"].append(col)
            elif unique_ratio < 0.1:
                feature_types["categorical"].append(col)
            else:
                feature_types["categorical"].append(col)
    
    # Calculate variability for numeric features
    variability_scores = []
    for col in feature_types["numeric"]:
        values = [r.get(col) for r in records if isinstance(r.get(col), (int, float))]
        if len(values) > 1:
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            std_dev = variance ** 0.5
            cv = std_dev / mean_val if mean_val != 0 else 0
            variability_scores.append(min(cv, 1))  # Cap at 1
    
    avg_variability = sum(variability_scores) / len(variability_scores) if variability_scores else 0.5
    
    # Calculate score
    feature_count = len(columns)
    type_diversity = sum(1 for t in feature_types.values() if t)
    
    if feature_count >= 20 and type_diversity >= 3 and avg_variability > 0.3:
        score = 4
    elif feature_count >= 10 and type_diversity >= 2 and avg_variability > 0.2:
        score = 3
    elif feature_count >= 5 and type_diversity >= 2:
        score = 2
    elif feature_count >= 3:
        score = 1
    else:
        score = 0
    
    return {
        "score": score,
        "max_score": 4,
        "feature_count": feature_count,
        "feature_types": {k: len(v) for k, v in feature_types.items()},
        "variability_score": round(avg_variability, 3),
        "type_diversity": type_diversity
    }


def assess_preprocessing_needs(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess preprocessing requirements."""
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 2,
            "max_score": 4,
            "preprocessing_tasks": [],
            "estimated_effort": "unknown"
        }
    
    columns = list(records[0].keys()) if records else []
    preprocessing_tasks = []
    
    # Check for missing values
    missing_count = 0
    for record in records:
        for col in columns:
            if record.get(col) is None or record.get(col) == "":
                missing_count += 1
    
    missing_rate = missing_count / (len(records) * len(columns)) if records and columns else 0
    if missing_rate > 0.01:
        preprocessing_tasks.append({
            "task": "handle_missing_values",
            "severity": "high" if missing_rate > 0.1 else "medium",
            "details": f"{missing_rate*100:.1f}% missing values"
        })
    
    # Check for text that needs encoding
    text_columns = []
    for col in columns:
        sample_values = [r.get(col) for r in records[:10] if isinstance(r.get(col), str)]
        if sample_values and sum(len(v) for v in sample_values) / len(sample_values) > 50:
            text_columns.append(col)
    
    if text_columns:
        preprocessing_tasks.append({
            "task": "text_encoding",
            "severity": "medium",
            "details": f"{len(text_columns)} text columns need encoding"
        })
    
    # Check for categorical encoding needs
    categorical_columns = []
    for col in columns:
        sample_values = [r.get(col) for r in records[:100] if r.get(col) is not None]
        if sample_values and all(isinstance(v, str) for v in sample_values):
            unique_ratio = len(set(sample_values)) / len(sample_values)
            if unique_ratio < 0.5:
                categorical_columns.append(col)
    
    if categorical_columns:
        preprocessing_tasks.append({
            "task": "categorical_encoding",
            "severity": "low",
            "details": f"{len(categorical_columns)} categorical columns need encoding"
        })
    
    # Check for scaling needs
    numeric_columns = []
    for col in columns:
        sample_values = [r.get(col) for r in records[:100] if isinstance(r.get(col), (int, float))]
        if sample_values:
            numeric_columns.append(col)
    
    if len(numeric_columns) > 1:
        preprocessing_tasks.append({
            "task": "feature_scaling",
            "severity": "low",
            "details": f"{len(numeric_columns)} numeric columns may need scaling"
        })
    
    # Calculate score based on preprocessing needs
    high_severity = sum(1 for t in preprocessing_tasks if t["severity"] == "high")
    medium_severity = sum(1 for t in preprocessing_tasks if t["severity"] == "medium")
    
    if high_severity == 0 and medium_severity == 0:
        score = 4
        effort = "minimal"
    elif high_severity == 0 and medium_severity <= 2:
        score = 3
        effort = "low"
    elif high_severity <= 1:
        score = 2
        effort = "moderate"
    elif high_severity <= 2:
        score = 1
        effort = "high"
    else:
        score = 0
        effort = "very_high"
    
    return {
        "score": score,
        "max_score": 4,
        "preprocessing_tasks": preprocessing_tasks,
        "estimated_effort": effort,
        "task_count": len(preprocessing_tasks)
    }


def assess_ai_compatibility(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run all AI compatibility assessments and aggregate results."""
    relevance = assess_relevance(data, metadata)
    labeling = assess_labeling(data, metadata)
    feature_richness = assess_feature_richness(data, metadata)
    preprocessing = assess_preprocessing_needs(data, metadata)
    
    # Calculate total score
    total_score = (
        relevance["score"] +
        labeling["score"] +
        feature_richness["score"] +
        preprocessing["score"]
    )
    max_score = 16  # 4 criteria * 4 points each
    
    return {
        "score": total_score,
        "max_score": max_score,
        "details": {
            "relevance": relevance,
            "labeling": labeling,
            "feature_richness": feature_richness,
            "preprocessing": preprocessing
        },
        "criteria": [
            {
                "name": "relevance",
                "score": relevance["score"],
                "max_score": 4,
                "weight": 0.05,
                "description": "Task alignment and suitability"
            },
            {
                "name": "labeling",
                "score": labeling["score"],
                "max_score": 4,
                "weight": 0.05,
                "description": "Label quality and consistency"
            },
            {
                "name": "feature_richness",
                "score": feature_richness["score"],
                "max_score": 4,
                "weight": 0.05,
                "description": "Feature variability and informativeness"
            },
            {
                "name": "preprocessing",
                "score": preprocessing["score"],
                "max_score": 4,
                "weight": 0.05,
                "description": "Preprocessing requirements"
            }
        ]
    }
