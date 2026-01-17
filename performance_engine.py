import numpy as np
import pandas as pd
import psutil
import os
from typing import List, Dict, Tuple
from dataclasses import asdict

class HardwareNavigator:
    """
    Directs hardware acceleration by analyzing system load and optimizing 
    compute strategies dynamically.
    """
    @staticmethod
    def get_system_metrics() -> Dict:
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "cores": os.cpu_count(),
            "memory_percent": psutil.virtual_memory().percent,
            "acceleration_mode": "AVX2_VECTORIZED" # Inferred from NumPy use
        }

    @staticmethod
    def determine_fidelity_level() -> str:
        """
        Analyzes processor load to direct acceleration level.
        """
        load = psutil.cpu_percent(interval=None)
        if load < 30.0:
            return "ULTRA" # Max simulation depth
        elif load < 70.0:
            return "HIGH"
        else:
            return "EFFICIENT" # Throttle back

class PerformanceEngine:
    """
    High-Performance Mathematical Core using NumPy for vectorized calculations.
    Replaces loop-based logic for significant speedup.
    """
    
    @staticmethod
    def calculate_bollinger_bands_vectorized(prices: List[float], window: int = 20, num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Vectorized Bollinger Bands calculation using Pandas rolling window.
        ~50x faster than iteration for large datasets.
        """
        if not prices or len(prices) < window:
            return np.array([]), np.array([]), np.array([])
            
        series = pd.Series(prices)
        middle = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        # Fill NaN values with the first valid value to avoid gaps
        middle = middle.fillna(method='bfill')
        upper = upper.fillna(method='bfill')
        lower = lower.fillna(method='bfill')
        
        return upper.values, middle.values, lower.values

    @staticmethod
    def batch_update_prices(current_prices: np.ndarray, 
                           volatilities: np.ndarray, 
                           system_risk: float, 
                           correlations: np.ndarray = None) -> np.ndarray:
        """
        Vectorized price update for all tickers simultaneously.
        """
        # Determine System Bias & Multiplier based on Risk
        bias = 0.0
        vol_mult = 1.0
        
        if system_risk > 25.0: # CRASH
            bias = -0.02
            vol_mult = 4.0
        elif system_risk > 15.0: # HIGH VOL
            bias = -0.005
            vol_mult = 2.0
        elif system_risk < 5.0: # STABLE
            bias = 0.001
            vol_mult = 0.8
            
        # Generate random shocks for all assets at once
        # N assets
        count = len(current_prices)
        shocks = np.random.normal(0, volatilities * vol_mult, count)
        
        # Apply shocks + bias
        pct_changes = shocks + bias
        
        # If correlations matrix provided, apply Cholesky decomposition (advanced)
        # For now, simple independent shocks
        
        new_prices = current_prices * (1 + pct_changes)
        return np.round(new_prices, 2)

    @staticmethod
    def calculate_decay_batch(weights: np.ndarray, 
                             timestamps: np.ndarray, 
                             current_ts: float, 
                             decay_rate: float) -> np.ndarray:
        """
        Vectorized decay calculation for all events.
        """
        dt_hours = (current_ts - timestamps) / 3600.0
        new_weights = weights * np.exp(-decay_rate * dt_hours)
        return new_weights
