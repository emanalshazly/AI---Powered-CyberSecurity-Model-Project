#!/usr/bin/env python3
"""
CyberShield AI Quick Setup Script
One-command setup for the revolutionary cybersecurity platform
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print CyberShield AI banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║  🛡️  CyberShield AI - Revolutionary Cybersecurity Platform                  ║
    ║                                                                              ║
    ║  🌟 Features:                                                               ║
    ║     • AI-Powered Threat Detection                                           ║
    ║     • Advanced Vulnerability Scanning                                       ║
    ║     • Autonomous Incident Response                                          ║
    ║     • Predictive Security Analytics                                         ║
    ║     • Zero-Trust Security Framework                                         ║
    ║     • Global Threat Intelligence                                            ║
    ║                                                                              ║
    ║  🚀 100% Free • Open Source • Enterprise Ready                              ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Check Python version"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_docker():
    """Check Docker availability"""
    print("🐳 Checking Docker...")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Docker not found - will use local setup")
    return False

def run_setup():
    """Run the setup process"""
    print("🚀 Starting CyberShield AI Setup...")
    
    # Check requirements
    if not check_python():
        return False
    
    docker_available = check_docker()
    
    # Choose setup method
    if docker_available:
        print("\n🐳 Docker setup detected")
        choice = input("Use Docker? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            return run_docker_setup()
    
    print("\n📦 Running local setup...")
    return run_local_setup()

def run_docker_setup():
    """Run Docker-based setup"""
    print("🐳 Setting up with Docker...")
    
    try:
        # Build and start services
        print("Building Docker images...")
        subprocess.run(['docker-compose', 'build'], check=True)
        
        print("Starting services...")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        print("\n✅ CyberShield AI is running!")
        print("\n🌐 Access the platform:")
        print("   • Web Interface: http://localhost")
        print("   • API Documentation: http://localhost/api/docs")
        print("   • Grafana Dashboard: http://localhost:3000")
        print("   • Prometheus Metrics: http://localhost:9091")
        
        print("\n🔧 Default credentials:")
        print("   • Grafana: admin / cybershield123")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker setup failed: {e}")
        return False

def run_local_setup():
    """Run local setup"""
    print("📦 Setting up locally...")
    
    try:
        # Run the main setup script
        subprocess.run([sys.executable, 'setup.py'], check=True)
        
        print("\n✅ Local setup completed!")
        print("\n🚀 To start CyberShield AI:")
        print("   python main.py")
        print("\n🌐 Access the platform:")
        print("   • Web Interface: http://localhost:8080")
        print("   • API Documentation: http://localhost:8080/api/docs")
        print("   • Health Check: http://localhost:8080/api/health")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Local setup failed: {e}")
        return False

def main():
    """Main function"""
    print_banner()
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the CyberShield AI directory")
        print("   cd cybershield_ai")
        print("   python run_setup.py")
        return False
    
    # Run setup
    success = run_setup()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Read README.md for detailed documentation")
        print("   2. Configure your environment in .env file")
        print("   3. Add assets to monitor via the API")
        print("   4. Explore the web interface")
        print("\n🌟 Welcome to the future of cybersecurity!")
        return True
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)