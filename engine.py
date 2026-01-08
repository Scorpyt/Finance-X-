import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models import MarketEvent, ProcessedEvent, SystemState, MarketSnapshot, Ticker, PricePoint, MarketRegime, Tanker, GeoPoint

class TechnicalAnalysis:
    @staticmethod
    def calculate_bollinger_bands(history: List[PricePoint], window: int = 20, num_std: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Returns (Upper Band, Middle Band, Lower Band)"""
        prices = [p.price for p in history]
        upper, middle, lower = [], [], []
        
        for i in range(len(prices)):
            if i < window - 1:
                # Not enough data
                upper.append(prices[i])
                middle.append(prices[i])
                lower.append(prices[i])
            else:
                slice_data = prices[i-window+1 : i+1]
                avg = sum(slice_data) / window
                variance = sum((x - avg) ** 2 for x in slice_data) / window
                std_dev = math.sqrt(variance)
                
                middle.append(avg)
                upper.append(avg + (std_dev * num_std))
                lower.append(avg - (std_dev * num_std))
        
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
        
        for t in self.tankers:
            if t.status == "MOVING":
                target = self.nodes[t.destination]
                dy = target.lat - t.location.lat
                dx = target.lon - t.location.lon
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 2.0:
                    # Reroute or anchor logic
                    if random.random() > 0.8:
                        t.status = "ANCHORED" 
                    else:
                         # New destination
                         t.destination = random.choice([k for k in self.nodes.keys() if k != t.destination])
                else:
                    speed = 0.8 * speed_factor # Faster simulation for "Real Time" feel
                    move_by_lat = (dy / dist) * speed
                    move_by_lon = (dx / dist) * speed
                    t.location.lat += move_by_lat
                    t.location.lon += move_by_lon
                    t.heading = math.degrees(math.atan2(dx, dy))

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
        bias = 0.0
        volatility_multiplier = 1.0

        if system_risk > 25.0: # CRASH
            bias = -0.02
            volatility_multiplier = 4.0
        elif system_risk > 15.0: # HIGH VOL
            bias = -0.005
            volatility_multiplier = 2.0
        elif system_risk < 5.0: # STABLE
            bias = 0.001
            volatility_multiplier = 0.8

        for sym, ticker in self.tickers.items():
            base_vol = 0.002 if sym != "VIX" else 0.05
            if sym == "BTC": base_vol = 0.01
            if sym in ["WTI", "BRENT"]: base_vol = 0.008

            shock = random.gauss(0, base_vol * volatility_multiplier)
            if sym == "VIX":
                change_pct = shock - (bias * 5)
            else:
                change_pct = shock + bias

            new_price = ticker.current_price * (1 + change_pct)
            ticker.current_price = round(new_price, 2)
            volume = int(random.uniform(1000, 5000) * volatility_multiplier)
            
            ticker.history.append(PricePoint(current_time, ticker.current_price, volume))
            if len(ticker.history) > 100:
                ticker.history.pop(0)

            ticker.change_pct = ((ticker.current_price - ticker.history[0].price) / ticker.history[0].price) * 100

class IntelligenceEngine:
    def __init__(self, decay_rate: float = 0.1):
        self.events: List[ProcessedEvent] = []
        self.decay_rate = decay_rate
        self.current_state = SystemState.STABLE
        self.current_regime = MarketRegime.LOW_VOL
        self.simulator = MarketSimulator()
        self.tanker_sim = TankerSimulator()

    def ingest(self, event: MarketEvent):
        relevance = event.base_impact * 1.0 
        processed = ProcessedEvent(
            original_event=event,
            current_weight=relevance,
            relevance_score=relevance
        )
        self.events.append(processed)
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] Ingested: {event.description} (Impact: {event.base_impact})")

    def apply_decay(self, current_time: datetime):
        active_events = []
        for p_event in self.events:
            time_delta = (current_time - p_event.original_event.timestamp).total_seconds() / 3600.0 # Hours
            new_weight = p_event.relevance_score * math.exp(-self.decay_rate * time_delta)
            p_event.current_weight = new_weight
            if new_weight > 0.5:
                active_events.append(p_event)
        self.events = active_events

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
                "sector": t.sector
            }
            for t in self.simulator.tickers.values()
        ]
