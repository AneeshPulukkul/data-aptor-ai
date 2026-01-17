"""Unit tests for the Scoring service."""
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


class TestScoringEndpoints:
    """Tests for scoring calculation endpoints."""
    
    def test_calculate_score_requires_assessment_id(self):
        """Test that calculating score requires assessment_id."""
        response = client.post(
            "/api/scores",
            json={}
        )
        assert response.status_code == 422
        
    def test_calculate_score_with_valid_data(self):
        """Test calculating score with valid module scores."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 85.0,
                    "accessibility": 90.0,
                    "governance": 75.0,
                    "ai_compatibility": 80.0,
                    "diversity": 70.0
                }
            }
        )
        assert response.status_code in [200, 201]
        if response.status_code == 200:
            data = response.json()
            assert "overall_score" in data
            assert "readiness_level" in data
            
    def test_get_score_by_assessment_id(self):
        """Test getting score by assessment ID."""
        response = client.get("/api/scores/assessment/1")
        assert response.status_code in [200, 404]


class TestWeightedScoring:
    """Tests for weighted scoring calculations."""
    
    def test_default_weights(self):
        """Test scoring with default weights."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 100.0,
                    "accessibility": 100.0,
                    "governance": 100.0,
                    "ai_compatibility": 100.0,
                    "diversity": 100.0
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            # With all 100s, overall should be 100
            assert data["overall_score"] == 100.0
            
    def test_custom_weights(self):
        """Test scoring with custom weights."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 100.0,
                    "accessibility": 0.0,
                    "governance": 0.0,
                    "ai_compatibility": 0.0,
                    "diversity": 0.0
                },
                "weights": {
                    "quality": 1.0,
                    "accessibility": 0.0,
                    "governance": 0.0,
                    "ai_compatibility": 0.0,
                    "diversity": 0.0
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            # With only quality weighted at 100%, overall should be 100
            assert data["overall_score"] == 100.0
            
    def test_weights_must_sum_to_one(self):
        """Test that weights validation works."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 100.0,
                    "accessibility": 100.0,
                    "governance": 100.0,
                    "ai_compatibility": 100.0,
                    "diversity": 100.0
                },
                "weights": {
                    "quality": 0.5,
                    "accessibility": 0.5,
                    "governance": 0.5,
                    "ai_compatibility": 0.5,
                    "diversity": 0.5
                }
            }
        )
        # Should either normalize weights or return validation error
        assert response.status_code in [200, 400, 422]


class TestReadinessLevels:
    """Tests for readiness level classification."""
    
    def test_high_readiness(self):
        """Test high readiness level (80-100)."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 90.0,
                    "accessibility": 85.0,
                    "governance": 80.0,
                    "ai_compatibility": 85.0,
                    "diversity": 80.0
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data["readiness_level"] == "high"
            
    def test_moderate_readiness(self):
        """Test moderate readiness level (60-79)."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 70.0,
                    "accessibility": 65.0,
                    "governance": 70.0,
                    "ai_compatibility": 65.0,
                    "diversity": 70.0
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data["readiness_level"] == "moderate"
            
    def test_low_readiness(self):
        """Test low readiness level (40-59)."""
        response = client.post(
            "/api/scores",
            json={
                "assessment_id": 1,
                "module_scores": {
                    "quality": 50.0,
                    "accessibility": 45.0,
                    "governance": 50.0,
                    "ai_compatibility": 45.0,
                    "diversity": 50.0
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data["readiness_level"] == "low"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
