"""
Sentinel X - Perception Engine (Layer 1)
Continuously observes raw market reality without interpretation.

This layer ONLY senses. No beliefs. No reasoning. Pure observation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import SentinelConfig
from utils.logging import SentinelLogger

logger = SentinelLogger.get_logger("perception_engine")


class PerceptionEngine:
    """
    Layer 1: Perception Engine
    
    Purpose: Continuously observe raw market reality
    
    Inputs:
    - Price returns
    - Volatility metrics
    - Correlation matrices
    - Volume anomalies
    - Macro indicators
    
    Outputs:
    - Feature vectors (normalized tensors)
    - Event pressure signals
    - No interpretation occurs here
    """
    
    def __init__(self, symbols: Optional[List[str]] = None):
        """
        Initialize Perception Engine.
        
        Args:
            symbols: List of symbols to monitor (defaults to config universe)
        """
        self.symbols = symbols or SentinelConfig.get_all_symbols()
        self.logger = logger
        
        # Perception state (raw observations only)
        self.latest_prices = {}
        self.latest_volumes = {}
        self.latest_features = {}
        
        # Observation timestamps
        self.last_observation_time = None
        
        self.logger.info(f"Perception Engine initialized with {len(self.symbols)} symbols")
    
    def observe_market(self, lookback_days: int = 90) -> Dict[str, pd.DataFrame]:
        """
        Observe current market state across all symbols.
        
        Args:
            lookback_days: Days of historical data to fetch
            
        Returns:
            Dictionary mapping symbols to OHLCV dataframes
        """
        self.logger.info(f"Observing market: {len(self.symbols)} symbols, {lookback_days} days lookback")
        
        market_data = {}
        
        # Parallel data fetching
        with ThreadPoolExecutor(max_workers=SentinelConfig.CPU_THREADS) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_symbol_data, symbol, lookback_days): symbol
                for symbol in self.symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None and not data.empty:
                        market_data[symbol] = data
                        self.latest_prices[symbol] = data['Close'].iloc[-1]
                        self.latest_volumes[symbol] = data['Volume'].iloc[-1]
                except Exception as e:
                    self.logger.warning(f"Failed to fetch {symbol}: {e}")
        
        self.last_observation_time = datetime.now()
        self.logger.info(f"Market observation complete: {len(market_data)}/{len(self.symbols)} symbols")
        
        return market_data
    
    def _fetch_symbol_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a single symbol"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                return None
            
            return data
        except Exception as e:
            self.logger.debug(f"Error fetching {symbol}: {e}")
            return None
    
    def extract_price_behavior_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract price behavior features (Group 1).
        
        Features:
        - log_return
        - rolling_return_5d
        - rolling_return_20d
        - drawdown_pct
        - price_distance_from_high
        """
        features = {}
        
        close = data['Close']
        
        # Log return
        features['log_return'] = np.log(close.iloc[-1] / close.iloc[-2]) if len(close) > 1 else 0.0
        
        # Rolling returns
        features['rolling_return_5d'] = (close.iloc[-1] / close.iloc[-6] - 1) if len(close) > 5 else 0.0
        features['rolling_return_20d'] = (close.iloc[-1] / close.iloc[-21] - 1) if len(close) > 20 else 0.0
        
        # Drawdown
        running_max = close.expanding().max()
        drawdown = (close - running_max) / running_max
        features['drawdown_pct'] = drawdown.iloc[-1]
        
        # Distance from high
        high_52w = close.rolling(window=min(252, len(close))).max().iloc[-1]
        features['price_distance_from_high'] = (close.iloc[-1] - high_52w) / high_52w
        
        return features
    
    def extract_volatility_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Extract volatility structure features (Group 2).
        
        Features:
        - vol_30
        - vol_90
        - vol_180
        - vol_ratio_30_180
        - vol_acceleration
        """
        features = {}
        
        close = data['Close']
        returns = close.pct_change().dropna()
        
        # Volatility at different windows
        features['vol_30'] = returns.rolling(window=min(30, len(returns))).std().iloc[-1] if len(returns) > 30 else 0.0
        features['vol_90'] = returns.rolling(window=min(90, len(returns))).std().iloc[-1] if len(returns) > 90 else 0.0
        features['vol_180'] = returns.rolling(window=min(180, len(returns))).std().iloc[-1] if len(returns) > 180 else 0.0
        
        # Volatility ratio
        if features['vol_180'] > 0:
            features['vol_ratio_30_180'] = features['vol_30'] / features['vol_180']
        else:
            features['vol_ratio_30_180'] = 1.0
        
        # Volatility acceleration (change in volatility)
        vol_recent = returns.rolling(window=min(10, len(returns))).std().iloc[-1] if len(returns) > 10 else 0.0
        vol_previous = returns.rolling(window=min(10, len(returns))).std().iloc[-11] if len(returns) > 20 else 0.0
        features['vol_acceleration'] = (vol_recent - vol_previous) / vol_previous if vol_previous > 0 else 0.0
        
        return features
    
    def extract_correlation_features(self, market_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        Extract correlation & contagion features (Group 3).
        
        Features:
        - avg_correlation
        - correlation_change
        - correlation_dispersion
        """
        features = {}
        
        # Build returns matrix
        returns_dict = {}
        for symbol, data in market_data.items():
            if len(data) > 1:
                returns_dict[symbol] = data['Close'].pct_change().dropna()
        
        if len(returns_dict) < 2:
            # Not enough data for correlation
            features['avg_correlation'] = 0.0
            features['correlation_change'] = 0.0
            features['correlation_dispersion'] = 0.0
            return features
        
        # Align all returns to same index
        returns_df = pd.DataFrame(returns_dict).dropna()
        
        if len(returns_df) < 30:
            features['avg_correlation'] = 0.0
            features['correlation_change'] = 0.0
            features['correlation_dispersion'] = 0.0
            return features
        
        # Current correlation matrix
        corr_matrix_recent = returns_df.tail(30).corr()
        
        # Extract upper triangle (excluding diagonal)
        mask = np.triu(np.ones_like(corr_matrix_recent), k=1).astype(bool)
        correlations_recent = corr_matrix_recent.where(mask).stack().values
        
        features['avg_correlation'] = np.mean(correlations_recent)
        features['correlation_dispersion'] = np.std(correlations_recent)
        
        # Correlation change (compare to 60 days ago)
        if len(returns_df) > 90:
            corr_matrix_old = returns_df.iloc[-90:-60].corr()
            correlations_old = corr_matrix_old.where(mask).stack().values
            features['correlation_change'] = np.mean(correlations_recent) - np.mean(correlations_old)
        else:
            features['correlation_change'] = 0.0
        
        return features
    
    def compute_feature_tensor(self, market_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
        """
        Compute complete feature tensor for all symbols.
        
        Returns:
            Dictionary mapping symbols to feature dictionaries
        """
        self.logger.info("Computing feature tensors...")
        
        feature_tensor = {}
        
        for symbol, data in market_data.items():
            try:
                features = {}
                
                # Price behavior
                features.update(self.extract_price_behavior_features(data))
                
                # Volatility structure
                features.update(self.extract_volatility_features(data))
                
                feature_tensor[symbol] = features
                
            except Exception as e:
                self.logger.warning(f"Failed to compute features for {symbol}: {e}")
        
        # Correlation features (cross-symbol)
        correlation_features = self.extract_correlation_features(market_data)
        
        # Add correlation features to all symbols
        for symbol in feature_tensor.keys():
            feature_tensor[symbol].update(correlation_features)
        
        self.latest_features = feature_tensor
        
        self.logger.info(f"Feature tensor computed for {len(feature_tensor)} symbols")
        
        return feature_tensor
    
    def get_perception_snapshot(self) -> Dict:
        """
        Get current perception state snapshot.
        
        Returns:
            Dictionary containing current observations
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "symbols_observed": len(self.latest_prices),
            "latest_prices": self.latest_prices.copy(),
            "latest_volumes": self.latest_volumes.copy(),
            "last_observation": self.last_observation_time.isoformat() if self.last_observation_time else None
        }


if __name__ == "__main__":
    # Test Perception Engine
    print("Testing Perception Engine...")
    print("=" * 60)
    
    # Initialize with small universe for testing
    test_symbols = ["SPY", "QQQ", "VIX"]
    perception = PerceptionEngine(symbols=test_symbols)
    
    # Observe market
    market_data = perception.observe_market(lookback_days=90)
    print(f"\n✅ Observed {len(market_data)} symbols")
    
    # Compute features
    features = perception.compute_feature_tensor(market_data)
    print(f"✅ Computed features for {len(features)} symbols")
    
    # Display sample features
    if "SPY" in features:
        print(f"\nSample features for SPY:")
        for feature_name, value in list(features["SPY"].items())[:10]:
            print(f"  {feature_name}: {value:.6f}")
    
    # Get snapshot
    snapshot = perception.get_perception_snapshot()
    print(f"\n✅ Perception snapshot:")
    print(f"  Timestamp: {snapshot['timestamp']}")
    print(f"  Symbols observed: {snapshot['symbols_observed']}")
    
    print("\n" + "=" * 60)
    print("Perception Engine test complete!")
