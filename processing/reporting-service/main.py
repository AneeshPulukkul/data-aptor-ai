"""
Reporting Service for DataAptor AI

This service generates reports and visualizations for assessment results.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from datetime import datetime
import json

app = FastAPI(
    title="DataAptor AI Reporting Service",
    description="Reporting service for generating assessment reports",
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

# In-memory storage for reports
reports_store: Dict[int, Dict[str, Any]] = {}
report_counter = 0


class ReportRequest(BaseModel):
    assessment_id: int
    results: Dict[str, Any]
    scores: Dict[str, Any]


class ReportSummary(BaseModel):
    id: int
    assessment_id: int
    created_at: str
    overall_score: float
    readiness_level: str


class ReportResponse(BaseModel):
    id: int
    assessment_id: int
    created_at: str
    summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    export_formats: List[str]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "reporting-service"}


def generate_recommendations(results: Dict[str, Any], scores: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendations based on assessment results."""
    recommendations = []
    
    # Quality recommendations
    if "quality" in results:
        quality = results["quality"]
        details = quality.get("details", {})
        
        # Completeness
        completeness = details.get("completeness", {})
        if completeness.get("missing_percentage", 0) > 5:
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "issue": "Missing values detected",
                "description": f"{completeness.get('missing_percentage', 0)}% of values are missing",
                "action": "Implement data imputation or collect missing values",
                "impact": "Improves model accuracy and reliability"
            })
        
        # Accuracy
        accuracy = details.get("accuracy", {})
        if accuracy.get("outliers_detected", 0) > 0:
            recommendations.append({
                "category": "quality",
                "priority": "medium",
                "issue": "Outliers detected",
                "description": f"{accuracy.get('outliers_detected', 0)} outliers found in the data",
                "action": "Review and handle outliers appropriately",
                "impact": "Reduces noise and improves model performance"
            })
    
    # Accessibility recommendations
    if "accessibility" in results:
        accessibility = results["accessibility"]
        details = accessibility.get("details", {})
        
        volume = details.get("volume", {})
        if volume.get("ratio", 1) < 1:
            recommendations.append({
                "category": "accessibility",
                "priority": "high",
                "issue": "Insufficient sample size",
                "description": f"Current sample is {volume.get('ratio', 0)*100:.0f}% of recommended minimum",
                "action": "Collect more data samples or use data augmentation",
                "impact": "Improves model generalization"
            })
    
    # Governance recommendations
    if "governance" in results:
        governance = results["governance"]
        details = governance.get("details", {})
        
        privacy = details.get("privacy", {})
        if privacy.get("pii_detected", False):
            recommendations.append({
                "category": "governance",
                "priority": "critical",
                "issue": "PII detected in dataset",
                "description": f"Found {privacy.get('pii_count', 0)} instances of personally identifiable information",
                "action": "Anonymize or remove PII before using for AI/ML",
                "impact": "Ensures compliance and protects privacy"
            })
        
        licensing = details.get("licensing", {})
        if licensing.get("score", 4) < 3:
            recommendations.append({
                "category": "governance",
                "priority": "high",
                "issue": "Licensing concerns",
                "description": licensing.get("status", "License information unclear"),
                "action": "Verify usage rights for AI/ML applications",
                "impact": "Ensures legal compliance"
            })
    
    # AI Compatibility recommendations
    if "ai_compatibility" in results:
        ai_compat = results["ai_compatibility"]
        details = ai_compat.get("details", {})
        
        labeling = details.get("labeling", {})
        if labeling.get("score", 4) < 3:
            recommendations.append({
                "category": "ai_compatibility",
                "priority": "medium",
                "issue": "Label quality concerns",
                "description": "Labels may have quality or coverage issues",
                "action": "Review and improve label quality",
                "impact": "Improves supervised learning performance"
            })
        
        preprocessing = details.get("preprocessing", {})
        if preprocessing.get("estimated_effort", "minimal") in ["high", "very_high"]:
            recommendations.append({
                "category": "ai_compatibility",
                "priority": "medium",
                "issue": "Significant preprocessing required",
                "description": f"{preprocessing.get('task_count', 0)} preprocessing tasks identified",
                "action": "Plan for data preprocessing pipeline",
                "impact": "Prepares data for ML algorithms"
            })
    
    # Diversity recommendations
    if "diversity" in results:
        diversity = results["diversity"]
        details = diversity.get("details", {})
        
        bias = details.get("bias", {})
        if bias.get("bias_indicators", []):
            recommendations.append({
                "category": "diversity",
                "priority": "high",
                "issue": "Potential bias detected",
                "description": f"{len(bias.get('bias_indicators', []))} bias indicators found",
                "action": "Implement bias mitigation strategies",
                "impact": "Ensures fair and equitable AI models"
            })
        
        representativeness = details.get("representativeness", {})
        if representativeness.get("score", 4) < 3:
            recommendations.append({
                "category": "diversity",
                "priority": "medium",
                "issue": "Low sample diversity",
                "description": "Data may not be representative of target population",
                "action": "Collect more diverse samples",
                "impact": "Improves model generalization across populations"
            })
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return recommendations


