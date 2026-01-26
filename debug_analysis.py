"""
Debug script for Finance-X Analysis Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_command(cmd):
    print(f"\n>> Testing Command: {cmd}")
    try:
        response = requests.post(f"{BASE_URL}/command", json={"command": cmd})
        if response.status_code == 200:
            data = response.json()
            if data.get("type") == "ERROR":
                print(f"[FAIL] (App Error): {data.get('content')}")
            else:
                print(f"[SUCCESS]: Type={data.get('type')}")
        else:
            print(f"[FAIL] (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[FAIL] (Exception): {str(e)}")

print("Starting Analysis Debug...")

# Test 1: Volatility Analysis
test_command("VOL TCS")

# Test 2: Heatmap
test_command("HEATMAP SECTOR")

# Test 3: Correlation
test_command("CORR")

# Test 4: AI Advisor
test_command("ADVISE SPX")

# Test 5: Volatility Scanner
test_command("VOLSCAN")
