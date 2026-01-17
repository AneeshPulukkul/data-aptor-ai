"""
Diversity/Bias Assessment Module

Evaluates:
- Representativeness: Sample diversity
- Bias Detection: Fairness metrics
"""

from typing import Dict, Any, List
import math


def calculate_entropy(values: List[Any]) -> float:
    """Calculate Shannon entropy for a list of values."""
    if not values:
        return 0
    
    # Count occurrences
    counts = {}
    for v in values:
        key = str(v)
        counts[key] = counts.get(key, 0) + 1
    
    # Calculate probabilities and entropy
    total = len(values)
    entropy = 0
    for count in counts.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log2(prob)
    
    return entropy


def calculate_gini_coefficient(values: List[float]) -> float:
    """Calculate Gini coefficient for numeric values."""
    if not values or len(values) < 2:
        return 0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumsum = sum(sorted_values)
    
    if cumsum == 0:
        return 0
    
    gini = (2 * sum((i + 1) * v for i, v in enumerate(sorted_values))) / (n * cumsum) - (n + 1) / n
    return gini


def assess_representativeness(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess sample representativeness and diversity."""
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 0,
            "max_score": 4,
            "diversity_metrics": {},
            "details": "No data available"
        }
    
    columns = list(records[0].keys()) if records else []
    diversity_metrics = {}
    
    # Analyze diversity for categorical columns
    for col in columns:
        values = [r.get(col) for r in records if r.get(col) is not None]
        if not values:
            continue
        
        # Check if categorical (string with limited unique values)
        if all(isinstance(v, str) for v in values[:10]):
            unique_values = set(values)
            unique_ratio = len(unique_values) / len(values)
            
            if unique_ratio < 0.5:  # Likely categorical
                entropy = calculate_entropy(values)
                max_entropy = math.log2(len(unique_values)) if len(unique_values) > 1 else 1
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                
                # Calculate distribution
                distribution = {}
                for v in values:
                    distribution[str(v)] = distribution.get(str(v), 0) + 1
                
                diversity_metrics[col] = {
                    "unique_values": len(unique_values),
                    "entropy": round(entropy, 3),
                    "normalized_entropy": round(normalized_entropy, 3),
                    "distribution": dict(sorted(
                        distribution.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10])  # Top 10
                }
    
    # Calculate overall diversity score
    if diversity_metrics:
        avg_normalized_entropy = sum(
            m["normalized_entropy"] for m in diversity_metrics.values()
        ) / len(diversity_metrics)
    else:
        avg_normalized_entropy = 0.5  # Default if no categorical columns
    
    # Score based on diversity
    if avg_normalized_entropy >= 0.8:
        score = 4  # Excellent diversity
    elif avg_normalized_entropy >= 0.6:
        score = 3  # Good diversity
    elif avg_normalized_entropy >= 0.4:
        score = 2  # Moderate diversity
    elif avg_normalized_entropy >= 0.2:
        score = 1  # Low diversity
    else:
        score = 0  # Very low diversity
    
    return {
        "score": score,
        "max_score": 4,
        "diversity_metrics": diversity_metrics,
        "average_normalized_entropy": round(avg_normalized_entropy, 3),
        "recommendation": get_representativeness_recommendation(score)
    }


def get_representativeness_recommendation(score: int) -> str:
    """Get representativeness recommendation based on assessment."""
    if score >= 4:
        return "Excellent sample diversity - data appears representative"
    elif score >= 3:
        return "Good diversity - minor improvements may help"
    elif score >= 2:
        return "Moderate diversity - consider collecting more diverse samples"
    elif score >= 1:
        return "Low diversity - data may not be representative of target population"
    else:
        return "Very low diversity - significant sampling bias likely present"


def assess_bias(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess potential bias in the dataset."""
    records = data.get("records", [])
    
    if not records:
        return {
            "score": 2,
            "max_score": 4,
            "bias_indicators": [],
            "protected_attributes": [],
            "details": "No data available for bias assessment"
        }
    
    columns = list(records[0].keys()) if records else []
    bias_indicators = []
    protected_attributes = []
    
    # Common protected attribute names
    protected_terms = [
        "gender", "sex", "race", "ethnicity", "age", "religion",
        "nationality", "disability", "marital_status", "income"
    ]
    
    # Find potential protected attributes
    for col in columns:
        col_lower = col.lower().replace("_", " ").replace("-", " ")
        for term in protected_terms:
            if term in col_lower:
                protected_attributes.append({
                    "column": col,
                    "attribute_type": term
                })
                break
    
    # Analyze distribution of protected attributes
    for attr in protected_attributes:
        col = attr["column"]
        values = [r.get(col) for r in records if r.get(col) is not None]
        
        if not values:
            continue
        
        # Calculate distribution
        distribution = {}
        for v in values:
            key = str(v)
            distribution[key] = distribution.get(key, 0) + 1
        
        # Check for imbalance
        if len(distribution) > 1:
            counts = list(distribution.values())
            max_count = max(counts)
            min_count = min(counts)
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            
            if imbalance_ratio > 5:
                bias_indicators.append({
                    "attribute": col,
                    "issue": "significant_imbalance",
                    "imbalance_ratio": round(imbalance_ratio, 2),
                    "distribution": distribution
                })
            elif imbalance_ratio > 2:
                bias_indicators.append({
                    "attribute": col,
                    "issue": "moderate_imbalance",
                    "imbalance_ratio": round(imbalance_ratio, 2),
                    "distribution": distribution
                })
    
    # Check for label correlation with protected attributes
    label_columns = [c for c in columns if any(
        term in c.lower() for term in ["label", "class", "target", "outcome"]
    )]
    
    if label_columns and protected_attributes:
        # Simple correlation check (more sophisticated methods would use statistical tests)
        label_col = label_columns[0]
        for attr in protected_attributes:
            attr_col = attr["column"]
            
            # Group labels by protected attribute
            groups = {}
            for record in records:
                attr_val = record.get(attr_col)
                label_val = record.get(label_col)
                if attr_val is not None and label_val is not None:
                    key = str(attr_val)
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(label_val)
            
            # Check for disparate outcomes
            if len(groups) > 1:
                # Calculate positive rate for each group (assuming binary labels)
                positive_rates = {}
                for group, labels in groups.items():
                    # Try to identify positive class
                    positive_count = sum(1 for l in labels if str(l).lower() in ["1", "true", "yes", "positive"])
                    positive_rates[group] = positive_count / len(labels) if labels else 0
                
                if positive_rates:
                    max_rate = max(positive_rates.values())
                    min_rate = min(positive_rates.values())
                    
                    if max_rate > 0 and min_rate / max_rate < 0.8:
                        bias_indicators.append({
                            "attribute": attr_col,
                            "issue": "potential_disparate_impact",
                            "positive_rates": {k: round(v, 3) for k, v in positive_rates.items()}
                        })
    
    # Calculate score based on bias indicators
    significant_issues = sum(1 for b in bias_indicators if b["issue"] in ["significant_imbalance", "potential_disparate_impact"])
    moderate_issues = sum(1 for b in bias_indicators if b["issue"] == "moderate_imbalance")
    
    if significant_issues == 0 and moderate_issues == 0:
        score = 4
    elif significant_issues == 0 and moderate_issues <= 2:
        score = 3
    elif significant_issues <= 1:
        score = 2
    elif significant_issues <= 2:
        score = 1
    else:
        score = 0
    
    return {
        "score": score,
        "max_score": 4,
        "bias_indicators": bias_indicators,
        "protected_attributes": protected_attributes,
        "recommendation": get_bias_recommendation(score, bias_indicators)
    }


def get_bias_recommendation(score: int, bias_indicators: List[Dict]) -> str:
    """Get bias recommendation based on assessment."""
    if score >= 4:
        return "No significant bias indicators detected"
    elif score >= 3:
        return "Minor imbalances detected - monitor for fairness during model training"
    elif score >= 2:
        return "Moderate bias indicators - consider resampling or bias mitigation techniques"
    elif score >= 1:
        return "Significant bias detected - implement fairness constraints during training"
    else:
        return "Severe bias present - data requires significant preprocessing for fair ML"


def assess_diversity(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run all diversity assessments and aggregate results."""
    representativeness = assess_representativeness(data, metadata)
    bias = assess_bias(data, metadata)
    
    # Calculate total score
    total_score = representativeness["score"] + bias["score"]
    max_score = 8  # 2 criteria * 4 points each
    
    return {
        "score": total_score,
        "max_score": max_score,
        "details": {
            "representativeness": representativeness,
            "bias": bias
        },
        "criteria": [
            {
                "name": "representativeness",
                "score": representativeness["score"],
                "max_score": 4,
                "weight": 0.025,
                "description": "Sample diversity and coverage"
            },
            {
                "name": "bias",
                "score": bias["score"],
                "max_score": 4,
                "weight": 0.025,
                "description": "Fairness and bias detection"
            }
        ]
    }
