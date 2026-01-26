"""
Sentinel X - Configuration Module
Institution-grade financial intelligence engine configuration
"""

import os
from pathlib import Path
from typing import Dict, List
import json

class SentinelConfig:
    """
    Central configuration for Sentinel X autonomous intelligence engine.
    
    This system is NOT a trading model.
    This system is NOT a forecasting engine.
    This IS a continuous market cognition system.
    """
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    CLEANED_DATA_DIR = DATA_DIR / "cleaned"
    FEATURES_DIR = DATA_DIR / "features"
    LABELS_DIR = DATA_DIR / "labels"
    SPLITS_DIR = DATA_DIR / "splits"
    
    MODELS_DIR = PROJECT_ROOT / "models"
    MEMORY_DIR = PROJECT_ROOT / "memory" / "snapshots"
    
    # Ensure directories exist
    for dir_path in [DATA_DIR, RAW_DATA_DIR, CLEANED_DATA_DIR, FEATURES_DIR, 
                     LABELS_DIR, SPLITS_DIR, MODELS_DIR, MEMORY_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Cognitive system parameters
    BELIEF_STATES = ["Stable", "Transitional", "Stressed", "Crisis"]
    INITIAL_BELIEF = {
        "Stable": 0.70,
        "Transitional": 0.20,
        "Stressed": 0.08,
        "Crisis": 0.02
    }
    
    # Inference loop timing
    INFERENCE_INTERVAL_SECONDS = 60  # 1 minute heartbeat
    MEMORY_DECAY_HALFLIFE_HOURS = 24  # 24 hour decay
    
    # Model ensemble configuration
    MODEL_CATEGORIES = {
        "statistical": ["zscore", "ewma", "changepoint"],
        "unsupervised": ["isolation_forest", "one_class_svm", "hdbscan"],
        "regime": ["hmm", "regime_classifier"],
        "similarity": ["crisis_vectors", "cosine_similarity", "dtw_similarity"]
    }
    
    MINIMUM_MODEL_AGREEMENT = 0.60  # 60% consensus required
    
    # Feature groups
    FEATURE_GROUPS = {
        "price_behavior": [
            "log_return", "rolling_return_5d", "rolling_return_20d",
            "drawdown_pct", "price_distance_from_high"
        ],
        "volatility_structure": [
            "vol_30", "vol_90", "vol_180",
            "vol_ratio_30_180", "vol_acceleration"
        ],
        "correlation_contagion": [
            "avg_correlation", "correlation_change", "correlation_dispersion"
        ],
        "energy_macro": [
            "energy_shock_index", "oil_volatility",
            "inflation_delta", "rate_change_velocity"
        ],
        "event_pressure": [
            "event_count", "weighted_event_score", "decay_adjusted_event_score"
        ],
        "regime_memory": [
            "regime_persistence", "days_in_current_regime", "transition_frequency"
        ]
    }
    
    # Data sources
    DATA_SOURCES = {
        "primary": "yfinance",  # Free, global coverage
        "secondary": "alpha_vantage",  # API-based
        "news": "newsapi",  # News intelligence
    }
    
    # Stock universe (can be expanded)
    STOCK_UNIVERSE = {
        "US_MAJOR": ["SPY", "QQQ", "DIA", "IWM"],  # US indices
        "US_SECTORS": ["XLF", "XLE", "XLK", "XLV", "XLI"],  # Sector ETFs
        "GLOBAL": ["EFA", "EEM", "VWO"],  # International
        "VOLATILITY": ["VIX", "^VIX"],  # Volatility indices
        "COMMODITIES": ["GLD", "USO", "UNG"],  # Commodities
    }
    
    # Performance optimization
    CPU_THREADS = os.cpu_count() or 4
    GPU_ENABLED = True  # Will auto-detect
    BATCH_SIZE = 1000
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Safety constraints
    SAFETY_RULES = {
        "no_trade_recommendations": True,
        "no_price_targets": True,
        "no_certainty_claims": True,
        "always_quantify_uncertainty": True,
        "explainability_required": True
    }
    
    @classmethod
    def get_all_symbols(cls) -> List[str]:
        """Get complete list of symbols to monitor"""
        all_symbols = []
        for category in cls.STOCK_UNIVERSE.values():
            all_symbols.extend(category)
        return list(set(all_symbols))  # Remove duplicates
    
    @classmethod
    def get_all_features(cls) -> List[str]:
        """Get complete list of feature names"""
        all_features = []
        for features in cls.FEATURE_GROUPS.values():
            all_features.extend(features)
        return all_features
    
    @classmethod
    def save_config(cls, filepath: str):
        """Save configuration to JSON"""
        config_dict = {
            "belief_states": cls.BELIEF_STATES,
            "initial_belief": cls.INITIAL_BELIEF,
            "inference_interval": cls.INFERENCE_INTERVAL_SECONDS,
            "model_categories": cls.MODEL_CATEGORIES,
            "feature_groups": cls.FEATURE_GROUPS,
            "stock_universe": cls.STOCK_UNIVERSE,
            "safety_rules": cls.SAFETY_RULES
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def validate_safety(cls):
        """Validate that safety constraints are enabled"""
        for rule, enabled in cls.SAFETY_RULES.items():
            if not enabled:
                raise ValueError(f"Safety rule '{rule}' must be enabled!")
        
        print("✅ All safety constraints validated")
        return True


# Auto-validate safety on import
SentinelConfig.validate_safety()

if __name__ == "__main__":
    print("Sentinel X Configuration")
    print("=" * 60)
    print(f"Project Root: {SentinelConfig.PROJECT_ROOT}")
    print(f"Belief States: {SentinelConfig.BELIEF_STATES}")
    print(f"Total Features: {len(SentinelConfig.get_all_features())}")
    print(f"Total Symbols: {len(SentinelConfig.get_all_symbols())}")
    print(f"CPU Threads: {SentinelConfig.CPU_THREADS}")
    print(f"GPU Enabled: {SentinelConfig.GPU_ENABLED}")
    print("=" * 60)
    
    # Save configuration
    config_path = SentinelConfig.PROJECT_ROOT / "config.json"
    SentinelConfig.save_config(str(config_path))
    print(f"✅ Configuration saved to {config_path}")
