from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

from models import MarketEvent, SystemState
from engine import IntelligenceEngine
from analyst import Analyst
from india_engine import IndiaMarketEngine
from user_data import UserManager
from study_engine import StudyEngine
from bloomberg_engine import BloombergEngine
from volatility import VolatilityAnalyzer, rolling_volatility, historical_volatility, volatility_regime_detection
from heatmap import HeatmapGenerator, sector_performance_heatmap, market_overview_heatmap, correlation_strength_heatmap
import secrets
import pandas as pd
import numpy as np

ADMIN_KEY = "FIN-X-" + secrets.token_hex(2).upper()
print(f"\n{'='*40}\n[SECURITY] ADMIN ACCESS KEY: {ADMIN_KEY}\n{'='*40}\n")
SESSION_TOKENS = set()

app = FastAPI(title="Financial Intelligence Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global System State
engine = IntelligenceEngine(decay_rate=0.2)
engine.db.initialize_db()
analyst = Analyst()
india_engine = IndiaMarketEngine()
user_manager = UserManager()
study_engine = StudyEngine()
bloomberg_engine = BloombergEngine()
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

# Global state for UI monitoring
LAST_COMMAND = {"cmd": "NONE", "status": "IDLE", "time": ""}

@app.post("/command")
def process_command(req: CommandRequest, x_auth_token: str = Header(None)):
    global LAST_COMMAND
    cmd = req.command.strip().upper()
    
    # Track command for Jarvis
    LAST_COMMAND = {
        "cmd": cmd,
        "status": "EXECUTED",
        "time": current_time.strftime("%H:%M:%S")
    }
    
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
                "type": "CHART",
                "title": f"Market Data: {symbol}",
                "data": engine.get_market_chart_data(symbol)
            }
        else:
            # Fallback: Try India engine for NSE stocks
            nse_symbol = symbol + ".NS" if not symbol.endswith(".NS") else symbol
            try:
                import yfinance as yf
                data = yf.Ticker(nse_symbol).history(period="5d")
                if not data.empty:
                    history = [{"t": str(idx.strftime("%H:%M")), "p": float(row['Close']), "v": int(row['Volume'])} 
                               for idx, row in data.iterrows()]
                    return {
                        "type": "CHART_FULL",
                        "symbol": symbol.upper(),
                        "history": history
                    }
            except Exception:
                pass
            return {"type": "ERROR", "content": "Symbol Not Found. Try NIFTY 50 symbols like TCS, INFY, RELIANCE."}

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

    elif cmd == "STUDY":
        # Main Study Section - Live News + Resources
        data = study_engine.get_study_overview()
        return {
            "type": "STUDY_VIEW",
            "title": "📚 STUDY CENTER",
            "news": data["news"],
            "resources": data["resources"],
            "glossary_count": data["glossary_count"],
            "last_updated": data["last_updated"]
        }
    
    elif cmd.startswith("LEARN "):
        # Learning resources by topic
        topic = cmd.split(" ", 1)[1] if len(cmd.split(" ")) > 1 else None
        resources = study_engine.get_study_resources(topic)
        return {
            "type": "LEARN_VIEW",
            "title": f"📖 Learning: {topic or 'All Topics'}",
            "resources": resources
        }
    
    elif cmd.startswith("GLOSSARY"):
        # Market terms glossary
        parts = cmd.split(" ", 1)
        term = parts[1] if len(parts) > 1 else None
        glossary = study_engine.get_glossary(term)
        return {
            "type": "GLOSSARY_VIEW",
            "title": f"📋 {term.title() if term else 'Market Glossary'}",
            "terms": glossary
        }

    # === BLOOMBERG-STYLE FEATURES ===
    elif cmd == "FX":
        rates = bloomberg_engine.get_fx_rates()
        return {
            "type": "FX_VIEW",
            "title": "💱 LIVE FX RATES",
            "rates": rates,
            "updated": datetime.now().strftime("%H:%M:%S")
        }
    
    elif cmd.startswith("SCREEN"):
        parts = cmd.split(" ")
        criteria = parts[1] if len(parts) > 1 else "GAINERS"
        market_data = india_engine.fetch_market_snapshot()
        results = bloomberg_engine.screen_stocks(market_data, criteria)
        return {
            "type": "SCREENER_VIEW",
            "title": f"🔍 SCREENER: {criteria.upper()}",
            "criteria": criteria.upper(),
            "results": results
        }
    
    elif cmd == "MOVERS":
        market_data = india_engine.fetch_market_snapshot()
        movers = bloomberg_engine.get_top_movers(market_data)
        summary = bloomberg_engine.get_market_summary(market_data)
        return {
            "type": "MOVERS_VIEW",
            "title": "📈 TOP MOVERS",
            "gainers": movers["gainers"],
            "losers": movers["losers"],
            "summary": summary
        }
    
    elif cmd == "SECTORS":
        sectors = bloomberg_engine.get_sector_performance()
        return {
            "type": "SECTORS_VIEW",
            "title": "🏢 SECTOR HEATMAP",
            "sectors": sectors,
            "updated": datetime.now().strftime("%H:%M:%S")
        }
    
    elif cmd == "CALENDAR":
        events = bloomberg_engine.get_economic_calendar()
        return {
            "type": "CALENDAR_VIEW",
            "title": "📅 ECONOMIC CALENDAR",
            "events": events
        }
    
    # === VOLATILITY ANALYSIS COMMANDS ===
    elif cmd.startswith("VOL "):
        # Volatility analysis for a specific symbol
        symbol = cmd.split(" ")[1]
        
        # Try to get data from India engine first
        nse_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
        try:
            import yfinance as yf
            ticker_data = yf.Ticker(nse_symbol)
            hist = ticker_data.history(period="3mo", interval="1d")
            
            if hist.empty:
                return {"type": "ERROR", "content": f"No data found for {symbol}"}
            
            # Create volatility analyzer
            prices = hist['Close']
            analyzer = VolatilityAnalyzer(
                prices=prices,
                high=hist['High'],
                low=hist['Low'],
                open_price=hist['Open']
            )
            
            # Get all metrics
            metrics = analyzer.get_all_metrics(window=20)
            
            # Calculate additional metrics
            vol_20 = historical_volatility(prices, window=20).iloc[-1] if len(prices) > 20 else 0
            vol_50 = historical_volatility(prices, window=50).iloc[-1] if len(prices) > 50 else 0
            regime = volatility_regime_detection(prices, window=20).iloc[-1]
            
            return {
                "type": "VOLATILITY_VIEW",
                "title": f"📊 VOLATILITY ANALYSIS: {symbol}",
                "symbol": symbol,
                "current_price": float(prices.iloc[-1]),
                "metrics": {
                    "rolling_vol_20d": f"{metrics.get('rolling_vol', 0):.4f}",
                    "historical_vol_annual": f"{metrics.get('historical_vol', 0):.2%}",
                    "ewma_vol": f"{metrics.get('ewma_vol', 0):.4f}",
                    "vol_percentile": f"{metrics.get('vol_percentile', 0):.1f}%",
                    "parkinson_vol": f"{metrics.get('parkinson_vol', 0):.4f}" if 'parkinson_vol' in metrics else "N/A",
                    "garman_klass_vol": f"{metrics.get('garman_klass_vol', 0):.4f}" if 'garman_klass_vol' in metrics else "N/A"
                },
                "regime": regime,
                "comparison": {
                    "vol_20d": f"{vol_20:.2%}",
                    "vol_50d": f"{vol_50:.2%}",
                    "vol_ratio": f"{(vol_20/vol_50 if vol_50 > 0 else 1.0):.2f}"
                }
            }
        except Exception as e:
            return {"type": "ERROR", "content": f"Volatility analysis error: {str(e)}"}
    
    elif cmd == "VOLSCAN":
        # Scan market for high volatility stocks
        market_data = india_engine.fetch_market_snapshot()
        
        if not market_data:
            return {"type": "ERROR", "content": "No market data available"}
        
        # Calculate volatility for each stock
        vol_stocks = []
        for stock in market_data[:20]:  # Limit to first 20 for performance
            try:
                symbol = stock['symbol'] + ".NS"
                import yfinance as yf
                hist = yf.Ticker(symbol).history(period="1mo", interval="1d")
                
                if not hist.empty and len(hist) > 10:
                    prices = hist['Close']
                    vol = historical_volatility(prices, window=10, annualize=True).iloc[-1]
                    regime = volatility_regime_detection(prices, window=10).iloc[-1]
                    
                    vol_stocks.append({
                        "symbol": stock['symbol'],
                        "price": stock['price'],
                        "volatility": vol,
                        "regime": regime,
                        "change_pct": stock.get('change_pct', 0)
                    })
            except:
                continue
        
        # Sort by volatility descending
        vol_stocks = sorted(vol_stocks, key=lambda x: x['volatility'], reverse=True)
        
        return {
            "type": "VOLSCAN_VIEW",
            "title": "🔥 HIGH VOLATILITY SCANNER",
            "count": len(vol_stocks),
            "data": vol_stocks[:15]  # Top 15
        }
    
    elif cmd.startswith("HEATMAP"):
        # Heatmap visualization
        parts = cmd.split(" ")
        heatmap_type = parts[1].upper() if len(parts) > 1 else "SECTOR"
        
        if heatmap_type == "SECTOR":
            sectors = bloomberg_engine.get_sector_performance()
            heatmap_data = sector_performance_heatmap(sectors)
            
            return {
                "type": "HEATMAP_VIEW",
                "title": "🗺️ SECTOR PERFORMANCE HEATMAP",
                "heatmap_type": "sector",
                "data": heatmap_data
            }
        
        elif heatmap_type == "MARKET":
            market_data = india_engine.fetch_market_snapshot()
            heatmap_data = market_overview_heatmap(market_data, metric='change_pct')
            
            return {
                "type": "HEATMAP_VIEW",
                "title": "🗺️ MARKET OVERVIEW HEATMAP",
                "heatmap_type": "market",
                "data": heatmap_data
            }
        
        elif heatmap_type == "VOLUME":
            market_data = india_engine.fetch_market_snapshot()
            heatmap_data = market_overview_heatmap(market_data, metric='volume')
            
            return {
                "type": "HEATMAP_VIEW",
                "title": "🗺️ VOLUME HEATMAP",
                "heatmap_type": "volume",
                "data": heatmap_data
            }
        
        else:
            return {"type": "ERROR", "content": "Usage: HEATMAP [SECTOR/MARKET/VOLUME]"}
    
    elif cmd == "CORR":
        # Correlation matrix heatmap
        try:
            # Get NIFTY 50 data for correlation analysis
            import yfinance as yf
            symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
                      "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS"]
            
            # Download data
            data = yf.download(symbols, period="3mo", interval="1d", progress=False)
            
            if 'Close' in data.columns:
                price_data = data['Close']
                
                # Calculate correlation matrix
                from heatmap import calculate_correlation_matrix
                corr_matrix = calculate_correlation_matrix(price_data)
                
                # Generate heatmap
                heatmap_data = correlation_strength_heatmap(corr_matrix, threshold=0.5)
                
                return {
                    "type": "CORRELATION_VIEW",
                    "title": "🔗 CORRELATION MATRIX",
                    "data": heatmap_data
                }
            else:
                return {"type": "ERROR", "content": "Unable to fetch correlation data"}
                
        except Exception as e:
            return {"type": "ERROR", "content": f"Correlation analysis error: {str(e)}"}

        
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
                {"category": "DASHBOARDS", "cmds": ["OVERVIEW (Main Grid)", "NIFTY (India Market)", "MOVERS (Top Gainers/Losers)"]},
                {"category": "BLOOMBERG", "cmds": ["FX (Currency Rates)", "SCREEN [GAINERS/LOSERS/VOLUME]", "SECTORS (Heatmap)", "CALENDAR (Events)"]},
                {"category": "ANALYSIS", "cmds": ["CHART [SYM] (View Chart)", "QUOTE [SYM] (Price)", "ADVISE [SYM] (AI Insight)", "NEWS (Intel Feed)"]},
                {"category": "VOLATILITY", "cmds": ["VOL [SYM] (Volatility Analysis)", "VOLSCAN (High Vol Scanner)", "CORR (Correlation Matrix)"]},
                {"category": "HEATMAPS", "cmds": ["HEATMAP SECTOR (Sector Map)", "HEATMAP MARKET (Market Map)", "HEATMAP VOLUME (Volume Map)"]},
                {"category": "STUDY", "cmds": ["STUDY (News & Learn)", "LEARN [TOPIC] (Resources)", "GLOSSARY [TERM] (Definitions)"]},
                {"category": "SYSTEM", "cmds": ["TODAY (Event Log)", "RISKS (System State)", "SCAN (Quick Diag)", "NEXT (Step Sim)"]},
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
        "regime": snapshot.regime.value,
        "lastCommand": LAST_COMMAND
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
    current_time += timedelta(minutes=15)
    engine.apply_decay(current_time)
    engine.detect_state(current_time)  # Updates prices
    
    # Inject Random Event
    if random.random() > 0.8:
        impact = random.uniform(1.0, 9.0)
        desc = f"Simulated Event at {current_time.strftime('%H:%M')}"
        if impact > 7: desc = f"ENERGY SECTOR ALERT at {current_time.strftime('%H:%M')}"
        engine.ingest(MarketEvent(current_time, "SIM", desc, impact, "GEN"))

app.mount("/", StaticFiles(directory="static", html=True), name="static")
