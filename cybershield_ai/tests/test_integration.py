"""
Integration tests for CyberShield AI
"""

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import app

class TestIntegration:
    """Integration tests for CyberShield AI platform"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check_integration(self, client):
        """Test health check integration"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_endpoints_integration(self, client):
        """Test all API endpoints integration"""
        endpoints = [
            "/api/v1/vulnerabilities",
            "/api/v1/assets", 
            "/api/v1/threat-intelligence/indicators",
            "/api/v1/incidents",
            "/api/v1/compliance/status",
            "/api/v1/dashboard/overview",
            "/api/v1/config"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    def test_cors_integration(self, client):
        """Test CORS integration"""
        response = client.options("/api/v1/health")
        assert response.status_code == 200
    
    def test_error_handling_integration(self, client):
        """Test error handling integration"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404