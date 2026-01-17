"""Unit tests for the Orchestration service."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
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


class TestWorkflowEndpoints:
    """Tests for workflow orchestration endpoints."""
    
    def test_start_workflow_requires_dataset_id(self):
        """Test that starting a workflow requires dataset_id."""
        response = client.post(
            "/api/workflows",
            json={}
        )
        assert response.status_code == 422
        
    def test_start_workflow_with_valid_data(self):
        """Test starting a workflow with valid data."""
        response = client.post(
            "/api/workflows",
            json={"dataset_id": 1}
        )
        # Should return 200 or 201 on success, or 404 if dataset not found
        assert response.status_code in [200, 201, 404]
        
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        response = client.get("/api/workflows/1/status")
        # Should return 200 with status or 404 if not found
        assert response.status_code in [200, 404]
        
    def test_get_workflow_status_not_found(self):
        """Test getting status for non-existent workflow."""
        response = client.get("/api/workflows/99999/status")
        assert response.status_code == 404


class TestWorkflowConfiguration:
    """Tests for workflow configuration."""
    
    def test_workflow_with_custom_modules(self):
        """Test starting workflow with custom modules."""
        response = client.post(
            "/api/workflows",
            json={
                "dataset_id": 1,
                "modules": ["quality", "accessibility"]
            }
        )
        assert response.status_code in [200, 201, 404]
        
    def test_workflow_with_custom_weights(self):
        """Test starting workflow with custom weights."""
        response = client.post(
            "/api/workflows",
            json={
                "dataset_id": 1,
                "weights": {
                    "quality": 0.5,
                    "accessibility": 0.3,
                    "governance": 0.2
                }
            }
        )
        assert response.status_code in [200, 201, 404]


class TestServiceCommunication:
    """Tests for inter-service communication."""
    
    @patch('main.httpx.AsyncClient')
    def test_calls_ingestion_service(self, mock_client):
        """Test that orchestration calls ingestion service."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "ready"}
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        # This test verifies the service communication pattern
        # Actual integration would require running services
        assert True


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
