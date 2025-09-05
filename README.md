# 🚇 Metro Door Cyber-Security System v2.0

A modern, enterprise-grade **AI-powered metro door security system** with advanced cybersecurity measures, real-time monitoring, and a beautiful React-based web interface. Built with the latest security practices and designed for production deployment.

## 🔒 Enhanced Security Features

### Modern Cybersecurity Measures
- **🔐 JWT Authentication** with role-based access control
- **🛡️ End-to-end encryption** for all command transmission
- **⚡ Rate limiting** and DDoS protection
- **📊 Real-time security monitoring** with Prometheus & Grafana
- **🔍 Comprehensive audit logging** with structured logging
- **🚨 Real-time security alerts** via WebSocket
- **🛡️ Input validation** and XSS protection
- **🔒 Secure session management** with Redis
- **📈 Risk scoring** for all commands
- **🔐 Password hashing** with bcrypt

### AI-Powered Threat Detection
- **🤖 Mistral 7B LLM** for intelligent command classification
- **📊 Risk assessment** with dynamic scoring
- **🚨 Real-time threat detection** and alerting
- **📈 Behavioral analysis** and pattern recognition
- **🛡️ Advanced input sanitization** and validation

## ✨ New Features in v2.0

### 🎨 Modern Web Interface
- **⚛️ React 18** with TypeScript
- **🎨 Material-UI** design system
- **📱 Responsive design** for all devices
- **🌙 Dark/Light theme** support
- **📊 Real-time dashboards** with charts
- **🔔 Toast notifications** and alerts
- **🎭 Smooth animations** with Framer Motion

### 🔧 Enterprise Features
- **👥 User management** with roles (Admin, Operator)
- **📊 Command history** with advanced filtering
- **🔍 Security event monitoring** dashboard
- **⚙️ Settings management** and preferences
- **📈 Performance metrics** and monitoring
- **🔌 WebSocket** real-time updates
- **📱 Mobile-responsive** design

### 🚀 Production Ready
- **🐳 Docker containerization** with multi-stage builds
- **🐘 PostgreSQL** database with migrations
- **🔴 Redis** caching and session storage
- **🌐 Nginx** reverse proxy with SSL support
- **📊 Prometheus** metrics collection
- **📈 Grafana** monitoring dashboards
- **🔒 Security headers** and HTTPS support

## 🛠 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI v5** for components
- **React Query** for data fetching
- **React Router** for navigation
- **Socket.IO** for real-time updates
- **Framer Motion** for animations
- **Recharts** for data visualization

### Backend
- **Python 3.11** with Flask
- **SQLAlchemy** ORM with PostgreSQL
- **Redis** for caching and sessions
- **JWT** authentication
- **Flask-SocketIO** for WebSocket support
- **Prometheus** metrics
- **Structured logging** with structlog

### AI/ML
- **Mistral 7B Instruct** (GGUF format)
- **llama-cpp-python** for local inference
- **Custom risk scoring** algorithms
- **Real-time classification** pipeline

### Infrastructure
- **Docker** & Docker Compose
- **Nginx** reverse proxy
- **PostgreSQL** database
- **Redis** cache
- **Prometheus** monitoring
- **Grafana** dashboards

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project.git
cd AI---Powered-CyberSecurity-Model-Project

# Download the AI model
mkdir -p models/mistral
wget -O models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
  https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Start all services
docker-compose up -d

# Access the application
open http://localhost
```

### Option 2: Development Setup

```bash
# Backend setup
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Download the AI model (same as above)
mkdir -p models/mistral
wget -O models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
  https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Start backend
python app.py

# Frontend setup (in another terminal)
cd frontend
npm install
npm start
```

## 📂 Project Structure

```
metro-security-system/
├── 📁 src/                    # React frontend source
│   ├── 📁 components/         # Reusable components
│   ├── 📁 contexts/          # React contexts
│   ├── 📁 pages/             # Page components
│   └── 📄 App.tsx            # Main app component
├── 📁 public/                # Static assets
├── 📄 app.py                 # Flask backend
├── 📄 requirements.txt       # Python dependencies
├── 📄 package.json           # Node.js dependencies
├── 📄 Dockerfile             # Multi-stage Docker build
├── 📄 docker-compose.yml     # Docker services
├── 📄 nginx.conf             # Nginx configuration
├── 📄 prometheus.yml         # Monitoring config
└── 📁 models/                # AI model files
    └── 📁 mistral/
        └── 📄 mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

