from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

from models import MarketEvent, SystemState
from engine import IntelligenceEngine
from analyst import Analyst
from india_engine import IndiaMarketEngine
from user_data import UserManager
import secrets

ADMIN_KEY = "FIN-X-" + secrets.token_hex(2).upper()
print(f"\n{'='*40}\n[SECURITY] ADMIN ACCESS KEY: {ADMIN_KEY}\n{'='*40}\n")
SESSION_TOKENS = set()

app = FastAPI(title="Financial Intelligence Terminal")

# Global System State
engine = IntelligenceEngine(decay_rate=0.2)
engine.db.initialize_db()
analyst = Analyst()
india_engine = IndiaMarketEngine()
user_manager = UserManager()
current_time = datetime(2024, 1, 1, 9, 0, 0) # Simulation Start

# Seed Initial Data
initial_events = [
    ("Market Open - Normal trading", 2.0),
    ("Breaking: Inflation data higher than expected", 7.5),
]
for desc, impact in initial_events:
    engine.ingest(MarketEvent(current_time, "NEWS", desc, impact, "GENERAL"))

# Pre-roll simulation to generate history (24 hours)
print("Generating historical data...")
for _ in range(96): # 96 * 15 mins = 24 hours
    current_time += timedelta(minutes=15)
    engine.apply_decay(current_time)
    engine.detect_state(current_time)
print("System ready.")

class CommandRequest(BaseModel):
    command: str

