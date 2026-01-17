import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models import MarketEvent, ProcessedEvent, SystemState, MarketSnapshot, Ticker, PricePoint, MarketRegime

import numpy as np
from performance_engine import PerformanceEngine, HardwareNavigator

class TechnicalAnalysis:
    @staticmethod
    def calculate_bollinger_bands(history: List[PricePoint], window: int = 20, num_std: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Returns (Upper Band, Middle Band, Lower Band)"""
        prices = [p.price for p in history]
        
        # Use High-Performance Vectorized Engine
        if len(prices) >= window:
            u, m, l = PerformanceEngine.calculate_bollinger_bands_vectorized(prices, window, num_std)
            return u.tolist(), m.tolist(), l.tolist()
            
        # Fallback for insufficient data
        upper, middle, lower = [], [], []
        for p in prices:
            upper.append(p)
            middle.append(p)
            lower.append(p)
        return upper, middle, lower

    @staticmethod
    def analyze_risk_depth(ticker: Ticker) -> Dict:
        """Analyzes price position relative to bands to determine Risk Depth."""
        if len(ticker.history) < 20:
             return {"depth": "LOW", "advice": "INSUFFICIENT DATA", "bid": 0.0}

        u, m, l = TechnicalAnalysis.calculate_bollinger_bands(ticker.history)
        current_price = ticker.current_price
        upper_curr = u[-1]
        lower_curr = l[-1]
        
        # Depth Logic
        if current_price > upper_curr:
             depth = "CRITICAL (OVERBOUGHT)"
             advice = "SELL / HEDGE"
             best_bid = lower_curr # Target return to mean or lower
        elif current_price < lower_curr:
             depth = "OPPORTUNITY (OVERSOLD)"
             advice = "ACCUMULATE"
             best_bid = current_price * 0.98 # Aggressive Bid
        else:
             depth = "NEUTRAL"
             advice = "HOLD"
             best_bid = lower_curr 
             
        return {
            "depth": depth,
            "advice": advice,
            "bid": best_bid,
            "volatility": (upper_curr - lower_curr) / m[-1]
        }

class MarketSimulator:
    def __init__(self):
        self.tickers: Dict[str, Ticker] = {
            "SPX": Ticker("SPX", "S&P 500", 4800.0, 0.0),
            "NDX": Ticker("NDX", "Nasdaq 100", 16800.0, 0.0),
            "BTC": Ticker("BTC", "Bitcoin", 42000.0, 0.0),
            "VIX": Ticker("VIX", "Volatility", 14.0, 0.0),
            "AAPL": Ticker("AAPL", "Apple Inc.", 185.0, 0.0, sector="TECH"),
            "NVDA": Ticker("NVDA", "NVIDIA", 550.0, 0.0, sector="TECH"),
            "JPM": Ticker("JPM", "JPMorgan", 170.0, 0.0, sector="FINANCE"),
            "XOM": Ticker("XOM", "Exxon Mobil", 100.0, 0.0, sector="ENERGY"),
            "WTI": Ticker("WTI", "Crude Oil (WTI)", 72.50, 0.0, sector="ENERGY"),
            "BRENT": Ticker("BRENT", "Crude Oil (Brent)", 77.80, 0.0, sector="ENERGY")
        }
        start_time = datetime(2024, 1, 1, 9, 0)
        for t in self.tickers.values():
            t.history.append(PricePoint(start_time, t.current_price, 0))

    def update_prices(self, current_time: datetime, system_risk: float):
        # Direct Acceleration Logic
        fidelity = HardwareNavigator.determine_fidelity_level()
        noise_factor = 1.0
        if fidelity == "ULTRA": noise_factor = 1.2 # More microstructure noise
        if fidelity == "EFFICIENT": noise_factor = 0.5 # Smoother, less compute
        
        # Gather current state
        tickers_list = list(self.tickers.values())
        current_prices = np.array([t.current_price for t in tickers_list])
        
        # Volatilities map
        vol_map = {
            "VIX": 0.05,
            "BTC": 0.01,
            "WTI": 0.008,
            "BRENT": 0.008
        }
        vols = np.array([vol_map.get(t.symbol, 0.002) for t in tickers_list])
        
        # Vectorized Update
        new_prices = PerformanceEngine.batch_update_prices(current_prices, vols, system_risk)
        
        # Update Objects
        for i, t in enumerate(tickers_list):
            old_p = t.current_price
            t.current_price = float(new_prices[i])
            
            # Simple volume sim
            multiplier = 4.0 if system_risk > 25.0 else 1.0
            volume = int(random.uniform(1000, 5000) * multiplier)
            
            t.history.append(PricePoint(current_time, t.current_price, volume))
            if len(t.history) > 100:
                t.history.pop(0)

            # Calculate change from start of history window
            if t.history:
              t.change_pct = ((t.current_price - t.history[0].price) / t.history[0].price) * 100

from database import DatabaseManager

class IntelligenceEngine:
    def __init__(self, decay_rate: float = 0.1):
        self.events: List[ProcessedEvent] = []
        self.decay_rate = decay_rate
        self.current_state = SystemState.STABLE
        self.current_regime = MarketRegime.LOW_VOL
        self.simulator = MarketSimulator()
        
        # Database Integration
        self.db = DatabaseManager()

    def ingest(self, event: MarketEvent):
        relevance = event.base_impact * 1.0 
        processed = ProcessedEvent(
            original_event=event,
            current_weight=relevance,
            relevance_score=relevance
        )
        self.events.append(processed)
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] Ingested: {event.description} (Impact: {event.base_impact})")
        
        # Log to DB
        self.db.log_event(event.timestamp, event.description, event.base_impact, event.event_type)

    def apply_decay(self, current_time: datetime):
        if not self.events:
            return

        # Vectorized Decay
        current_ts = current_time.timestamp()
        
        # Extract arrays
        weights = np.array([e.relevance_score for e in self.events])
        timestamps = np.array([e.original_event.timestamp.timestamp() for e in self.events])
        
        # Batch Calculate
        new_weights = PerformanceEngine.calculate_decay_batch(weights, timestamps, current_ts, self.decay_rate)
        
        # Update and Filter (Python loop needed for object update, but math is done)
        active_rec = []
        for i, event in enumerate(self.events):
            w = float(new_weights[i])
            event.current_weight = w
            if w > 0.5:
                active_rec.append(event)
        
        self.events = active_rec

    def detect_state(self, current_time: datetime) -> MarketSnapshot:
        total_risk = sum(e.current_weight for e in self.events)
        
        if total_risk > 25.0:
            self.current_state = SystemState.CRASH
            self.current_regime = MarketRegime.HIGH_VOL
        elif total_risk > 15.0:
            self.current_state = SystemState.HIGH_VOLATILITY
            self.current_regime = MarketRegime.HIGH_VOL
        elif total_risk < 5.0:
            self.current_state = SystemState.STABLE
            self.current_regime = MarketRegime.LOW_VOL
            
        self.simulator.update_prices(current_time, total_risk)

        top_events = sorted(self.events, key=lambda x: x.current_weight, reverse=True)[:5]
        
        # Log State Snapshot
        state_val = self.current_state.value if hasattr(self.current_state, 'value') else str(self.current_state)
        regime_val = self.current_regime.value if hasattr(self.current_regime, 'value') else str(self.current_regime)
        self.db.log_snapshot(current_time, state_val, total_risk, regime_val)
        
        # Log Prices
        price_batch = []
        for t in self.simulator.tickers.values():
             if t.history:
                 last_pt = t.history[-1]
                 price_batch.append({
                     "timestamp": current_time,
                     "symbol": t.symbol,
                     "price": last_pt.price,
                     "change": t.change_pct,
                     "volume": last_pt.volume
                 })
        self.db.log_price_batch(price_batch)
        
        return MarketSnapshot(
            timestamp=current_time,
            state=self.current_state,
            risk_score=round(total_risk, 2),
            active_events=top_events,
            regime=self.current_regime
        )
            
    def get_ticker(self, symbol: str) -> Ticker:
        return self.simulator.tickers.get(symbol)
    
    def get_all_tickers(self) -> List[Dict]:
        return [
            {
                "symbol": t.symbol,
                "price": t.current_price,
                "change": t.change_pct,
                "sector": t.sector,
                "history": [p.price for p in t.history[-30:]] # Last 30 points for sparkline
            }
            for t in self.simulator.tickers.values()
        ]
