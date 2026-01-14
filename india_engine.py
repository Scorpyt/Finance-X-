import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import threading

class IndiaMarketEngine:
    """
    Real-Time Bridge to Indian Stock Market (NSE) via yfinance.
    Focus: NIFTY 50 Universe.
    """
    
    # NIFTY 50 Constituents
    NIFTY_SYMBOLS = [
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

    def __init__(self, cache_ttl=60):
        self.cache_ttl = cache_ttl
        self.market_cache = {} # {symbol: {data: df, timestamp: ts}}
        self.last_batch_fetch = None
        self.batch_data = None
        self.lock = threading.Lock()

    def fetch_market_snapshot(self):
        """
        Fetches live data for the entire tracked universe.
        Uses threading to parallelize requests via yfinance batch download.
        """
        now = time.time()
        with self.lock:
            if self.last_batch_fetch and (now - self.last_batch_fetch < self.cache_ttl):
                return self.batch_data

        print(f"[INDIA-ENGINE] Fetching Live NIFTY Data for {len(self.NIFTY_SYMBOLS)} symbols...")
        try:
            # Download batch data (Last 5 days to calculate trends)
            data = yf.download(self.NIFTY_SYMBOLS, period="5d", interval="1d", group_by='ticker', threads=True, progress=False)
            
            snapshot = []
            for symbol in self.NIFTY_SYMBOLS:
                try:
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
                    
                    snapshot.append({
                        "symbol": symbol.replace(".NS", ""),
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "volume": int(last_row['Volume']),
                        "trend": trend,
                        "high": float(last_row['High']),
                        "low": float(last_row['Low']),
                        "history": history_points
                    })
                except Exception as e:
                    # print(f"Error processing {symbol}: {e}")
                    continue
            
            with self.lock:
                self.batch_data = snapshot
                self.last_batch_fetch = now
            
            return snapshot
            
        except Exception as e:
            print(f"[INDIA-ENGINE] Critical Fetch Error: {e}")
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
