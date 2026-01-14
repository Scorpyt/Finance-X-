import sqlite3
from datetime import datetime
from typing import List, Dict, Any

class DatabaseManager:
    DB_NAME = "finance.db"

    def __init__(self):
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.DB_NAME, check_same_thread=False)

    def initialize_db(self):
        self.connect()
        cursor = self.conn.cursor()
        
        # Events Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                description TEXT,
                impact REAL,
                type TEXT
            )
        ''')

        # Prices Table
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

        # System State Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                state TEXT,
                risk_score REAL,
                regime TEXT
            )
        ''')
        
        self.conn.commit()
        print("[Database] Initialized finance.db with schema.")

    def log_event(self, timestamp: datetime, description: str, impact: float, type_str: str):
        try:
            self.connect()
            self.conn.execute(
                "INSERT INTO market_events (timestamp, description, impact, type) VALUES (?, ?, ?, ?)",
                (timestamp.isoformat(), description, impact, type_str)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[DB Error] Log Event: {e}")

    def log_price_batch(self, prices: List[Dict[str, Any]]):
        try:
            self.connect()
            data = [
                (p['timestamp'].isoformat(), p['symbol'], p['price'], p['change'], p['volume'])
                for p in prices
            ]
            self.conn.executemany(
                "INSERT INTO ticker_history (timestamp, symbol, price, change_pct, volume) VALUES (?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"[DB Error] Log Prices: {e}")

    def log_snapshot(self, timestamp: datetime, state: str, risk: float, regime: str):
        try:
            self.connect()
            self.conn.execute(
                "INSERT INTO system_state (timestamp, state, risk_score, regime) VALUES (?, ?, ?, ?)",
                (timestamp.isoformat(), state, risk, regime)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[DB Error] Log Snapshot: {e}")
