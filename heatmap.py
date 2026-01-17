"""
Heatmap Generation Module
Provides utilities for creating financial heatmaps and correlation matrices.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime, timedelta


def calculate_correlation_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix from price data.
    
    Args:
        price_data: DataFrame with symbols as columns and dates as index
    
    Returns:
        Correlation matrix DataFrame
    """
    returns = price_data.pct_change().dropna()
    return returns.corr()


def calculate_returns_heatmap(price_data: pd.DataFrame, period: str = 'daily') -> pd.DataFrame:
    """
    Calculate returns heatmap for multiple assets.
    
    Args:
        price_data: DataFrame with symbols as columns and dates as index
        period: 'daily', 'weekly', 'monthly'
    
    Returns:
        DataFrame of returns
    """
    if period == 'daily':
        returns = price_data.pct_change()
    elif period == 'weekly':
        returns = price_data.resample('W').last().pct_change()
    elif period == 'monthly':
        returns = price_data.resample('M').last().pct_change()
    else:
        returns = price_data.pct_change()
    
    return returns.dropna()


def sector_performance_heatmap(sector_data: List[Dict]) -> Dict:
    """
    Generate sector performance heatmap data.
    
    Args:
        sector_data: List of dicts with 'sector', 'change_pct' keys
    
    Returns:
        Dictionary with heatmap configuration
    """
    # Sort by performance
    sorted_data = sorted(sector_data, key=lambda x: x.get('change_pct', 0), reverse=True)
    
    heatmap = {
        'type': 'sector_heatmap',
        'data': [],
        'max_value': max([s.get('change_pct', 0) for s in sorted_data]) if sorted_data else 0,
        'min_value': min([s.get('change_pct', 0) for s in sorted_data]) if sorted_data else 0
    }
    
    for sector in sorted_data:
        change_pct = sector.get('change_pct', 0)
        
        # Determine color intensity
        if change_pct > 0:
            intensity = min(change_pct / 5.0, 1.0)  # Cap at 5% for max green
            color_class = 'green'
        elif change_pct < 0:
            intensity = min(abs(change_pct) / 5.0, 1.0)  # Cap at -5% for max red
            color_class = 'red'
        else:
            intensity = 0
            color_class = 'neutral'
        
        heatmap['data'].append({
            'sector': sector.get('sector', 'Unknown'),
            'value': change_pct,
            'intensity': intensity,
            'color_class': color_class,
            'display_value': f"{change_pct:+.2f}%"
        })
    
    return heatmap


def market_overview_heatmap(market_data: List[Dict], metric: str = 'change_pct') -> Dict:
    """
    Generate market overview heatmap for stocks.
    
    Args:
        market_data: List of stock data dicts
        metric: Metric to visualize ('change_pct', 'volume', 'volatility')
    
    Returns:
        Heatmap configuration dictionary
    """
    heatmap = {
        'type': 'market_heatmap',
        'metric': metric,
        'data': [],
        'grid_size': calculate_grid_size(len(market_data))
    }
    
    for stock in market_data:
        value = stock.get(metric, 0)
        
        # Determine color based on metric
        if metric == 'change_pct':
            color_class = 'green' if value > 0 else 'red' if value < 0 else 'neutral'
            intensity = min(abs(value) / 3.0, 1.0)  # Cap at 3%
        elif metric == 'volume':
            # Normalize volume (higher = more intense)
            max_vol = max([s.get('volume', 1) for s in market_data])
            intensity = value / max_vol if max_vol > 0 else 0
            color_class = 'blue'
        elif metric == 'volatility':
            intensity = min(value / 5.0, 1.0)  # Cap at 5% volatility
            color_class = 'orange'
        else:
            intensity = 0.5
            color_class = 'neutral'
        
        heatmap['data'].append({
            'symbol': stock.get('symbol', 'N/A'),
            'value': value,
            'price': stock.get('price', 0),
            'intensity': intensity,
            'color_class': color_class,
            'display_value': format_metric_value(value, metric)
        })
    
    return heatmap


def calculate_grid_size(num_items: int) -> Tuple[int, int]:
    """
    Calculate optimal grid dimensions for heatmap.
    
    Args:
        num_items: Number of items to display
    
    Returns:
        Tuple of (rows, cols)
    """
    # Try to make it roughly square
    cols = int(np.ceil(np.sqrt(num_items)))
    rows = int(np.ceil(num_items / cols))
    return (rows, cols)


def format_metric_value(value: float, metric: str) -> str:
    """
    Format metric value for display.
    
    Args:
        value: Numeric value
        metric: Metric type
    
    Returns:
        Formatted string
    """
    if metric == 'change_pct':
        return f"{value:+.2f}%"
    elif metric == 'volume':
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.0f}"
    elif metric == 'volatility':
        return f"{value:.2f}%"
    else:
        return f"{value:.2f}"


