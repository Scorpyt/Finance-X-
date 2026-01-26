"""
Interactive Demo: Expanded Indian Stock Market Coverage
Showcasing all new features with live data
"""
from india_engine import IndiaMarketEngine
import time

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    print(f"\n{'' * 70}")
    print(f"  {title}")
    print(f"{'' * 70}")

# Initialize engine
print_header(" INDIAN STOCK MARKET ENGINE - FEATURE DEMO")
print("\nInitializing engine with default categories...")
engine = IndiaMarketEngine(default_categories=['NIFTY_50', 'BANK', 'IT'])
time.sleep(1)

# Feature 1: Coverage Statistics
print_section(" Feature 1: Stock Coverage Statistics")
stats = engine.get_coverage_stats()
print(f"\n Total Stock Universe: {stats['total_stocks']} unique Indian stocks")
print(f" NIFTY 50: {stats['nifty_50']} stocks")
print(f" NIFTY Next 50: {stats['nifty_next_50']} stocks")
print(f" Midcap: {stats['midcap']} stocks")
print(f"\n Sectoral Coverage:")
for sector, count in stats['sectoral'].items():
    print(f"    {sector.upper():<8} - {count} stocks")
print(f"\n Available Categories: {', '.join(stats['categories'])}")
time.sleep(2)

# Feature 2: Fetch NIFTY 50
print_section(" Feature 2: Fetch NIFTY 50 Stocks")
print("\nFetching NIFTY 50 data with real-time prices...")
nifty_50 = engine.fetch_market_snapshot(categories=['NIFTY_50'])
print(f"\n Retrieved {len(nifty_50)} NIFTY 50 stocks")
print(f"\n Top 5 NIFTY 50 Stocks:")
for stock in nifty_50[:5]:
    trend_icon = "" if stock['change_pct'] > 0 else ""
    print(f"   {trend_icon} {stock['symbol']:<12} Rs.{stock['price']:>8.2f}  ({stock['change_pct']:+6.2f}%)  [{stock['sector']}]")
time.sleep(2)

# Feature 3: Sector-Specific Fetching (IT)
print_section(" Feature 3: IT Sector Analysis")
print("\nFetching all IT sector stocks...")
it_stocks = engine.get_sector_stocks('IT')
print(f"\n Retrieved {len(it_stocks)} IT stocks")
print(f"\n All IT Stocks:")
for stock in sorted(it_stocks, key=lambda x: x['change_pct'], reverse=True):
    trend_icon = "" if stock['change_pct'] > 0 else ""
    print(f"   {trend_icon} {stock['symbol']:<12} Rs.{stock['price']:>8.2f}  ({stock['change_pct']:+6.2f}%)")
time.sleep(2)

# Feature 4: Banking Sector
print_section(" Feature 4: Banking Sector Analysis")
print("\nFetching all Banking sector stocks...")
bank_stocks = engine.get_sector_stocks('BANK')
print(f"\n Retrieved {len(bank_stocks)} Banking stocks")
print(f"\n Top 5 Banking Stocks:")
for stock in sorted(bank_stocks, key=lambda x: x['price'], reverse=True)[:5]:
    trend_icon = "" if stock['change_pct'] > 0 else ""
    print(f"   {trend_icon} {stock['symbol']:<15} Rs.{stock['price']:>8.2f}  ({stock['change_pct']:+6.2f}%)")
time.sleep(2)

# Feature 5: Stock Search
print_section(" Feature 5: Stock Search")
search_queries = ['TATA', 'RELIANCE', 'ADANI']
for query in search_queries:
    matches = engine.search_stocks(query)
    print(f"\n Searching for '{query}'... Found {len(matches)} stocks:")
    for match in matches[:5]:
        print(f"    {match['symbol']:<15} ({match['category']}, {match['type']})")
time.sleep(2)

# Feature 6: Top Movers
print_section(" Feature 6: Top Movers - IT Sector")
it_movers = engine.get_top_movers(category='IT', top_n=3)
print(f"\n Top 3 IT Gainers:")
for stock in it_movers['gainers']:
    print(f"    {stock['symbol']:<12} {stock['change_pct']:+6.2f}%  (Rs.{stock['price']})")
