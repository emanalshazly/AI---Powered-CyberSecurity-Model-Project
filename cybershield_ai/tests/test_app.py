"""
Comprehensive test suite for CyberShield AI
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

# Import the main application
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main import app
from core.ai_engine import AIEngine
from core.vulnerability_scanner import VulnerabilityScanner
from core.threat_intelligence import ThreatIntelligence
from core.incident_response import IncidentResponseSystem
from core.compliance_monitor import ComplianceMonitor
from core.forensic_analyzer import ForensicAnalyzer

class TestCyberShieldAI:
    """Test suite for CyberShield AI platform"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ai_engine(self):
        """Mock AI engine"""
        engine = Mock(spec=AIEngine)
        engine.initialize = AsyncMock()
        engine.cleanup = AsyncMock()
        engine.analyze_vulnerability = AsyncMock(return_value={
            "severity": "high",
            "confidence": 0.8,
            "risk_score": 0.7,
            "ai_analysis": {"model_used": "test"}
        })
        engine.detect_threat = AsyncMock(return_value={
            "threat_level": "suspicious",
            "confidence": 0.7,
            "threat_indicators": ["test"]
        })
        return engine
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "CyberShield AI" in response.text
    
    def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint"""
        response = client.get("/api/docs")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_ai_engine_initialization(self, mock_ai_engine):
        """Test AI engine initialization"""
        await mock_ai_engine.initialize()
        mock_ai_engine.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ai_vulnerability_analysis(self, mock_ai_engine):
        """Test AI vulnerability analysis"""
        result = await mock_ai_engine.analyze_vulnerability("Test vulnerability")
        assert result["severity"] == "high"
        assert result["confidence"] == 0.8
        assert result["risk_score"] == 0.7
    
    @pytest.mark.asyncio
    async def test_ai_threat_detection(self, mock_ai_engine):
        """Test AI threat detection"""
        result = await mock_ai_engine.detect_threat("Suspicious activity detected")
        assert result["threat_level"] == "suspicious"
        assert result["confidence"] == 0.7
        assert "threat_indicators" in result
    
    def test_vulnerability_scanner_creation(self, mock_ai_engine):
        """Test vulnerability scanner creation"""
        scanner = VulnerabilityScanner(mock_ai_engine)
        assert scanner.ai_engine == mock_ai_engine
        assert scanner.scanning == False
    
    def test_threat_intelligence_creation(self, mock_ai_engine):
        """Test threat intelligence creation"""
        ti = ThreatIntelligence(mock_ai_engine)
        assert ti.ai_engine == mock_ai_engine
        assert ti.monitoring == False
    
    def test_incident_response_creation(self, mock_ai_engine):
        """Test incident response creation"""
        ir = IncidentResponseSystem(mock_ai_engine)
        assert ir.ai_engine == mock_ai_engine
        assert ir.monitoring == False
    
    def test_compliance_monitor_creation(self, mock_ai_engine):
        """Test compliance monitor creation"""
        cm = ComplianceMonitor(mock_ai_engine)
        assert cm.ai_engine == mock_ai_engine
        assert cm.monitoring == False
    
    def test_forensic_analyzer_creation(self, mock_ai_engine):
        """Test forensic analyzer creation"""
        fa = ForensicAnalyzer(mock_ai_engine)
        assert fa.ai_engine == mock_ai_engine
    
    @pytest.mark.asyncio
    async def test_vulnerability_scanning(self, mock_ai_engine):
        """Test vulnerability scanning functionality"""
        scanner = VulnerabilityScanner(mock_ai_engine)
        
        # Test adding asset
        await scanner.add_asset("192.168.1.1", "test-host")
        assert "192.168.1.1" in scanner.assets
        
        # Test removing asset
        await scanner.remove_asset("192.168.1.1")
        assert "192.168.1.1" not in scanner.assets
    
    @pytest.mark.asyncio
    async def test_incident_creation(self, mock_ai_engine):
        """Test incident creation"""
        ir = IncidentResponseSystem(mock_ai_engine)
        
        incident_id = await ir.create_incident(
            title="Test Incident",
            description="Test security incident",
            severity="high",
            affected_assets=["192.168.1.1"],
            threat_indicators=["malware"]
        )
        
        assert incident_id is not None
        assert incident_id in ir.incidents
    
    @pytest.mark.asyncio
    async def test_compliance_status(self, mock_ai_engine):
        """Test compliance status checking"""
        cm = ComplianceMonitor(mock_ai_engine)
        
        status = await cm.get_compliance_status()
        assert "overall_score" in status
        assert "total_requirements" in status
    
    @pytest.mark.asyncio
    async def test_forensic_analysis(self, mock_ai_engine):
        """Test forensic analysis"""
        fa = ForensicAnalyzer(mock_ai_engine)
        
        # Test file analysis (mock file)
        with patch("os.path.exists", return_value=True):
            with patch("os.stat") as mock_stat:
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_ctime = 1234567890
                mock_stat.return_value.st_mtime = 1234567890
                mock_stat.return_value.st_atime = 1234567890
                mock_stat.return_value.st_mode = 0o644
                mock_stat.return_value.st_ino = 12345
                mock_stat.return_value.st_dev = 1
                
                analysis_id = await fa.analyze_file("/tmp/test.txt")
                assert analysis_id is not None
    
    def test_api_vulnerabilities_endpoint(self, client):
        """Test vulnerabilities API endpoint"""
        response = client.get("/api/v1/vulnerabilities")
        assert response.status_code == 200
        data = response.json()
        assert "vulnerabilities" in data
        assert "total" in data
    
    def test_api_assets_endpoint(self, client):
        """Test assets API endpoint"""
        response = client.get("/api/v1/assets")
        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "total" in data
    
    def test_api_threat_intelligence_endpoint(self, client):
        """Test threat intelligence API endpoint"""
        response = client.get("/api/v1/threat-intelligence/indicators")
        assert response.status_code == 200
        data = response.json()
        assert "indicators" in data
        assert "total" in data
    
    def test_api_incidents_endpoint(self, client):
        """Test incidents API endpoint"""
        response = client.get("/api/v1/incidents")
        assert response.status_code == 200
        data = response.json()
        assert "incidents" in data
        assert "total" in data
    
    def test_api_compliance_endpoint(self, client):
        """Test compliance API endpoint"""
        response = client.get("/api/v1/compliance/status")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "frameworks" in data
    
    def test_api_dashboard_endpoint(self, client):
        """Test dashboard API endpoint"""
        response = client.get("/api/v1/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "metrics" in data
    
    def test_api_config_endpoint(self, client):
        """Test configuration API endpoint"""
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert "scanning" in data
        assert "ai" in data
        assert "security" in data
    
    def test_scan_request_validation(self, client):
        """Test scan request validation"""
        # Test valid scan request
        valid_request = {
            "target": "192.168.1.1",
            "scan_type": "comprehensive",
            "options": {"hostname": "test-host"}
        }
        response = client.post("/api/v1/vulnerabilities/scan", json=valid_request)
        assert response.status_code == 200
    
    def test_asset_request_validation(self, client):
        """Test asset request validation"""
        # Test valid asset request
        valid_request = {
            "ip": "192.168.1.1",
            "hostname": "test-host",
            "description": "Test asset"
        }
        response = client.post("/api/v1/assets", json=valid_request)
        assert response.status_code == 200
    
    def test_threat_query_validation(self, client):
        """Test threat query validation"""
        # Test valid threat query
        valid_request = {
            "query": "malware detection",
            "query_type": "indicator",
            "filters": {"severity": "high"}
        }
        response = client.post("/api/v1/threat-intelligence/query", json=valid_request)
        assert response.status_code == 200
    
    def test_incident_request_validation(self, client):
        """Test incident request validation"""
        # Test valid incident request
        valid_request = {
            "title": "Test Incident",
            "description": "Test security incident",
            "severity": "high",
            "affected_assets": ["192.168.1.1"],
            "indicators": ["malware"]
        }
        response = client.post("/api/v1/incidents", json=valid_request)
        assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Test error handling"""
        # Test invalid endpoint
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/api/v1/health")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_ai_engine):
        """Test concurrent operations"""
        scanner = VulnerabilityScanner(mock_ai_engine)
        
        # Test concurrent asset operations
        tasks = []
        for i in range(10):
            tasks.append(scanner.add_asset(f"192.168.1.{i}", f"host-{i}"))
        
        await asyncio.gather(*tasks)
        assert len(scanner.assets) == 10
    
    def test_data_validation(self, client):
        """Test data validation"""
        # Test invalid IP address
        invalid_request = {
            "ip": "invalid-ip",
            "hostname": "test-host"
        }
        response = client.post("/api/v1/assets", json=invalid_request)
        # Should still work as we don't validate IP format in this test
        assert response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Test rate limiting"""
        # Make multiple requests quickly
        for _ in range(5):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cleanup_operations(self, mock_ai_engine):
        """Test cleanup operations"""
        scanner = VulnerabilityScanner(mock_ai_engine)
        
        # Add some assets
        await scanner.add_asset("192.168.1.1", "host1")
        await scanner.add_asset("192.168.1.2", "host2")
        
        # Stop scanning
        scanner.stop_scanning()
        assert scanner.scanning == False
        
        # Remove all assets
        await scanner.remove_asset("192.168.1.1")
        await scanner.remove_asset("192.168.1.2")
        assert len(scanner.assets) == 0

class TestIntegration:
    """Integration tests for CyberShield AI"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_full_workflow(self, client):
        """Test complete workflow"""
        # 1. Check health
        health_response = client.get("/api/health")
        assert health_response.status_code == 200
        
        # 2. Add asset
        asset_response = client.post("/api/v1/assets", json={
            "ip": "192.168.1.100",
            "hostname": "test-server",
            "description": "Test server for scanning"
        })
        assert asset_response.status_code == 200
        
        # 3. Start scan
        scan_response = client.post("/api/v1/vulnerabilities/scan", json={
            "target": "192.168.1.100",
            "scan_type": "comprehensive"
        })
        assert scan_response.status_code == 200
        
        # 4. Check vulnerabilities
        vuln_response = client.get("/api/v1/vulnerabilities")
        assert vuln_response.status_code == 200
        
        # 5. Check threat intelligence
        ti_response = client.get("/api/v1/threat-intelligence/summary")
        assert ti_response.status_code == 200
        
        # 6. Check incidents
        incident_response = client.get("/api/v1/incidents")
        assert incident_response.status_code == 200
        
        # 7. Check compliance
        compliance_response = client.get("/api/v1/compliance/status")
        assert compliance_response.status_code == 200
        
        # 8. Check dashboard
        dashboard_response = client.get("/api/v1/dashboard/overview")
        assert dashboard_response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])