"""
Enhanced Financial Intelligence Server
Extends the original server.py with institutional-grade features.

IMPORTANT: This file IMPORTS the original server, does not modify it.
Run with: uvicorn server_enhanced:app --port 8001
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Import ORIGINAL server components (read-only)
from server import app as original_app, engine, analyst, current_time, step_simulation
from models import MarketEvent, SystemState

# Import NEW extensions
from extensions.persistence import get_db
from extensions.data_feeds import get_feed
from extensions.audit import get_audit

# Initialize extensions
db = get_db()
feeds = get_feed()
audit = get_audit()

# Create enhanced app
app = FastAPI(title="Financial Intelligence Terminal - Enhanced")

# Feature flags from environment
USE_REAL_DATA = os.getenv("USE_REAL_DATA", "false").lower() == "true"
USE_PERSISTENCE = os.getenv("USE_PERSISTENCE", "true").lower() == "true"
USE_AUDIT = os.getenv("USE_AUDIT", "true").lower() == "true"

print(f"""
[Enhanced Server] Configuration:
  - Real Data: {'✅ ENABLED' if USE_REAL_DATA else '❌ DISABLED (using simulation)'}
  - Persistence: {'✅ ENABLED' if USE_PERSISTENCE else '❌ DISABLED'}
  - Audit Logging: {'✅ ENABLED' if USE_AUDIT else '❌ DISABLED'}
