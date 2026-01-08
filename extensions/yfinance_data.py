"""
YFinance data provider for landing page market overview
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class YFinanceProvider:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 30  # seconds
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get('timestamp')
        if not cached_time:
            return False
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def get_landing_data(self) -> Dict:
        """Fetch all landing page data"""
        try:
            return {
                "indices": self.get_major_indices(),
                "movers": self.get_market_movers(),
                "sectors": self.get_sector_performance(),
                "summary": self.get_market_summary(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching landing data: {e}")
            return self._get_fallback_data()
    
    def get_major_indices(self) -> List[Dict]:
        """Fetch major market indices"""
        cache_key = 'indices'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'Nasdaq',
            '^RUT': 'Russell 2000'
        }
        
        result = []
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period='1d', interval='1m')
                
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                
                # Get mini sparkline data (last 20 points)
                sparkline = hist['Close'].tail(20).tolist() if not hist.empty else []
                
                result.append({
                    'symbol': symbol,
                    'name': name,
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'volume': info.get('volume', 0),
                    'sparkline': sparkline
                })
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
                result.append({
                    'symbol': symbol,
                    'name': name,
                    'price': 0,
                    'change': 0,
                    'change_pct': 0,
                    'volume': 0,
                    'sparkline': []
                })
        
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        return result
    
    def get_market_movers(self) -> Dict:
        """Get top gainers/losers from popular stocks"""
        cache_key = 'movers'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # Popular tech/mega-cap stocks for quick movers
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 
                   'JPM', 'V', 'WMT', 'JNJ', 'PG', 'MA', 'HD', 'BAC']
        
        movers_data = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                
                movers_data.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': round(current_price, 2),
                    'change_pct': round(change_pct, 2),
                    'volume': info.get('volume', 0)
                })
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
        
        # Sort and get top 5 gainers and losers
        sorted_movers = sorted(movers_data, key=lambda x: x['change_pct'], reverse=True)
        
        result = {
            'gainers': sorted_movers[:5],
            'losers': sorted_movers[-5:][::-1],  # Reverse to show worst first
            'active': sorted(movers_data, key=lambda x: x['volume'], reverse=True)[:5]
        }
        
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        return result
    
    def get_sector_performance(self) -> List[Dict]:
        """Fetch sector ETF performance"""
        cache_key = 'sectors'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        sector_etfs = {
            'XLK': 'Technology',
            'XLV': 'Healthcare',
            'XLF': 'Financials',
            'XLE': 'Energy',
            'XLI': 'Industrials',
            'XLY': 'Consumer Disc.',
            'XLP': 'Consumer Staples',
            'XLU': 'Utilities',
            'XLRE': 'Real Estate',
            'XLB': 'Materials',
            'XLC': 'Communication'
        }
        
        result = []
        for symbol, name in sector_etfs.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                
                result.append({
                    'symbol': symbol,
                    'name': name,
                    'change_pct': round(change_pct, 2)
                })
            except Exception as e:
                logger.warning(f"Error fetching sector {symbol}: {e}")
                result.append({
                    'symbol': symbol,
                    'name': name,
                    'change_pct': 0
                })
        
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        return result
    
    def get_market_summary(self) -> Dict:
        """Get overall market summary"""
        cache_key = 'summary'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Get VIX for volatility
            vix = yf.Ticker('^VIX')
            vix_info = vix.info
            vix_price = vix_info.get('regularMarketPrice', 0)
            
            # Get S&P 500 for volume
            sp500 = yf.Ticker('^GSPC')
            sp500_info = sp500.info
            
            result = {
                'vix': round(vix_price, 2),
                'volume': sp500_info.get('volume', 0),
                'market_state': sp500_info.get('marketState', 'CLOSED')
            }
        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")
            result = {
                'vix': 0,
                'volume': 0,
                'market_state': 'UNKNOWN'
            }
        
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        return result
    
    def _get_fallback_data(self) -> Dict:
        """Return fallback data if API fails"""
        return {
            "indices": [],
            "movers": {"gainers": [], "losers": [], "active": []},
            "sectors": [],
            "summary": {"vix": 0, "volume": 0, "market_state": "UNKNOWN"},
            "timestamp": datetime.now().isoformat(),
            "error": "Unable to fetch market data"
        }
