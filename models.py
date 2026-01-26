"""
DEPRECATED: This file is kept for backward compatibility only.
Please use: from models import SystemState, MarketEvent, etc.

The models have been restructured into a modular package:
- models.enums: All enum definitions
- models.market: Market-related models
- models.ml_models: ML prediction models
- models.sentinel_models: Sentinel X cognitive models
- models.portfolio: Portfolio and position models
- models.validators: Validation utilities
"""

import warnings

# Show deprecation warning
warnings.warn(
    "Importing from models.py is deprecated. "
    "Use 'from models import ...' instead. "
    "This compatibility shim will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new models package for backward compatibility
from models.enums import SystemState, MarketRegime, AssetClass
from models.market import MarketEvent, ProcessedEvent, PricePoint, Ticker, MarketSnapshot
from models.ml_models import MLPrediction, FeatureVector, ModelMetrics
from models.sentinel_models import BeliefDistribution, CognitiveSnapshot, RegimeTransition
from models.portfolio import Position, Portfolio

__all__ = [
    'SystemState',
    'MarketRegime',
    'AssetClass',
    'MarketEvent',
    'ProcessedEvent',
    'PricePoint',
    'Ticker',
    'MarketSnapshot',
    'MLPrediction',
    'FeatureVector',
    'ModelMetrics',
    'BeliefDistribution',
    'CognitiveSnapshot',
    'RegimeTransition',
    'Position',
    'Portfolio',
]
