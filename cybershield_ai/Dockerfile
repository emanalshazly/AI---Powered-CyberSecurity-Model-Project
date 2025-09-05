# CyberShield AI - Revolutionary Cybersecurity Platform
# Multi-stage Docker build for production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    nmap \
    netcat-openbsd \
    procps \
    htop \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash cybershield

# Stage 2: Python dependencies
FROM base as python-deps

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: AI Models
FROM python-deps as ai-models

# Download AI models
RUN python -c "
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer

# Download models
models = [
    'microsoft/DialoGPT-medium',
    'distilbert-base-uncased', 
    'sentence-transformers/all-MiniLM-L6-v2'
]

for model in models:
    try:
        if 'sentence-transformers' in model:
            SentenceTransformer(model)
        else:
            AutoTokenizer.from_pretrained(model)
            AutoModel.from_pretrained(model)
        print(f'Downloaded {model}')
    except Exception as e:
        print(f'Failed to download {model}: {e}')
"

# Stage 4: Application
FROM ai-models as app

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data models logs reports static .cache

# Set permissions
RUN chown -R cybershield:cybershield /app

# Switch to non-root user
USER cybershield

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Default command
CMD ["python", "main.py"]

# Stage 5: Production (optional)
FROM app as production

# Additional production configurations
ENV FLASK_ENV=production
ENV DEBUG=False

# Security headers and optimizations
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf || true

# Final command for production
CMD ["python", "main.py"]