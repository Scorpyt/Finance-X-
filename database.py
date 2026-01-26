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
            
            # ML Prediction Tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    prediction_date TIMESTAMPTZ,
                    predicted_direction VARCHAR(10),
                    confidence_score NUMERIC(5,4),
                    actual_direction VARCHAR(10),
                    model_version VARCHAR(20),
                    features_json TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(50),
                    model_type VARCHAR(50),
                    version VARCHAR(20),
                    trained_date TIMESTAMPTZ,
                    accuracy NUMERIC(6,4),
                    precision_score NUMERIC(6,4),
                    recall_score NUMERIC(6,4),
                    f1_score NUMERIC(6,4),
                    model_path TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_performance (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMPTZ,
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    accuracy NUMERIC(6,4),
                    sharpe_ratio NUMERIC(8,4)
                )
            ''')
            
            # ML indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ml_pred_symbol ON ml_predictions(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ml_pred_date ON ml_predictions(prediction_date)')
            
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
            
            # ML Prediction Tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    prediction_date TEXT,
                    predicted_direction TEXT,
                    confidence_score REAL,
                    actual_direction TEXT,
                    model_version TEXT,
                    features_json TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    model_type TEXT,
                    version TEXT,
                    trained_date TEXT,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    model_path TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    accuracy REAL,
                    sharpe_ratio REAL
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
    
    def execute_query(self, query: str, params: tuple = None) -> List:
        """Execute a custom query (for ML engine)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
            else:
                conn.commit()
                results = []
            
            self._release(conn)
            return results
        except Exception as e:
            print(f"[DB Error] Execute Query: {e}")
            return []
