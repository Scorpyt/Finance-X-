"""
Finance-X Machine Learning Module

This package contains the complete ML infrastructure for market prediction.

Modules:
    - feature_engineering: Extract 50+ technical indicators from market data
    - ml_models: Ensemble (RF, XGB, LGBM) and LSTM model definitions
    - ml_trainer: Training pipeline with cross-validation
    - ml_predictor: Real-time prediction engine
    - ml_engine: Main orchestration layer

Quick Start:
    >>> from ML.ml_engine import MLEngine
    >>> engine = MLEngine()
    >>> prediction = engine.predict('SPY')
    >>> print(f"Direction: {prediction['final_prediction']}")
    >>> print(f"Confidence: {prediction['final_confidence']:.2%}")

For detailed documentation, see README.md in this directory.
"""

__version__ = "1.0.0"
__author__ = "Finance-X Team"

# Import main classes for easy access
from .feature_engineering import FeatureEngineer
from .ml_models import EnsembleModel, LSTMModel
from .ml_trainer import MLTrainer
from .ml_predictor import MLPredictor
from .ml_engine import MLEngine

__all__ = [
    'FeatureEngineer',
    'EnsembleModel',
    'LSTMModel',
    'MLTrainer',
    'MLPredictor',
    'MLEngine',
]
