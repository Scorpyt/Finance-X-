"""
Portfolio Models
Models for positions, portfolios, and portfolio analytics
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime

from .validators import validate_price, validate_quantity, validate_percentage


@dataclass
class Position:
    """Individual position in a portfolio"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_date: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def __post_init__(self):
        """Validate position data"""
        validate_quantity(self.quantity, "quantity")
        validate_price(self.entry_price, "entry_price")
        validate_price(self.current_price, "current_price")
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_pct(self) -> float:
        """Calculate P&L percentage"""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def current_value(self) -> float:
        """Calculate current position value"""
        return self.current_price * self.quantity
    
    @property
    def cost_basis(self) -> float:
        """Calculate original cost basis"""
        return self.entry_price * self.quantity
    
    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable"""
        return self.unrealized_pnl > 0
    
    @property
    def is_long(self) -> bool:
        """Check if position is long (quantity > 0)"""
        return self.quantity > 0
    
    @property
    def is_short(self) -> bool:
        """Check if position is short (quantity < 0)"""
        return self.quantity < 0
    
    @property
    def holding_period_days(self) -> int:
        """Calculate holding period in days"""
        return (datetime.datetime.now() - self.entry_date).days


@dataclass
class Portfolio:
    """Portfolio containing multiple positions"""
    user_id: str
    positions: List[Position] = field(default_factory=list)
    cash_balance: float = 0.0
    risk_score: float = 0.0
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def __post_init__(self):
        """Validate portfolio data"""
        if self.cash_balance < 0:
            raise ValueError(f"cash_balance cannot be negative, got {self.cash_balance}")
    
    @property
    def total_value(self) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(p.current_value for p in self.positions)
        return positions_value + self.cash_balance
    
    @property
    def total_pnl(self) -> float:
        """Calculate total unrealized P&L"""
        return sum(p.unrealized_pnl for p in self.positions)
    
    @property
    def total_pnl_pct(self) -> float:
        """Calculate total P&L percentage"""
        total_cost = sum(p.cost_basis for p in self.positions)
        if total_cost == 0:
            return 0.0
        return (self.total_pnl / total_cost) * 100
    
    @property
    def position_count(self) -> int:
        """Count of positions"""
        return len(self.positions)
    
    @property
    def profitable_positions(self) -> List[Position]:
        """Get list of profitable positions"""
        return [p for p in self.positions if p.is_profitable]
    
    @property
    def losing_positions(self) -> List[Position]:
        """Get list of losing positions"""
        return [p for p in self.positions if not p.is_profitable]
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate (% of profitable positions)"""
        if not self.positions:
            return 0.0
        return len(self.profitable_positions) / len(self.positions)
    
    @property
    def largest_position(self) -> Optional[Position]:
        """Get largest position by value"""
        if not self.positions:
            return None
        return max(self.positions, key=lambda p: abs(p.current_value))
    
    @property
    def best_performer(self) -> Optional[Position]:
        """Get best performing position by P&L %"""
        if not self.positions:
            return None
        return max(self.positions, key=lambda p: p.pnl_pct)
    
    @property
    def worst_performer(self) -> Optional[Position]:
        """Get worst performing position by P&L %"""
        if not self.positions:
            return None
        return min(self.positions, key=lambda p: p.pnl_pct)
    
    @property
    def concentration_risk(self) -> float:
        """Calculate concentration risk (largest position as % of total)"""
        if not self.positions or self.total_value == 0:
            return 0.0
        
        largest = self.largest_position
        if largest is None:
            return 0.0
        
        return (abs(largest.current_value) / self.total_value) * 100
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position by symbol"""
        for position in self.positions:
            if position.symbol == symbol:
                return position
        return None
    
    def add_position(self, position: Position) -> None:
        """Add a new position"""
        # Check if position already exists
        existing = self.get_position(position.symbol)
        if existing:
            # Merge positions (average entry price)
            total_qty = existing.quantity + position.quantity
            if total_qty != 0:
                avg_entry = (
                    (existing.entry_price * existing.quantity + 
                     position.entry_price * position.quantity) / total_qty
                )
                existing.quantity = total_qty
                existing.entry_price = avg_entry
                existing.current_price = position.current_price
        else:
            self.positions.append(position)
        
        self.last_updated = datetime.datetime.now()
    
    def remove_position(self, symbol: str) -> bool:
        """Remove a position by symbol"""
        position = self.get_position(symbol)
        if position:
            self.positions.remove(position)
            self.last_updated = datetime.datetime.now()
            return True
        return False
    
    def get_allocation(self) -> Dict[str, float]:
        """Get portfolio allocation by symbol (as percentages)"""
        if self.total_value == 0:
            return {}
        
        allocation = {}
        for position in self.positions:
            pct = (abs(position.current_value) / self.total_value) * 100
            allocation[position.symbol] = pct
        
        return allocation
