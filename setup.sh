#!/bin/bash

# Metro Security System Setup Script
# This script sets up the development environment

set -e

echo "🚇 Setting up Metro Security System v2.0..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11 or later."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $python_version is installed"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or later."
        exit 1
    fi
    
    node_version=$(node --version)
    print_success "Node.js $node_version is installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p models/mistral
    mkdir -p logs
    mkdir -p ssl
    mkdir -p grafana/provisioning
    print_success "Directories created"
}

# Download AI model
download_model() {
    print_status "Checking for AI model..."
    if [ ! -f "models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf" ]; then
        print_status "Downloading Mistral 7B model (this may take a while)..."
        wget -O models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
            https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
        print_success "AI model downloaded"
    else
        print_success "AI model already exists"
    fi
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python environment setup complete"
}

# Setup Node.js environment
setup_node() {
    print_status "Setting up Node.js environment..."
    if [ -f "package.json" ]; then
        npm install
        print_success "Node.js dependencies installed"
    else
        print_warning "No package.json found, skipping Node.js setup"
    fi
}

# Create environment file
create_env() {
    print_status "Creating environment configuration..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_success "Environment file already exists"
    fi
}

# Generate SSL certificates for development
generate_ssl() {
    print_status "Generating SSL certificates for development..."
    if [ ! -f "ssl/cert.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi
}

# Create Grafana provisioning
create_grafana_config() {
    print_status "Creating Grafana configuration..."
    cat > grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    print_success "Grafana configuration created"
}

# Main setup function
main() {
    echo "Starting Metro Security System setup..."
    echo "======================================"
    
    # Check prerequisites
    check_docker
    check_python
    check_node
    
    # Setup environment
    create_directories
    download_model
    setup_python
    setup_node
    create_env
    generate_ssl
    create_grafana_config
    
    echo ""
    echo "======================================"
    print_success "Setup complete! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Start the application:"
    echo "   - Development: docker-compose up -d"
    echo "   - Or run locally: python app.py"
    echo ""
    echo "Access the application at:"
    echo "  - Web Interface: http://localhost"
    echo "  - API: http://localhost/api"
    echo "  - Grafana: http://localhost:3000"
    echo "  - Prometheus: http://localhost:9090"
    echo ""
    echo "Default credentials:"
    echo "  - Username: admin"
    echo "  - Password: admin123!"
    echo ""
}

# Run main function
main "$@"