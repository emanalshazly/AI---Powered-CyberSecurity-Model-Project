# Metro Security System - Deployment Guide

## Overview

This guide covers deploying the Metro Security System v2.0 in various environments, from development to production.

## Prerequisites

### System Requirements

- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available space
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (for development)
- **Node.js**: 18+ (for development)
- **Git**: Latest version

## Quick Start (Docker)

### 1. Clone Repository

```bash
git clone https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project.git
cd AI---Powered-CyberSecurity-Model-Project
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Access Application

- **Web Interface**: http://localhost
- **API**: http://localhost/api
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Development Setup

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Download AI model
mkdir -p models/mistral
wget -O models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
  https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Start database and Redis
docker-compose up -d postgres redis

# Run migrations
python app.py --migrate

# Start backend
python app.py
```

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm start
```

## Production Deployment

### 1. Environment Configuration

Create production environment file:

```bash
cp .env.example .env.production
```

Edit `.env.production`:

```bash
# Database
DATABASE_URL=postgresql://metro_user:secure_password@postgres:5432/metro_security
REDIS_URL=redis://redis:6379

# Security (Generate new keys!)
SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-production-jwt-secret-key-here

# AI Model
MODEL_PATH=models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Application
FLASK_ENV=production
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
```

### 2. SSL Certificate Setup

```bash
# Generate SSL certificates
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
  -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

### 3. Database Setup

```bash
# Create production database
docker-compose exec postgres psql -U metro_user -d metro_security -c "
  CREATE DATABASE metro_security_prod;
  GRANT ALL PRIVILEGES ON DATABASE metro_security_prod TO metro_user;
"

# Run migrations
docker-compose exec metro-security python -c "
from app import app, db
with app.app_context():
    db.create_all()
"
```

### 4. Deploy with Docker Compose

```bash
# Use production environment
docker-compose --env-file .env.production up -d

# Check logs
docker-compose logs -f metro-security
```

### 5. Configure Nginx (Production)

Update `nginx.conf` for production:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    # Your application configuration
    location / {
        proxy_pass http://metro-security:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Kubernetes Deployment

### 1. Create Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: metro-security
```

### 2. Deploy PostgreSQL

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: metro-security
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: metro_security
        - name: POSTGRES_USER
          value: metro_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: metro-security
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

### 3. Deploy Application

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metro-security
  namespace: metro-security
spec:
  replicas: 3
  selector:
    matchLabels:
      app: metro-security
  template:
    metadata:
      labels:
        app: metro-security
    spec:
      containers:
      - name: metro-security
        image: metro-security:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: database-url
        - name: REDIS_URL
          value: "redis://redis:6379"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: metro-security
  namespace: metro-security
spec:
  selector:
    app: metro-security
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Monitoring Setup

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'metro-security'
    static_configs:
      - targets: ['metro-security:5000']
    metrics_path: '/api/metrics'
```

### 2. Grafana Dashboards

Import the provided Grafana dashboard JSON files:

- `grafana/dashboards/metro-security-overview.json`
- `grafana/dashboards/security-events.json`
- `grafana/dashboards/performance-metrics.json`

### 3. Alerting Rules

Configure alerting in Prometheus:

```yaml
# metro_security_rules.yml
groups:
  - name: metro_security_alerts
    rules:
      - alert: HighRiskCommandDetected
        expr: metro_commands_total{classification="Invalid - Malicious"} > 5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High number of malicious commands detected"
```

## Security Hardening

### 1. Network Security

```bash
# Configure firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 2. Database Security

```sql
-- Create read-only user
CREATE USER metro_readonly WITH PASSWORD 'readonly_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metro_readonly;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
SELECT pg_reload_conf();
```

### 3. Application Security

```bash
# Set secure file permissions
chmod 600 .env.production
chmod 600 ssl/*.pem

# Use non-root user
docker-compose exec metro-security adduser --disabled-password --gecos "" appuser
docker-compose exec metro-security chown -R appuser:appuser /app
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U metro_user metro_security > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U metro_user metro_security < backup_20240115_120000.sql
```

### 2. Application Backup

```bash
# Backup application data
tar -czf metro_security_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  models/ logs/ ssl/ .env.production
```

### 3. Automated Backups

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/metro_security"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U metro_user metro_security > \
  $BACKUP_DIR/db_backup_$DATE.sql

# Application backup
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz models/ logs/ ssl/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:

```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Common Issues

#### 1. AI Model Not Loading

```bash
# Check model file
ls -la models/mistral/
file models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Check logs
docker-compose logs metro-security | grep -i model
```

#### 2. Database Connection Issues

```bash
# Test database connection
docker-compose exec metro-security python -c "
from app import app, db
with app.app_context():
    db.engine.execute('SELECT 1')
"

# Check database logs
docker-compose logs postgres
```

#### 3. High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart metro-security
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f metro-security

# View specific log levels
docker-compose logs metro-security | grep ERROR

# View security events
docker-compose exec metro-security python -c "
from app import SecurityEvent
for event in SecurityEvent.query.filter_by(severity='high').all():
    print(f'{event.timestamp}: {event.description}')
"
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_command_logs_user_id ON command_logs(user_id);
CREATE INDEX idx_command_logs_timestamp ON command_logs(timestamp);
CREATE INDEX idx_security_events_severity ON security_events(severity);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM command_logs WHERE user_id = 1;
```

### 2. Redis Optimization

```bash
# Configure Redis for performance
echo "maxmemory 1gb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

### 3. Application Optimization

```python
# Enable connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## Scaling

### Horizontal Scaling

```yaml
# Scale application
kubectl scale deployment metro-security --replicas=5

# Scale with Docker Compose
docker-compose up -d --scale metro-security=3
```

### Load Balancing

```nginx
upstream metro_security {
    server metro-security-1:5000;
    server metro-security-2:5000;
    server metro-security-3:5000;
}
```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review security logs
   - Check system performance
   - Update dependencies

2. **Monthly**:
   - Security patches
   - Database optimization
   - Backup verification

3. **Quarterly**:
   - Security audit
   - Performance review
   - Disaster recovery test

### Update Procedure

```bash
# 1. Backup current deployment
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt
npm install

# 4. Run migrations
python app.py --migrate

# 5. Restart services
docker-compose restart

# 6. Verify deployment
curl http://localhost/api/health
```

## Support

For deployment issues:

1. Check logs: `docker-compose logs -f`
2. Review documentation: [API Docs](docs/api.md)
3. Create issue: [GitHub Issues](https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project/issues)
4. Contact support: support@metro-security.com

---

> **Note**: This deployment guide is regularly updated. Always check for the latest version before deploying.