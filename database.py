"""
Database Manager for Finance-X
Supports Neon PostgreSQL (production) and SQLite (local development)
"""
from datetime import datetime
from typing import List, Dict, Any
from db_config import (
    get_db_type, 
    get_pooled_connection, 
    release_connection, 
    adapt_query,
    get_placeholder
)

class DatabaseManager:
    """
    Manages market data storage.
    Automatically uses PostgreSQL or SQLite based on configuration.
    """
    
    def __init__(self):
        self.conn = None
        self.db_type = get_db_type()
        print(f"[DatabaseManager] Using {self.db_type.upper()}")

    def get_connection(self):
        """Get a database connection (pooled for PostgreSQL)"""
        return get_pooled_connection()

    def _release(self, conn):
        """Release connection back to pool"""
        release_connection(conn)

    def initialize_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            # PostgreSQL schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_events (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ,
                    description TEXT,
                    impact NUMERIC(10,4),
                    type VARCHAR(50)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticker_history (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ,
                    symbol VARCHAR(20),
                    price NUMERIC(15,4),
                    change_pct NUMERIC(8,4),
                    volume BIGINT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ,
                    state TEXT,
                    risk_score NUMERIC(6,4),
                    regime VARCHAR(50)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_symbol ON ticker_history(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_timestamp ON ticker_history(timestamp)')
            
        else:
            # SQLite schema (same as before)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    description TEXT,
                    impact REAL,
                    type TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticker_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    price REAL,
                    change_pct REAL,
                    volume INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    state TEXT,
                    risk_score REAL,
                    regime TEXT
                )
            ''')
        
        conn.commit()
        self._release(conn)
        print(f"[Database] Initialized with {self.db_type.upper()} schema.")

    def log_event(self, timestamp: datetime, description: str, impact: float, type_str: str):
        """Log a market event"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            query = f"INSERT INTO market_events (timestamp, description, impact, type) VALUES ({ph}, {ph}, {ph}, {ph})"
            
            ts = timestamp if self.db_type == 'postgresql' else timestamp.isoformat()
            cursor.execute(query, (ts, description, impact, type_str))
            
            conn.commit()
            self._release(conn)
        except Exception as e:
            print(f"[DB Error] Log Event: {e}")

    def log_price_batch(self, prices: List[Dict[str, Any]]):
        """Log batch of price data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            query = f"INSERT INTO ticker_history (timestamp, symbol, price, change_pct, volume) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"
            
            for p in prices:
                ts = p['timestamp'] if self.db_type == 'postgresql' else p['timestamp'].isoformat()
                cursor.execute(query, (ts, p['symbol'], p['price'], p['change'], p['volume']))
            
            conn.commit()
            self._release(conn)
        except Exception as e:
            print(f"[DB Error] Log Prices: {e}")

    def log_snapshot(self, timestamp: datetime, state: str, risk: float, regime: str):
        """Log system state snapshot"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            query = f"INSERT INTO system_state (timestamp, state, risk_score, regime) VALUES ({ph}, {ph}, {ph}, {ph})"
            
            ts = timestamp if self.db_type == 'postgresql' else timestamp.isoformat()
            cursor.execute(query, (ts, state, risk, regime))
            
            conn.commit()
            self._release(conn)
        except Exception as e:
            print(f"[DB Error] Log Snapshot: {e}")

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get recent market events"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            cursor.execute(f"SELECT * FROM market_events ORDER BY id DESC LIMIT {ph}", (limit,))
            
            columns = ['id', 'timestamp', 'description', 'impact', 'type']
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            self._release(conn)
            return rows
        except Exception as e:
            print(f"[DB Error] Get Events: {e}")
            return []

    def get_price_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get price history for a symbol"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            cursor.execute(
                f"SELECT * FROM ticker_history WHERE symbol = {ph} ORDER BY id DESC LIMIT {ph}",
                (symbol, limit)
            )
            
            columns = ['id', 'timestamp', 'symbol', 'price', 'change_pct', 'volume']
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            self._release(conn)
            return rows
        except Exception as e:
            print(f"[DB Error] Get Price History: {e}")
            return []
