#!/usr/bin/env python3
"""
Test Setup Script for CyberShield AI
Ensures all tests pass and dependencies are properly installed
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ Command succeeded: {command}")
        return True
    except Exception as e:
        print(f"❌ Exception running command {command}: {e}")
        return False

def setup_python_tests():
    """Setup Python test environment"""
    print("🐍 Setting up Python tests...")
    
    # Install test dependencies
    test_deps = [
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1", 
        "pytest-cov==4.1.0",
        "httpx==0.25.2",
        "black==23.11.0",
        "flake8==6.1.0",
        "mypy==1.7.1",
        "bandit==1.7.5"
    ]
    
    for dep in test_deps:
        if not run_command(f"pip install {dep}"):
            return False
    
    return True

def setup_frontend_tests():
    """Setup frontend test environment"""
    print("🌐 Setting up frontend tests...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found, skipping frontend tests")
        return True
    
    # Install frontend dependencies
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    return True

def run_python_tests():
    """Run Python tests"""
    print("🧪 Running Python tests...")
    
    # Run linting
    if not run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"):
        print("⚠️  Linting issues found, but continuing...")
    
    # Run type checking
    if not run_command("mypy . --ignore-missing-imports"):
        print("⚠️  Type checking issues found, but continuing...")
    
    # Run security check
    if not run_command("bandit -r . -f json -o bandit-report.json"):
        print("⚠️  Security issues found, but continuing...")
    
    # Run tests
    if not run_command("pytest tests/ -v --cov=core --cov=api --cov-report=xml --cov-report=html"):
        return False
    
    return True

def run_frontend_tests():
    """Run frontend tests"""
    print("🧪 Running frontend tests...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found, skipping frontend tests")
        return True
    
    # Run linting
    if not run_command("npm run lint", cwd=frontend_dir):
        print("⚠️  Frontend linting issues found, but continuing...")
    
    # Run type checking
    if not run_command("npm run type-check", cwd=frontend_dir):
        print("⚠️  Frontend type checking issues found, but continuing...")
    
    # Run tests
    if not run_command("npm test -- --coverage --watchAll=false", cwd=frontend_dir):
        return False
    
    return True

def main():
    """Main test setup function"""
    print("🚀 Setting up CyberShield AI tests...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Setup test environments
    if not setup_python_tests():
        print("❌ Python test setup failed")
        return False
    
    if not setup_frontend_tests():
        print("❌ Frontend test setup failed")
        return False
    
    # Run tests
    if not run_python_tests():
        print("❌ Python tests failed")
        return False
    
    if not run_frontend_tests():
        print("❌ Frontend tests failed")
        return False
    
    print("✅ All tests completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)