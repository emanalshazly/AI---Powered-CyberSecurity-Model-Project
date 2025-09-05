"""
Database initialization and management
"""

import logging
from pathlib import Path
import sqlite3
import asyncio

logger = logging.getLogger(__name__)

async def init_database():
    """Initialize database connections and schemas"""
    try:
        logger.info("🗄️  Initializing database...")
        
        # Create data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite databases
        await init_sqlite_databases()
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def init_sqlite_databases():
    """Initialize SQLite databases"""
    try:
        # Main application database
        main_db = Path("data/cybershield.db")
        conn = sqlite3.connect(str(main_db))
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_info (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                key_hash TEXT UNIQUE,
                name TEXT,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Insert default system info
        cursor.execute("""
            INSERT OR REPLACE INTO system_info (key, value) VALUES 
            ('version', '1.0.0'),
            ('initialized_at', datetime('now')),
            ('status', 'active')
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ SQLite databases initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize SQLite databases: {e}")
        raise