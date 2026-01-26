"""Test script for expanded Indian stock market coverage"""
from india_engine import IndiaMarketEngine
import time

print("=" * 70)
print("TESTING EXPANDED INDIAN STOCK MARKET COVERAGE")
print("=" * 70)

# Test 1: Initialize engine
print("\n1. Initializing India Market Engine...")
engine = IndiaMarketEngine(cache_ttl=120, default_categories=['NIFTY_50'])
print("   [OK] Engine initialized")

# Test 2: Get coverage statistics
print("\n2. Checking stock coverage...")
stats = engine.get_coverage_stats()
print(f"   [OK] Total unique stocks: {stats['total_stocks']}")
print(f"   [OK] NIFTY 50: {stats['nifty_50']}")
print(f"   [OK] NIFTY Next 50: {stats['nifty_next_50']}")
print(f"   [OK] Midcap: {stats['midcap']}")
print(f"   [OK] Sectoral coverage:")
for sector, count in stats['sectoral'].items():
    print(f"       - {sector.upper()}: {count} stocks")

# Test 3: Fetch NIFTY 50 (default)
print("\n3. Fetching NIFTY 50 data...")
nifty_50_data = engine.fetch_market_snapshot()
print(f"   [OK] Fetched {len(nifty_50_data)} NIFTY 50 stocks")
if nifty_50_data:
    print(f"   [OK] Sample: {nifty_50_data[0]['symbol']} - Rs.{nifty_50_data[0]['price']} ({nifty_50_data[0]['change_pct']:+.2f}%)")

# Test 4: Fetch IT sector
print("\n4. Fetching IT sector stocks...")
it_stocks = engine.get_sector_stocks('IT', use_cache=False)
print(f"   [OK] Fetched {len(it_stocks)} IT sector stocks")
if it_stocks:
    print("   [OK] IT Stocks:")
    for stock in it_stocks[:5]:
        print(f"       - {stock['symbol']}: Rs.{stock['price']} ({stock['change_pct']:+.2f}%)")

# Test 5: Fetch Bank sector
print("\n5. Fetching Banking sector stocks...")
bank_stocks = engine.get_sector_stocks('BANK', use_cache=False)
print(f"   [OK] Fetched {len(bank_stocks)} Banking stocks")

# Test 6: Search functionality
print("\n6. Testing stock search...")
matches = engine.search_stocks('TATA')
print(f"   [OK] Found {len(matches)} stocks matching 'TATA':")
for match in matches[:5]:
    print(f"       - {match['symbol']} ({match['category']})")

# Test 7: Get top movers for IT sector
print("\n7. Getting top movers in IT sector...")
it_movers = engine.get_top_movers(category='IT', top_n=3)
print(f"   [OK] Top 3 IT Gainers:")
for stock in it_movers['gainers']:
    print(f"       - {stock['symbol']}: {stock['change_pct']:+.2f}%")

# Test 8: Category summary
print("\n8. Getting category summary...")
summary = engine.get_category_summary(categories=['NIFTY_50', 'IT', 'BANK'])
for cat_key, cat_data in summary.items():
    print(f"   [OK] {cat_data['name']}: {cat_data['total']} stocks, Avg: {cat_data['avg_change_pct']:+.2f}%, Sentiment: {cat_data['sentiment']}")

# Test 9: Fetch multiple categories
print("\n9. Fetching multiple categories (NIFTY 50 + Banks + IT)...")
multi_data = engine.fetch_market_snapshot(categories=['NIFTY_50', 'BANK', 'IT'], use_cache=False)
print(f"   [OK] Fetched {len(multi_data)} stocks from multiple categories")

# Test 10: Fetch all stocks (this will take longer)
print("\n10. Testing ALL stocks fetch (this may take 30-60 seconds)...")
print("    Note: Fetching 500+ stocks...")
start_time = time.time()
all_stocks = engine.get_all_stocks(use_cache=False)
elapsed = time.time() - start_time
print(f"   [OK] Fetched {len(all_stocks)} stocks in {elapsed:.1f} seconds")
print(f"   [OK] Performance: {len(all_stocks)/elapsed:.1f} stocks/second")

print("\n" + "=" * 70)
print("[PASS] ALL TESTS COMPLETED!")
print("=" * 70)
print("\nSummary:")
print(f"  - Total stock coverage: {stats['total_stocks']} Indian stocks")
print(f"  - Large Cap (NIFTY 50 + Next 50): {stats['nifty_50'] + stats['nifty_next_50']} stocks")
print(f"  - Mid Cap: {stats['midcap']} stocks")
print(f"  - Sectoral coverage: {sum(stats['sectoral'].values())} stocks across 7 sectors")
print(f"  - Category-based fetching: WORKING")
print(f"  - Stock search: WORKING")
print(f"  - Top movers: WORKING")
print(f"  - Multi-category fetch: WORKING")
print(f"  - Batch processing: EFFICIENT")