def time_series_heatmap(price_data: pd.DataFrame, window: int = 20) -> Dict:
    """
    Generate time series heatmap showing performance over time.
    
    Args:
        price_data: DataFrame with dates as index, symbols as columns
        window: Number of periods to display
    
    Returns:
        Heatmap configuration
    """
    # Get last N periods
    recent_data = price_data.tail(window)
    
    # Calculate daily returns
    returns = recent_data.pct_change().fillna(0) * 100  # Convert to percentage
    
    heatmap = {
        'type': 'timeseries_heatmap',
        'dates': [d.strftime('%Y-%m-%d') for d in returns.index],
        'symbols': list(returns.columns),
        'data': []
    }
    
    # Create matrix data
    for symbol in returns.columns:
        symbol_data = {
            'symbol': symbol,
            'values': []
        }
        
        for date, value in returns[symbol].items():
            intensity = min(abs(value) / 3.0, 1.0)
            color_class = 'green' if value > 0 else 'red' if value < 0 else 'neutral'
            
            symbol_data['values'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': value,
                'intensity': intensity,
                'color_class': color_class,
                'display': f"{value:+.2f}%"
            })
        
        heatmap['data'].append(symbol_data)
    
    return heatmap


def risk_heatmap(portfolio: List[Dict], risk_metrics: Dict) -> Dict:
    """
    Generate risk heatmap for portfolio positions.
    
    Args:
        portfolio: List of position dicts with 'symbol', 'value', 'weight'
        risk_metrics: Dict with risk metrics per symbol
    
    Returns:
        Risk heatmap configuration
    """
    heatmap = {
        'type': 'risk_heatmap',
        'data': []
    }
    
    for position in portfolio:
        symbol = position.get('symbol', 'N/A')
        metrics = risk_metrics.get(symbol, {})
        
        # Calculate composite risk score
        volatility = metrics.get('volatility', 0)
        beta = metrics.get('beta', 1.0)
        var = metrics.get('var', 0)  # Value at Risk
        
        risk_score = (volatility * 0.4) + (abs(beta - 1.0) * 0.3) + (var * 0.3)
        
        # Determine risk level
        if risk_score < 0.15:
            risk_level = 'LOW'
            color_class = 'green'
        elif risk_score < 0.30:
            risk_level = 'MEDIUM'
            color_class = 'yellow'
        else:
            risk_level = 'HIGH'
            color_class = 'red'
        
        intensity = min(risk_score / 0.5, 1.0)
        
        heatmap['data'].append({
            'symbol': symbol,
            'weight': position.get('weight', 0),
            'value': position.get('value', 0),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'volatility': volatility,
            'beta': beta,
            'intensity': intensity,
            'color_class': color_class
        })
    
    # Sort by risk score descending
    heatmap['data'] = sorted(heatmap['data'], key=lambda x: x['risk_score'], reverse=True)
    
    return heatmap


def correlation_strength_heatmap(correlation_matrix: pd.DataFrame, 
                                 threshold: float = 0.5) -> Dict:
    """
    Generate heatmap highlighting strong correlations.
    
    Args:
        correlation_matrix: Correlation matrix DataFrame
        threshold: Minimum correlation strength to highlight
    
    Returns:
        Heatmap configuration
    """
    heatmap = {
        'type': 'correlation_heatmap',
        'symbols': list(correlation_matrix.columns),
        'data': []
    }
    
    for i, symbol1 in enumerate(correlation_matrix.columns):
        row_data = {
            'symbol': symbol1,
            'correlations': []
        }
        
        for j, symbol2 in enumerate(correlation_matrix.columns):
            corr_value = correlation_matrix.iloc[i, j]
            
            # Skip self-correlation
            if i == j:
                color_class = 'self'
                intensity = 1.0
            else:
                # Determine color based on correlation
                if corr_value > threshold:
                    color_class = 'strong_positive'
                elif corr_value < -threshold:
                    color_class = 'strong_negative'
                elif corr_value > 0:
                    color_class = 'weak_positive'
                else:
                    color_class = 'weak_negative'
                
                intensity = abs(corr_value)
            
            row_data['correlations'].append({
                'with_symbol': symbol2,
                'value': corr_value,
                'intensity': intensity,
                'color_class': color_class,
                'display': f"{corr_value:.2f}"
            })
        
        heatmap['data'].append(row_data)
    
    return heatmap


