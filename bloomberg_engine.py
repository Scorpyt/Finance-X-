"""
Bloomberg-Style Engine - Professional Market Features
Provides FX rates, screeners, top movers, sector analysis, and economic calendar.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import threading
from economic_calendar_fetcher import EconomicCalendarFetcher

@dataclass
class FXRate:
    pair: str
    rate: float
    change: float
    change_pct: float

class BloombergEngine:
    """Professional market data features inspired by Bloomberg Terminal."""
    
    # Major currency pairs
    FX_PAIRS = {
        "USD/INR": "USDINR=X",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "EUR/INR": "EURINR=X",
        "GBP/INR": "GBPINR=X",
        "BTC/USD": "BTC-USD",
        "ETH/USD": "ETH-USD",
    }
    
    # US Sector ETFs
    SECTOR_ETFS = {
        "Technology": "XLK",
        "Financials": "XLF",
        "Energy": "XLE",
        "Healthcare": "XLV",
        "Industrials": "XLI",
        "Consumer": "XLY",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Materials": "XLB",
        "Communications": "XLC",
    }
    
    # Economic Calendar now uses real-time data from EconomicCalendarFetcher
    # No static events needed - all data is fetched live
    
    def __init__(self):
        self.fx_cache = {}
        self.fx_cache_time = None
        self.sector_cache = {}
        self.sector_cache_time = None
        self.lock = threading.Lock()
        
        # Initialize economic calendar fetcher with auto-updates every hour
        self.economic_fetcher = EconomicCalendarFetcher(update_interval_seconds=3600)
        self.economic_fetcher.start_background_updates()
    
    def get_fx_rates(self) -> List[Dict]:
        """Fetch live FX rates from yfinance."""
        now = datetime.now()
        
        # Cache for 30 seconds
        with self.lock:
            if self.fx_cache_time and (now - self.fx_cache_time).seconds < 30:
                return self.fx_cache.get("rates", [])
        
        rates = []
        symbols = list(self.FX_PAIRS.values())
        
        try:
            data = yf.download(symbols, period="2d", interval="1d", progress=False, threads=True)
            
            for pair_name, symbol in self.FX_PAIRS.items():
                try:
                    if symbol in data['Close'].columns:
                        closes = data['Close'][symbol].dropna()
                        if len(closes) >= 2:
                            current = float(closes.iloc[-1])
                            prev = float(closes.iloc[-2])
                            change = current - prev
                            change_pct = (change / prev) * 100
                            
                            rates.append({
                                "pair": pair_name,
                                "rate": round(current, 4),
                                "change": round(change, 4),
                                "change_pct": round(change_pct, 2),
                                "direction": "up" if change >= 0 else "down"
                            })
                except Exception as e:
                    continue
            
            with self.lock:
                self.fx_cache["rates"] = rates
                self.fx_cache_time = now
                
        except Exception as e:
            print(f"[Bloomberg Engine] FX Error: {e}")
        
        return rates
    
    def get_top_movers(self, market_data: List[Dict]) -> Dict:
        """Get top 5 gainers and losers from market data."""
        if not market_data:
            return {"gainers": [], "losers": []}
        
        # Sort by change percentage
        sorted_data = sorted(market_data, key=lambda x: x.get("change_pct", 0), reverse=True)
        
        gainers = [
            {
                "symbol": s["symbol"],
                "price": s["price"],
                "change": s.get("change", 0),
                "change_pct": s.get("change_pct", 0),
                "volume": s.get("volume", 0)
            }
            for s in sorted_data[:5] if s.get("change_pct", 0) > 0
        ]
        
        losers = [
            {
                "symbol": s["symbol"],
                "price": s["price"],
                "change": s.get("change", 0),
                "change_pct": s.get("change_pct", 0),
                "volume": s.get("volume", 0)
            }
            for s in reversed(sorted_data[-5:]) if s.get("change_pct", 0) < 0
        ]
        
        return {"gainers": gainers, "losers": losers}
    
    def screen_stocks(self, market_data: List[Dict], criteria: str = "GAINERS") -> List[Dict]:
        """Screen stocks based on criteria."""
        if not market_data:
            return []
        
        criteria = criteria.upper()
        
        if criteria == "GAINERS":
            return sorted(market_data, key=lambda x: x.get("change_pct", 0), reverse=True)[:10]
        
        elif criteria == "LOSERS":
            return sorted(market_data, key=lambda x: x.get("change_pct", 0))[:10]
        
        elif criteria == "VOLUME":
            return sorted(market_data, key=lambda x: x.get("volume", 0), reverse=True)[:10]
        
        elif criteria == "VOLATILE":
            # High range = high - low as % of price
            for s in market_data:
                if s.get("high") and s.get("low") and s.get("price"):
                    s["volatility"] = ((s["high"] - s["low"]) / s["price"]) * 100
                else:
                    s["volatility"] = 0
            return sorted(market_data, key=lambda x: x.get("volatility", 0), reverse=True)[:10]
        
        else:
            # Default to gainers
            return sorted(market_data, key=lambda x: x.get("change_pct", 0), reverse=True)[:10]
    
    def get_sector_performance(self) -> List[Dict]:
        """Get US sector ETF performance."""
        now = datetime.now()
        
        # Cache for 60 seconds
        with self.lock:
            if self.sector_cache_time and (now - self.sector_cache_time).seconds < 60:
                return self.sector_cache.get("sectors", [])
        
        sectors = []
        symbols = list(self.SECTOR_ETFS.values())
        
        try:
            data = yf.download(symbols, period="2d", interval="1d", progress=False, threads=True)
            
            for sector_name, symbol in self.SECTOR_ETFS.items():
                try:
                    if symbol in data['Close'].columns:
                        closes = data['Close'][symbol].dropna()
                        if len(closes) >= 2:
                            current = float(closes.iloc[-1])
                            prev = float(closes.iloc[-2])
                            change_pct = ((current - prev) / prev) * 100
                            
                            sectors.append({
                                "sector": sector_name,
                                "symbol": symbol,
                                "price": round(current, 2),
                                "change_pct": round(change_pct, 2),
                                "direction": "up" if change_pct >= 0 else "down"
                            })
                except Exception as e:
                    continue
            
            # Sort by performance
            sectors = sorted(sectors, key=lambda x: x["change_pct"], reverse=True)
            
            with self.lock:
                self.sector_cache["sectors"] = sectors
                self.sector_cache_time = now
                
        except Exception as e:
            print(f"[Bloomberg Engine] Sector Error: {e}")
        
        return sectors
    
    def get_economic_calendar(self, days_ahead: int = 10, impact: Optional[str] = None, 
                             currency: Optional[str] = None) -> List[Dict]:
        """Get upcoming economic events from live data sources.
        
        Args:
            days_ahead: Number of days to look ahead (default: 10)
            impact: Filter by impact level (HIGH, MEDIUM, LOW)
            currency: Filter by currency code (USD, EUR, INR, etc.)
            
        Returns:
            List of upcoming economic events with enriched data
        """
        return self.economic_fetcher.get_events(days_ahead=days_ahead, impact=impact, currency=currency)
    
    def refresh_economic_calendar(self) -> List[Dict]:
        """Force refresh of economic calendar data."""
        return self.economic_fetcher.force_refresh()
    
    def get_calendar_cache_info(self) -> Dict:
        """Get information about economic calendar cache status."""
        return self.economic_fetcher.get_cache_info()
    
    def stop_background_updates(self):
        """Stop background updates for economic calendar."""
        self.economic_fetcher.stop_background_updates()
    
    def get_market_summary(self, market_data: List[Dict]) -> Dict:
        """Get overall market summary stats."""
        if not market_data:
            return {}
        
        gainers = len([s for s in market_data if s.get("change_pct", 0) > 0])
        losers = len([s for s in market_data if s.get("change_pct", 0) < 0])
        unchanged = len(market_data) - gainers - losers
        
        avg_change = sum(s.get("change_pct", 0) for s in market_data) / len(market_data)
        total_volume = sum(s.get("volume", 0) for s in market_data)
        
        return {
            "total_stocks": len(market_data),
            "gainers": gainers,
            "losers": losers,
            "unchanged": unchanged,
            "avg_change": round(avg_change, 2),
            "total_volume": total_volume,
            "market_sentiment": "BULLISH" if gainers > losers else "BEARISH" if losers > gainers else "NEUTRAL"
        }
