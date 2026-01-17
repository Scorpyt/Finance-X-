#!/usr/bin/env python3
"""
Fast Migration Script: SQLite to Neon PostgreSQL
Uses batch inserts for speed (handles 50K+ rows)
"""
import os
import sqlite3
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

def main():
    import psycopg2
    
    print("=" * 50)
    print("🚀 Finance-X: FAST Migration to Neon PostgreSQL")
    print("=" * 50)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    pg_conn = psycopg2.connect(database_url)
    print("✅ Connected to Neon PostgreSQL!")
    
    # Create schema
    print("\n📦 Creating schema...")
    cursor = pg_conn.cursor()
    
    # Drop existing tables to start fresh (optional - comment out if you want to keep data)
    cursor.execute('DROP TABLE IF EXISTS ticker_history CASCADE')
    cursor.execute('DROP TABLE IF EXISTS system_state CASCADE')
    cursor.execute('DROP TABLE IF EXISTS market_events CASCADE')
    cursor.execute('DROP TABLE IF EXISTS portfolio CASCADE')
    cursor.execute('DROP TABLE IF EXISTS alerts CASCADE')
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_events (
            id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ, description TEXT,
            impact NUMERIC(10,4), type VARCHAR(50)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticker_history (
            id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ, symbol VARCHAR(20),
            price NUMERIC(15,4), change_pct NUMERIC(8,4), volume BIGINT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_state (
            id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ, state TEXT,
            risk_score NUMERIC(6,4), regime VARCHAR(50)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id SERIAL PRIMARY KEY, symbol VARCHAR(20) NOT NULL,
            entry_price NUMERIC(15,4) NOT NULL, quantity INTEGER DEFAULT 1,
            stop_loss_limit NUMERIC(6,2) DEFAULT 10.0, timestamp NUMERIC(20,6)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY, symbol VARCHAR(20) NOT NULL,
            message TEXT, timestamp NUMERIC(20,6)
        )
    ''')
    pg_conn.commit()
    print("✅ Schema created!")
    
    # Migrate finance.db
    print("\n📊 Migrating finance.db...")
    if os.path.exists('finance.db'):
        sqlite_conn = sqlite3.connect('finance.db')
        
        # market_events
        rows = sqlite_conn.execute('SELECT timestamp, description, impact, type FROM market_events').fetchall()
        if rows:
            execute_values(cursor, 
                'INSERT INTO market_events (timestamp, description, impact, type) VALUES %s',
                rows, page_size=1000)
            print(f"   ✅ market_events: {len(rows)} rows")
        
        # ticker_history (BATCH)
        rows = sqlite_conn.execute('SELECT timestamp, symbol, price, change_pct, volume FROM ticker_history').fetchall()
        if rows:
            execute_values(cursor,
                'INSERT INTO ticker_history (timestamp, symbol, price, change_pct, volume) VALUES %s',
                rows, page_size=5000)
            print(f"   ✅ ticker_history: {len(rows)} rows")
        
        # system_state
        rows = sqlite_conn.execute('SELECT timestamp, state, risk_score, regime FROM system_state').fetchall()
        if rows:
            execute_values(cursor,
                'INSERT INTO system_state (timestamp, state, risk_score, regime) VALUES %s',
                rows, page_size=1000)
            print(f"   ✅ system_state: {len(rows)} rows")
        
        sqlite_conn.close()
        pg_conn.commit()
    
    # Migrate users.db
    print("\n👤 Migrating users.db...")
    if os.path.exists('users.db'):
        sqlite_conn = sqlite3.connect('users.db')
        
        # portfolio
        rows = sqlite_conn.execute('SELECT symbol, entry_price, quantity, stop_loss_limit, timestamp FROM portfolio').fetchall()
        if rows:
            execute_values(cursor,
                'INSERT INTO portfolio (symbol, entry_price, quantity, stop_loss_limit, timestamp) VALUES %s',
                rows, page_size=1000)
            print(f"   ✅ portfolio: {len(rows)} rows")
        
        # alerts
        rows = sqlite_conn.execute('SELECT symbol, message, timestamp FROM alerts').fetchall()
        if rows:
            execute_values(cursor,
                'INSERT INTO alerts (symbol, message, timestamp) VALUES %s',
                rows, page_size=1000)
            print(f"   ✅ alerts: {len(rows)} rows")
        
        sqlite_conn.close()
        pg_conn.commit()
    
    # Create indexes
    print("\n📇 Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_symbol ON ticker_history(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_timestamp ON ticker_history(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)')
    pg_conn.commit()
    print("✅ Indexes created!")
    
    pg_conn.close()
    
    print("\n" + "=" * 50)
    print("🎉 Migration complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