def intraday_heatmap(intraday_data: pd.DataFrame, interval: str = '15min') -> Dict:
    """
    Generate intraday performance heatmap.
    
    Args:
        intraday_data: DataFrame with datetime index and symbol columns
        interval: Time interval ('5min', '15min', '30min', '1h')
    
    Returns:
        Intraday heatmap configuration
    """
    # Resample to desired interval
    resampled = intraday_data.resample(interval).last()
    returns = resampled.pct_change().fillna(0) * 100
    
    heatmap = {
        'type': 'intraday_heatmap',
        'interval': interval,
        'times': [t.strftime('%H:%M') for t in returns.index],
        'symbols': list(returns.columns),
        'data': []
    }
    
    for symbol in returns.columns:
        symbol_data = {
            'symbol': symbol,
            'intervals': []
        }
        
        for time, value in returns[symbol].items():
            intensity = min(abs(value) / 2.0, 1.0)  # Cap at 2% for intraday
            color_class = 'green' if value > 0 else 'red' if value < 0 else 'neutral'
            
            symbol_data['intervals'].append({
                'time': time.strftime('%H:%M'),
                'value': value,
                'intensity': intensity,
                'color_class': color_class,
                'display': f"{value:+.2f}%"
            })
        
        heatmap['data'].append(symbol_data)
    
    return heatmap


class HeatmapGenerator:
    """
    Comprehensive heatmap generation class for financial data.
    """
    
    def __init__(self, data: Union[pd.DataFrame, List[Dict]]):
        """
        Initialize heatmap generator.
        
        Args:
            data: Price data (DataFrame) or market data (List of dicts)
        """
        self.data = data
    
    def generate_sector_heatmap(self) -> Dict:
        """Generate sector performance heatmap."""
        if isinstance(self.data, list):
            return sector_performance_heatmap(self.data)
        else:
            raise ValueError("Sector heatmap requires list of sector data")
    
    def generate_market_heatmap(self, metric: str = 'change_pct') -> Dict:
        """Generate market overview heatmap."""
        if isinstance(self.data, list):
            return market_overview_heatmap(self.data, metric)
        else:
            raise ValueError("Market heatmap requires list of stock data")
    
    def generate_correlation_heatmap(self) -> Dict:
        """Generate correlation heatmap."""
        if isinstance(self.data, pd.DataFrame):
            corr_matrix = calculate_correlation_matrix(self.data)
            return correlation_strength_heatmap(corr_matrix)
        else:
            raise ValueError("Correlation heatmap requires DataFrame")
    
    def generate_timeseries_heatmap(self, window: int = 20) -> Dict:
        """Generate time series heatmap."""
        if isinstance(self.data, pd.DataFrame):
            return time_series_heatmap(self.data, window)
        else:
            raise ValueError("Time series heatmap requires DataFrame")
    
    def export_to_json(self, heatmap_type: str, **kwargs) -> str:
        """
        Export heatmap to JSON format.
        
        Args:
            heatmap_type: Type of heatmap to generate
            **kwargs: Additional arguments for heatmap generation
        
        Returns:
            JSON string
        """
        import json
        
        if heatmap_type == 'sector':
            heatmap = self.generate_sector_heatmap()
        elif heatmap_type == 'market':
            heatmap = self.generate_market_heatmap(**kwargs)
        elif heatmap_type == 'correlation':
            heatmap = self.generate_correlation_heatmap()
        elif heatmap_type == 'timeseries':
            heatmap = self.generate_timeseries_heatmap(**kwargs)
        else:
            raise ValueError(f"Unknown heatmap type: {heatmap_type}")
        
        return json.dumps(heatmap, indent=2)


def generate_html_heatmap(heatmap_data: Dict, title: str = "Financial Heatmap") -> str:
    """
    Generate standalone HTML heatmap visualization.
    
    Args:
        heatmap_data: Heatmap configuration dictionary
        title: Title for the heatmap
    
    Returns:
        HTML string
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }}
            .heatmap-container {{ padding: 20px; }}
            .heatmap-title {{ font-size: 24px; margin-bottom: 20px; }}
            .heatmap-grid {{ display: grid; gap: 5px; }}
            .heatmap-cell {{ 
                padding: 10px; 
                text-align: center; 
                border-radius: 4px;
                transition: transform 0.2s;
            }}
            .heatmap-cell:hover {{ transform: scale(1.05); }}
            .green {{ background: rgba(0, 255, 0, var(--intensity)); }}
            .red {{ background: rgba(255, 0, 0, var(--intensity)); }}
            .blue {{ background: rgba(0, 100, 255, var(--intensity)); }}
            .neutral {{ background: rgba(128, 128, 128, 0.3); }}
        </style>
    </head>
    <body>
        <div class="heatmap-container">
            <div class="heatmap-title">{title}</div>
            <div class="heatmap-grid" id="heatmap"></div>
        </div>
        <script>
            const heatmapData = {heatmap_data};
            // Render logic would go here
        </script>
    </body>
    </html>
    """
    return html
