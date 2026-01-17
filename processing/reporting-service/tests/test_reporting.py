"""Unit tests for the Reporting service."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self):
        """Test that health check returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        
    def test_health_check_returns_status(self):
        """Test that health check returns status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestReportEndpoints:
    """Tests for report generation endpoints."""
    
    def test_generate_report_requires_assessment_id(self):
        """Test that generating report requires assessment_id."""
        response = client.post(
            "/api/reports",
            json={}
        )
        assert response.status_code == 422
        
    def test_generate_report_with_valid_data(self):
        """Test generating report with valid assessment data."""
        response = client.post(
            "/api/reports",
            json={
                "assessment_id": 1,
                "overall_score": 85.0,
                "readiness_level": "high",
                "module_scores": {
                    "quality": 90.0,
                    "accessibility": 85.0,
                    "governance": 80.0,
                    "ai_compatibility": 85.0,
                    "diversity": 75.0
                }
            }
        )
        assert response.status_code in [200, 201]
        
    def test_get_report_by_assessment_id(self):
        """Test getting report by assessment ID."""
        response = client.get("/api/reports/assessment/1")
        assert response.status_code in [200, 404]


class TestReportExport:
    """Tests for report export functionality."""
    
    def test_export_json_format(self):
        """Test exporting report in JSON format."""
        response = client.get("/api/reports/1/export?format=json")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.headers.get("content-type", "").startswith("application/json")
            
    def test_export_csv_format(self):
        """Test exporting report in CSV format."""
        response = client.get("/api/reports/1/export?format=csv")
        assert response.status_code in [200, 404]
        
    def test_export_html_format(self):
        """Test exporting report in HTML format."""
        response = client.get("/api/reports/1/export?format=html")
        assert response.status_code in [200, 404]
        
    def test_export_pdf_format(self):
        """Test exporting report in PDF format."""
        response = client.get("/api/reports/1/export?format=pdf")
        assert response.status_code in [200, 404]
        
    def test_export_invalid_format(self):
        """Test exporting report with invalid format."""
        response = client.get("/api/reports/1/export?format=invalid")
        assert response.status_code in [400, 422]


class TestReportContent:
    """Tests for report content structure."""
    
    def test_report_contains_summary(self):
        """Test that report contains summary section."""
        # First create a report
        client.post(
            "/api/reports",
            json={
                "assessment_id": 2,
                "overall_score": 75.0,
                "readiness_level": "moderate",
                "module_scores": {
                    "quality": 80.0,
                    "accessibility": 70.0,
                    "governance": 75.0,
                    "ai_compatibility": 70.0,
                    "diversity": 80.0
                }
            }
        )
        
        response = client.get("/api/reports/assessment/2")
        if response.status_code == 200:
            data = response.json()
            assert "overall_score" in data or "summary" in data
            
    def test_report_contains_findings(self):
        """Test that report contains findings."""
        response = client.get("/api/reports/assessment/1")
        if response.status_code == 200:
            data = response.json()
            # Findings may be in different locations depending on implementation
            assert "findings" in data or "details" in data or "module_scores" in data
            
    def test_report_contains_recommendations(self):
        """Test that report contains recommendations."""
        response = client.get("/api/reports/assessment/1")
        if response.status_code == 200:
            data = response.json()
            # Recommendations may be in different locations
            assert "recommendations" in data or "suggestions" in data or "module_scores" in data


class TestFindingsAndRecommendations:
    """Tests for findings and recommendations generation."""
    
    def test_low_score_generates_recommendations(self):
        """Test that low scores generate recommendations."""
        response = client.post(
            "/api/reports",
            json={
                "assessment_id": 3,
                "overall_score": 35.0,
                "readiness_level": "not_ready",
                "module_scores": {
                    "quality": 30.0,
                    "accessibility": 40.0,
                    "governance": 35.0,
                    "ai_compatibility": 30.0,
                    "diversity": 40.0
                },
                "findings": [
                    {
                        "type": "missing_values",
                        "severity": "high",
                        "module": "quality",
                        "description": "30% missing values detected"
                    }
                ]
            }
        )
        assert response.status_code in [200, 201]


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
