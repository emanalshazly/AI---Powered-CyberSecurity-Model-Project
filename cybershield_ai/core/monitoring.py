"""
Monitoring and Metrics System
Comprehensive monitoring for CyberShield AI
"""

import logging
import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
from prometheus_client.core import CollectorRegistry
import structlog

logger = structlog.get_logger()

# Prometheus metrics
vulnerability_scans_total = Counter('vulnerability_scans_total', 'Total vulnerability scans', ['status'])
threat_indicators_total = Counter('threat_indicators_total', 'Total threat indicators', ['type', 'severity'])
incidents_total = Counter('incidents_total', 'Total security incidents', ['severity', 'status'])
compliance_checks_total = Counter('compliance_checks_total', 'Total compliance checks', ['framework', 'status'])
forensic_analyses_total = Counter('forensic_analyses_total', 'Total forensic analyses', ['type', 'status'])

scan_duration = Histogram('scan_duration_seconds', 'Time spent on vulnerability scans', ['scan_type'])
ai_analysis_duration = Histogram('ai_analysis_duration_seconds', 'Time spent on AI analysis', ['analysis_type'])
incident_response_duration = Histogram('incident_response_duration_seconds', 'Time spent on incident response')

system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percentage')
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage percentage')

active_scans = Gauge('active_scans', 'Number of active vulnerability scans')
active_incidents = Gauge('active_incidents', 'Number of active security incidents')
total_assets = Gauge('total_assets', 'Total number of monitored assets')
total_vulnerabilities = Gauge('total_vulnerabilities', 'Total number of vulnerabilities')

def setup_monitoring():
    """Setup monitoring and metrics collection"""
    try:
        # Start Prometheus metrics server
        start_http_server(9090)
        logger.info("✅ Prometheus metrics server started on port 9090")
        
        # Start system monitoring
        asyncio.create_task(monitor_system_resources())
        
        logger.info("✅ Monitoring system initialized")
        
    except Exception as e:
        logger.error(f"Failed to setup monitoring: {e}")

async def monitor_system_resources():
    """Monitor system resources"""
    while True:
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            system_disk_usage.set(disk_percent)
            
            # Log resource usage
            logger.info("System resources", 
                       cpu_percent=cpu_percent, 
                       memory_percent=memory.percent, 
                       disk_percent=disk_percent)
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error monitoring system resources: {e}")
            await asyncio.sleep(60)

def record_vulnerability_scan(status: str, scan_type: str = "comprehensive", duration: float = 0.0):
    """Record vulnerability scan metrics"""
    vulnerability_scans_total.labels(status=status).inc()
    scan_duration.labels(scan_type=scan_type).observe(duration)

def record_threat_indicator(indicator_type: str, severity: str):
    """Record threat indicator metrics"""
    threat_indicators_total.labels(type=indicator_type, severity=severity).inc()

def record_incident(severity: str, status: str):
    """Record incident metrics"""
    incidents_total.labels(severity=severity, status=status).inc()

def record_compliance_check(framework: str, status: str):
    """Record compliance check metrics"""
    compliance_checks_total.labels(framework=framework, status=status).inc()

def record_forensic_analysis(analysis_type: str, status: str):
    """Record forensic analysis metrics"""
    forensic_analyses_total.labels(type=analysis_type, status=status).inc()

def record_ai_analysis(analysis_type: str, duration: float):
    """Record AI analysis metrics"""
    ai_analysis_duration.labels(analysis_type=analysis_type).observe(duration)

def record_incident_response(duration: float):
    """Record incident response metrics"""
    incident_response_duration.observe(duration)

def update_active_scans(count: int):
    """Update active scans gauge"""
    active_scans.set(count)

def update_active_incidents(count: int):
    """Update active incidents gauge"""
    active_incidents.set(count)

def update_total_assets(count: int):
    """Update total assets gauge"""
    total_assets.set(count)

def update_total_vulnerabilities(count: int):
    """Update total vulnerabilities gauge"""
    total_vulnerabilities.set(count)

def get_metrics() -> str:
    """Get Prometheus metrics"""
    return generate_latest()

def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    try:
        # System resources
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "process": {
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            },
            "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning"
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }