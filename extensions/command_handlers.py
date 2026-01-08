"""
Enhanced command handlers with route data for tanker map
"""

import random
from typing import Dict, List, Tuple
from models import GeoPoint

def enhance_tankers_command(engine) -> Dict:
    """
    Enhanced TANKERS command with trade route data.
    Returns detailed shipping information with route waypoints.
    """
    metrics = engine.tanker_sim.get_supply_metrics()
    
    # Major ports with coordinates
    ports = {
        "HOUSTON": GeoPoint(29.76, -95.36),
        "ROTTERDAM": GeoPoint(51.92, 4.48),
        "SINGAPORE": GeoPoint(1.35, 103.82),
        "FUJAIRAH": GeoPoint(25.12, 56.33),
        "QINGDAO": GeoPoint(36.07, 120.38),
        "SANTOS": GeoPoint(-23.96, -46.33),
        "RAS_TANURA": GeoPoint(26.65, 50.17)
    }
    
    # Country mapping
    port_countries = {
        "HOUSTON": ("USA", "🇺🇸"),
        "ROTTERDAM": ("Netherlands", "🇳🇱"),
        "SINGAPORE": ("Singapore", "🇸🇬"),
        "FUJAIRAH": ("UAE", "🇦🇪"),
        "QINGDAO": ("China", "🇨🇳"),
        "SANTOS": ("Brazil", "🇧🇷"),
        "RAS_TANURA": ("Saudi Arabia", "🇸🇦")
    }
    
    cargo_types = ["CRUDE_OIL", "REFINED", "LNG", "DIESEL"]
    cargo_grades = ["WTI", "BRENT", "DUBAI", "URALS", "MAYA"]
    vessel_types = ["VLCC", "Suezmax", "Aframax", "Panamax"]
    
    enhanced_assets = []
    
    for i, t in enumerate(engine.tanker_sim.tankers):
        # Determine origin and destination
        origin_port = list(ports.keys())[i % len(ports)]
        dest_port = t.destination
        
        origin_country, origin_flag = port_countries.get(origin_port, ("Unknown", "🏴"))
        dest_country, dest_flag = port_countries.get(dest_port, ("Unknown", "🏴"))
        
        # Assign cargo based on route
        if "HOUSTON" in [origin_port, dest_port]:
            cargo = "WTI"
        elif "RAS_TANURA" in [origin_port, dest_port] or "FUJAIRAH" in [origin_port, dest_port]:
            cargo = "DUBAI"
        elif "ROTTERDAM" in [origin_port, dest_port]:
            cargo = "BRENT"
        else:
            cargo = random.choice(cargo_grades)
        
        # Get port coordinates
        origin_coords = ports.get(origin_port, GeoPoint(0, 0))
        dest_coords = ports.get(dest_port, GeoPoint(0, 0))
        
        enhanced_assets.append({
            "id": t.id,
            "name": t.name,
            "lat": t.location.lat,
            "lon": t.location.lon,
            "status": t.status,
            "dest": dest_port,
            "heading": t.heading,
            
            # RICH METADATA
            "cargo_type": "CRUDE_OIL" if cargo in ["WTI", "BRENT", "DUBAI", "URALS"] else random.choice(cargo_types),
            "cargo_grade": cargo,
            "cargo_level": round(t.cargo_level, 1),
            "origin_port": origin_port,
            "origin_country": origin_country,
            "origin_flag": origin_flag,
            "destination_country": dest_country,
            "destination_flag": dest_flag,
            "vessel_type": random.choice(vessel_types),
            "dwt": random.choice([300000, 250000, 150000, 100000]),
            "speed_knots": round(random.uniform(10, 15), 1) if t.status == "MOVING" else 0.0,
            "eta_hours": random.randint(24, 168) if t.status == "MOVING" else 0,
            
            # ROUTE DATA
            "origin_lat": origin_coords.lat,
            "origin_lon": origin_coords.lon,
            "dest_lat": dest_coords.lat,
            "dest_lon": dest_coords.lon,
            "route_color": "red"
        })
    
    return {
        "type": "MAP_DATA",
        "map_mode": "TANKER",
        "title": f"Global Asset Tracking ({metrics['total_ships']} Vessels)",
        "metrics": f"VOL AT SEA: {int(metrics['volume_index'])} | ACTIVE: {int(metrics['moving_ratio']*100)}%",
        "assets": enhanced_assets
    }


