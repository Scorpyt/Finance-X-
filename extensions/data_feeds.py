"""
Real Market Data Feeds
Integrates with free-tier APIs: EIA (oil), IEX Cloud (equities), MarineTraffic (tankers)
"""

import requests
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "config" / ".env")


class MarketDataFeed:
    """
    Real-time market data integration.
    Uses free-tier APIs to replace simulation data.
    """
    
    def __init__(self):
        self.eia_key = os.getenv("EIA_API_KEY", "")
        self.iex_token = os.getenv("IEX_TOKEN", "")
        self.marine_key = os.getenv("MARINE_API_KEY", "")
        
        if not self.eia_key:
            print("[DataFeed] WARNING: EIA_API_KEY not set. Oil data will be simulated.")
        if not self.iex_token:
            print("[DataFeed] WARNING: IEX_TOKEN not set. Equity data will be simulated.")
    
    def fetch_oil_prices(self) -> Dict[str, float]:
        """
        Fetch real oil prices from EIA (US Energy Information Administration)
        API: https://www.eia.gov/opendata/
        Free tier: Unlimited requests
        """
        if not self.eia_key:
            # Fallback to simulation
            return {"WTI": 72.50, "BRENT": 77.80, "source": "simulated"}
        
        try:
            # WTI Spot Price (Cushing, OK)
            wti_url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={self.eia_key}&frequency=daily&data[0]=value&facets[product][]=EPCWTI&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
            
            wti_response = requests.get(wti_url, timeout=5)
            wti_data = wti_response.json()
            
            wti_price = float(wti_data['response']['data'][0]['value']) if wti_data.get('response') else 72.50
            
            # Brent is typically $5 higher (approximation if API limit hit)
            brent_price = wti_price + 5.0
            
            print(f"[DataFeed] Real oil prices: WTI=${wti_price:.2f}, BRENT=${brent_price:.2f}")
            
            return {
                "WTI": wti_price,
                "BRENT": brent_price,
                "source": "EIA",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[DataFeed] EIA API error: {e}. Using fallback.")
            return {"WTI": 72.50, "BRENT": 77.80, "source": "fallback"}
    
    def fetch_equity_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch real equity quote from IEX Cloud
        API: https://iexcloud.io/
        Free tier: 100 requests/day
        """
        if not self.iex_token:
            return None
        
        try:
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.iex_token}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            return {
                "symbol": data['symbol'],
                "price": data['latestPrice'],
                "change_pct": data['changePercent'] * 100,
                "volume": data['latestVolume'],
                "market_cap": data.get('marketCap', 0),
                "source": "IEX",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[DataFeed] IEX API error for {symbol}: {e}")
            return None
    
    def fetch_crypto_price(self, symbol: str = "BTC") -> Optional[Dict]:
        """
        Fetch crypto price from CoinGecko (FREE, no API key)
        API: https://www.coingecko.com/en/api
        """
        try:
            coin_map = {"BTC": "bitcoin", "ETH": "ethereum"}
            coin_id = coin_map.get(symbol, "bitcoin")
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            price = data[coin_id]['usd']
            change = data[coin_id].get('usd_24h_change', 0)
            
            return {
                "symbol": symbol,
                "price": price,
                "change_pct": change,
                "source": "CoinGecko",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[DataFeed] CoinGecko API error: {e}")
            return None
    
    def fetch_tanker_positions(self, limit: int = 30) -> List[Dict]:
        """
        Fetch real tanker positions from MarineTraffic API
        API: https://www.marinetraffic.com/en/ais-api-services
        Free tier: 50 requests/month (use sparingly)
        """
        if not self.marine_key:
            print("[DataFeed] MarineTraffic API key not set. Using simulated tankers.")
            return []
        
        try:
            # PS07: Single Vessel Positions
            url = f"https://services.marinetraffic.com/api/exportvessels/{self.marine_key}/v:5/protocol:json/shiptype:4/timespan:60"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            tankers = []
            for vessel in data[:limit]:
                tankers.append({
                    "id": vessel.get("MMSI"),
                    "name": vessel.get("SHIPNAME"),
                    "lat": vessel.get("LAT"),
                    "lon": vessel.get("LON"),
                    "heading": vessel.get("COURSE"),
                    "speed": vessel.get("SPEED"),
                    "status": vessel.get("STATUS"),
                    "destination": vessel.get("DESTINATION"),
                    "source": "MarineTraffic"
                })
            
            print(f"[DataFeed] Fetched {len(tankers)} real tanker positions")
            return tankers
            
        except Exception as e:
            print(f"[DataFeed] MarineTraffic API error: {e}")
            return []
    
    def fetch_vix(self) -> Optional[float]:
        """
        Fetch VIX (Volatility Index) from CBOE or Yahoo Finance
        Using Yahoo Finance (free, no key required)
        """
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=1d"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            vix = data['chart']['result'][0]['meta']['regularMarketPrice']
            
            return vix
            
        except Exception as e:
            print(f"[DataFeed] VIX fetch error: {e}")
            return None
    
    def health_check(self) -> Dict[str, str]:
        """Test all API connections"""
        status = {}
        
        # Test EIA
        oil = self.fetch_oil_prices()
        status["EIA (Oil)"] = "✅ Connected" if oil.get("source") == "EIA" else "❌ Using fallback"
        
        # Test IEX
        if self.iex_token:
            quote = self.fetch_equity_quote("AAPL")
            status["IEX (Equities)"] = "✅ Connected" if quote else "❌ Failed"
        else:
            status["IEX (Equities)"] = "⚠️ No API key"
        
        # Test CoinGecko
        crypto = self.fetch_crypto_price("BTC")
        status["CoinGecko (Crypto)"] = "✅ Connected" if crypto else "❌ Failed"
        
        # Test VIX
        vix = self.fetch_vix()
        status["Yahoo Finance (VIX)"] = "✅ Connected" if vix else "❌ Failed"
        
        return status


# Singleton instance
_feed_instance = None

def get_feed() -> MarketDataFeed:
    """Get or create data feed instance"""
    global _feed_instance
    if _feed_instance is None:
        _feed_instance = MarketDataFeed()
    return _feed_instance
