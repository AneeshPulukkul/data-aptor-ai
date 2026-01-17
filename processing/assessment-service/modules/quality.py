"""
Data Quality Assessment Module

Evaluates:
- Completeness: Missing value detection
- Accuracy: Outlier detection, type consistency
- Consistency: Format uniformity
- Timeliness: Data freshness
"""

from typing import Dict, Any, List
import re
from datetime import datetime, timedelta


def assess_completeness(data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data completeness by detecting missing values."""
    if not data or "records" not in data:
        return {
            "score": 0,
            "max_score": 4,
            "missing_count": 0,
            "total_values": 0,
            "missing_percentage": 100,
            "columns_with_missing": []
        }
    
    records = data.get("records", [])
    if not records:
        return {
            "score": 0,
            "max_score": 4,
            "missing_count": 0,
            "total_values": 0,
            "missing_percentage": 100,
            "columns_with_missing": []
        }
    
    total_values = 0
    missing_count = 0
    columns_with_missing = {}
    
    # Get all columns from first record
    columns = list(records[0].keys()) if records else []
    
    for record in records:
        for col in columns:
            total_values += 1
            value = record.get(col)
            if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
                missing_count += 1
                columns_with_missing[col] = columns_with_missing.get(col, 0) + 1
    
    missing_percentage = (missing_count / total_values * 100) if total_values > 0 else 100
    
    # Score based on completeness percentage
    if missing_percentage <= 1:
        score = 4  # Excellent
    elif missing_percentage <= 5:
        score = 3  # Good
    elif missing_percentage <= 15:
        score = 2  # Moderate
    elif missing_percentage <= 30:
        score = 1  # Poor
    else:
        score = 0  # Very poor
    
    return {
        "score": score,
        "max_score": 4,
        "missing_count": missing_count,
        "total_values": total_values,
        "missing_percentage": round(missing_percentage, 2),
        "columns_with_missing": [
            {"column": col, "missing_count": count}
            for col, count in columns_with_missing.items()
        ]
    }


def assess_accuracy(data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data accuracy by detecting outliers and type consistency."""
    if not data or "records" not in data:
        return {
            "score": 2,
            "max_score": 4,
            "outliers_detected": 0,
            "type_inconsistencies": 0,
            "details": []
        }
    
    records = data.get("records", [])
    if not records:
        return {
            "score": 2,
            "max_score": 4,
            "outliers_detected": 0,
            "type_inconsistencies": 0,
            "details": []
        }
    
    columns = list(records[0].keys()) if records else []
    outliers_detected = 0
    type_inconsistencies = 0
    details = []
    
    for col in columns:
        values = [r.get(col) for r in records if r.get(col) is not None]
        if not values:
            continue
        
        # Check type consistency
        types = set(type(v).__name__ for v in values)
        if len(types) > 1:
            type_inconsistencies += 1
            details.append({
                "column": col,
                "issue": "type_inconsistency",
                "types_found": list(types)
            })
        
        # Check for numeric outliers using IQR method
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        if len(numeric_values) > 4:
            sorted_vals = sorted(numeric_values)
            q1_idx = len(sorted_vals) // 4
            q3_idx = 3 * len(sorted_vals) // 4
            q1 = sorted_vals[q1_idx]
            q3 = sorted_vals[q3_idx]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            col_outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
            if col_outliers:
                outliers_detected += len(col_outliers)
                details.append({
                    "column": col,
                    "issue": "outliers",
                    "count": len(col_outliers)
                })
    
    # Calculate score
    total_issues = outliers_detected + type_inconsistencies * 10
    total_records = len(records)
    issue_rate = total_issues / total_records if total_records > 0 else 0
    
    if issue_rate <= 0.01:
        score = 4
    elif issue_rate <= 0.05:
        score = 3
    elif issue_rate <= 0.15:
        score = 2
    elif issue_rate <= 0.30:
        score = 1
    else:
        score = 0
    
    return {
        "score": score,
        "max_score": 4,
        "outliers_detected": outliers_detected,
        "type_inconsistencies": type_inconsistencies,
        "details": details
    }


def assess_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data consistency by checking format uniformity."""
    if not data or "records" not in data:
        return {
            "score": 2,
            "max_score": 4,
            "format_issues": 0,
            "details": []
        }
    
    records = data.get("records", [])
    if not records:
        return {
            "score": 2,
            "max_score": 4,
            "format_issues": 0,
            "details": []
        }
    
    columns = list(records[0].keys()) if records else []
    format_issues = 0
    details = []
    
    # Common patterns
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{2}/\d{2}/\d{4}$',
        r'^\d{2}-\d{2}-\d{4}$'
    ]
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    phone_patterns = [
        r'^\d{10}$',
        r'^\d{3}-\d{3}-\d{4}$',
        r'^\(\d{3}\)\s?\d{3}-\d{4}$'
    ]
    
    for col in columns:
        values = [str(r.get(col, "")) for r in records if r.get(col) is not None]
        if not values:
            continue
        
        # Check for date format consistency
        date_formats_found = set()
        for val in values:
            for i, pattern in enumerate(date_patterns):
                if re.match(pattern, val):
                    date_formats_found.add(i)
                    break
        
        if len(date_formats_found) > 1:
            format_issues += 1
            details.append({
                "column": col,
                "issue": "inconsistent_date_format",
                "formats_found": len(date_formats_found)
            })
        
        # Check for case consistency in text fields
        if all(isinstance(r.get(col), str) for r in records[:10] if r.get(col)):
            cases = set()
            for val in values[:100]:
                if val.isupper():
                    cases.add("upper")
                elif val.islower():
                    cases.add("lower")
                elif val.istitle():
                    cases.add("title")
                else:
                    cases.add("mixed")
            
            if len(cases) > 2:
                format_issues += 1
                details.append({
                    "column": col,
                    "issue": "inconsistent_case",
                    "cases_found": list(cases)
                })
    
    # Calculate score
    if format_issues == 0:
        score = 4
    elif format_issues <= 2:
        score = 3
    elif format_issues <= 5:
        score = 2
    elif format_issues <= 10:
        score = 1
    else:
        score = 0
    
    return {
        "score": score,
        "max_score": 4,
        "format_issues": format_issues,
        "details": details
    }


def assess_timeliness(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess data timeliness by checking data freshness."""
    # Check metadata for timestamps
    created_at = metadata.get("created_at")
    updated_at = metadata.get("updated_at")
    
    if not created_at and not updated_at:
        return {
            "score": 2,
            "max_score": 4,
            "data_age_days": None,
            "details": "No timestamp information available"
        }
    
    # Parse timestamp
    timestamp_str = updated_at or created_at
    try:
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = timestamp_str
        
        age = datetime.utcnow() - timestamp.replace(tzinfo=None)
        age_days = age.days
    except (ValueError, TypeError):
        return {
            "score": 2,
            "max_score": 4,
            "data_age_days": None,
            "details": "Could not parse timestamp"
        }
    
    # Score based on age
    if age_days <= 7:
        score = 4  # Very fresh
    elif age_days <= 30:
        score = 3  # Fresh
    elif age_days <= 90:
        score = 2  # Moderate
    elif age_days <= 365:
        score = 1  # Stale
    else:
        score = 0  # Very stale
    
    return {
        "score": score,
        "max_score": 4,
        "data_age_days": age_days,
        "details": f"Data is {age_days} days old"
    }


def assess_quality(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run all quality assessments and aggregate results."""
    completeness = assess_completeness(data)
    accuracy = assess_accuracy(data)
    consistency = assess_consistency(data)
    timeliness = assess_timeliness(data, metadata)
    
    # Calculate total score (each criterion has max 4 points)
    total_score = (
        completeness["score"] +
        accuracy["score"] +
        consistency["score"] +
        timeliness["score"]
    )
    max_score = 16  # 4 criteria * 4 points each
    
    return {
        "score": total_score,
        "max_score": max_score,
        "details": {
            "completeness": completeness,
            "accuracy": accuracy,
            "consistency": consistency,
            "timeliness": timeliness
        },
        "criteria": [
            {
                "name": "completeness",
                "score": completeness["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Missing value detection"
            },
            {
                "name": "accuracy",
                "score": accuracy["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Outlier detection and type consistency"
            },
            {
                "name": "consistency",
                "score": consistency["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Format uniformity"
            },
            {
                "name": "timeliness",
                "score": timeliness["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "Data freshness"
            }
        ]
    }
