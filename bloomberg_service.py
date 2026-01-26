"""
Bloomberg Engine Microservice
Standalone FastAPI service for Bloomberg-style market features.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import uvicorn
from bloomberg_engine import BloombergEngine

# Initialize FastAPI app
app = FastAPI(
    title="Bloomberg Engine API",
    description="Professional market data features - FX rates, screeners, sectors, and more",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bloomberg Engine
bloomberg = BloombergEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("[Bloomberg Service] Starting up...")
    print("[Bloomberg Service] Economic calendar auto-refresh: ACTIVE")
    cache_info = bloomberg.get_calendar_cache_info()
    print(f"[Bloomberg Service] Calendar cache: {cache_info}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("[Bloomberg Service] Shutting down...")
    bloomberg.stop_background_updates()
    print("[Bloomberg Service] Background updates stopped")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Bloomberg Engine API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "fx_rates": "/fx-rates",
            "top_movers": "/top-movers",
            "screen": "/screen",
            "sectors": "/sectors",
            "economic_calendar": "/economic-calendar",
            "economic_calendar_refresh": "/economic-calendar/refresh",
            "economic_calendar_cache_info": "/economic-calendar/cache-info",
            "market_summary": "/market-summary"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "bloomberg-engine",
        "timestamp": bloomberg.get_economic_calendar(days_ahead=0)
    }

@app.get("/fx-rates")
async def get_fx_rates():
    """
    Get live foreign exchange rates for major currency pairs.
    
    Returns:
        List of FX rates with current price, change, and percentage change
    """
    try:
        rates = bloomberg.get_fx_rates()
        return {
            "success": True,
            "count": len(rates),
            "data": rates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FX rates: {str(e)}")

@app.get("/top-movers")
async def get_top_movers(
    market_data: Optional[str] = Query(None, description="JSON string of market data")
):
    """
    Get top 5 gainers and losers from market data.
    
    Args:
        market_data: Optional JSON string containing market data
        
    Returns:
        Dictionary with gainers and losers lists
    """
    try:
        # For standalone service, we'll return empty if no data provided
        # In production, this would fetch from a data source
        if not market_data:
            return {
                "success": True,
                "message": "No market data provided",
                "data": {"gainers": [], "losers": []}
            }
        
        import json
        data = json.loads(market_data)
        movers = bloomberg.get_top_movers(data)
        
        return {
            "success": True,
            "data": movers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top movers: {str(e)}")

@app.get("/screen")
async def screen_stocks(
    criteria: str = Query("GAINERS", description="Screening criteria: GAINERS, LOSERS, VOLUME, VOLATILE"),
    market_data: Optional[str] = Query(None, description="JSON string of market data")
):
    """
    Screen stocks based on specified criteria.
    
    Args:
        criteria: Screening criteria (GAINERS, LOSERS, VOLUME, VOLATILE)
        market_data: Optional JSON string containing market data
        
    Returns:
        List of screened stocks
    """
    try:
        if not market_data:
            return {
                "success": True,
                "message": "No market data provided",
                "criteria": criteria,
                "data": []
            }
        
        import json
        data = json.loads(market_data)
        screened = bloomberg.screen_stocks(data, criteria)
        
        return {
            "success": True,
            "criteria": criteria,
            "count": len(screened),
            "data": screened
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error screening stocks: {str(e)}")

@app.get("/sectors")
async def get_sector_performance():
    """
    Get US sector ETF performance data.
    
    Returns:
        List of sector performance data sorted by change percentage
    """
    try:
        sectors = bloomberg.get_sector_performance()
        return {
            "success": True,
            "count": len(sectors),
            "data": sectors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector data: {str(e)}")

@app.get("/economic-calendar")
async def get_economic_calendar(
    days_ahead: int = Query(10, ge=1, le=30, description="Number of days to look ahead"),
    impact: Optional[str] = Query(None, description="Filter by impact level (HIGH, MEDIUM, LOW)"),
    currency: Optional[str] = Query(None, description="Filter by currency (USD, EUR, INR, etc.)")
):
    """
    Get upcoming economic events with optional filtering.
    
    Args:
        days_ahead: Number of days to look ahead (1-30)
        impact: Filter by impact level (HIGH, MEDIUM, LOW)
        currency: Filter by currency code (USD, EUR, INR, etc.)
        
    Returns:
        List of upcoming economic events
    """
    try:
        events = bloomberg.get_economic_calendar(days_ahead=days_ahead, impact=impact, currency=currency)
        return {
            "success": True,
            "days_ahead": days_ahead,
            "filters": {
                "impact": impact,
                "currency": currency
            },
            "count": len(events),
            "data": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching economic calendar: {str(e)}")

@app.get("/economic-calendar/refresh")
async def refresh_economic_calendar():
    """
    Force refresh of economic calendar data from all sources.
    
    Returns:
        Refreshed economic events
    """
    try:
        events = bloomberg.refresh_economic_calendar()
        return {
            "success": True,
            "message": "Economic calendar refreshed",
            "count": len(events),
            "data": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing economic calendar: {str(e)}")

@app.get("/economic-calendar/cache-info")
async def get_calendar_cache_info():
    """
    Get information about the economic calendar cache.
    
    Returns:
        Cache status and metadata
    """
    try:
        cache_info = bloomberg.get_calendar_cache_info()
        return {
            "success": True,
            "data": cache_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache info: {str(e)}")

@app.get("/market-summary")
async def get_market_summary(
    market_data: Optional[str] = Query(None, description="JSON string of market data")
):
    """
    Get overall market summary statistics.
    
    Args:
        market_data: Optional JSON string containing market data
        
    Returns:
        Market summary with gainers, losers, volume, and sentiment
    """
    try:
        if not market_data:
            return {
                "success": True,
                "message": "No market data provided",
                "data": {}
            }
        
        import json
        data = json.loads(market_data)
        summary = bloomberg.get_market_summary(data)
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting market summary: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "bloomberg_service:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
