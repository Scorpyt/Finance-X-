from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

from models import MarketEvent, SystemState
from engine import IntelligenceEngine
from analyst import Analyst

app = FastAPI(title="Financial Intelligence Terminal")

# Global System State
engine = IntelligenceEngine(decay_rate=0.2)
analyst = Analyst()
current_time = datetime(2024, 1, 1, 9, 0, 0) # Simulation Start

# Seed Initial Data
initial_events = [
    ("Market Open - Normal trading", 2.0),
    ("Breaking: Inflation data higher than expected", 7.5),
]
for desc, impact in initial_events:
    engine.ingest(MarketEvent(current_time, "NEWS", desc, impact, "GENERAL"))

class CommandRequest(BaseModel):
    command: str

@app.post("/command")
def process_command(req: CommandRequest):
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
