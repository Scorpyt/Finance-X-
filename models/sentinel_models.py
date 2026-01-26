"""
Sentinel X Cognitive Models
Models for belief states, cognitive snapshots, and regime transitions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime
import math

from .enums import BeliefState
from .validators import validate_probability, validate_probability_distribution


@dataclass
class BeliefDistribution:
    """Probability distribution over belief states"""
    stable: float
    transitional: float
    stressed: float
    crisis: float
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    uncertainty_entropy: float = 0.0
    regime_persistence: int = 0  # days in current regime
    
    def __post_init__(self):
        """Validate and compute entropy"""
        # Validate individual probabilities
        validate_probability(self.stable, "stable")
        validate_probability(self.transitional, "transitional")
        validate_probability(self.stressed, "stressed")
        validate_probability(self.crisis, "crisis")
        
        # Validate distribution sums to 1.0
        dist = {
            'stable': self.stable,
            'transitional': self.transitional,
            'stressed': self.stressed,
            'crisis': self.crisis
        }
        validate_probability_distribution(dist)
        
        # Compute entropy if not provided
        if self.uncertainty_entropy == 0.0:
            self.uncertainty_entropy = self.compute_entropy()
    
    def compute_entropy(self) -> float:
        """Calculate Shannon entropy of belief distribution"""
        probs = [self.stable, self.transitional, self.stressed, self.crisis]
        entropy = 0.0
        
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    @property
    def dominant_regime(self) -> BeliefState:
        """Get the belief state with highest probability"""
        beliefs = {
            BeliefState.STABLE: self.stable,
            BeliefState.TRANSITIONAL: self.transitional,
            BeliefState.STRESSED: self.stressed,
            BeliefState.CRISIS: self.crisis
        }
        return max(beliefs.items(), key=lambda x: x[1])[0]
    
    @property
    def dominant_confidence(self) -> float:
        """Get confidence in dominant regime"""
        return max(self.stable, self.transitional, self.stressed, self.crisis)
    
    @property
    def is_certain(self) -> bool:
        """Check if belief is certain (entropy < 0.5)"""
        return self.uncertainty_entropy < 0.5
    
    @property
    def is_uncertain(self) -> bool:
        """Check if belief is highly uncertain (entropy > 1.5)"""
        return self.uncertainty_entropy > 1.5
    
    @property
    def belief_vector(self) -> List[float]:
        """Get belief as a vector [stable, transitional, stressed, crisis]"""
        return [self.stable, self.transitional, self.stressed, self.crisis]
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'stable': self.stable,
            'transitional': self.transitional,
            'stressed': self.stressed,
            'crisis': self.crisis
        }


@dataclass
class RegimeTransition:
    """Record of a regime transition"""
    from_regime: BeliefState
    to_regime: BeliefState
    timestamp: datetime.datetime
    trigger_features: List[str]
    confidence: float
    belief_before: Optional[BeliefDistribution] = None
    belief_after: Optional[BeliefDistribution] = None
    
    def __post_init__(self):
        """Validate transition data"""
        validate_probability(self.confidence, "confidence")
    
    @property
    def transition_type(self) -> str:
        """Classify transition type"""
        severity_order = [
            BeliefState.STABLE,
            BeliefState.TRANSITIONAL,
            BeliefState.STRESSED,
            BeliefState.CRISIS
        ]
        
        from_idx = severity_order.index(self.from_regime)
        to_idx = severity_order.index(self.to_regime)
        
        if to_idx > from_idx:
            return "ESCALATION"
        elif to_idx < from_idx:
            return "DE-ESCALATION"
        else:
            return "STABLE"
    
    @property
    def severity_change(self) -> int:
        """Calculate change in severity (-3 to +3)"""
        severity_order = [
            BeliefState.STABLE,
            BeliefState.TRANSITIONAL,
            BeliefState.STRESSED,
            BeliefState.CRISIS
        ]
        
        from_idx = severity_order.index(self.from_regime)
        to_idx = severity_order.index(self.to_regime)
        
        return to_idx - from_idx
    
    @property
    def is_critical_transition(self) -> bool:
        """Check if transition is critical (to/from crisis)"""
        return (self.from_regime == BeliefState.CRISIS or 
                self.to_regime == BeliefState.CRISIS)


@dataclass
class CognitiveSnapshot:
    """Complete snapshot of Sentinel X cognitive state"""
    timestamp: datetime.datetime
    perception_features: Dict[str, float]
    belief_state: BeliefDistribution
    reasoning_narrative: str
    crisis_similarity: Dict[str, float] = field(default_factory=dict)
    model_outputs: Dict[str, float] = field(default_factory=dict)
    
    @property
    def feature_count(self) -> int:
        """Count of perception features"""
        return len(self.perception_features)
    
    @property
    def current_regime(self) -> BeliefState:
        """Get current dominant regime"""
        return self.belief_state.dominant_regime
    
    @property
    def regime_confidence(self) -> float:
        """Get confidence in current regime"""
        return self.belief_state.dominant_confidence
    
    @property
    def most_similar_crisis(self) -> Optional[str]:
        """Get most similar historical crisis"""
        if not self.crisis_similarity:
            return None
        
        return max(self.crisis_similarity.items(), key=lambda x: x[1])[0]
    
    @property
    def max_crisis_similarity(self) -> float:
        """Get highest crisis similarity score"""
        if not self.crisis_similarity:
            return 0.0
        
        return max(self.crisis_similarity.values())
    
    @property
    def is_crisis_like(self) -> bool:
        """Check if current state is similar to a crisis (>50% similarity)"""
        return self.max_crisis_similarity > 0.50
    
    def get_top_features(self, n: int = 5) -> List[tuple]:
        """Get top N perception features by absolute value"""
        sorted_features = sorted(
            self.perception_features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        return sorted_features[:n]
