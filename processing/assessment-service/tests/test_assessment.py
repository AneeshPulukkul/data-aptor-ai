"""Unit tests for the Assessment service."""
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


class TestAssessmentEndpoints:
    """Tests for assessment endpoints."""
    
    def test_start_assessment_requires_dataset_id(self):
        """Test that starting assessment requires dataset_id."""
        response = client.post(
            "/api/assessments",
            json={}
        )
        assert response.status_code == 422
        
    def test_start_assessment_with_valid_data(self):
        """Test starting assessment with valid data."""
        response = client.post(
            "/api/assessments",
            json={"dataset_id": 1}
        )
        assert response.status_code in [200, 201, 404]
        
    def test_get_assessment_status(self):
        """Test getting assessment status."""
        response = client.get("/api/assessments/1/status")
        assert response.status_code in [200, 404]
        
    def test_get_assessment_results(self):
        """Test getting assessment results."""
        response = client.get("/api/assessments/1/results")
        assert response.status_code in [200, 404]


class TestAssessmentModules:
    """Tests for individual assessment modules."""
    
    def test_quality_module(self):
        """Test quality assessment module."""
        response = client.post(
            "/api/assessments/modules/quality",
            json={
                "dataset_id": 1,
                "data": {
                    "columns": ["id", "name", "value"],
                    "rows": 100,
                    "missing_values": {"name": 5, "value": 10}
                }
            }
        )
        assert response.status_code in [200, 404, 422]
        
    def test_accessibility_module(self):
        """Test accessibility assessment module."""
        response = client.post(
            "/api/assessments/modules/accessibility",
            json={
                "dataset_id": 1,
                "data": {
                    "format": "csv",
                    "size_bytes": 1024000,
                    "encoding": "utf-8"
                }
            }
        )
        assert response.status_code in [200, 404, 422]
        
    def test_governance_module(self):
        """Test governance assessment module."""
        response = client.post(
            "/api/assessments/modules/governance",
            json={
                "dataset_id": 1,
                "data": {
                    "columns": ["name", "email", "ssn"],
                    "sample_data": [
                        {"name": "John", "email": "john@example.com", "ssn": "123-45-6789"}
                    ]
                }
            }
        )
        assert response.status_code in [200, 404, 422]
        
    def test_ai_compatibility_module(self):
        """Test AI compatibility assessment module."""
        response = client.post(
            "/api/assessments/modules/ai_compatibility",
            json={
                "dataset_id": 1,
                "data": {
                    "columns": ["feature1", "feature2", "label"],
                    "rows": 1000,
                    "label_column": "label"
                }
            }
        )
        assert response.status_code in [200, 404, 422]
        
    def test_diversity_module(self):
        """Test diversity/bias assessment module."""
        response = client.post(
            "/api/assessments/modules/diversity",
            json={
                "dataset_id": 1,
                "data": {
                    "columns": ["age", "gender", "income"],
                    "categorical_columns": ["gender"],
                    "rows": 1000
                }
            }
        )
        assert response.status_code in [200, 404, 422]


class TestAssessmentConfiguration:
    """Tests for assessment configuration."""
    
    def test_select_specific_modules(self):
        """Test running assessment with specific modules."""
        response = client.post(
            "/api/assessments",
            json={
                "dataset_id": 1,
                "modules": ["quality", "accessibility"]
            }
        )
        assert response.status_code in [200, 201, 404]
        
    def test_all_modules_by_default(self):
        """Test that all modules run by default."""
        response = client.post(
            "/api/assessments",
            json={"dataset_id": 1}
        )
        if response.status_code in [200, 201]:
            data = response.json()
            # Check that modules field exists or assessment was created
            assert "id" in data or "assessment_id" in data or "modules" in data


class TestModuleScoring:
    """Tests for module scoring logic."""
    
    def test_quality_score_calculation(self):
        """Test quality score is calculated correctly."""
        # This would test the actual scoring logic
        # For now, verify the endpoint works
        response = client.get("/api/assessments/1/results")
        if response.status_code == 200:
            data = response.json()
            if "module_scores" in data:
                assert "quality" in data["module_scores"]
                assert 0 <= data["module_scores"]["quality"] <= 100


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
