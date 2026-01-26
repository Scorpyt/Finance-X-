"""
Market Data Models
Core models for market events, tickers, and snapshots
"""

from dataclasses import dataclass, field
from typing import List, Optional
import datetime

from .enums import SystemState, MarketRegime, AssetClass
from .validators import validate_price


@dataclass
class MarketEvent:
    """Represents a significant market event"""
    timestamp: datetime.datetime
    event_type: str
    description: str
    base_impact: float  # 0.0 to 10.0
    asset_class: AssetClass
    affected_symbols: List[str] = field(default_factory=list)
    source: str = "SYSTEM"
    
    def __post_init__(self):
        """Validate event data"""
        if not 0.0 <= self.base_impact <= 10.0:
            raise ValueError(f"base_impact must be 0.0-10.0, got {self.base_impact}")


@dataclass
class ProcessedEvent:
    """Event after time-decay processing"""
    original_event: MarketEvent
    current_weight: float
    relevance_score: float
    age_hours: float = 0.0
    
    @property
    def is_active(self) -> bool:
        """Check if event is still relevant (weight > 0.1)"""
        return self.current_weight > 0.1
    
    @property
    def decay_rate(self) -> float:
        """Calculate decay rate based on age"""
        if self.age_hours == 0:
            return 0.0
        return (self.original_event.base_impact - self.current_weight) / self.age_hours


@dataclass
class PricePoint:
    """Single price data point"""
    timestamp: datetime.datetime
    price: float
    volume: int = 0
    
    def __post_init__(self):
        """Validate price data"""
        validate_price(self.price, "price")
        if self.volume < 0:
            raise ValueError(f"volume cannot be negative, got {self.volume}")


@dataclass
class Ticker:
    """Stock/asset ticker information"""
    symbol: str
    name: str
    current_price: float
    change_pct: float
    history: List[PricePoint] = field(default_factory=list)
    sector: str = "GENERAL"
    asset_class: AssetClass = AssetClass.STOCKS
    
    def __post_init__(self):
        """Validate ticker data"""
        validate_price(self.current_price, "current_price")
    
    @property
    def previous_close(self) -> Optional[float]:
        """Get previous closing price"""
        if not self.history:
            return None
        return self.history[-1].price if self.history else None
    
    @property
    def change_amount(self) -> float:
        """Calculate absolute price change"""
        if self.previous_close is None:
            return 0.0
        return self.current_price - self.previous_close
    
    @property
    def is_gaining(self) -> bool:
        """Check if price is increasing"""
        return self.change_pct > 0
    
    @property
    def volatility(self) -> float:
        """Calculate simple volatility from history"""
        if len(self.history) < 2:
            return 0.0
        
        prices = [p.price for p in self.history]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        if not returns:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return variance ** 0.5


@dataclass
class MarketSnapshot:
    """Complete market state at a point in time"""
    timestamp: datetime.datetime
    state: SystemState
    risk_score: float
    active_events: List[ProcessedEvent]
    regime: MarketRegime = MarketRegime.LOW_VOL
    tickers: List[Ticker] = field(default_factory=list)
    
    @property
    def event_count(self) -> int:
        """Count of active events"""
        return len([e for e in self.active_events if e.is_active])
    
    @property
    def total_event_weight(self) -> float:
        """Sum of all event weights"""
        return sum(e.current_weight for e in self.active_events)
    
    @property
    def is_stable(self) -> bool:
        """Check if market is in stable state"""
        return self.state == SystemState.STABLE
    
    @property
    def is_crisis(self) -> bool:
        """Check if market is in crisis"""
        return self.state == SystemState.CRASH
