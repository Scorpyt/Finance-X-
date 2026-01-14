import sqlite3
import time
import os

class UserManager:
    """
    Manages User Data: Portfolio, Settings, Disruption Limits.
    Storage: users.db (SQLite)
    """
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def initialize_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Portfolio Table
        # Tracks what the user bought, at what price
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
        
        # Disruption History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                message TEXT,
                timestamp REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_position(self, symbol, price, qty=1, limit=10.0):
        try:
            conn = self.get_connection()
            conn.execute('''
                INSERT INTO portfolio (symbol, entry_price, quantity, stop_loss_limit, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol.upper(), price, qty, limit, time.time()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    def get_portfolio(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM portfolio')
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def log_alert(self, symbol, message):
        conn = self.get_connection()
        conn.execute('INSERT INTO alerts (symbol, message, timestamp) VALUES (?, ?, ?)',
                     (symbol, message, time.time()))
        conn.commit()
        conn.close()
