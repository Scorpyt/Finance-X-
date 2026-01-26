"""
India Market Engine API Service
FastAPI service exposing all Indian stock market features
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import uvicorn
from india_engine import IndiaMarketEngine

# Initialize FastAPI app
app = FastAPI(
    title="India Market Engine API",
    description="Comprehensive Indian stock market data - NIFTY 50, Next 50, Midcap, and 7 sectors",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize India Market Engine
india_engine = IndiaMarketEngine(default_categories=['NIFTY_50', 'BANK', 'IT'])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("[INDIA-API] Starting India Market Engine API...")
    stats = india_engine.get_coverage_stats()
    print(f"[INDIA-API] Coverage: {stats['total_stocks']} stocks")
    print(f"[INDIA-API] Categories: {', '.join(stats['categories'])}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    stats = india_engine.get_coverage_stats()
    return {
        "service": "India Market Engine API",
        "version": "2.0.0",
        "coverage": {
            "total_stocks": stats['total_stocks'],
            "nifty_50": stats['nifty_50'],
            "nifty_next_50": stats['nifty_next_50'],
            "midcap": stats['midcap'],
            "sectors": stats['sectoral']
        },
        "endpoints": {
            "health": "/health",
            "coverage_stats": "/stats",
            "nifty_50": "/nifty-50",
            "sector_stocks": "/sector/{sector}",
            "search": "/search?q={query}",
            "top_movers": "/top-movers",
            "category_summary": "/summary",
            "all_stocks": "/all-stocks",
            "market_snapshot": "/market-snapshot"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "india-market-engine",
        "stocks_tracked": len(india_engine.ALL_STOCKS)
    }

@app.get("/stats")
async def get_statistics():
    """
    Get comprehensive coverage statistics.
    
    Returns:
        Stock coverage breakdown by category
    """
    try:
        stats = india_engine.get_coverage_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.get("/nifty-50")
async def get_nifty_50():
    """
    Get NIFTY 50 stocks with real-time data.
    
    Returns:
        List of NIFTY 50 stocks with prices and metadata
    """
    try:
        data = india_engine.fetch_market_snapshot(categories=['NIFTY_50'])
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching NIFTY 50: {str(e)}")

@app.get("/sector/{sector}")
async def get_sector_stocks(sector: str):
    """
    Get stocks from a specific sector.
    
    Args:
        sector: Sector name (BANK, IT, PHARMA, AUTO, FMCG, METAL, ENERGY)
        
    Returns:
        List of sector stocks with real-time data
    """
    try:
        data = india_engine.get_sector_stocks(sector.upper())
        if not data:
            raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")
        
        return {
            "success": True,
            "sector": sector.upper(),
            "count": len(data),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector stocks: {str(e)}")

@app.get("/search")
async def search_stocks(q: str = Query(..., description="Search query (stock symbol or partial name)")):
    """
    Search for stocks by symbol or name.
    
    Args:
        q: Search query (case-insensitive)
        
    Returns:
        List of matching stocks
    """
    try:
        matches = india_engine.search_stocks(q)
        return {
            "success": True,
            "query": q,
            "count": len(matches),
            "data": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching stocks: {str(e)}")

@app.get("/top-movers")
async def get_top_movers(
    category: Optional[str] = Query(None, description="Category filter (NIFTY_50, BANK, IT, etc.)"),
    top_n: int = Query(10, ge=1, le=50, description="Number of top stocks to return")
):
    """
    Get top gainers and losers.
    
    Args:
        category: Optional category filter
        top_n: Number of top stocks (1-50)
        
    Returns:
        Top gainers and losers
    """
    try:
        movers = india_engine.get_top_movers(category=category, top_n=top_n)
        return {
            "success": True,
            "category": category or "all",
            "top_n": top_n,
            "data": movers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top movers: {str(e)}")

@app.get("/summary")
async def get_category_summary(
    categories: Optional[str] = Query(None, description="Comma-separated categories (NIFTY_50,BANK,IT)")
):
    """
    Get summary statistics for categories.
    
    Args:
        categories: Comma-separated list of categories (default: NIFTY_50,BANK,IT)
        
    Returns:
        Category summaries with sentiment analysis
    """
    try:
        cat_list = categories.split(',') if categories else ['NIFTY_50', 'BANK', 'IT']
        cat_list = [c.strip().upper() for c in cat_list]
        
        summary = india_engine.get_category_summary(categories=cat_list)
        return {
            "success": True,
            "categories": cat_list,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")

@app.get("/all-stocks")
async def get_all_stocks():
    """
    Get all tracked stocks (240+ stocks, may take 10-15 seconds).
    
    Returns:
        Complete stock universe with real-time data
    """
    try:
        data = india_engine.get_all_stocks(use_cache=True)
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all stocks: {str(e)}")

@app.get("/market-snapshot")
async def get_market_snapshot(
    categories: Optional[str] = Query(None, description="Comma-separated categories")
):
    """
    Get market snapshot for specific categories.
    
    Args:
        categories: Comma-separated list of categories (default: NIFTY_50,BANK,IT)
        
    Returns:
        Market data for requested categories
    """
    try:
        cat_list = categories.split(',') if categories else ['NIFTY_50', 'BANK', 'IT']
        cat_list = [c.strip().upper() for c in cat_list]
        
        data = india_engine.fetch_market_snapshot(categories=cat_list)
        return {
            "success": True,
            "categories": cat_list,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market snapshot: {str(e)}")

if __name__ == "__main__":
    print("=" * 70)
    print("  INDIA MARKET ENGINE API SERVER")
    print("=" * 70)
    print("\n  Starting server on http://localhost:8002")
    print("\n  API Documentation: http://localhost:8002/docs")
    print("  Coverage: 240+ Indian stocks across 10 categories")
    print("\n" + "=" * 70)
    
    uvicorn.run(
        "india_service:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