## 🎮 Usage Guide

### 1. **Dashboard**
- Real-time system status
- Command statistics
- Security alerts overview
- Performance metrics

### 2. **Command Center**
- Send predefined commands (open_door, close_door, emergency_stop)
- Test custom commands
- Visual door simulation
- Real-time command results

### 3. **Security Monitor** (Admin only)
- Security events dashboard
- Threat analysis charts
- Real-time alerts
- Event management

### 4. **Command History**
- Complete command log
- Advanced filtering
- Risk score analysis
- Export capabilities

### 5. **Settings**
- User preferences
- Security settings
- System configuration
- Activity logs

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin/Operator)
- Secure password hashing with bcrypt
- Session management with Redis

### Data Protection
- End-to-end encryption for commands
- Input validation and sanitization
- XSS and injection attack prevention
- Secure headers and HTTPS support

### Monitoring & Alerting
- Real-time security event monitoring
- Prometheus metrics collection
- Grafana dashboards
- WebSocket-based alerts
- Structured logging with audit trails

### Rate Limiting & DDoS Protection
- API rate limiting
- Login attempt throttling
- IP-based blocking
- Nginx-level protection

## 📊 Monitoring & Observability

### Metrics
- Command processing rates
- Security event counts
- System performance metrics
- User activity tracking

### Dashboards
- **Grafana**: Real-time monitoring dashboards
- **Prometheus**: Metrics collection and alerting
- **Application**: Built-in security monitoring

### Alerts
- High-risk command detection
- Suspicious activity spikes
- System health monitoring
- Security event notifications

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using Kubernetes
kubectl apply -f k8s/

# Using Docker Swarm
docker stack deploy -c docker-compose.yml metro-security
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# AI Model
MODEL_PATH=models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## 🔧 Configuration

### Nginx Configuration
- SSL/TLS termination
- Security headers
- Rate limiting
- Gzip compression
- WebSocket support

### Database Configuration
- PostgreSQL with connection pooling
- Automated migrations
- Backup strategies
- Performance optimization

### Redis Configuration
- Session storage
- Caching strategies
- Persistence settings
- Memory optimization

## 📈 Performance

### Optimization Features
- Database query optimization
- Redis caching
- CDN integration
- Image optimization
- Code splitting
- Lazy loading

### Scalability
- Horizontal scaling support
- Load balancing
- Database sharding
- Microservices architecture

## 🧪 Testing

### Test Coverage
- Unit tests for components
- Integration tests for APIs
- End-to-end tests for workflows
- Security testing with OWASP ZAP

### Running Tests
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test

# E2E tests
npm run test:e2e

# Security tests
bandit -r app.py
```

## 🔄 CI/CD Pipeline

### Automated Workflows
- Code quality checks
- Security scanning
- Automated testing
- Docker image building
- Deployment automation

### Quality Gates
- Code coverage > 80%
- Security scan passes
- All tests pass
- Performance benchmarks met

## 📚 API Documentation

### Authentication
```bash
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh
```

### Commands
```bash
POST /api/classify
GET /api/commands/history
GET /api/commands/stats
```

### Security
```bash
GET /api/security/events
POST /api/security/events/{id}/resolve
GET /api/metrics
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** for the language model
- **Hugging Face** for model hosting
- **Material-UI** for the design system
- **React** team for the framework
- **Flask** team for the backend framework

## 📞 Support

- **Documentation**: [Wiki](https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project/wiki)
- **Issues**: [GitHub Issues](https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AvichalTrivedi7/AI---Powered-CyberSecurity-Model-Project/discussions)

---

> Built with ❤️ by [Avi](https://github.com/AvichalTrivedi7) | Enhanced with modern cybersecurity practices and enterprise features
