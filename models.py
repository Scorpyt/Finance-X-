from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
import datetime

class SystemState(Enum):
    STABLE = "STABLE"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    BULL_RUN = "BULL_RUN"
    BEAR_MARKET = "BEAR_MARKET"
    CRASH = "CRASH"

class MarketRegime(Enum):
    LOW_VOL = "LOW_VOL"
    HIGH_VOL = "HIGH_VOL"
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"

@dataclass
class MarketEvent:
    timestamp: datetime.datetime
    event_type: str
    description: str
    base_impact: float  # 0.0 to 10.0
    asset_class: str    # e.g., "CRYPTO", "STOCKS", "FOREX"
    
@dataclass
class ProcessedEvent:
    original_event: MarketEvent
    current_weight: float
    relevance_score: float

@dataclass
class PricePoint:
    timestamp: datetime.datetime
    price: float
    volume: int

@dataclass
class Ticker:
    symbol: str
    name: str
    current_price: float
    change_pct: float
    history: List[PricePoint] = field(default_factory=list)
    sector: str = "GENERAL"

@dataclass
class GeoPoint:
    lat: float
    lon: float

@dataclass
class Tanker:
    id: str
    name: str
    location: GeoPoint
    destination: str
    status: str # "MOVING", "ANCHORED", "LOADING"
    cargo_level: float # 0-100%
    heading: float = 0.0

@dataclass
class MarketSnapshot:
    timestamp: datetime.datetime
    state: SystemState
    risk_score: float
    active_events: List[ProcessedEvent]
    regime: MarketRegime = MarketRegime.LOW_VOL