def generate_summary(results: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a summary of the assessment."""
    overall_score = scores.get("overall_score", 0)
    readiness_level = scores.get("readiness_level", "unknown")
    
    # Count issues by severity
    critical_issues = 0
    high_issues = 0
    medium_issues = 0
    
    for module, result in results.items():
        if isinstance(result, dict):
            score = result.get("score", 0)
            max_score = result.get("max_score", 1)
            normalized = (score / max_score * 100) if max_score > 0 else 0
            
            if normalized < 25:
                critical_issues += 1
            elif normalized < 50:
                high_issues += 1
            elif normalized < 75:
                medium_issues += 1
    
    return {
        "overall_score": overall_score,
        "readiness_level": readiness_level,
        "readiness_description": scores.get("readiness_description", ""),
        "modules_assessed": len(results),
        "critical_issues": critical_issues,
        "high_issues": high_issues,
        "medium_issues": medium_issues,
        "assessment_complete": True
    }


@app.post("/api/reporting/{dataset_id}", response_model=ReportResponse)
async def generate_report(dataset_id: int, request: ReportRequest):
    """Generate a comprehensive report for an assessment."""
    global report_counter
    
    report_counter += 1
    report_id = report_counter
    
    # Generate report components
    summary = generate_summary(request.results, request.scores)
    recommendations = generate_recommendations(request.results, request.scores)
    
    report = {
        "id": report_id,
        "assessment_id": request.assessment_id,
        "dataset_id": dataset_id,
        "created_at": datetime.utcnow().isoformat(),
        "summary": summary,
        "detailed_results": request.results,
        "scores": request.scores,
        "recommendations": recommendations,
        "export_formats": ["json", "csv", "pdf", "html"]
    }
    
    reports_store[report_id] = report
    
    return ReportResponse(
        id=report_id,
        assessment_id=request.assessment_id,
        created_at=report["created_at"],
        summary=summary,
        detailed_results=request.results,
        recommendations=recommendations,
        export_formats=["json", "csv", "pdf", "html"]
    )


@app.get("/api/reporting/{assessment_id}")
async def get_report(assessment_id: int):
    """Get the report for an assessment."""
    for report in reports_store.values():
        if report["assessment_id"] == assessment_id:
            return report
    
    raise HTTPException(status_code=404, detail="Report not found")


@app.get("/api/reporting/{assessment_id}/export")
async def export_report(assessment_id: int, format: str = "json"):
    """Export the report in the specified format."""
    report = None
    for r in reports_store.values():
        if r["assessment_id"] == assessment_id:
            report = r
            break
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if format == "json":
        return JSONResponse(content=report)
    
    elif format == "csv":
        # Generate CSV format
        csv_data = generate_csv_report(report)
        return {
            "format": "csv",
            "content": csv_data,
            "filename": f"report_{assessment_id}.csv"
        }
    
    elif format == "html":
        # Generate HTML format
        html_data = generate_html_report(report)
        return {
            "format": "html",
            "content": html_data,
            "filename": f"report_{assessment_id}.html"
        }
    
    elif format == "pdf":
        # PDF generation would require additional libraries
        return {
            "format": "pdf",
            "message": "PDF export requires additional processing",
            "fallback": "json",
            "content": report
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Supported: json, csv, html, pdf"
        )


def generate_csv_report(report: Dict[str, Any]) -> str:
    """Generate CSV format report."""
    lines = []
    
    # Header
    lines.append("DataAptor AI Assessment Report")
    lines.append(f"Assessment ID,{report['assessment_id']}")
    lines.append(f"Generated,{report['created_at']}")
    lines.append("")
    
    # Summary
    summary = report.get("summary", {})
    lines.append("Summary")
    lines.append(f"Overall Score,{summary.get('overall_score', 0)}")
    lines.append(f"Readiness Level,{summary.get('readiness_level', 'unknown')}")
    lines.append(f"Critical Issues,{summary.get('critical_issues', 0)}")
    lines.append(f"High Issues,{summary.get('high_issues', 0)}")
    lines.append(f"Medium Issues,{summary.get('medium_issues', 0)}")
    lines.append("")
    
    # Module Scores
    lines.append("Module Scores")
    lines.append("Module,Score,Max Score,Normalized")
    for module, result in report.get("detailed_results", {}).items():
        if isinstance(result, dict):
            score = result.get("score", 0)
            max_score = result.get("max_score", 1)
            normalized = (score / max_score * 100) if max_score > 0 else 0
            lines.append(f"{module},{score},{max_score},{normalized:.1f}%")
    lines.append("")
    
    # Recommendations
    lines.append("Recommendations")
    lines.append("Priority,Category,Issue,Action")
    for rec in report.get("recommendations", []):
        lines.append(f"{rec['priority']},{rec['category']},{rec['issue']},{rec['action']}")
    
    return "\n".join(lines)


def generate_html_report(report: Dict[str, Any]) -> str:
    """Generate HTML format report."""
    summary = report.get("summary", {})
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>DataAptor AI Assessment Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .score {{ font-size: 48px; font-weight: bold; color: #2196F3; }}
        .level {{ font-size: 24px; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        .critical {{ color: #f44336; }}
        .high {{ color: #ff9800; }}
        .medium {{ color: #2196F3; }}
        .low {{ color: #4caf50; }}
    </style>
</head>
<body>
    <h1>DataAptor AI Assessment Report</h1>
    <p>Assessment ID: {report['assessment_id']} | Generated: {report['created_at']}</p>
    
    <div class="summary">
        <div class="score">{summary.get('overall_score', 0)}/100</div>
        <div class="level">{summary.get('readiness_level', 'Unknown').upper()}</div>
        <p>{summary.get('readiness_description', '')}</p>
    </div>
    
    <h2>Module Scores</h2>
    <table>
        <tr><th>Module</th><th>Score</th><th>Max Score</th><th>Normalized</th></tr>
"""
    
    for module, result in report.get("detailed_results", {}).items():
        if isinstance(result, dict):
            score = result.get("score", 0)
            max_score = result.get("max_score", 1)
            normalized = (score / max_score * 100) if max_score > 0 else 0
            html += f"        <tr><td>{module.title()}</td><td>{score}</td><td>{max_score}</td><td>{normalized:.1f}%</td></tr>\n"
    
    html += """    </table>
    
    <h2>Recommendations</h2>
    <table>
        <tr><th>Priority</th><th>Category</th><th>Issue</th><th>Action</th></tr>
"""
    
    for rec in report.get("recommendations", []):
        priority_class = rec['priority']
        html += f"        <tr><td class='{priority_class}'>{rec['priority'].upper()}</td><td>{rec['category'].title()}</td><td>{rec['issue']}</td><td>{rec['action']}</td></tr>\n"
    
    html += """    </table>
</body>
</html>"""
    
    return html


@app.get("/api/reporting")
async def list_reports(skip: int = 0, limit: int = 100):
    """List all reports."""
    reports = list(reports_store.values())
    return reports[skip:skip + limit]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
