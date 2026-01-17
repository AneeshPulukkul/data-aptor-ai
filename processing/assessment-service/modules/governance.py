"""
Governance Assessment Module

Evaluates:
- Privacy: PII detection
- Licensing: Usage rights validation
"""

from typing import Dict, Any, List
import re


# PII patterns for detection
PII_PATTERNS = {
    "email": {
        "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "severity": "high"
    },
    "phone": {
        "pattern": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        "severity": "high"
    },
    "ssn": {
        "pattern": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        "severity": "critical"
    },
    "credit_card": {
        "pattern": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        "severity": "critical"
    },
    "ip_address": {
        "pattern": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        "severity": "medium"
    },
    "date_of_birth": {
        "pattern": r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b',
        "severity": "medium"
    }
}

# Column names that might contain PII
PII_COLUMN_NAMES = [
    "name", "first_name", "last_name", "full_name",
    "email", "phone", "telephone", "mobile",
    "ssn", "social_security", "tax_id",
    "address", "street", "city", "zip", "postal",
    "dob", "date_of_birth", "birthday",
    "credit_card", "card_number", "cvv",
    "password", "secret", "token"
]


def detect_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Detect PII in the dataset."""
    if not data or "records" not in data:
        return {
            "pii_detected": False,
            "pii_count": 0,
            "pii_types": [],
            "affected_columns": []
        }
    
    records = data.get("records", [])
    if not records:
        return {
            "pii_detected": False,
            "pii_count": 0,
            "pii_types": [],
            "affected_columns": []
        }
    
    pii_findings = {}
    affected_columns = set()
    columns = list(records[0].keys()) if records else []
    
    # Check column names for PII indicators
    for col in columns:
        col_lower = col.lower().replace("_", " ").replace("-", " ")
        for pii_name in PII_COLUMN_NAMES:
            if pii_name in col_lower:
                affected_columns.add(col)
                if "column_name_match" not in pii_findings:
                    pii_findings["column_name_match"] = []
                pii_findings["column_name_match"].append({
                    "column": col,
                    "matched_pattern": pii_name
                })
    
    # Check data values for PII patterns
    sample_size = min(100, len(records))  # Sample for performance
    for record in records[:sample_size]:
        for col, value in record.items():
            if value is None:
                continue
            
            str_value = str(value)
            for pii_type, pii_info in PII_PATTERNS.items():
                if re.search(pii_info["pattern"], str_value, re.IGNORECASE):
                    affected_columns.add(col)
                    if pii_type not in pii_findings:
                        pii_findings[pii_type] = {
                            "count": 0,
                            "severity": pii_info["severity"],
                            "columns": set()
                        }
                    pii_findings[pii_type]["count"] += 1
                    pii_findings[pii_type]["columns"].add(col)
    
    # Convert sets to lists for JSON serialization
    pii_types = []
    total_pii_count = 0
    for pii_type, info in pii_findings.items():
        if pii_type == "column_name_match":
            continue
        pii_types.append({
            "type": pii_type,
            "count": info["count"],
            "severity": info["severity"],
            "columns": list(info["columns"])
        })
        total_pii_count += info["count"]
    
    return {
        "pii_detected": len(pii_findings) > 0,
        "pii_count": total_pii_count,
        "pii_types": pii_types,
        "affected_columns": list(affected_columns),
        "column_name_matches": pii_findings.get("column_name_match", [])
    }


def assess_privacy(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess privacy by detecting PII."""
    pii_result = detect_pii(data)
    
    # Score based on PII detection
    if not pii_result["pii_detected"]:
        score = 4  # No PII detected
    else:
        # Check severity
        has_critical = any(p["severity"] == "critical" for p in pii_result["pii_types"])
        has_high = any(p["severity"] == "high" for p in pii_result["pii_types"])
        
        if has_critical:
            score = 0  # Critical PII found
        elif has_high:
            score = 1  # High severity PII found
        elif pii_result["pii_count"] > 10:
            score = 2  # Multiple PII instances
        else:
            score = 3  # Minor PII concerns
    
    return {
        "score": score,
        "max_score": 4,
        "pii_detected": pii_result["pii_detected"],
        "pii_count": pii_result["pii_count"],
        "pii_types": pii_result["pii_types"],
        "affected_columns": pii_result["affected_columns"],
        "recommendation": get_privacy_recommendation(score, pii_result)
    }


def get_privacy_recommendation(score: int, pii_result: Dict[str, Any]) -> str:
    """Get privacy recommendation based on assessment."""
    if score == 4:
        return "No PII detected - data appears safe for AI/ML use"
    elif score == 0:
        return "Critical PII detected (SSN, credit card) - must anonymize or remove before use"
    elif score == 1:
        return "High severity PII detected (email, phone) - consider anonymization"
    elif score == 2:
        return "Multiple PII instances found - review and anonymize sensitive fields"
    else:
        return "Minor PII concerns - review affected columns before use"


def assess_licensing(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess licensing and usage rights."""
    # Check metadata for licensing information
    license_info = metadata.get("license")
    source = metadata.get("source")
    usage_rights = metadata.get("usage_rights")
    
    # Determine license status
    if license_info:
        # Check for common open licenses
        open_licenses = ["mit", "apache", "gpl", "bsd", "cc0", "public domain", "cc-by"]
        license_lower = license_info.lower()
        
        if any(lic in license_lower for lic in open_licenses):
            score = 4
            status = "Open license - free to use"
        elif "commercial" in license_lower or "proprietary" in license_lower:
            score = 2
            status = "Commercial license - verify usage rights"
        else:
            score = 3
            status = "License specified - review terms"
    elif usage_rights:
        score = 3
        status = "Usage rights specified - review terms"
    else:
        score = 1
        status = "No license information - usage rights unclear"
    
    return {
        "score": score,
        "max_score": 4,
        "license": license_info,
        "source": source,
        "usage_rights": usage_rights,
        "status": status,
        "recommendation": get_licensing_recommendation(score)
    }


def get_licensing_recommendation(score: int) -> str:
    """Get licensing recommendation based on assessment."""
    if score == 4:
        return "Open license allows free use for AI/ML applications"
    elif score == 3:
        return "Review license terms to ensure AI/ML use is permitted"
    elif score == 2:
        return "Commercial license - verify AI/ML usage is covered"
    else:
        return "No license information - obtain explicit permission before use"


def assess_governance(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run all governance assessments and aggregate results."""
    privacy = assess_privacy(data, metadata)
    licensing = assess_licensing(data, metadata)
    
    # Calculate total score
    total_score = privacy["score"] + licensing["score"]
    max_score = 8  # 2 criteria * 4 points each
    
    return {
        "score": total_score,
        "max_score": max_score,
        "details": {
            "privacy": privacy,
            "licensing": licensing
        },
        "criteria": [
            {
                "name": "privacy",
                "score": privacy["score"],
                "max_score": 4,
                "weight": 0.10,
                "description": "PII detection and privacy compliance"
            },
            {
                "name": "licensing",
                "score": licensing["score"],
                "max_score": 4,
                "weight": 0.05,
                "description": "Usage rights and licensing validation"
            }
        ]
    }
