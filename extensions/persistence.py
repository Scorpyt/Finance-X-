"""
Persistence Layer - Database Integration
Provides SQLite storage for price history and audit trails
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

# Import from core system (read-only)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import PricePoint, ProcessedEvent, MarketEvent


class PersistenceEngine:
    """
    Time-series database for market data and audit trails.
    Uses SQLite for development, easily upgradable to PostgreSQL/TimescaleDB.
    """
    
    def __init__(self, db_path: str = "data/market_data.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_schema()
        
    def _create_schema(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_time 
            ON price_history(ticker, timestamp DESC)
        """)
        
        # Audit log table (compliance)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                user TEXT DEFAULT 'system',
                command TEXT NOT NULL,
                inputs TEXT,
                outputs TEXT,
                model_version TEXT DEFAULT '1.0.0',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Event history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                base_impact REAL NOT NULL,
                asset_class TEXT,
                current_weight REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        print(f"[Persistence] Database initialized: {self.db_path}")
    
    def store_price_tick(self, ticker: str, point: PricePoint):
        """Store a single price point"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO price_history (ticker, timestamp, price, volume)
            VALUES (?, ?, ?, ?)
        """, (ticker, point.timestamp, point.price, point.volume))
        self.conn.commit()
    
    def store_price_batch(self, ticker: str, points: List[PricePoint]):
        """Bulk insert for efficiency"""
        cursor = self.conn.cursor()
        data = [(ticker, p.timestamp, p.price, p.volume) for p in points]
        cursor.executemany("""
            INSERT INTO price_history (ticker, timestamp, price, volume)
            VALUES (?, ?, ?, ?)
        """, data)
        self.conn.commit()
        print(f"[Persistence] Stored {len(points)} ticks for {ticker}")
    
    def query_history(self, ticker: str, hours: int = 24) -> List[PricePoint]:
        """Retrieve historical data"""
        cursor = self.conn.cursor()
        cutoff = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT timestamp, price, volume
            FROM price_history
            WHERE ticker = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (ticker, cutoff))
        
        rows = cursor.fetchall()
        return [
            PricePoint(
                timestamp=datetime.fromisoformat(row[0]),
                price=row[1],
                volume=row[2]
            )
            for row in rows
        ]
    
    def query_latest_price(self, ticker: str) -> Optional[PricePoint]:
        """Get most recent price"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, price, volume
            FROM price_history
            WHERE ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (ticker,))
        
        row = cursor.fetchone()
        if row:
            return PricePoint(
                timestamp=datetime.fromisoformat(row[0]),
                price=row[1],
                volume=row[2]
            )
        return None
    
    def store_event(self, event: ProcessedEvent):
        """Store event for audit trail"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO event_history 
            (timestamp, event_type, description, base_impact, asset_class, current_weight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.original_event.timestamp,
            event.original_event.event_type,
            event.original_event.description,
            event.original_event.base_impact,
            event.original_event.asset_class,
            event.current_weight
        ))
        self.conn.commit()
    
    def log_command(self, command: str, inputs: Dict = None, outputs: Dict = None, user: str = "terminal"):
        """Compliance logging - every command tracked"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, user, command, inputs, outputs)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            user,
            command,
            json.dumps(inputs) if inputs else None,
            json.dumps(outputs) if outputs else None
        ))
        self.conn.commit()
    
    def export_audit_trail(self, start: datetime, end: datetime) -> List[Dict]:
        """Export audit log for compliance reporting"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, user, command, inputs, outputs
            FROM audit_log
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (start, end))
        
        rows = cursor.fetchall()
        return [
            {
                "timestamp": row[0],
                "user": row[1],
                "command": row[2],
                "inputs": json.loads(row[3]) if row[3] else {},
                "outputs": json.loads(row[4]) if row[4] else {}
            }
            for row in rows
        ]
    
    def get_statistics(self) -> Dict:
        """Database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM price_history")
        price_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        audit_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM event_history")
        event_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT ticker) FROM price_history")
        ticker_count = cursor.fetchone()[0]
        
        return {
            "total_price_ticks": price_count,
            "total_audit_logs": audit_count,
            "total_events": event_count,
            "tracked_tickers": ticker_count,
            "database_path": self.db_path
        }
    
    def close(self):
        """Clean shutdown"""
        self.conn.close()
        print("[Persistence] Database connection closed")


# Singleton instance
_db_instance = None

def get_db() -> PersistenceEngine:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = PersistenceEngine()
    return _db_instance
