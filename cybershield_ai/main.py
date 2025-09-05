"""
CyberShield AI - Revolutionary Cybersecurity Platform
Main application entry point
"""

import asyncio
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import structlog

from core.config import settings
from core.database import init_database
from core.ai_engine import AIEngine
from core.vulnerability_scanner import VulnerabilityScanner
from core.threat_intelligence import ThreatIntelligence
from core.incident_response import IncidentResponseSystem
from core.compliance_monitor import ComplianceMonitor
from core.forensic_analyzer import ForensicAnalyzer
from api.routes import api_router, set_service_instances
from core.monitoring import setup_monitoring

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global AI Engine instance
ai_engine = None
vulnerability_scanner = None
threat_intelligence = None
incident_response = None
compliance_monitor = None
forensic_analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_engine, vulnerability_scanner, threat_intelligence
    global incident_response, compliance_monitor, forensic_analyzer
    
    logger.info("🚀 Starting CyberShield AI Platform...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")
        
        # Initialize AI Engine
        ai_engine = AIEngine()
        await ai_engine.initialize()
        logger.info("✅ AI Engine initialized")
        
        # Initialize core services
        vulnerability_scanner = VulnerabilityScanner(ai_engine)
        threat_intelligence = ThreatIntelligence(ai_engine)
        incident_response = IncidentResponseSystem(ai_engine)
        compliance_monitor = ComplianceMonitor(ai_engine)
        forensic_analyzer = ForensicAnalyzer(ai_engine)
        
        # Set service instances for API routes
        set_service_instances(
            vulnerability_scanner,
            threat_intelligence,
            incident_response,
            compliance_monitor,
            forensic_analyzer
        )
        
        # Start background tasks
        asyncio.create_task(threat_intelligence.start_monitoring())
        asyncio.create_task(vulnerability_scanner.start_continuous_scanning())
        asyncio.create_task(incident_response.start_monitoring())
        
        logger.info("✅ All services initialized successfully")
        logger.info("🛡️ CyberShield AI Platform is ready!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize platform: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down CyberShield AI Platform...")
        if ai_engine:
            await ai_engine.cleanup()
        logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="CyberShield AI",
    description="Revolutionary AI-Powered Cybersecurity Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CyberShield AI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; color: #2c3e50; }
                .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; }
                .features { margin-top: 30px; }
                .feature { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">🛡️ CyberShield AI Platform</h1>
                <div class="status">✅ Platform is running successfully!</div>
                
                <div class="features">
                    <h2>Revolutionary Features:</h2>
                    <div class="feature">🧠 AI-Powered Threat Detection</div>
                    <div class="feature">🔍 Advanced Vulnerability Scanning</div>
                    <div class="feature">🤖 Autonomous Incident Response</div>
                    <div class="feature">📊 Predictive Security Analytics</div>
                    <div class="feature">🔒 Zero-Trust Security Framework</div>
                    <div class="feature">🌐 Global Threat Intelligence</div>
                </div>
                
                <p><a href="/api/docs">📚 API Documentation</a></p>
                <p><a href="/api/v1/health">🏥 Health Check</a></p>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "ai_engine": ai_engine is not None,
            "vulnerability_scanner": vulnerability_scanner is not None,
            "threat_intelligence": threat_intelligence is not None,
            "incident_response": incident_response is not None,
            "compliance_monitor": compliance_monitor is not None,
            "forensic_analyzer": forensic_analyzer is not None
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )

def main():
    """Main entry point"""
    # Setup monitoring
    setup_monitoring()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()