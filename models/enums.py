"""
Enum Definitions for Finance-X
Comprehensive enumerations for states, risk levels, and classifications
"""

from enum import Enum


class SystemState(Enum):
    """Overall market system state"""
    STABLE = "STABLE"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    BULL_RUN = "BULL_RUN"
    BEAR_MARKET = "BEAR_MARKET"
    CRASH = "CRASH"


class MarketRegime(Enum):
    """Market volatility and trend regime"""
    LOW_VOL = "LOW_VOL"
    HIGH_VOL = "HIGH_VOL"
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"


class RiskLevel(Enum):
    """Granular risk level classification"""
    MINIMAL = "MINIMAL"          # 0-10
    LOW = "LOW"                  # 10-25
    MODERATE = "MODERATE"        # 25-40
    ELEVATED = "ELEVATED"        # 40-60
    HIGH = "HIGH"                # 60-75
    SEVERE = "SEVERE"            # 75-90
    CRITICAL = "CRITICAL"        # 90-100
    
    @classmethod
    def from_score(cls, score: float) -> 'RiskLevel':
        """Convert risk score (0-100) to RiskLevel"""
        if score < 10:
            return cls.MINIMAL
        elif score < 25:
            return cls.LOW
        elif score < 40:
            return cls.MODERATE
        elif score < 60:
            return cls.ELEVATED
        elif score < 75:
            return cls.HIGH
        elif score < 90:
            return cls.SEVERE
        else:
            return cls.CRITICAL


class ConfidenceLevel(Enum):
    """Confidence level for predictions and beliefs"""
    VERY_LOW = "VERY_LOW"        # 0-20%
    LOW = "LOW"                  # 20-40%
    MODERATE = "MODERATE"        # 40-60%
    HIGH = "HIGH"                # 60-80%
    VERY_HIGH = "VERY_HIGH"      # 80-100%
    
    @classmethod
    def from_probability(cls, prob: float) -> 'ConfidenceLevel':
        """Convert probability (0.0-1.0) to ConfidenceLevel"""
        pct = prob * 100
        if pct < 20:
            return cls.VERY_LOW
        elif pct < 40:
            return cls.LOW
        elif pct < 60:
            return cls.MODERATE
        elif pct < 80:
            return cls.HIGH
        else:
            return cls.VERY_HIGH


class PredictionDirection(Enum):
    """ML prediction direction"""
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


class PredictionHorizon(Enum):
    """Time horizon for predictions"""
    INTRADAY = "INTRADAY"          # Same day
    SHORT_TERM = "SHORT_TERM"      # 1-5 days
    MEDIUM_TERM = "MEDIUM_TERM"    # 1-4 weeks
    LONG_TERM = "LONG_TERM"        # 1+ months


class BeliefState(Enum):
    """Sentinel X belief states"""
    STABLE = "STABLE"
    TRANSITIONAL = "TRANSITIONAL"
    STRESSED = "STRESSED"
    CRISIS = "CRISIS"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AssetClass(Enum):
    """Asset class categorization"""
    STOCKS = "STOCKS"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    COMMODITIES = "COMMODITIES"
    BONDS = "BONDS"
    INDICES = "INDICES"
