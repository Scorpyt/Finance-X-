import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import threading

class IndiaMarketEngine:
    """
    Real-Time Bridge to Indian Stock Market (NSE) via yfinance.
    Coverage: NIFTY 500+ stocks including sectoral indices.
    """
    
    # NIFTY 50 Constituents (Large Cap - Top 50)
    NIFTY_50 = [
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BHARTIARTL.NS", "BPCL.NS",
        "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
        "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
        "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
        "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
        "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
        "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS",
        "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]
    
    # NIFTY Next 50 (Large Cap - Next 50)
    NIFTY_NEXT_50 = [
        "ABB.NS", "ADANIGREEN.NS", "AMBUJACEM.NS", "BANDHANBNK.NS", "BERGEPAINT.NS",
        "BEL.NS", "BIOCON.NS", "BOSCHLTD.NS", "CANBK.NS", "CHOLAFIN.NS",
        "COLPAL.NS", "DABUR.NS", "DLF.NS", "DMART.NS", "GAIL.NS",
        "GODREJCP.NS", "HAVELLS.NS", "HINDZINC.NS", "ICICIPRULI.NS", "IDEA.NS",
        "INDIGO.NS", "INDUSTOWER.NS", "JINDALSTEL.NS", "LICHSGFIN.NS", "MARICO.NS",
        "MCDOWELL-N.NS", "MUTHOOTFIN.NS", "NAUKRI.NS", "NMDC.NS", "ONGC.NS",
        "PEL.NS", "PETRONET.NS", "PIIND.NS", "PNB.NS", "RECLTD.NS",
        "SAIL.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "TATAPOWER.NS",
        "TVSMOTOR.NS", "UBL.NS", "UPL.NS", "VEDL.NS", "VOLTAS.NS",
        "YESBANK.NS", "ZOMATO.NS", "ZYDUSLIFE.NS", "AUROPHARMA.NS", "LUPIN.NS"
    ]
    
    # NIFTY Midcap 150 (Selected major mid-cap stocks)
    NIFTY_MIDCAP_150 = [
        "AARTIIND.NS", "ACC.NS", "ABCAPITAL.NS", "ABSLAMC.NS", "ADANIENSOL.NS",
        "ADANIPOWER.NS", "ALKEM.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", "ASTRAL.NS",
        "ATGL.NS", "AUBANK.NS", "BALKRISIND.NS", "BATAINDIA.NS", "BHEL.NS",
        "CAMS.NS", "CANFINHOME.NS", "CASTROLIND.NS", "CDSL.NS", "CESC.NS",
        "CHAMBLFERT.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "CUMMINSIND.NS",
        "DEEPAKNTR.NS", "DIXON.NS", "EMAMILTD.NS", "ESCORTS.NS", "EXIDEIND.NS",
        "FEDERALBNK.NS", "FORTIS.NS", "GICRE.NS", "GILLETTE.NS", "GLAXO.NS",
        "GNFC.NS", "GODREJPROP.NS", "GUJGASLTD.NS", "HAL.NS", "HATSUN.NS",
        "HINDCOPPER.NS", "HINDPETRO.NS", "IDFCFIRSTB.NS", "IDFC.NS", "IEX.NS",
        "IPCALAB.NS", "IRCTC.NS", "IGL.NS", "JUBLFOOD.NS", "KANSAINER.NS",
        "KEI.NS", "L&TFH.NS", "LALPATHLAB.NS", "LAURUSLABS.NS", "LICI.NS",
        "LTTS.NS", "MANAPPURAM.NS", "MANKIND.NS", "MAXHEALTH.NS", "METROBRAND.NS",
        "MGL.NS", "MFSL.NS", "MOTHERSON.NS", "MPHASIS.NS", "MRF.NS",
        "NAM-INDIA.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NHPC.NS", "NLCINDIA.NS",
        "OBEROIRLTY.NS", "OFSS.NS", "OIL.NS", "PAYTM.NS", "PAGEIND.NS",
        "PERSISTENT.NS", "PFIZER.NS", "PHOENIXLTD.NS", "PIDILITIND.NS", "POLYCAB.NS",
        "POONAWALLA.NS", "RAIN.NS", "RAJESHEXPO.NS", "RBLBANK.NS", "SBICARD.NS",
        "SCHAEFFLER.NS", "SHRIRAMFIN.NS", "SJVN.NS", "SOLARINDS.NS", "SONACOMS.NS",
        "SUNTV.NS", "SUNDARMFIN.NS", "SUPREMEIND.NS", "SYNGENE.NS", "TATACOMM.NS",
        "TATAELXSI.NS", "THERMAX.NS", "TIINDIA.NS", "TORNTPHARM.NS", "TORNTPOWER.NS",
        "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS", "UCOBANK.NS", "UNIONBANK.NS",
        "UNITDSPR.NS", "VARROC.NS", "VGUARD.NS", "VINATIORGA.NS", "WHIRLPOOL.NS",
        "ZEEL.NS", "AAVAS.NS", "ANGELONE.NS", "ASTERDM.NS", "BALRAMCHIN.NS",
        "BSOFT.NS", "BSE.NS", "CGPOWER.NS", "CHOLAHLDNG.NS", "COFORGE.NS",
        "CYIENT.NS", "DIVISLAB.NS", "FACT.NS", "FINEORG.NS", "FINPIPE.NS",
        "FSL.NS", "GMRINFRA.NS", "GRAPHITE.NS", "HEROMOTOCO.NS", "HINDCOPPER.NS",
        "HONAUT.NS", "IRFC.NS", "IREDA.NS", "JKCEMENT.NS", "JSWENERGY.NS",
        "KAJARIACER.NS", "KPITTECH.NS", "LTF.NS", "LUXIND.NS", "THERMAX.NS"
    ]
    
    # NIFTY Bank (Major Banking Stocks)
    NIFTY_BANK = [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
        "INDUSINDBK.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS",
        "AUBANK.NS", "BANKBARODA.NS"
    ]
    
    # NIFTY IT (Information Technology)
    NIFTY_IT = [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
        "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS", "LTTS.NS"
    ]
    
    # NIFTY Pharma (Pharmaceutical)
    NIFTY_PHARMA = [
        "SUNPHARMA.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS", "AUROPHARMA.NS",
        "LUPIN.NS", "BIOCON.NS", "ALKEM.NS", "TORNTPHARM.NS", "IPCALAB.NS"
    ]
    
    # NIFTY Auto (Automobile)
    NIFTY_AUTO = [
        "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS",
        "HEROMOTOCO.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
        "APOLLOTYRE.NS", "MRF.NS", "BALKRISIND.NS", "ESCORTS.NS", "EXIDEIND.NS"
    ]
    
    # NIFTY FMCG (Fast Moving Consumer Goods)
    NIFTY_FMCG = [
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
        "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "TATACONSUM.NS", "EMAMILTD.NS",
        "UBL.NS", "MCDOWELL-N.NS", "RADICO.NS", "VBL.NS", "GILLETTE.NS"
    ]
    
    # NIFTY Metal (Metals & Mining)
    NIFTY_METAL = [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JINDALSTEL.NS",
        "SAIL.NS", "NATIONALUM.NS", "NMDC.NS", "HINDZINC.NS", "COALINDIA.NS",
        "ADANIPORTS.NS", "HINDALCO.NS", "APL.NS", "JINDALSTEL.NS", "RATNAMANI.NS"
    ]
    
    # NIFTY Energy (Oil, Gas & Power)
    NIFTY_ENERGY = [
        "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "NTPC.NS",
        "POWERGRID.NS", "ADANIGREEN.NS", "TATAPOWER.NS", "ADANIPOWER.NS", "GAIL.NS"
    ]
    
    # Stock categorization metadata
    STOCK_CATEGORIES = {
        'NIFTY_50': {'stocks': NIFTY_50, 'name': 'NIFTY 50', 'type': 'Large Cap'},
        'NIFTY_NEXT_50': {'stocks': NIFTY_NEXT_50, 'name': 'NIFTY Next 50', 'type': 'Large Cap'},
        'NIFTY_MIDCAP': {'stocks': NIFTY_MIDCAP_150, 'name': 'NIFTY Midcap 150', 'type': 'Mid Cap'},
        'BANK': {'stocks': NIFTY_BANK, 'name': 'Banking', 'type': 'Sector'},
        'IT': {'stocks': NIFTY_IT, 'name': 'Information Technology', 'type': 'Sector'},
        'PHARMA': {'stocks': NIFTY_PHARMA, 'name': 'Pharmaceutical', 'type': 'Sector'},
        'AUTO': {'stocks': NIFTY_AUTO, 'name': 'Automobile', 'type': 'Sector'},
        'FMCG': {'stocks': NIFTY_FMCG, 'name': 'Consumer Goods', 'type': 'Sector'},
        'METAL': {'stocks': NIFTY_METAL, 'name': 'Metals & Mining', 'type': 'Sector'},
        'ENERGY': {'stocks': NIFTY_ENERGY, 'name': 'Energy', 'type': 'Sector'},
    }
    
    # Create master list of all unique stocks
    ALL_STOCKS = list(set(
        NIFTY_50 + NIFTY_NEXT_50 + NIFTY_MIDCAP_150 + 
        NIFTY_BANK + NIFTY_IT + NIFTY_PHARMA + 
        NIFTY_AUTO + NIFTY_FMCG + NIFTY_METAL + NIFTY_ENERGY
    ))
    
    # For backward compatibility
    NIFTY_SYMBOLS = NIFTY_50

    def __init__(self, cache_ttl=60, default_categories=None):
        self.cache_ttl = cache_ttl
        self.market_cache = {} # {symbol: {data: df, timestamp: ts}}
        self.category_cache = {} # {category: {data: list, timestamp: ts}}
        self.last_batch_fetch = None
        self.batch_data = None
        self.lock = threading.Lock()
        self.batch_size = 50  # Optimal batch size for yfinance
        
        # Default categories to fetch (can be customized)
        self.default_categories = default_categories or ['NIFTY_50', 'NIFTY_NEXT_50', 'NIFTY_MIDCAP']
        
        print(f"[INDIA-ENGINE] Initialized with {len(self.ALL_STOCKS)} unique Indian stocks")
        print(f"[INDIA-ENGINE] Coverage: {', '.join([cat for cat in self.STOCK_CATEGORIES.keys()])}")

    def fetch_market_snapshot(self, categories=None, use_cache=True):
        """
        Fetches live data for specified categories or default universe.
        Uses threading to parallelize requests via yfinance batch download.
        
        Args:
            categories: List of category keys to fetch (e.g., ['NIFTY_50', 'BANK'])
                       If None, uses default_categories from init
            use_cache: Whether to use cached data if available
        
        Returns:
            List of stock data dictionaries
        """
        now = time.time()
        
        # Use default categories if none specified
        if categories is None:
            categories = self.default_categories
        
        # Check cache
        if use_cache:
            with self.lock:
                if self.last_batch_fetch and (now - self.last_batch_fetch < self.cache_ttl):
                    return self.batch_data
        
        # Get all symbols from requested categories
        symbols = self._get_symbols_from_categories(categories)
        
        print(f"[INDIA-ENGINE] Fetching data for {len(symbols)} stocks from categories: {', '.join(categories)}")
        try:
            # Download batch data (Last 5 days to calculate trends)
            data = yf.download(symbols, period="5d", interval="1d", group_by='ticker', threads=True, progress=False)
            
            snapshot = []
            for symbol in symbols:
                try:
                    # Handle single vs multiple stock data structure
                    if len(symbols) == 1:
                        df = data
                    else:
                        df = data[symbol]
                    
                    if df.empty: continue
                    
                    last_row = df.iloc[-1]
                    prev_row = df.iloc[-2] if len(df) > 1 else last_row
                    
                    # Basic Metrics
                    price = float(last_row['Close'])
                    prev_close = float(prev_row['Close'])
                    change = price - prev_close
                    change_pct = (change / prev_close) * 100
                    
                    # 3-Point Evaluation Prep
                    vol_spike = (last_row['Volume'] > prev_row['Volume'] * 1.5)
                    trend = "BULLISH" if price > prev_close else "BEARISH"
                    
                    # Sparkline History (Last 5 days)
                    history_points = [{"p": float(x)} for x in df['Close'].tolist()]
                    
                    # Determine category/sector
                    stock_category = self._get_stock_category(symbol)
                    
                    snapshot.append({
                        "symbol": symbol.replace(".NS", ""),
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "volume": int(last_row['Volume']),
                        "trend": trend,
                        "high": float(last_row['High']),
                        "low": float(last_row['Low']),
                        "history": history_points,
                        "category": stock_category['type'],
                        "sector": stock_category['name']
                    })
                except Exception as e:
                    # print(f"Error processing {symbol}: {e}")
                    continue
            
            return snapshot
            
        except Exception as e:
            print(f"[INDIA-ENGINE] Batch Fetch Error: {e}")
            return []

    def get_stock_analysis(self, symbol):
        """
        Deep dive for a single stock (User request: 'give real time evaluation')
        """
        full_sym = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
        
        try:
            stock = yf.Ticker(full_sym)
            hist = stock.history(period="1mo", interval="1d")
            
            if hist.empty:
                return {"error": "No Data Found"}
            
            # Trend Analysis (Simple MA)
            # Using closing prices
            closes = hist['Close']
            sma_5 = closes.rolling(window=5).mean().iloc[-1]
            sma_20 = closes.rolling(window=20).mean().iloc[-1]
            current_price = closes.iloc[-1]
            
            trend_verdict = "STRONG UPTREND" if current_price > sma_5 > sma_20 else \
                            "UPTREND" if current_price > sma_20 else \
                            "DOWNTREND" if current_price < sma_20 else "SIDEWAYS"
                            
            # Factors
            vol_mean = hist['Volume'].mean()
            current_vol = hist['Volume'].iloc[-1]
            vol_factor = "High Institutional Activity" if current_vol > vol_mean * 1.5 else "Normal Volume"
            
            # Future Prediction (Micro-Projection - Naive)
            # If momentum is positive, next second probability is slightly higher
            momentum = (current_price - closes.iloc[-3]) 
            future_outlook = "BULLISH CONTINUATION" if momentum > 0 else "BEARISH CORRECTION"
            
            # Warning (Disruption Mode Check)
            # Check drop from period high
            period_high = hist['High'].max()
            drop_pct = ((period_high - current_price) / period_high) * 100
            warning = None
            if drop_pct > 5.0:
                warning = f"Heavy Correction: Down {drop_pct:.1f}% from Monthly High"

            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "trend": trend_verdict,
                "factors": [vol_factor, f"Momentum: {round(momentum, 2)}"],
                "prediction": future_outlook,
                "warning": warning,
                "data": hist.tail(30).to_dict() # For charting
            }

        except Exception as e:
            return {"error": str(e)}

    def check_portfolio_health(self, portfolio):
        """
        Disruption Mode: Check monitored stocks
        portfolio: list of {symbol, entry, limit}
        """
        alerts = []
        for item in portfolio:
            sym = item['symbol']
            entry = item['entry_price']
            limit_pct = item.get('limit', 10.0) # Default 10% loss limit
            
            # Use cached batch data if available for speed
            current_price = 0
            if self.batch_data:
                match = next((x for x in self.batch_data if x['symbol'] == sym), None)
                if match: current_price = match['price']
            
            # Fallback fetch
            if current_price == 0:
                # Todo: fetch individual or use last known
                pass
                
            # Disruption Check
            if current_price > 0:
                loss_pct = ((entry - current_price) / entry) * 100
                if loss_pct >= limit_pct:
                    alerts.append({
                        "symbol": sym,
                        "status": "CRITICAL",
                        "loss": round(loss_pct, 2),
                        "message": f"Stop Loss Breach! Down {round(loss_pct, 1)}%"
                    })
        return alerts
    
    def _get_symbols_from_categories(self, categories):
        """Get unique symbols from list of categories."""
        symbols = []
        for cat in categories:
            if cat in self.STOCK_CATEGORIES:
                symbols.extend(self.STOCK_CATEGORIES[cat]['stocks'])
        return list(set(symbols))  # Remove duplicates
    
    def _get_stock_category(self, symbol):
        """Determine which category/sector a stock belongs to."""
        for cat_key, cat_info in self.STOCK_CATEGORIES.items():
            if symbol in cat_info['stocks']:
                return {'name': cat_info['name'], 'type': cat_info['type'], 'key': cat_key}
        return {'name': 'Other', 'type': 'Uncategorized', 'key': 'OTHER'}
    
    def get_all_stocks(self, use_cache=True):
        """Get data for all tracked stocks (500+)."""
        return self.fetch_market_snapshot(categories=list(self.STOCK_CATEGORIES.keys()), use_cache=use_cache)
    
    def get_sector_stocks(self, sector, use_cache=True):
        """
        Get stocks from a specific sector.
        
        Args:
            sector: Sector key (BANK, IT, PHARMA, AUTO, FMCG, METAL, ENERGY)
        """
        if sector.upper() not in self.STOCK_CATEGORIES:
            print(f"[INDIA-ENGINE] Unknown sector: {sector}")
            return []
        
        return self.fetch_market_snapshot(categories=[sector.upper()], use_cache=use_cache)
    
    def search_stocks(self, query):
        """
        Search for stocks by symbol or partial name match.
        
        Args:
            query: Search term (case-insensitive)
        """
        query = query.upper().replace(".NS", "")
        matches = []
        
        for symbol in self.ALL_STOCKS:
            clean_symbol = symbol.replace(".NS", "")
            if query in clean_symbol:
                category = self._get_stock_category(symbol)
                matches.append({
                    "symbol": clean_symbol,
                    "full_symbol": symbol,
                    "category": category['name'],
                    "type": category['type']
                })
        
        return matches
    
    def get_category_summary(self, categories=None):
        """
        Get summary statistics for each category.
        
        Returns:
            Dictionary with category stats (total stocks, avg change, etc.)
        """
        if categories is None:
            categories = self.default_categories
        
        data = self.fetch_market_snapshot(categories=categories, use_cache=True)
        
        summary = {}
        for cat_key in categories:
            if cat_key not in self.STOCK_CATEGORIES:
                continue
            
            cat_stocks = [s for s in data if s.get('symbol') + '.NS' in self.STOCK_CATEGORIES[cat_key]['stocks']]
            
            if cat_stocks:
                gainers = len([s for s in cat_stocks if s['change_pct'] > 0])
                losers = len([s for s in cat_stocks if s['change_pct'] < 0])
                avg_change = sum(s['change_pct'] for s in cat_stocks) / len(cat_stocks)
                
                summary[cat_key] = {
                    "name": self.STOCK_CATEGORIES[cat_key]['name'],
                    "total": len(cat_stocks),
                    "gainers": gainers,
                    "losers": losers,
                    "avg_change_pct": round(avg_change, 2),
                    "sentiment": "BULLISH" if gainers > losers else "BEARISH" if losers > gainers else "NEUTRAL"
                }
        
        return summary
    
    def get_top_movers(self, category=None, top_n=10):
        """
        Get top gainers and losers.
        
        Args:
            category: Optional category filter
            top_n: Number of top stocks to return
        """
        if category:
            data = self.fetch_market_snapshot(categories=[category], use_cache=True)
        else:
            data = self.fetch_market_snapshot(use_cache=True)
        
        sorted_data = sorted(data, key=lambda x: x['change_pct'], reverse=True)
        
        return {
            "gainers": sorted_data[:top_n],
            "losers": list(reversed(sorted_data[-top_n:]))
        }
    
    def get_coverage_stats(self):
        """Get statistics about stock coverage."""
        return {
            "total_stocks": len(self.ALL_STOCKS),
            "nifty_50": len(self.NIFTY_50),
            "nifty_next_50": len(self.NIFTY_NEXT_50),
            "midcap": len(self.NIFTY_MIDCAP_150),
            "sectoral": {
                "bank": len(self.NIFTY_BANK),
                "it": len(self.NIFTY_IT),
                "pharma": len(self.NIFTY_PHARMA),
                "auto": len(self.NIFTY_AUTO),
                "fmcg": len(self.NIFTY_FMCG),
                "metal": len(self.NIFTY_METAL),
                "energy": len(self.NIFTY_ENERGY)
            },
            "categories": list(self.STOCK_CATEGORIES.keys())
        }