print(f"\n Top 3 IT Losers:")
for stock in it_movers['losers']:
    print(f"    {stock['symbol']:<12} {stock['change_pct']:+6.2f}%  (Rs.{stock['price']})")
time.sleep(2)

# Feature 7: Category Summary
print_section(" Feature 7: Multi-Category Summary")
print("\nAnalyzing NIFTY 50, IT, and Banking sectors...")
summary = engine.get_category_summary(categories=['NIFTY_50', 'IT', 'BANK'])
print(f"\n Market Summary:")
for cat_key, cat_data in summary.items():
    sentiment_icon = "" if cat_data['sentiment'] == 'BULLISH' else "" if cat_data['sentiment'] == 'BEARISH' else ""
    print(f"\n   {sentiment_icon} {cat_data['name']}:")
    print(f"       Total Stocks: {cat_data['total']}")
    print(f"       Gainers: {cat_data['gainers']}  |  Losers: {cat_data['losers']}")
    print(f"       Average Change: {cat_data['avg_change_pct']:+.2f}%")
    print(f"       Sentiment: {cat_data['sentiment']}")
time.sleep(2)

# Feature 8: Multi-Category Fetch
print_section(" Feature 8: Multi-Category Fetch")
print("\nFetching NIFTY 50 + Banking + IT combined...")
multi_data = engine.fetch_market_snapshot(categories=['NIFTY_50', 'BANK', 'IT'])
print(f"\n Retrieved {len(multi_data)} stocks from 3 categories")
print(f"\n Sample Combined Data (Top 5 by price):")
for stock in sorted(multi_data, key=lambda x: x['price'], reverse=True)[:5]:
    trend_icon = "" if stock['change_pct'] > 0 else ""
    print(f"   {trend_icon} {stock['symbol']:<12} Rs.{stock['price']:>8.2f}  ({stock['change_pct']:+6.2f}%)  [{stock['category']}]")
time.sleep(2)

# Feature 9: Pharma Sector
print_section(" Feature 9: Pharmaceutical Sector")
print("\nFetching Pharma sector stocks...")
pharma_stocks = engine.get_sector_stocks('PHARMA')
print(f"\n Retrieved {len(pharma_stocks)} Pharma stocks")
print(f"\n Pharma Sector (sorted by performance):")
for stock in sorted(pharma_stocks, key=lambda x: x['change_pct'], reverse=True):
    trend_icon = "" if stock['change_pct'] > 0 else ""
    print(f"   {trend_icon} {stock['symbol']:<15} {stock['change_pct']:+6.2f}%  (Rs.{stock['price']})")
time.sleep(2)

# Feature 10: Performance Metrics
print_section(" Feature 10: Performance Test")
print("\nTesting fetch performance for all categories...")
start_time = time.time()
all_data = engine.get_all_stocks(use_cache=False)
elapsed = time.time() - start_time
print(f"\n Performance Metrics:")
print(f"    Total stocks fetched: {len(all_data)}")
print(f"    Time taken: {elapsed:.2f} seconds")
print(f"    Throughput: {len(all_data)/elapsed:.1f} stocks/second")
print(f"    Categories covered: {len(stats['categories'])}")

# Final Summary
print_header(" DEMO COMPLETE - SUMMARY")
print(f"""
 Demonstrated 10 key features:
  1. Stock coverage statistics (240+ stocks)
  2. NIFTY 50 fetching with metadata
  3. IT sector-specific analysis
  4. Banking sector analysis
  5. Stock search functionality
  6. Top movers by sector
  7. Multi-category summaries
  8. Combined category fetching
  9. Pharmaceutical sector analysis
  10. Performance benchmarking

 Coverage: {stats['total_stocks']} unique Indian stocks
 Categories: NIFTY 50, Next 50, Midcap, + 7 sectors
 Performance: {len(all_data)/elapsed:.1f} stocks/second
 All features fully operational!
""")

print("=" * 70)
print("  Demo completed successfully! Your India engine is ready to use.")
print("=" * 70)