""")

# ============================================================================
# ORIGINAL ENDPOINTS (Proxied from server.py)
# ============================================================================

class CommandRequest(BaseModel):
    command: str

@app.post("/command")
def process_command_enhanced(req: CommandRequest):
    """
    Enhanced command processor with audit logging.
    Wraps original server.py logic.
    """
    # Audit logging
    if USE_AUDIT:
        audit.log_command(req.command, user="terminal")
    
    # INTERCEPT TANKERS command for rich metadata
    cmd = req.command.strip().upper()
    if cmd == "TANKERS":
        from extensions.command_handlers import enhance_tankers_command
        result = enhance_tankers_command(engine)
    elif cmd == "MARKETS":
        from extensions.command_handlers import get_market_map_data
        result = get_market_map_data()
    else:
        # Call original command processor
        from server import process_command
        result = process_command(req)
    
    # Log output for compliance
    if USE_AUDIT:
        audit.log_command(req.command, outputs=result)
    
    # Persist data if enabled
    if USE_PERSISTENCE and result.get("type") == "CHART_FULL":
        symbol = result.get("symbol")
        if symbol:
            ticker = engine.get_ticker(symbol)
            if ticker and ticker.history:
                db.store_price_batch(symbol, ticker.history)
    
    return result

@app.get("/api/v2/landing")
def get_landing_page_data():
    """
    Landing page market overview data from yfinance.
    Returns major indices, market movers, sector performance, and market summary.
    """
    try:
        from extensions.yfinance_data import YFinanceProvider
        provider = YFinanceProvider()
        return provider.get_landing_data()
    except Exception as e:
        logger.error(f"Landing page error: {e}")
        return {
            "indices": [],
            "movers": {"gainers": [], "losers": [], "active": []},
            "sectors": [],
            "summary": {"vix": 0, "volume": 0, "market_state": "UNKNOWN"},
            "error": str(e)
        }

# ============================================================================
# WRI AQUEDUCT WATER RISK ENDPOINTS
# ============================================================================

@app.get("/api/v2/water-risk/ports")
def get_port_water_risks():
    """
    Get water risk data for major shipping ports.
    Returns risk indicators, scores, and categories.
    """
    try:
        from extensions.wri_aqueduct import WRIAqueductProvider
        provider = WRIAqueductProvider()
        port_risks = provider.get_port_water_risks()
        return {
            "ports": [risk.dict() for risk in port_risks],
            "count": len(port_risks),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Water risk data error: {str(e)}")

@app.get("/api/v2/water-risk/commodities")
def get_commodity_region_risks():
    """
    Get water risk data for commodity-producing regions.
    Returns risk scores, trends, and alert levels.
    """
    try:
        from extensions.wri_aqueduct import WRIAqueductProvider
        provider = WRIAqueductProvider()
        commodity_risks = provider.get_commodity_region_risks()
        return {
            "regions": [risk.dict() for risk in commodity_risks],
            "count": len(commodity_risks),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commodity risk data error: {str(e)}")

@app.get("/api/v2/water-risk/alerts")
def get_water_risk_alerts():
    """
    Get active water risk alerts for supply chain monitoring.
    Returns critical and warning alerts.
    """
    try:
        from extensions.wri_aqueduct import WRIAqueductProvider
        provider = WRIAqueductProvider()
        alerts = provider.get_active_alerts()
        return {
            "alerts": [alert.dict() for alert in alerts],
            "count": len(alerts),
            "critical_count": sum(1 for a in alerts if a.alert_type == "Critical"),
            "warning_count": sum(1 for a in alerts if a.alert_type == "Warning"),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert data error: {str(e)}")

@app.get("/api/v2/water-risk/summary")
def get_water_risk_summary():
    """
    Get aggregate water risk summary dashboard.
    Returns overall statistics and top risk regions.
    """
    try:
        from extensions.wri_aqueduct import WRIAqueductProvider
        provider = WRIAqueductProvider()
        summary = provider.get_water_risk_summary()
        return summary.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary data error: {str(e)}")

# ============================================================================
# ORIGINAL ENDPOINTS (Continued)
# ============================================================================

@app.get("/status")
def get_status_enhanced():
    """Enhanced status with database stats"""
    from server import get_status
    original_status = get_status()
    
    if USE_PERSISTENCE:
        db_stats = db.get_statistics()
        original_status["database"] = db_stats
    
    return original_status

@app.get("/market")
def get_market_enhanced():
    """Enhanced market data with optional real feeds"""
    from server import get_market
    market_data = get_market()
    
    # Optionally inject real data
    if USE_REAL_DATA:
        try:
            # Update oil prices with real data
            oil_prices = feeds.fetch_oil_prices()
            for ticker in market_data:
                if ticker["symbol"] == "WTI":
                    ticker["price"] = oil_prices.get("WTI", ticker["price"])
                    ticker["source"] = oil_prices.get("source", "simulated")
                elif ticker["symbol"] == "BRENT":
                    ticker["price"] = oil_prices.get("BRENT", ticker["price"])
                    ticker["source"] = oil_prices.get("source", "simulated")
            
            # Update VIX with real data
            vix_price = feeds.fetch_vix()
            if vix_price:
                for ticker in market_data:
                    if ticker["symbol"] == "VIX":
                        ticker["price"] = vix_price
                        ticker["source"] = "Yahoo Finance"
            
            # Update BTC with real data
            btc_data = feeds.fetch_crypto_price("BTC")
            if btc_data:
                for ticker in market_data:
                    if ticker["symbol"] == "BTC":
                        ticker["price"] = btc_data["price"]
                        ticker["change"] = btc_data["change_pct"]
                        ticker["source"] = btc_data["source"]
        
        except Exception as e:
            print(f"[Enhanced] Real data fetch error: {e}")
    
    return market_data

# ============================================================================
# NEW ENDPOINTS (Institutional Features)
# ============================================================================

@app.get("/api/v2/history/{symbol}")
def get_historical_data(symbol: str, hours: int = 24):
    """
    Retrieve historical price data from database.
    Enables backtesting and analysis.
    """
    if not USE_PERSISTENCE:
        raise HTTPException(status_code=503, detail="Persistence not enabled")
    
    history = db.query_history(symbol, hours)
    
    return {
        "symbol": symbol,
        "hours": hours,
        "data_points": len(history),
        "history": [
            {
                "timestamp": p.timestamp.isoformat(),
                "price": p.price,
                "volume": p.volume
            }
            for p in history
        ]
    }

@app.get("/api/v2/database/stats")
def get_database_statistics():
    """Database health and statistics"""
    if not USE_PERSISTENCE:
        raise HTTPException(status_code=503, detail="Persistence not enabled")
    
    return db.get_statistics()

@app.get("/api/v2/audit/export")
def export_audit_trail(start: str, end: str):
    """
    Export audit trail for compliance.
    Format: ISO datetime strings
    Example: /api/v2/audit/export?start=2024-01-01T00:00:00&end=2024-01-02T00:00:00
    """
    if not USE_AUDIT:
        raise HTTPException(status_code=503, detail="Audit logging not enabled")
    
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format.")
    
    records = audit.export_audit_trail(start_dt, end_dt)
    
    return {
        "period": {"start": start, "end": end},
        "record_count": len(records),
        "records": records
    }

@app.get("/api/v2/audit/report")
def get_compliance_report(hours: int = 24):
    """
    Generate compliance report for auditors.
    Includes command statistics, anomalies, model decisions.
    """
    if not USE_AUDIT:
        raise HTTPException(status_code=503, detail="Audit logging not enabled")
    
    end = datetime.now()
    start = end - timedelta(hours=hours)
    
    return audit.generate_compliance_report(start, end)

@app.get("/api/v2/feeds/health")
def check_data_feeds():
    """
    Test all market data API connections.
    Returns status of EIA, IEX, CoinGecko, etc.
    """
    return feeds.health_check()

@app.post("/api/v2/ingest/realtime")
def ingest_realtime_data():
    """
    Manually trigger real-time data ingestion.
    Updates engine with latest market prices.
    """
    if not USE_REAL_DATA:
        return {"status": "disabled", "message": "Real data feeds not enabled"}
    
    results = {}
    
    # Fetch and update oil prices
    oil = feeds.fetch_oil_prices()
    if oil.get("source") == "EIA":
        wti_ticker = engine.get_ticker("WTI")
        brent_ticker = engine.get_ticker("BRENT")
        
        if wti_ticker:
            wti_ticker.current_price = oil["WTI"]
            results["WTI"] = oil["WTI"]
        
        if brent_ticker:
            brent_ticker.current_price = oil["BRENT"]
            results["BRENT"] = oil["BRENT"]
    
    # Fetch VIX
    vix_price = feeds.fetch_vix()
    if vix_price:
        vix_ticker = engine.get_ticker("VIX")
        if vix_ticker:
            vix_ticker.current_price = vix_price
            results["VIX"] = vix_price
    
    # Fetch BTC
    btc = feeds.fetch_crypto_price("BTC")
    if btc:
        btc_ticker = engine.get_ticker("BTC")
        if btc_ticker:
            btc_ticker.current_price = btc["price"]
            results["BTC"] = btc["price"]
    
    return {
        "status": "success",
        "updated_tickers": results,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v2/system/info")
def get_system_info():
    """
    System information and feature flags.
    Useful for monitoring and debugging.
    """
    return {
        "version": "2.0.0-enhanced",
        "features": {
            "real_data": USE_REAL_DATA,
            "persistence": USE_PERSISTENCE,
            "audit_logging": USE_AUDIT
        },
        "extensions": {
            "database": db.get_statistics() if USE_PERSISTENCE else None,
            "data_feeds": feeds.health_check() if USE_REAL_DATA else None
        },
        "uptime": "N/A",  # TODO: Track server start time
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# STATIC FILES (Same as original)
# ============================================================================

app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
def startup_event():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Financial Intelligence Terminal - ENHANCED               ║
    ║  Institutional-Grade Extensions Active                    ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  🗄️  Database: SQLite (data/market_data.db)              ║
    ║  📊 Real Data: EIA, IEX, CoinGecko, Yahoo Finance         ║
    ║  📝 Audit Log: MiFID II / SOX Compliant                  ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Original API: http://localhost:8000                      ║
    ║  Enhanced API: http://localhost:8001                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run health checks
    if USE_REAL_DATA:
        print("\n[Startup] Running data feed health checks...")
        health = feeds.health_check()
        for service, status in health.items():
            print(f"  {service}: {status}")
    
    if USE_PERSISTENCE:
        stats = db.get_statistics()
        print(f"\n[Startup] Database loaded: {stats['total_price_ticks']} price ticks, {stats['total_audit_logs']} audit logs")
