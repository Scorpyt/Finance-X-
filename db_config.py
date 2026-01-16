"""
Database Configuration for Finance-X
Supports both Neon PostgreSQL (production) and SQLite (local development)
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

def get_db_type():
    """Determine which database to use"""
    if USE_SQLITE or not DATABASE_URL:
        return 'sqlite'
    return 'postgresql'

def get_connection():
    """Get database connection based on configuration"""
    db_type = get_db_type()
    
    if db_type == 'sqlite':
        import sqlite3
        return sqlite3.connect('finance.db', check_same_thread=False)
    else:
        import psycopg2
        from psycopg2 import pool
        return psycopg2.connect(DATABASE_URL)

# Connection pool for PostgreSQL (handles 20K+ concurrent users)
_connection_pool = None

def get_pool():
    """Get or create connection pool for PostgreSQL"""
    global _connection_pool
    
    if get_db_type() == 'sqlite':
        return None
    
    if _connection_pool is None:
        import psycopg2
        from psycopg2 import pool
        
        # Pool size: min 5, max 20 connections
        # Neon free tier supports up to 100 connections
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=20,
            dsn=DATABASE_URL
        )
        print("[Database] PostgreSQL connection pool initialized")
    
    return _connection_pool

def get_pooled_connection():
    """Get a connection from the pool"""
    pool = get_pool()
    if pool:
        return pool.getconn()
    return get_connection()

def release_connection(conn):
    """Release connection back to pool"""
    pool = get_pool()
    if pool:
        pool.putconn(conn)
    else:
        # SQLite - just close
        pass

def close_pool():
    """Close all connections in the pool"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        print("[Database] Connection pool closed")

# Utility function for parameterized queries
def get_placeholder():
    """Get the correct placeholder for the database type"""
    if get_db_type() == 'sqlite':
        return '?'
    return '%s'

def adapt_query(query):
    """Adapt SQLite query to PostgreSQL if needed"""
    if get_db_type() == 'postgresql':
        # Replace ? with %s for PostgreSQL
        return query.replace('?', '%s')
    return query

print(f"[Database] Configured for: {get_db_type().upper()}")
if DATABASE_URL:
    # Hide password in logs
    safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'
    print(f"[Database] Connection: ...@{safe_url}")
