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

class StudyCategory(Enum):
    INVESTMENT_BANKING = "investment_banking"
    PRIVATE_EQUITY = "private_equity"
    HEDGE_FUNDS = "hedge_funds"
    ASSET_MANAGEMENT = "asset_management"
    FINANCIAL_ANALYSIS = "financial_analysis"

class QuestionDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class InterviewQuestion:
    id: str
    category: StudyCategory
    difficulty: QuestionDifficulty
    question: str
    answer: str
    explanation: str
    uses_market_data: bool = False
    related_topics: List[str] = field(default_factory=list)

@dataclass
class StudyTopic:
    id: str
    name: str
    category: StudyCategory
    description: str
    questions_count: int
    resources: List[str] = field(default_factory=list)

@dataclass
class StudyProgress:
    topic_id: str
    questions_answered: int
    correct_answers: int
    last_accessed: datetime.datetime = None

@dataclass
class MarketScenario:
    id: str
    title: str
    description: str
    challenge: str
    market_context: Dict = field(default_factory=dict)
    hints: List[str] = field(default_factory=list)
    solution_approach: str = ""

@dataclass
class MarketSnapshot:
    timestamp: datetime.datetime
    state: SystemState
    risk_score: float
    active_events: List[ProcessedEvent]
    regime: MarketRegime = MarketRegime.LOW_VOL
