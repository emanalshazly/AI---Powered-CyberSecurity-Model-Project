"""
Metro Door Cyber-Security System - Enhanced Version
Modern web application with advanced security measures
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from functools import wraps

import structlog
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity, get_jwt
)
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import redis
from llama_cpp import Llama
import bleach
import validators
from prometheus_client import Counter, Histogram, generate_latest
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry for error monitoring
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv('ENVIRONMENT', 'development')
)

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

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///metro_security.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RATELIMIT_STORAGE_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Initialize extensions
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(','))
jwt = JWTManager(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Initialize Redis for caching and session management
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

# Prometheus metrics
command_counter = Counter('metro_commands_total', 'Total commands processed', ['command_type', 'classification'])
command_duration = Histogram('metro_command_duration_seconds', 'Time spent processing commands')
security_events = Counter('metro_security_events_total', 'Security events', ['event_type'])

# Encryption setup
def get_encryption_key():
    """Generate or retrieve encryption key"""
    key = redis_client.get('encryption_key')
    if not key:
        key = Fernet.generate_key()
        redis_client.setex('encryption_key', 86400 * 30, key)  # 30 days
    return key

fernet = Fernet(get_encryption_key())

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='operator')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CommandLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    command = db.Column(db.Text, nullable=False)
    classification = db.Column(db.String(50), nullable=False)
    encrypted_command = db.Column(db.LargeBinary)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    risk_score = db.Column(db.Float, default=0.0)

class SecurityEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    severity = db.Column(db.String(20), default='medium')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)

# Load AI Model
try:
    llm = Llama(
        model_path=os.getenv('MODEL_PATH', 'models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf'),
        n_ctx=2048,
        max_tokens=512,
        temperature=0.3,
        top_p=0.9,
        repeat_penalty=1.1,
        verbose=False
    )
    logger.info("AI model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load AI model: {e}")
    llm = None

# Security decorators and utilities
def require_role(role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = User.query.get(get_jwt_identity())
            if not current_user or current_user.role != role:
                security_events.labels(event_type='unauthorized_access').inc()
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type: str, description: str, severity: str = 'medium', user_id: int = None):
    """Log security events"""
    event = SecurityEvent(
        event_type=event_type,
        description=description,
        ip_address=request.remote_addr,
        user_id=user_id,
        severity=severity
    )
    db.session.add(event)
    db.session.commit()
    security_events.labels(event_type=event_type).inc()
    logger.warning("Security event", event_type=event_type, description=description, severity=severity)

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text:
        return ""
    # Remove potentially dangerous characters and HTML tags
    sanitized = bleach.clean(text, tags=[], strip=True)
    return sanitized.strip()

def validate_command(command: str) -> Tuple[bool, str]:
    """Validate command format and content"""
    if not command or len(command) > 1000:
        return False, "Command too long or empty"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        'script', 'javascript', 'eval', 'exec', 'import', 'os.system',
        'subprocess', 'shell', 'cmd', 'powershell', 'bash', 'sh'
    ]
    
    command_lower = command.lower()
    for pattern in suspicious_patterns:
        if pattern in command_lower:
            return False, f"Suspicious pattern detected: {pattern}"
    
    return True, "Valid"

def calculate_risk_score(command: str, classification: str) -> float:
    """Calculate risk score based on command and classification"""
    base_score = 0.0
    
    if "Malicious" in classification:
        base_score += 0.8
    elif "Suspicious" in classification:
        base_score += 0.4
    
    # Additional risk factors
    if len(command) > 100:
        base_score += 0.1
    if any(char in command for char in ['<', '>', '&', '|', ';']):
        base_score += 0.2
    
    return min(base_score, 1.0)

def classify_command(user_command: str) -> str:
    """Enhanced command classification with security measures"""
    if not llm:
        return "Category = Invalid, Type = Malicious (AI model unavailable)"
    
    # Validate and sanitize input
    is_valid, error_msg = validate_command(user_command)
    if not is_valid:
        log_security_event('invalid_command', f"Invalid command rejected: {error_msg}")
        return f"Category = Invalid, Type = Malicious ({error_msg})"
    
    sanitized_command = sanitize_input(user_command)
    
    prompt = f"""
You are a Metro Door Security AI with advanced threat detection capabilities.
Classify the following user command into one of three categories:
1. Valid - Normal (standard operational commands)
2. Invalid - Suspicious (unusual but potentially harmless)
3. Invalid - Malicious (clearly dangerous or unauthorized)

Valid commands are strictly from this list: ["open_door", "close_door", "emergency_stop"].
Consider command length, wording, and potential security implications.

Command: {sanitized_command}

