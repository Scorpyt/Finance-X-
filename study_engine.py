"""
Study Engine - Financial News & Learning Resources
Provides live news fetching, sentiment analysis, and educational content.
"""

import feedparser
import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class NewsItem:
    title: str
    source: str
    link: str
    published: str
    sentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    impact: str     # 'HIGH', 'MEDIUM', 'LOW'
    tickers: List[str]

@dataclass
class StudyResource:
    title: str
    category: str
    description: str
    difficulty: str  # 'BEGINNER', 'INTERMEDIATE', 'ADVANCED'

class StudyEngine:
    """Fetches live financial news and provides learning resources."""
    
    # RSS Feed Sources
    NEWS_FEEDS = [
        {"name": "Yahoo Finance", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"},
        {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories/"},
        {"name": "Reuters Business", "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"},
    ]
    
    # Ticker mapping for common company names
    TICKER_MAP = {
        "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
        "amazon": "AMZN", "meta": "META", "facebook": "META", "nvidia": "NVDA",
        "tesla": "TSLA", "netflix": "NFLX", "jpmorgan": "JPM", "goldman": "GS",
        "berkshire": "BRK.A", "visa": "V", "mastercard": "MA", "paypal": "PYPL",
        "s&p": "SPX", "nasdaq": "NDX", "dow": "DJI", "bitcoin": "BTC",
        "reliance": "RELIANCE", "tata": "TCS", "infosys": "INFY", "hdfc": "HDFCBANK",
        "adani": "ADANIENT", "nifty": "NIFTY50"
    }
    
    # Sentiment keywords
    BULLISH_KEYWORDS = [
        "surge", "soar", "rally", "gain", "jump", "rise", "high", "record", 
        "growth", "profit", "beat", "upgrade", "bullish", "optimistic", "strong"
    ]
    BEARISH_KEYWORDS = [
        "fall", "drop", "crash", "plunge", "decline", "loss", "low", "miss",
        "downgrade", "bearish", "concern", "risk", "warning", "weak", "sell-off"
    ]
    
    # Study Resources
    RESOURCES = [
        StudyResource("Technical Analysis Basics", "ANALYSIS", 
                     "Learn candlestick patterns, support/resistance, and trend lines.", "BEGINNER"),
        StudyResource("Understanding P/E Ratios", "FUNDAMENTALS",
                     "How to evaluate stock valuations using price-to-earnings.", "BEGINNER"),
        StudyResource("Reading Financial Statements", "FUNDAMENTALS",
                     "Balance sheets, income statements, and cash flow analysis.", "INTERMEDIATE"),
        StudyResource("Options Trading 101", "DERIVATIVES",
                     "Calls, puts, and basic options strategies.", "INTERMEDIATE"),
        StudyResource("Risk Management", "STRATEGY",
                     "Position sizing, stop-losses, and portfolio diversification.", "BEGINNER"),
        StudyResource("Sector Rotation Strategy", "STRATEGY",
                     "How to identify and trade sector cycles.", "ADVANCED"),
        StudyResource("Bollinger Bands Trading", "ANALYSIS",
                     "Using volatility bands for entry and exit signals.", "INTERMEDIATE"),
        StudyResource("Market Sentiment Analysis", "ANALYSIS",
                     "Understanding fear & greed indicators and market psychology.", "ADVANCED"),
    ]
    
    # Market Terms Glossary
    GLOSSARY = {
        "Bull Market": "A market condition where prices are rising or expected to rise.",
        "Bear Market": "A market condition where prices are falling by 20% or more.",
        "P/E Ratio": "Price-to-Earnings ratio - stock price divided by earnings per share.",
        "Market Cap": "Total value of a company's shares (price × shares outstanding).",
        "Volume": "Number of shares traded during a given period.",
        "Volatility": "Measure of price fluctuation; higher = more risk/opportunity.",
        "Dividend": "Regular payment to shareholders from company profits.",
        "IPO": "Initial Public Offering - first sale of stock to the public.",
        "ETF": "Exchange-Traded Fund - basket of securities traded like a stock.",
        "Short Selling": "Borrowing shares to sell, hoping to buy back cheaper later.",
        "Stop Loss": "Order to sell when price drops to a specified level.",
        "Support Level": "Price level where buying pressure prevents further decline.",
        "Resistance Level": "Price level where selling pressure prevents further rise.",
        "RSI": "Relative Strength Index - momentum indicator (0-100 scale).",
        "MACD": "Moving Average Convergence Divergence - trend-following indicator.",
    }
    
    def __init__(self):
        self._news_cache = []
        self._last_fetch = None
    
    def fetch_live_news(self, max_items: int = 15) -> List[Dict]:
        """Fetch news from multiple RSS feeds."""
        all_news = []
        
        for feed_info in self.NEWS_FEEDS:
            try:
                feed = feedparser.parse(feed_info["url"])
                for entry in feed.entries[:5]:  # Max 5 per source
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    published = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M"))
                    
                    sentiment = self._analyze_sentiment(title)
                    impact = self._estimate_impact(title)
                    tickers = self._extract_tickers(title)
                    
                    all_news.append({
                        "title": title,
                        "source": feed_info["name"],
                        "link": link,
                        "published": published[:16] if len(published) > 16 else published,
                        "sentiment": sentiment,
                        "impact": impact,
                        "tickers": tickers
                    })
            except Exception as e:
                print(f"[Study Engine] Error fetching {feed_info['name']}: {e}")
                continue
        
        # Sort by recency and limit
        self._news_cache = all_news[:max_items]
        self._last_fetch = datetime.now()
        return self._news_cache
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze headline sentiment."""
        text_lower = text.lower()
        
        bullish_count = sum(1 for kw in self.BULLISH_KEYWORDS if kw in text_lower)
        bearish_count = sum(1 for kw in self.BEARISH_KEYWORDS if kw in text_lower)
        
        if bullish_count > bearish_count:
            return "BULLISH"
        elif bearish_count > bullish_count:
            return "BEARISH"
        return "NEUTRAL"
    
    def _estimate_impact(self, text: str) -> str:
        """Estimate market impact of news."""
        text_lower = text.lower()
        
        high_impact = ["fed", "rate", "inflation", "gdp", "recession", "war", 
                       "crash", "crisis", "record", "billion", "trillion"]
        medium_impact = ["earnings", "revenue", "profit", "growth", "merger", 
                         "acquisition", "ipo", "dividend"]
        
        if any(kw in text_lower for kw in high_impact):
            return "HIGH"
        elif any(kw in text_lower for kw in medium_impact):
            return "MEDIUM"
        return "LOW"
    
    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from headline."""
        tickers = []
        text_lower = text.lower()
        
        # Check for company name mentions
        for name, ticker in self.TICKER_MAP.items():
            if name in text_lower and ticker not in tickers:
                tickers.append(ticker)
        
        # Check for explicit ticker patterns like $AAPL or (AAPL)
        explicit = re.findall(r'\$([A-Z]{1,5})|$$([A-Z]{1,5})$$', text.upper())
        for match in explicit:
            ticker = match[0] or match[1]
            if ticker and ticker not in tickers:
                tickers.append(ticker)
        
        return tickers[:3]  # Max 3 tickers per headline
    
    def get_study_resources(self, category: Optional[str] = None) -> List[Dict]:
        """Get learning resources, optionally filtered by category."""
        resources = self.RESOURCES
        if category:
            resources = [r for r in resources if r.category == category.upper()]
        
        return [
            {
                "title": r.title,
                "category": r.category,
                "description": r.description,
                "difficulty": r.difficulty
            }
            for r in resources
        ]
    
    def get_glossary(self, term: Optional[str] = None) -> Dict:
        """Get market terms glossary."""
        if term:
            term_title = term.title()
            if term_title in self.GLOSSARY:
                return {term_title: self.GLOSSARY[term_title]}
            # Fuzzy search
            matches = {k: v for k, v in self.GLOSSARY.items() 
                      if term.lower() in k.lower()}
            return matches if matches else {"error": f"Term '{term}' not found"}
        return self.GLOSSARY
    
    def get_study_overview(self) -> Dict:
        """Get complete study section data."""
        news = self.fetch_live_news()
        resources = self.get_study_resources()
        
        return {
            "news": news,
            "resources": resources,
            "glossary_count": len(self.GLOSSARY),
            "last_updated": datetime.now().strftime("%H:%M:%S")
        }
