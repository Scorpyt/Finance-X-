import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models import MarketEvent, ProcessedEvent, SystemState, MarketSnapshot, Ticker, PricePoint, MarketRegime, Tanker, GeoPoint

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

class TankerSimulator:
    def __init__(self):
        self.tankers: List[Tanker] = []
        self.nodes = {
            "HOUSTON": GeoPoint(29.76, -95.36),
            "ROTTERDAM": GeoPoint(51.92, 4.47),
            "SINGAPORE": GeoPoint(1.35, 103.81),
            "FUJAIRAH": GeoPoint(25.12, 56.32),
            "QINGDAO": GeoPoint(36.06, 120.38),
            "SANTOS": GeoPoint(-23.96, -46.33),
            "RAS_TANURA": GeoPoint(26.64, 50.16)
        }
        self._init_fleet()

    def _init_fleet(self):
        # 30 Ships
        prefixes = ["NORDIC", "PACIFIC", "ATLANTIC", "GULF", "ARCTIC", "AEGEAN"]
        suffixes = ["PRIDE", "STAR", "VOYAGER", "TITAN", "STREAM", "SPIRIT", "LEADER", "DREAM"]
        
        for i in range(30):
            name = f"{random.choice(prefixes)} {random.choice(suffixes)} {i+1}"
            start_node = random.choice(list(self.nodes.keys()))
            target_node = random.choice([k for k in self.nodes.keys() if k != start_node])
            start_loc = self.nodes[start_node]
            
            # Scatter starts a bit so they aren't all ON the node
            lat_jitter = random.uniform(-5, 5)
            lon_jitter = random.uniform(-10, 10)
            
            self.tankers.append(Tanker(
                id=f"T-{1000+i}",
                name=name,
                location=GeoPoint(start_loc.lat + lat_jitter, start_loc.lon + lon_jitter),
                destination=target_node,
                status="MOVING",
                cargo_level=random.uniform(50, 100),
                heading=random.uniform(0, 360)
            ))

    def update_positions(self, state: SystemState):
        speed_factor = 1.0
        if state == SystemState.CRASH:
            speed_factor = 0.3 # Major disruptions

        # FAST PATH: Vectorized Update
        if len(self.tankers) > 0:
            # Extract arrays
            lats = np.array([t.location.lat for t in self.tankers])
            lons = np.array([t.location.lon for t in self.tankers])
            dest_nodes = [self.nodes[t.destination] for t in self.tankers]
            dest_lats = np.array([n.lat for n in dest_nodes])
            dest_lons = np.array([n.lon for n in dest_nodes])
            statuses = np.array([1 if t.status == "MOVING" else 0 for t in self.tankers])
            
            # Batch Update
            new_lats, new_lons, new_headings, arrived_mask = PerformanceEngine.batch_update_tankers(
                lats, lons, dest_lats, dest_lons, statuses, speed_factor
            )
            
            # Write back
            for i, t in enumerate(self.tankers):
                if t.status == "MOVING":
                    if arrived_mask[i]:
                        # Arrival Logic
                        if random.random() > 0.8:
                            t.status = "ANCHORED"
                        else:
                            t.destination = random.choice([k for k in self.nodes.keys() if k != t.destination])
                    else:
                        t.location.lat = new_lats[i]
                        t.location.lon = new_lons[i]
                        t.heading = float(new_headings[i])

    def get_supply_metrics(self) -> Dict:
        total = len(self.tankers)
        moving = len([t for t in self.tankers if t.status == "MOVING"])
        volume_at_sea = sum([t.cargo_level for t in self.tankers if t.status == "MOVING"])
        return {
            "total_ships": total,
            "moving_ratio": moving / total,
            "volume_index": volume_at_sea
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
        self.tanker_sim = TankerSimulator()
        
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
        self.tanker_sim.update_positions(self.current_state)

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