Answer in only one line:
Category = <Valid/Invalid>, Type = <Normal/Suspicious/Malicious>
"""
    
    try:
        response = llm(prompt, max_tokens=128, stop=["</s>"])
        result = response["choices"][0]["text"].strip()
        
        # Additional validation of AI response
        if not any(keyword in result for keyword in ["Valid", "Invalid"]):
            log_security_event('ai_response_error', "AI returned unexpected response format")
            return "Category = Invalid, Type = Malicious (AI response validation failed)"
        
        return result
    except Exception as e:
        logger.error(f"AI classification error: {e}")
        log_security_event('ai_error', f"AI classification failed: {str(e)}")
        return "Category = Invalid, Type = Malicious (AI processing error)"

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'ai_model_loaded': llm is not None
    })

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    # Validate input
    username = sanitize_input(data['username'])
    email = sanitize_input(data.get('email', ''))
    password = data['password']
    
    if not validators.email(email) and email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        log_security_event('registration_attempt', f"Duplicate username: {username}")
        return jsonify({'error': 'Username already exists'}), 409
    
    # Create user
    user = User(username=username, email=email, role='operator')
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        logger.info(f"User registered: {username}")
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = sanitize_input(data['username'])
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        log_security_event('failed_login', f"Failed login attempt for username: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        log_security_event('inactive_user_login', f"Inactive user login attempt: {username}")
        return jsonify({'error': 'Account deactivated'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    
    logger.info(f"User logged in: {username}")
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    })

@app.route('/api/classify', methods=['POST'])
@jwt_required()
@limiter.limit("100 per hour")
def classify_command_endpoint():
    """Enhanced command classification endpoint"""
    start_time = datetime.utcnow()
    
    try:
        data = request.get_json()
        if not data or not data.get('command'):
            return jsonify({'error': 'No command provided'}), 400
        
        user_command = data['command']
        current_user_id = get_jwt_identity()
        
        # Classify command
        classification = classify_command(user_command)
        
        # Calculate risk score
        risk_score = calculate_risk_score(user_command, classification)
        
        # Encrypt command for storage
        encrypted_command = fernet.encrypt(user_command.encode())
        
        # Log command
        command_log = CommandLog(
            user_id=current_user_id,
            command=user_command,
            classification=classification,
            encrypted_command=encrypted_command,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            risk_score=risk_score
        )
        db.session.add(command_log)
        db.session.commit()
        
        # Update metrics
        command_type = "valid" if "Valid" in classification else "invalid"
        command_counter.labels(command_type=command_type, classification=classification.split(',')[1].strip()).inc()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        command_duration.observe(duration)
        
        # Emit real-time update via WebSocket
        socketio.emit('command_processed', {
            'command': user_command,
            'classification': classification,
            'risk_score': risk_score,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # High risk commands trigger additional security measures
        if risk_score > 0.7:
            log_security_event('high_risk_command', f"High risk command detected: {user_command}", 'high', current_user_id)
            socketio.emit('security_alert', {
                'type': 'high_risk_command',
                'command': user_command,
                'risk_score': risk_score,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'command': user_command,
            'classification': classification,
            'risk_score': risk_score,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Command classification error: {e}")
        log_security_event('classification_error', f"Error processing command: {str(e)}", 'high')
        return jsonify({'error': 'Command processing failed'}), 500

@app.route('/api/commands/history', methods=['GET'])
@jwt_required()
def get_command_history():
    """Get command history for current user"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    commands = CommandLog.query.filter_by(user_id=current_user_id)\
        .order_by(CommandLog.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'commands': [{
            'id': cmd.id,
            'command': cmd.command,
            'classification': cmd.classification,
            'risk_score': cmd.risk_score,
            'timestamp': cmd.timestamp.isoformat()
        } for cmd in commands.items],
        'total': commands.total,
        'pages': commands.pages,
        'current_page': page
    })

@app.route('/api/security/events', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_security_events():
    """Get security events (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 200)
    
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'events': [{
            'id': event.id,
            'event_type': event.event_type,
            'description': event.description,
            'severity': event.severity,
            'ip_address': event.ip_address,
            'timestamp': event.timestamp.isoformat(),
            'resolved': event.resolved
        } for event in events.items],
        'total': events.total,
        'pages': events.pages,
        'current_page': page
    })

@app.route('/api/metrics', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

# WebSocket events
@socketio.on('connect')
@jwt_required()
def handle_connect():
    """Handle WebSocket connection"""
    user_id = get_jwt_identity()
    join_room(f'user_{user_id}')
    logger.info(f"User {user_id} connected via WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("User disconnected from WebSocket")

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit exceeded handler"""
    log_security_event('rate_limit_exceeded', f"Rate limit exceeded from {request.remote_addr}")
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(401)
def unauthorized_handler(e):
    """Unauthorized access handler"""
    log_security_event('unauthorized_access', f"Unauthorized access attempt from {request.remote_addr}")
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden_handler(e):
    """Forbidden access handler"""
    log_security_event('forbidden_access', f"Forbidden access attempt from {request.remote_addr}")
    return jsonify({'error': 'Forbidden'}), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@metro-security.local', role='admin')
            admin.set_password('admin123!')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin user created: admin/admin123!")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)