"""
Machine Learning Models
Models for predictions, features, and ML metrics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime
import uuid

from .enums import PredictionDirection, PredictionHorizon, ConfidenceLevel, RiskLevel
from .validators import validate_probability, validate_probability_distribution


@dataclass
class FeatureVector:
    """Feature vector for ML model input"""
    symbol: str
    timestamp: datetime.datetime
    features: Dict[str, float]
    feature_groups: Dict[str, List[str]] = field(default_factory=dict)
    
    @property
    def feature_count(self) -> int:
        """Total number of features"""
        return len(self.features)
    
    @property
    def group_count(self) -> int:
        """Number of feature groups"""
        return len(self.feature_groups)
    
    def get_group_features(self, group_name: str) -> Dict[str, float]:
        """Get all features for a specific group"""
        if group_name not in self.feature_groups:
            return {}
        
        feature_names = self.feature_groups[group_name]
        return {name: self.features[name] for name in feature_names if name in self.features}


@dataclass
class ModelMetrics:
    """ML model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def __post_init__(self):
        """Validate metrics"""
        validate_probability(self.accuracy, "accuracy")
        validate_probability(self.precision, "precision")
        validate_probability(self.recall, "recall")
        validate_probability(self.f1_score, "f1_score")
        validate_probability(self.roc_auc, "roc_auc")
    
    @property
    def is_good_performance(self) -> bool:
        """Check if model has good performance (>70% accuracy)"""
        return self.accuracy > 0.70
    
    @property
    def performance_summary(self) -> str:
        """Generate performance summary"""
        return (
            f"Accuracy: {self.accuracy:.2%}, "
            f"Precision: {self.precision:.2%}, "
            f"Recall: {self.recall:.2%}, "
            f"F1: {self.f1_score:.2%}, "
            f"ROC-AUC: {self.roc_auc:.2%}"
        )


@dataclass
class MLPrediction:
    """Machine learning prediction result"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    direction: PredictionDirection = PredictionDirection.NEUTRAL
    confidence: float = 0.5
    probability_distribution: Dict[str, float] = field(default_factory=dict)
    horizon: PredictionHorizon = PredictionHorizon.SHORT_TERM
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    model_version: str = "1.0.0"
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate prediction data"""
        validate_probability(self.confidence, "confidence")
        
        if self.probability_distribution:
            validate_probability_distribution(self.probability_distribution)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get confidence level enum"""
        return ConfidenceLevel.from_probability(self.confidence)
    
    @property
    def risk_level(self) -> RiskLevel:
        """Estimate risk level based on confidence"""
        # Lower confidence = higher risk
        risk_score = (1.0 - self.confidence) * 100
        return RiskLevel.from_score(risk_score)
    
    @property
    def top_features(self) -> List[tuple]:
        """Get top 5 most important features"""
        if not self.feature_importance:
            return []
        
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_features[:5]
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if prediction has high confidence (>80%)"""
        return self.confidence > 0.80
    
    @property
    def prediction_summary(self) -> str:
        """Generate human-readable prediction summary"""
        return (
            f"{self.symbol} prediction: {self.direction.value} "
            f"({self.confidence:.0%} confidence, "
            f"{self.confidence_level.value} level, "
            f"{self.horizon.value} horizon)"
        )


@dataclass
class EnsemblePrediction:
    """Ensemble of multiple model predictions"""
    symbol: str
    predictions: List[MLPrediction]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    @property
    def consensus_direction(self) -> PredictionDirection:
        """Get consensus prediction direction"""
        if not self.predictions:
            return PredictionDirection.NEUTRAL
        
        direction_counts = {}
        for pred in self.predictions:
            direction = pred.direction
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        return max(direction_counts.items(), key=lambda x: x[1])[0]
    
    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all predictions"""
        if not self.predictions:
            return 0.0
        
        return sum(p.confidence for p in self.predictions) / len(self.predictions)
    
    @property
    def model_agreement(self) -> float:
        """Calculate percentage of models agreeing with consensus"""
        if not self.predictions:
            return 0.0
        
        consensus = self.consensus_direction
        agreeing = sum(1 for p in self.predictions if p.direction == consensus)
        return agreeing / len(self.predictions)
    
    @property
    def is_strong_consensus(self) -> bool:
        """Check if >75% of models agree"""
        return self.model_agreement > 0.75