@app.post("/command")
def process_command(req: CommandRequest, x_auth_token: str = Header(None)):
    cmd = req.command.strip().upper()
    
    # 1. Deterministic Command Routing
    if cmd == "TODAY":
        return {
            "type": "TABLE",
            "title": "Today's Event Log",
            "data": [
                {
                    "ID": i,
                    "Time": e.original_event.timestamp.strftime("%H:%M"),
                    "Description": e.original_event.description,
                    "Relevance": round(e.current_weight, 2)
                }
                for i, e in enumerate(engine.events)
            ]
        }
    
    elif cmd == "RISKS":
        snapshot = engine.detect_state(current_time) # Also triggers price update step if not called elsewhere, but we usually call step_simulation
        # But for UI consistency, let's just GET the state.
        # Ideally, simulation steps happen on a clock, but here we drive it via commands or specific update calls.
        # Let's verify we are getting the latest.
        return {
            "type": "REPORT",
            "title": "Risk Analysis",
            "state": snapshot.state.value,
            "risk_score": snapshot.risk_score,
            "details": f"Regime: {snapshot.regime.value}\nTotal Risk: {snapshot.risk_score}\nDrivers: {len(snapshot.active_events)}"
        }
    
    elif cmd == "MEMORY":
        return {
            "type": "CHART",
            "title": "Memory Decay Visualization",
            "data": [
                {"label": e.original_event.description[:15]+"...", "value": e.current_weight}
                for e in engine.events
            ]
        }

    elif cmd.startswith("EVENT "):
        try:
            evt_id = int(cmd.split(" ")[1])
            target_event = engine.events[evt_id]
            explanation = analyst.explain_event(target_event)
            return {
                "type": "TEXT",
                "title": f"Analyst Insight: Event #{evt_id}",
                "content": explanation
            }
        except:
             return {"type": "ERROR", "content": "Event ID Not Found."}
             
    elif cmd == "NIFTY":
        snapshot = india_engine.fetch_market_snapshot()
        return {
            "type": "OVERVIEW_GRID",
            "title": "REAL-TIME NIFTY 50 (LIVE)",
            "grids": snapshot
        }
        
    elif cmd.startswith("EVAL "):
        target = cmd.split(" ")[1]
        analysis = india_engine.get_stock_analysis(target)
        if "error" in analysis: return {"type": "ERROR", "content": analysis["error"]}
        
        return {
            "type": "REPORT",
            "title": f"DEEP DIVE: {analysis['symbol']}",
            "state": analysis['trend'],
            "risk_score": 0.0,
            "details": f"PREDICTION: {analysis['prediction']}\nFACTORS: {', '.join(analysis['factors'])}\nPRICE: {analysis['price']}\nWARNING: {analysis.get('warning') or 'None'}"
        }

    elif cmd == "DISRUPTION":
         alerts = india_engine.check_portfolio_health(user_manager.get_portfolio())
         status_text = "SAFE" if not alerts else "CRITICAL RISK"
         content = "Portfolio stable. No stop-loss breaches."
         if alerts:
             content = "⚠️ WARNING: DISRUPTION DETECTED ⚠️\n" + "\n".join([f"{a['symbol']}: {a['message']}" for a in alerts])
             
         return {
             "type": "TEXT",
             "title": f"DISRUPTION MONITOR: {status_text}",
             "content": content
         }

    elif cmd.startswith("BUY "):
        # Syntax: BUY SYM PRICE QTY
        try:
            parts = cmd.split(" ")
            sym = parts[1]
            price = float(parts[2])
            qty = int(parts[3]) if len(parts) > 3 else 1
            
            success = user_manager.add_position(sym, price, qty)
            if success:
                return {"type": "SUCCESS", "content": f"Position Added: {qty} x {sym} @ {price}"}
            else:
                return {"type": "ERROR", "content": "Database Error."}
        except:
             return {"type": "ERROR", "content": "Usage: BUY [SYMBOL] [PRICE] [QTY]"}

    elif cmd.startswith("QUOTE "):
        symbol = cmd.split(" ")[1]
        ticker = engine.get_ticker(symbol)
        if ticker:
            return {
                "type": "QUOTE",
                "title": f"Quote: {symbol}",
                "symbol": ticker.symbol,
                "price": ticker.current_price,
                "change": float(f"{ticker.change_pct:.2f}"),
                "history": [{"t": p.timestamp.strftime("%H:%M"), "p": p.price, "v": p.volume} for p in ticker.history]
            }
        else:
            return {"type": "ERROR", "content": "Symbol Not Found."}

    elif cmd.startswith("CHART "):
        symbol = cmd.split(" ")[1]
        ticker = engine.get_ticker(symbol)
        if ticker:
             return {
                "type": "CHART_FULL",
                "symbol": ticker.symbol,
                "history": [{"t": p.timestamp.strftime("%H:%M"), "p": p.price, "v": p.volume} for p in ticker.history]
            }
        else:
            return {"type": "ERROR", "content": "Symbol Not Found."}

    elif cmd == "DISRUPTION":
         return {
            "type": "TEXT",
            "title": "Disruption Logic",
            "content": "CRASH State Logic:\nIF Total_Risk_Score > 25.0\nAND Active_High_Impact_Events > 2\nTHEN STATE = CRASH\nELSE STATE = VOLATILE or STABLE"
        }
    
    elif cmd == "SCAN":
        snapshot = engine.detect_state(current_time)
        return {
            "type": "TEXT",
            "title": "System Scan",
            "content": f"SCAN COMPLETE.\nREGIME: {snapshot.regime.value}\nVOLATILITY INDEX: {engine.get_ticker('VIX').current_price}\nANOMALIES: {len(snapshot.active_events)} active risk events."
        }

    elif cmd == "OVERVIEW":
        # Return history for a grid of key/popular tickers
        targets = ["SPX", "NDX", "BTC", "VIX", "AAPL", "NVDA", "WTI", "JPM", "XOM"]
        grid_data = []
        for sym in targets:
            t = engine.get_ticker(sym)
            if t:
                grid_data.append({
                    "symbol": t.symbol,
                    "price": t.current_price,
                    "change": float(f"{t.change_pct:.2f}"),
                    "history": [{"p": p.price} for p in t.history] # minimal history
                })
        
        return {
            "type": "OVERVIEW_GRID",
            "title": "Global Market Overview",
            "grids": grid_data
        }

    elif cmd == "TANKERS":
        # Return geospatial data
        metrics = engine.tanker_sim.get_supply_metrics()
        return {
            "type": "MAP_DATA",
            "title": f"Global Asset Tracking ({metrics['total_ships']} Vessels)",
            "metrics": f"VOL AT SEA: {int(metrics['volume_index'])} | ACTIVE: {int(metrics['moving_ratio']*100)}%",
            "assets": [
                {
                    "id": t.id,
                    "name": t.name,
                    "lat": t.location.lat,
                    "lon": t.location.lon,
                    "status": t.status,
                    "dest": t.destination,
                    "heading": t.heading
                }
                for t in engine.tanker_sim.tankers
            ]
        }

    elif cmd == "NEWS":
        # Filter for high importance or energy
        news_items = [e for e in engine.events if e.current_weight > 4.0 or "Inf" in e.original_event.description]
        return {
            "type": "NEWS_FEED",
            "title": "High-Impact Intelligence Stream",
            "data": [
                 {
                    "time": e.original_event.timestamp.strftime("%H:%M"),
                    "source": "REUTERS/BLOOMBERG",
                    "headline": e.original_event.description,
                    "impact": e.original_event.base_impact
                 }
                 for e in news_items
            ]
        }
        
    elif cmd.startswith("ADVISE"):
        # "Heavy Logic" Advisor
        # usage: ADVISE AAPL or just ADVISE (for general system)
        parts = cmd.split(" ")
        target = parts[1] if len(parts) > 1 else "SPX"
        ticker = engine.get_ticker(target)
        
        if not ticker:
             return {"type": "ERROR", "content": "Symbol Not Found."}
             
        from engine import TechnicalAnalysis
        analysis = TechnicalAnalysis.analyze_risk_depth(ticker)
        
        return {
            "type": "REPORT",
            "title": f"ALGORITHMIC ADVISOR: {target}",
            "state": analysis['depth'],
            "risk_score": engine.detect_state(current_time).risk_score,
            "details": f"STRATEGY: {analysis['advice']}\nBEST BID: {analysis['bid']:.2f}\nVOLATILITY SPREAD: {analysis['volatility']:.4f}\n\nLOGIC: Price deviation from Bollinger Mean suggests {analysis['depth'].lower()} conditions. Supply metrics confirm trend."
        }
        

    
    # AUTH Handshake
    if cmd.startswith("AUTH "):
        key = cmd.split(" ")[1]
        if key == ADMIN_KEY:
            token = secrets.token_hex(16)
            SESSION_TOKENS.add(token)
            return {
                "type": "AUTH_SUCCESS", 
                "title": "ACCESS GRANTED",
                "token": token,
                "content": "Identity Verified. Admin Console Unlocked."
            }
        else:
             return {"type": "ERROR", "content": "ACCESS DENIED. Invalid Key."}

    # Protected Commands
    is_admin = x_auth_token in SESSION_TOKENS
    
    if cmd.startswith("SQL "):
        if not is_admin:
            return {"type": "ERROR", "content": "UNAUTHORIZED. Admin Access Required (Use AUTH [KEY])."}
        
        query = cmd[4:]
        try:
            # Dangerous! Only for simulated admin console
            conn = engine.db.conn
            cursor = conn.execute(query)
            conn.commit()
            
            if query.strip().upper().startswith("SELECT"):
                cols = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                # Format as simple text table
                res = " | ".join(cols) + "\n" + "-" * 50 + "\n"
                for row in rows[:20]: # Limit output
                    res += " | ".join(map(str, row)) + "\n"
                if len(rows) > 20: res += f"... ({len(rows)} total rows)"
                
                return {"type": "TEXT", "title": "SQL RESULT", "content": res}
            else:
                return {"type": "SUCCESS", "content": f"Query Executed. Rows affected: {cursor.rowcount}"}
                
        except Exception as e:
            return {"type": "ERROR", "content": f"SQL ERROR: {str(e)}"}

    if cmd == "HELP" or cmd == "ACTIONS":
        return {
            "type": "HELP_MENU",
            "title": "Command Palette Actions",
            "sections": [
                {"category": "DASHBOARDS", "cmds": ["OVERVIEW (Main Grid)", "TANKERS (Asset Map)", "RISKS (System State)", "SCAN (Quick Diag)"]},
                {"category": "ANALYSIS", "cmds": ["CHART [SYM] (View Chart)", "QUOTE [SYM] (Price)", "ADVISE [SYM] (AI Insight)", "NEWS (Intel Feed)"]},
                {"category": "SYSTEM", "cmds": ["TODAY (Event Log)", "MEMORY (Decay Viz)", "NEXT (Step Sim)", "DISRUPTION (Logic Info)"]},
                {"category": "ADMIN", "cmds": ["AUTH [KEY] (Login)", "SQL [QUERY] (DB Access)"]}
            ]
        }


    elif cmd.startswith("CHART "):
        symbol = cmd.split(" ")[1]
        ticker = engine.get_ticker(symbol)
        if ticker:
             from engine import TechnicalAnalysis
             u, m, l = TechnicalAnalysis.calculate_bollinger_bands(ticker.history)
             return {
                "type": "CHART_FULL",
                "symbol": ticker.symbol,
                "history": [{"t": p.timestamp.strftime("%H:%M"), "p": p.price, "v": p.volume} for p in ticker.history],
                "bands": {"upper": u, "middle": m, "lower": l}
            }
        else:
            return {"type": "ERROR", "content": "Symbol Not Found."}
        
    elif cmd == "NEXT":
        step_simulation()
        return {"type": "TEXT", "title": "System Update", "content": "Time advanced +30 mins. Prices updated."}

    else:
        return {"type": "ERROR", "content": f"Unknown Command: {cmd}"}

@app.get("/status")
def get_status():
    snapshot = engine.detect_state(current_time) 
    return {
        "time": current_time.strftime("%H:%M"),
        "state": snapshot.state.value,
        "risk": snapshot.risk_score,
        "regime": snapshot.regime.value
    }

@app.get("/market")
def get_market():
    return engine.get_all_tickers()

from performance_engine import HardwareNavigator

@app.get("/system/diagnostics")
def get_sys_diagnostics():
    return HardwareNavigator.get_system_metrics()

def step_simulation():
    global current_time
    # Smaller steps for smoother tanker movement appearance if we spam NEXT
    current_time += timedelta(minutes=15)
    engine.apply_decay(current_time)
    engine.detect_state(current_time) # Updates prices & tankers
    
    # Inject Random Event
    if random.random() > 0.8:
        impact = random.uniform(1.0, 9.0)
        desc = f"Simulated Event at {current_time.strftime('%H:%M')}"
        if impact > 7: desc = f"ENERGY SECTOR ALERT at {current_time.strftime('%H:%M')}"
        engine.ingest(MarketEvent(current_time, "SIM", desc, impact, "GEN"))

app.mount("/", StaticFiles(directory="static", html=True), name="static")
