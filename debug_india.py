from india_engine import IndiaMarketEngine
import time

print("Initializing Engine...")
engine = IndiaMarketEngine()
print("Fetching Snapshot...")
try:
    data = engine.fetch_market_snapshot()
    print(f"Snapshot Type: {type(data)}")
    print(f"Snapshot Len: {len(data)}")
    if data:
        print(f"Sample: {data[0]}")
    else:
        print("DATA IS EMPTY!")
except Exception as e:
    print(f"EXCEPTION: {e}")
