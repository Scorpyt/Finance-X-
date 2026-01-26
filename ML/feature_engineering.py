"""
Feature Engineering Module for Market Prediction ML Model
Extracts technical indicators, price patterns, and market context features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf


class FeatureEngineer:
    """
    Comprehensive feature extraction for market prediction.
    Generates 50+ features from price/volume data.
    """
    
    def __init__(self):
        self.feature_names = []
        
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD, Signal line, and Histogram"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=3).mean()
        return k, d
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = self.calculate_atr(high, low, close, period)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx
    
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    def calculate_vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    def extract_features(self, symbol: str, lookback_days: int = 365) -> pd.DataFrame:
        """
        Extract all features for a given symbol.
        
        Args:
            symbol: Stock/index symbol (e.g., 'SPY', 'NIFTY50.NS')
            lookback_days: Number of days of historical data
            
        Returns:
            DataFrame with features and target variable
        """
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        df = pd.DataFrame()
        
        # Price features
        df['close'] = data['Close']
        df['open'] = data['Open']
        df['high'] = data['High']
        df['low'] = data['Low']
        df['volume'] = data['Volume']
        
        # Returns
        df['return_1d'] = df['close'].pct_change()
        df['return_5d'] = df['close'].pct_change(5)
        df['return_20d'] = df['close'].pct_change(20)
        
        # Moving Averages
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            df[f'price_to_sma_{period}'] = df['close'] / df[f'sma_{period}']
        
        # MA Crossovers
        df['sma_5_20_cross'] = (df['sma_5'] > df['sma_20']).astype(int)
        df['sma_20_50_cross'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['ema_12_26_cross'] = (df['ema_12'] > df['ema_26']).astype(int)
        
        # Technical Indicators
        df['rsi_14'] = self.calculate_rsi(df['close'], 14)
        df['rsi_7'] = self.calculate_rsi(df['close'], 7)
        
        macd, signal, histogram = self.calculate_macd(df['close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_histogram'] = histogram
        
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = upper_bb
        df['bb_middle'] = middle_bb
        df['bb_lower'] = lower_bb
        df['bb_width'] = (upper_bb - lower_bb) / middle_bb
        df['bb_position'] = (df['close'] - lower_bb) / (upper_bb - lower_bb)
        
        df['atr_14'] = self.calculate_atr(df['high'], df['low'], df['close'], 14)
        df['atr_pct'] = df['atr_14'] / df['close']
        
        stoch_k, stoch_d = self.calculate_stochastic(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch_k
        df['stoch_d'] = stoch_d
        
        df['adx_14'] = self.calculate_adx(df['high'], df['low'], df['close'], 14)
        
        # Volume Indicators
        df['obv'] = self.calculate_obv(df['close'], df['volume'])
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']
        df['vwap'] = self.calculate_vwap(df['high'], df['low'], df['close'], df['volume'])
        
        # Volatility
        df['volatility_20'] = df['return_1d'].rolling(window=20).std()
        df['volatility_60'] = df['return_1d'].rolling(window=60).std()
        
        # Price Patterns
        df['high_low_range'] = (df['high'] - df['low']) / df['close']
        df['close_open_range'] = (df['close'] - df['open']) / df['open']
        
        # Momentum
        df['momentum_5'] = df['close'] - df['close'].shift(5)
        df['momentum_10'] = df['close'] - df['close'].shift(10)
        df['momentum_20'] = df['close'] - df['close'].shift(20)
        
        # Target Variable: 1 if next day closes higher, 0 otherwise
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        # Drop rows with NaN values
        df = df.dropna()
        
        # Store feature names (excluding target and OHLCV)
        self.feature_names = [col for col in df.columns if col not in ['target', 'close', 'open', 'high', 'low', 'volume']]
        
        return df
    
    def get_latest_features(self, symbol: str) -> Dict:
        """
        Get features for the most recent trading day (for real-time prediction).
        
        Args:
            symbol: Stock/index symbol
            
        Returns:
            Dictionary of feature values
        """
        df = self.extract_features(symbol, lookback_days=365)
        latest = df.iloc[-1]
        
        features = {name: latest[name] for name in self.feature_names}
        return features
    
    def prepare_training_data(self, symbol: str, lookback_days: int = 730) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features (X) and target (y) for model training.
        
        Args:
            symbol: Stock/index symbol
            lookback_days: Number of days of historical data (default: 2 years)
            
        Returns:
            Tuple of (features_df, target_series)
        """
        df = self.extract_features(symbol, lookback_days)
        X = df[self.feature_names]
        y = df['target']
        
        return X, y


if __name__ == "__main__":
    # Test feature engineering
    engineer = FeatureEngineer()
    
    print("Testing feature extraction for SPY...")
    X, y = engineer.prepare_training_data('SPY', lookback_days=365)
    
    print(f"\nDataset shape: {X.shape}")
    print(f"Number of features: {len(engineer.feature_names)}")
    print(f"Target distribution: {y.value_counts()}")
    print(f"\nFeature names:\n{engineer.feature_names}")
    
    print("\n\nTesting latest features extraction...")
    latest_features = engineer.get_latest_features('SPY')
    print(f"Latest features for SPY: {latest_features}")
