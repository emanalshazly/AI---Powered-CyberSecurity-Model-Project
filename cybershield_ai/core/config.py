"""
Configuration management for CyberShield AI
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "CyberShield AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8080, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    
    # AI Models
    AI_MODELS_PATH: str = Field(default="models", env="AI_MODELS_PATH")
    HUGGINGFACE_CACHE_DIR: str = Field(default=".cache/huggingface", env="HUGGINGFACE_CACHE_DIR")
    TORCH_HOME: str = Field(default=".cache/torch", env="TORCH_HOME")
    
    # Security Scanning
    NMAP_PATH: str = Field(default="/usr/bin/nmap", env="NMAP_PATH")
    OPENVAS_HOST: str = Field(default="localhost", env="OPENVAS_HOST")
    OPENVAS_PORT: int = Field(default=9392, env="OPENVAS_PORT")
    OPENVAS_USERNAME: str = Field(default="admin", env="OPENVAS_USERNAME")
    OPENVAS_PASSWORD: str = Field(default="admin", env="OPENVAS_PASSWORD")
    
    # Threat Intelligence
    THREAT_FEEDS: List[str] = Field(default=[
        "https://feeds.feedburner.com/eset/blog",
        "https://www.malware-traffic-analysis.net/blog-entries.html",
        "https://www.bleepingcomputer.com/feed/",
        "https://krebsonsecurity.com/feed/",
        "https://www.darkreading.com/rss.xml"
    ], env="THREAT_FEEDS")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3000, env="GRAFANA_PORT")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=200, env="RATE_LIMIT_BURST")
    
    # Scanning Configuration
    MAX_CONCURRENT_SCANS: int = Field(default=10, env="MAX_CONCURRENT_SCANS")
    SCAN_TIMEOUT: int = Field(default=300, env="SCAN_TIMEOUT")  # 5 minutes
    VULNERABILITY_SCAN_INTERVAL: int = Field(default=3600, env="VULNERABILITY_SCAN_INTERVAL")  # 1 hour
    
    # AI Configuration
    AI_BATCH_SIZE: int = Field(default=32, env="AI_BATCH_SIZE")
    AI_MAX_LENGTH: int = Field(default=512, env="AI_MAX_LENGTH")
    AI_TEMPERATURE: float = Field(default=0.7, env="AI_TEMPERATURE")
    AI_TOP_P: float = Field(default=0.9, env="AI_TOP_P")
    
    # Quantum-Safe Crypto (Future)
    QUANTUM_SAFE_ENABLED: bool = Field(default=False, env="QUANTUM_SAFE_ENABLED")
    QUANTUM_ALGORITHM: str = Field(default="CRYSTALS-Kyber", env="QUANTUM_ALGORITHM")
    
    # Blockchain (Future)
    BLOCKCHAIN_ENABLED: bool = Field(default=False, env="BLOCKCHAIN_ENABLED")
    BLOCKCHAIN_NETWORK: str = Field(default="ethereum", env="BLOCKCHAIN_NETWORK")
    BLOCKCHAIN_RPC_URL: Optional[str] = Field(default=None, env="BLOCKCHAIN_RPC_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()