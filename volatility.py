"""
Volatility Analysis Module
Provides various volatility calculation methods for financial analysis.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List

def rolling_volatility(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate rolling volatility using log returns.
    
    Args:
        prices: Pandas Series of price data
        window: Rolling window size (e.g., 20 for 20-day volatility)
    
    Returns:
        Pandas Series of rolling volatility values
    """
    returns = np.log(prices / prices.shift(1))
    return returns.rolling(window).std()


def historical_volatility(prices: pd.Series, window: int = 20, annualize: bool = True) -> pd.Series:
    """
    Calculate historical volatility (realized volatility).
    
    Args:
        prices: Pandas Series of price data
        window: Rolling window size
        annualize: If True, annualize the volatility (multiply by sqrt(252))
    
    Returns:
        Pandas Series of historical volatility
    """
    returns = np.log(prices / prices.shift(1))
    vol = returns.rolling(window).std()
    
    if annualize:
        vol = vol * np.sqrt(252)  # Annualize assuming 252 trading days
    
    return vol


def parkinson_volatility(high: pd.Series, low: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate Parkinson's volatility using high-low range.
    More efficient than close-to-close volatility.
    
    Args:
        high: Pandas Series of high prices
        low: Pandas Series of low prices
        window: Rolling window size
    
    Returns:
        Pandas Series of Parkinson volatility
    """
    hl_ratio = np.log(high / low)
    parkinson_vol = np.sqrt((1 / (4 * np.log(2))) * (hl_ratio ** 2))
    return parkinson_vol.rolling(window).mean()


def garman_klass_volatility(open_price: pd.Series, high: pd.Series, 
                            low: pd.Series, close: pd.Series, 
                            window: int = 20) -> pd.Series:
    """
    Calculate Garman-Klass volatility estimator.
    Uses OHLC data for more accurate volatility estimation.
    
    Args:
        open_price: Pandas Series of open prices
        high: Pandas Series of high prices
        low: Pandas Series of low prices
        close: Pandas Series of close prices
        window: Rolling window size
    
    Returns:
        Pandas Series of Garman-Klass volatility
    """
    hl = np.log(high / low)
    co = np.log(close / open_price)
    
    gk_vol = np.sqrt(0.5 * (hl ** 2) - (2 * np.log(2) - 1) * (co ** 2))
    return gk_vol.rolling(window).mean()


def ewma_volatility(prices: pd.Series, span: int = 20) -> pd.Series:
    """
    Calculate Exponentially Weighted Moving Average (EWMA) volatility.
    Gives more weight to recent observations.
    
    Args:
        prices: Pandas Series of price data
        span: Span for EWMA calculation
    
    Returns:
        Pandas Series of EWMA volatility
    """
    returns = np.log(prices / prices.shift(1))
    return returns.ewm(span=span).std()


def volatility_cone(prices: pd.Series, windows: List[int] = [10, 20, 30, 60, 90]) -> pd.DataFrame:
    """
    Calculate volatility cone showing volatility across different time windows.
    
    Args:
        prices: Pandas Series of price data
        windows: List of window sizes to calculate
    
    Returns:
        DataFrame with min, max, median, current volatility for each window
    """
    results = []
    
    for window in windows:
        vol = historical_volatility(prices, window=window, annualize=True)
        
        results.append({
            'window': window,
            'current': vol.iloc[-1] if not vol.empty else np.nan,
            'min': vol.min(),
            'max': vol.max(),
            'median': vol.median(),
            'mean': vol.mean()
        })
    
    return pd.DataFrame(results)


def volatility_ratio(prices: pd.Series, short_window: int = 10, long_window: int = 30) -> pd.Series:
    """
    Calculate volatility ratio (short-term vol / long-term vol).
    Values > 1 indicate increasing volatility.
    
    Args:
        prices: Pandas Series of price data
        short_window: Short-term window
        long_window: Long-term window
    
    Returns:
        Pandas Series of volatility ratios
    """
    short_vol = rolling_volatility(prices, short_window)
    long_vol = rolling_volatility(prices, long_window)
    
    return short_vol / long_vol


def volatility_percentile(prices: pd.Series, window: int = 20, lookback: int = 252) -> pd.Series:
    """
    Calculate current volatility percentile relative to historical range.
    
    Args:
        prices: Pandas Series of price data
        window: Window for volatility calculation
        lookback: Lookback period for percentile calculation
    
    Returns:
        Pandas Series of volatility percentiles (0-100)
    """
    vol = historical_volatility(prices, window=window, annualize=False)
    
    def calc_percentile(x):
        if len(x) < 2:
            return np.nan
        current = x.iloc[-1]
        return (x < current).sum() / len(x) * 100
    
    return vol.rolling(lookback).apply(calc_percentile, raw=False)


def realized_vs_implied_spread(realized_vol: float, implied_vol: float) -> dict:
    """
    Calculate the spread between realized and implied volatility.
    
    Args:
        realized_vol: Current realized volatility
        implied_vol: Implied volatility (e.g., from options)
    
    Returns:
        Dictionary with spread metrics
    """
    spread = implied_vol - realized_vol
    spread_pct = (spread / realized_vol) * 100 if realized_vol != 0 else 0
    
    return {
        'realized_vol': realized_vol,
        'implied_vol': implied_vol,
        'spread': spread,
        'spread_pct': spread_pct,
        'signal': 'OVERPRICED' if spread > 0 else 'UNDERPRICED' if spread < 0 else 'FAIR'
    }


def volatility_regime_detection(prices: pd.Series, window: int = 20, 
                                low_threshold: float = 0.15, 
                                high_threshold: float = 0.30) -> pd.Series:
    """
    Detect volatility regime (LOW, MEDIUM, HIGH).
    
    Args:
        prices: Pandas Series of price data
        window: Window for volatility calculation
        low_threshold: Threshold for low volatility (annualized)
        high_threshold: Threshold for high volatility (annualized)
    
    Returns:
        Pandas Series of regime labels
    """
    vol = historical_volatility(prices, window=window, annualize=True)
    
    def classify_regime(v):
        if pd.isna(v):
            return 'UNKNOWN'
        elif v < low_threshold:
            return 'LOW_VOL'
        elif v < high_threshold:
            return 'MEDIUM_VOL'
        else:
            return 'HIGH_VOL'
    
    return vol.apply(classify_regime)


def volatility_breakout_signal(prices: pd.Series, window: int = 20, 
                               threshold_std: float = 2.0) -> pd.Series:
    """
    Detect volatility breakouts (when vol exceeds threshold).
    
    Args:
        prices: Pandas Series of price data
        window: Window for volatility calculation
        threshold_std: Number of standard deviations for breakout
    
    Returns:
        Pandas Series of boolean breakout signals
    """
    vol = rolling_volatility(prices, window)
    vol_mean = vol.rolling(window * 2).mean()
    vol_std = vol.rolling(window * 2).std()
    
    upper_band = vol_mean + (threshold_std * vol_std)
    
    return vol > upper_band


class VolatilityAnalyzer:
    """
    Comprehensive volatility analysis class for financial instruments.
    """
    
    def __init__(self, prices: pd.Series, high: pd.Series = None, 
                 low: pd.Series = None, open_price: pd.Series = None):
        """
        Initialize volatility analyzer.
        
        Args:
            prices: Close prices (required)
            high: High prices (optional, for advanced calculations)
            low: Low prices (optional, for advanced calculations)
            open_price: Open prices (optional, for advanced calculations)
        """
        self.prices = prices
        self.high = high
        self.low = low
        self.open = open_price
    
    def get_all_metrics(self, window: int = 20) -> dict:
        """
        Calculate all available volatility metrics.
        
        Args:
            window: Window size for calculations
        
        Returns:
            Dictionary of volatility metrics
        """
        metrics = {
            'rolling_vol': rolling_volatility(self.prices, window).iloc[-1],
            'historical_vol': historical_volatility(self.prices, window).iloc[-1],
            'ewma_vol': ewma_volatility(self.prices, window).iloc[-1],
            'vol_percentile': volatility_percentile(self.prices, window).iloc[-1],
            'regime': volatility_regime_detection(self.prices, window).iloc[-1]
        }
        
        # Add advanced metrics if OHLC data available
        if self.high is not None and self.low is not None:
            metrics['parkinson_vol'] = parkinson_volatility(self.high, self.low, window).iloc[-1]
            
            if self.open is not None:
                metrics['garman_klass_vol'] = garman_klass_volatility(
                    self.open, self.high, self.low, self.prices, window
                ).iloc[-1]
        
        return metrics
    
    def get_summary(self, window: int = 20) -> str:
        """
        Get human-readable volatility summary.
        
        Args:
            window: Window size for calculations
        
        Returns:
            Formatted summary string
        """
        metrics = self.get_all_metrics(window)
        
        summary = f"""
Volatility Analysis Summary ({window}-period)
{'=' * 50}
Rolling Volatility:     {metrics.get('rolling_vol', 0):.4f}
Historical Volatility:  {metrics.get('historical_vol', 0):.2%}
EWMA Volatility:        {metrics.get('ewma_vol', 0):.4f}
Volatility Percentile:  {metrics.get('vol_percentile', 0):.1f}%
Volatility Regime:      {metrics.get('regime', 'UNKNOWN')}
"""
        
        if 'parkinson_vol' in metrics:
            summary += f"Parkinson Volatility:   {metrics['parkinson_vol']:.4f}\n"
        
        if 'garman_klass_vol' in metrics:
            summary += f"Garman-Klass Vol:       {metrics['garman_klass_vol']:.4f}\n"
        
        return summary
