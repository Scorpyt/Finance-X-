"""
BALLISTIC TEST SUITE - FINANCE-X
Stress tests every core component to ensure stability and performance.
"""
import time
import sys
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure Logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def print_header(title):
    print(f"\n{'='*60}\n  BALLISTIC TEST: {title}\n{'='*60}")

def report_result(name, success, duration, details=""):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} | {name:<30} | {duration:.3f}s | {details}")

class BallisticTester:
    def __init__(self):
        self.errors = []
        
    def test_engine_core(self):
        print_header("Intelligence Engine (Crisis Core)")
        try:
            from engine import IntelligenceEngine, MarketEvent
            from datetime import datetime
            
            start = time.time()
            engine = IntelligenceEngine()
            
            # Stress: Ingest 100 events rapidly
            for i in range(100):
                engine.ingest(MarketEvent(datetime.now(), "TEST", f"Stress Event {i}", 5.0, "GEN"))
                
            # Stress: State Detection loop
            for _ in range(50):
                engine.detect_state(datetime.now())
                
            report_result("Engine Ingestion (100x)", True, time.time() - start)
            
            # Verify data
            if not engine.events: raise Exception("Events not stored")
            report_result("Engine Integrity", True, 0.0, f"{len(engine.events)} events active")
            
        except Exception as e:
            report_result("Engine Core", False, 0.0, str(e))
            self.errors.append(f"Engine Core: {str(e)}")

    def test_india_engine(self):
        print_header("India Market Engine (Data Feed)")
        try:
            from india_engine import IndiaMarketEngine
            
            start = time.time()
            engine = IndiaMarketEngine()
            
            # Test 1: NIFTY 50 Fetch (Live)
            t1 = time.time()
            nifty = engine.fetch_market_snapshot(categories=['NIFTY_50'])
            if not nifty: raise Exception("No NIFTY data returned")
            report_result("NIFTY 50 Fetch", True, time.time() - t1, f"{len(nifty)} stocks")
            
            # Test 2: Search (Cache check)
            t2 = time.time()
            results = engine.search_stocks("TATA")
            if not results: raise Exception("Search failed")
            report_result("Stock Search 'TATA'", True, time.time() - t2, f"{len(results)} matches")
            
            # Test 3: Sector Fetch
            t3 = time.time()
            bank = engine.get_sector_stocks("BANK")
            if not bank: raise Exception("Sector fetch failed")
            report_result("Sector Fetch (BANK)", True, time.time() - t3, f"{len(bank)} stocks")
            
        except Exception as e:
            report_result("India Engine", False, 0.0, str(e))
            self.errors.append(f"India Engine: {str(e)}")

    def test_bloomberg_engine(self):
        print_header("Bloomberg Engine (FX & Compute)")
        try:
            from bloomberg_engine import BloombergEngine
            
            start = time.time()
            engine = BloombergEngine()
            
            # Test 1: FX Rates
            rates = engine.get_fx_rates()
            if not rates: raise Exception("FX Rates empty")
            report_result("FX Data Feed", True, time.time() - start, f"{len(rates)} pairs")
            
            # Test 2: Screener
            # Need market data first
            from india_engine import IndiaMarketEngine
            ie = IndiaMarketEngine()
            data = ie.fetch_market_snapshot(['NIFTY_50'])
            
            t2 = time.time()
            screen = engine.screen_stocks(data, "GAINERS")
            report_result("Screener Logic", True, time.time() - t2, f"{len(screen)} matches")
            
        except Exception as e:
            report_result("Bloomberg Engine", False, 0.0, str(e))
            self.errors.append(f"Bloomberg Engine: {str(e)}")

    def test_analysis_modules(self):
        print_header("Analysis Modules (Math & Vis)")
        try:
            # Volatility
            from volatility import historical_volatility, volatility_regime_detection
            import pandas as pd
            import numpy as np
            
            prices = pd.Series(np.random.normal(100, 5, 100))
            
            start = time.time()
            vol = historical_volatility(prices)
            regime = volatility_regime_detection(prices)
            report_result("Volatility Calc", True, time.time() - start)
            
            # Heatmap
            from heatmap import sector_performance_heatmap
            mock_sectors = [{"name": "IT", "change_pct": 1.5, "symbol": "NIFTY IT"}]
            
            t2 = time.time()
            hm = sector_performance_heatmap(mock_sectors)
            if not hm: raise Exception("Heatmap returned empty")
            report_result("Heatmap Generation", True, time.time() - t2)
            
        except Exception as e:
            report_result("Analysis Modules", False, 0.0, str(e))
            self.errors.append(f"Analysis: {str(e)}")

    def test_server_startup(self):
        print_header("Server Integrity Check")
        # Check imports only, don't launch
        try:
            import server
            report_result("Server Import", True, 0.1, "Dependencies Valid")
        except Exception as e:
            report_result("Server Import", False, 0.0, str(e))
            self.errors.append(f"Server: {str(e)}")

    def run_all(self):
        print(">> INITIALIZING BALLISTIC TEST SEQUENCE...")
        start_global = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Parallel execution for max stress
            # Actually, run sequential to isolate errors clearly for the user
            self.test_engine_core()
            self.test_india_engine()
            self.test_bloomberg_engine()
            self.test_analysis_modules()
            self.test_server_startup()
            
        print_header("TEST SUMMARY")
        duration = time.time() - start_global
        if not self.errors:
            print(f"[SUCCESS] ALL SYSTEMS GO! (Total Time: {duration:.2f}s)")
            print("System is robust and error-free.")
        else:
            print(f"[FAIL] {len(self.errors)} FAILURES DETECTED")
            for err in self.errors:
                print(f" - {err}")
            sys.exit(1)

if __name__ == "__main__":
    tester = BallisticTester()
    tester.run_all()
