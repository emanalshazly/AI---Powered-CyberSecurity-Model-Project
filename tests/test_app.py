"""
Test suite for Metro Security System
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from app import app, db, User, CommandLog, SecurityEvent

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['SECRET_KEY'] = 'test-secret'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Create test user
    user = User(username='testuser', email='test@example.com', role='operator')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_headers(client):
    """Create admin user and return auth headers"""
    # Create admin user
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('adminpass')
    db.session.add(admin)
    db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created successfully'
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # Create first user
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Try to create second user with same username
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == 409
    
    def test_login_success(self, client):
        """Test successful login"""
        # Create user first
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401

class TestCommandClassification:
    """Test command classification endpoint"""
    
    @patch('app.llm')
    def test_classify_valid_command(self, mock_llm, client, auth_headers):
        """Test classification of valid command"""
        mock_llm.return_value = {
            'choices': [{'text': 'Category = Valid, Type = Normal'}]
        }
        
        response = client.post('/api/classify', 
                             json={'command': 'open_door'},
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'classification' in data
        assert 'risk_score' in data
        assert 'timestamp' in data
    
    @patch('app.llm')
    def test_classify_malicious_command(self, mock_llm, client, auth_headers):
        """Test classification of malicious command"""
        mock_llm.return_value = {
            'choices': [{'text': 'Category = Invalid, Type = Malicious'}]
        }
        
        response = client.post('/api/classify',
                             json={'command': 'hack system'},
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Malicious' in data['classification']
        assert data['risk_score'] > 0.7
    
    def test_classify_unauthorized(self, client):
        """Test classification without authentication"""
        response = client.post('/api/classify',
                             json={'command': 'open_door'})
        
        assert response.status_code == 401
    
    def test_classify_empty_command(self, client, auth_headers):
        """Test classification with empty command"""
        response = client.post('/api/classify',
                             json={'command': ''},
                             headers=auth_headers)
        
        assert response.status_code == 400

class TestCommandHistory:
    """Test command history endpoint"""
    
    def test_get_command_history(self, client, auth_headers):
        """Test getting command history"""
        # Create some test commands
        for i in range(5):
            cmd = CommandLog(
                user_id=1,
                command=f'test_command_{i}',
                classification='Valid - Normal',
                risk_score=0.1
            )
            db.session.add(cmd)
        db.session.commit()
        
        response = client.get('/api/commands/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'commands' in data
        assert len(data['commands']) == 5
    
    def test_get_command_history_unauthorized(self, client):
        """Test getting command history without authentication"""
        response = client.get('/api/commands/history')
        assert response.status_code == 401

class TestSecurityEvents:
    """Test security events endpoint"""
    
    def test_get_security_events_admin(self, client, admin_headers):
        """Test getting security events as admin"""
        # Create some test events
        for i in range(3):
            event = SecurityEvent(
                event_type='test_event',
                description=f'Test event {i}',
                severity='medium'
            )
            db.session.add(event)
        db.session.commit()
        
        response = client.get('/api/security/events', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) == 3
    
    def test_get_security_events_unauthorized(self, client, auth_headers):
        """Test getting security events as non-admin"""
        response = client.get('/api/security/events', headers=auth_headers)
        assert response.status_code == 403

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_classify(self, client, auth_headers):
        """Test rate limiting on classify endpoint"""
        # Make many requests quickly
        for _ in range(150):  # Exceed the 100/hour limit
            response = client.post('/api/classify',
                                 json={'command': 'test'},
                                 headers=auth_headers)
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        assert response.status_code == 429

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_protection(self, client, auth_headers):
        """Test XSS protection in command input"""
        malicious_command = '<script>alert("xss")</script>'
        
        response = client.post('/api/classify',
                             json={'command': malicious_command},
                             headers=auth_headers)
        
        # Should not contain script tags
        assert '<script>' not in response.get_json()['command']
    
    def test_command_length_validation(self, client, auth_headers):
        """Test command length validation"""
        long_command = 'a' * 2000  # Exceeds 1000 char limit
        
        response = client.post('/api/classify',
                             json={'command': long_command},
                             headers=auth_headers)
        
        # Should be rejected as malicious due to length
        assert 'Malicious' in response.get_json()['classification']

class TestDatabaseModels:
    """Test database models"""
    
    def test_user_creation(self, client):
        """Test user model creation"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        
        assert user.check_password('testpass')
        assert not user.check_password('wrongpass')
    
    def test_command_log_creation(self, client):
        """Test command log model creation"""
        cmd = CommandLog(
            user_id=1,
            command='test_command',
            classification='Valid - Normal',
            risk_score=0.1
        )
        
        assert cmd.command == 'test_command'
        assert cmd.risk_score == 0.1
    
    def test_security_event_creation(self, client):
        """Test security event model creation"""
        event = SecurityEvent(
            event_type='test_event',
            description='Test description',
            severity='high'
        )
        
        assert event.event_type == 'test_event'
        assert event.severity == 'high'
        assert not event.resolved

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_handling(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_500_handling(self, client, auth_headers):
        """Test 500 error handling"""
        with patch('app.classify_command', side_effect=Exception('Test error')):
            response = client.post('/api/classify',
                                 json={'command': 'test'},
                                 headers=auth_headers)
            assert response.status_code == 500

if __name__ == '__main__':
    pytest.main([__file__])