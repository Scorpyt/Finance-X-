"""
User Data Manager for Finance-X
Supports Neon PostgreSQL (production) and SQLite (local development)
"""
import time
from db_config import (
    get_db_type, 
    get_pooled_connection, 
    release_connection,
    get_placeholder
)

class UserManager:
    """
    Manages User Data: Portfolio, Settings, Disruption Limits.
    Automatically uses PostgreSQL or SQLite based on configuration.
    """
    
    def __init__(self):
        self.db_type = get_db_type()
        self.initialize_db()
        print(f"[UserManager] Using {self.db_type.upper()}")

    def get_connection(self):
        """Get a database connection (pooled for PostgreSQL)"""
        return get_pooled_connection()

    def _release(self, conn):
        """Release connection back to pool"""
        release_connection(conn)

    def initialize_db(self):
        """Initialize user database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            # PostgreSQL schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    entry_price NUMERIC(15,4) NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    stop_loss_limit NUMERIC(6,2) DEFAULT 10.0,
                    timestamp NUMERIC(20,6)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    message TEXT,
                    timestamp NUMERIC(20,6)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)')
            
        else:
            # SQLite schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    stop_loss_limit REAL DEFAULT 10.0,
                    timestamp REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    message TEXT,
                    timestamp REAL
                )
            ''')
        
        conn.commit()
        self._release(conn)
        print(f"[UserManager] Database initialized")

    def add_position(self, symbol, price, qty=1, limit=10.0):
        """Add a new position to portfolio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            query = f'''
                INSERT INTO portfolio (symbol, entry_price, quantity, stop_loss_limit, timestamp)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            '''
            cursor.execute(query, (symbol.upper(), price, qty, limit, time.time()))
            
            conn.commit()
            self._release(conn)
            return True
        except Exception as e:
            print(f"[DB Error] Add Position: {e}")
            return False

    def get_portfolio(self):
        """Get all portfolio positions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM portfolio')
            
            columns = ['id', 'symbol', 'entry_price', 'quantity', 'stop_loss_limit', 'timestamp']
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            self._release(conn)
            return rows
        except Exception as e:
            print(f"[DB Error] Get Portfolio: {e}")
            return []

    def remove_position(self, position_id: int):
        """Remove a position by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            cursor.execute(f'DELETE FROM portfolio WHERE id = {ph}', (position_id,))
            
            conn.commit()
            self._release(conn)
            return True
        except Exception as e:
            print(f"[DB Error] Remove Position: {e}")
            return False

    def update_stop_loss(self, position_id: int, new_limit: float):
        """Update stop loss limit for a position"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            cursor.execute(
                f'UPDATE portfolio SET stop_loss_limit = {ph} WHERE id = {ph}',
                (new_limit, position_id)
            )
            
            conn.commit()
            self._release(conn)
            return True
        except Exception as e:
            print(f"[DB Error] Update Stop Loss: {e}")
            return False

    def log_alert(self, symbol, message):
        """Log a disruption alert"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            query = f'INSERT INTO alerts (symbol, message, timestamp) VALUES ({ph}, {ph}, {ph})'
            cursor.execute(query, (symbol, message, time.time()))
            
            conn.commit()
            self._release(conn)
        except Exception as e:
            print(f"[DB Error] Log Alert: {e}")

    def get_alerts(self, limit: int = 50):
        """Get recent alerts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            ph = get_placeholder()
            cursor.execute(f'SELECT * FROM alerts ORDER BY id DESC LIMIT {ph}', (limit,))
            
            columns = ['id', 'symbol', 'message', 'timestamp']
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            self._release(conn)
            return rows
        except Exception as e:
            print(f"[DB Error] Get Alerts: {e}")
            return []