def get_market_map_data() -> Dict:
    """
    Generate market sentiment map data with country cards.
    """
    from datetime import datetime
    import pytz
    
    # Major market data
    markets = [
        {
            "country": "USA",
            "flag": "🇺🇸",
            "lat": 40.7128,
            "lon": -74.0060,
            "timezone": "America/New_York",
            "market_name": "NYSE",
            "index_symbol": "SPX",
            "index_name": "S&P 500",
            "current_value": 4850.25,
            "change_pct": 1.2,
            "sentiment": "BULLISH"
        },
        {
            "country": "UK",
            "flag": "🇬🇧",
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "market_name": "LSE",
            "index_symbol": "FTSE",
            "index_name": "FTSE 100",
            "current_value": 7650.50,
            "change_pct": 0.5,
            "sentiment": "NEUTRAL"
        },
        {
            "country": "Germany",
            "flag": "🇩🇪",
            "lat": 50.1109,
            "lon": 8.6821,
            "timezone": "Europe/Berlin",
            "market_name": "DAX",
            "index_symbol": "DAX",
            "index_name": "DAX 40",
            "current_value": 16500.75,
            "change_pct": -0.8,
            "sentiment": "BEARISH"
        },
        {
            "country": "Japan",
            "flag": "🇯🇵",
            "lat": 35.6762,
            "lon": 139.6503,
            "timezone": "Asia/Tokyo",
            "market_name": "TSE",
            "index_symbol": "NIKKEI",
            "index_name": "Nikkei 225",
            "current_value": 33500.00,
            "change_pct": 1.8,
            "sentiment": "BULLISH"
        },
        {
            "country": "China",
            "flag": "🇨🇳",
            "lat": 31.2304,
            "lon": 121.4737,
            "timezone": "Asia/Shanghai",
            "market_name": "SSE",
            "index_symbol": "SHCOMP",
            "index_name": "Shanghai Comp",
            "current_value": 3050.25,
            "change_pct": -1.2,
            "sentiment": "BEARISH"
        },
        {
            "country": "India",
            "flag": "🇮🇳",
            "lat": 19.0760,
            "lon": 72.8777,
            "timezone": "Asia/Kolkata",
            "market_name": "NSE",
            "index_symbol": "NIFTY",
            "index_name": "NIFTY 50",
            "current_value": 21500.50,
            "change_pct": 0.9,
            "sentiment": "BULLISH"
        },
        {
            "country": "Brazil",
            "flag": "🇧🇷",
            "lat": -23.5505,
            "lon": -46.6333,
            "timezone": "America/Sao_Paulo",
            "market_name": "B3",
            "index_symbol": "IBOV",
            "index_name": "IBOVESPA",
            "current_value": 125000.00,
            "change_pct": 0.3,
            "sentiment": "NEUTRAL"
        }
    ]
    
    # Add local time and market status
    for market in markets:
        try:
            tz = pytz.timezone(market["timezone"])
            local_time = datetime.now(tz)
            market["local_time"] = local_time.strftime("%H:%M")
            market["local_date"] = local_time.strftime("%Y-%m-%d")
            
            # Market hours (simplified - 9:30-16:00 local time)
            hour = local_time.hour
            is_weekday = local_time.weekday() < 5
            market["is_open"] = is_weekday and 9 <= hour < 16
        except:
            market["local_time"] = "N/A"
            market["is_open"] = False
    
    return {
        "type": "MAP_DATA",
        "map_mode": "MARKET",
        "title": "Global Market Sentiment",
        "markets": markets
    }
