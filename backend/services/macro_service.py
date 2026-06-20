"""
RetailWise AI — Macro Intelligence Service
Section 7 — The Final 4 Pillars

Fetches live proxy data for:
1. Consumer Confidence (Sensex via yfinance)
2. Social Sentiment (r/Kerala RSS via feedparser)
3. Traffic Congestion (Deduction)
4. Competitor Pricing (Deduction)
"""

import logging
import feedparser
import yfinance as yf

logger = logging.getLogger(__name__)

# RSS Feed for local community sentiment
_REDDIT_RSS_URL = "https://www.reddit.com/r/Kerala.rss"

def get_consumer_confidence() -> str:
    """
    Proxy: BSE Sensex daily return.
    Up > 0.5% -> high
    Down < -0.5% -> low
    Else -> moderate
    """
    try:
        # ^BSESN is the ticker for BSE Sensex
        ticker = yf.Ticker("^BSESN")
        hist = ticker.history(period="5d")
        if len(hist) < 2:
            return "moderate"
        
        latest_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        
        logger.info("[macro] Sensex daily return: %.2f%%", pct_change)
        
        if pct_change > 0.5:
            return "high"
        elif pct_change < -0.5:
            return "low"
        return "moderate"
    except Exception as exc:
        logger.warning("[macro] Consumer confidence fetch failed: %s", exc)
        return "moderate"

def get_social_media_sentiment(gemini_service) -> str:
    """
    Proxy: Top 10 posts from r/Kerala RSS -> Gemini Flash Sentiment.
    """
    try:
        feed = feedparser.parse(_REDDIT_RSS_URL)
        entries = feed.entries[:10]
        
        if not entries:
            return "neutral"
            
        posts = [entry.title for entry in entries]
        logger.info("[macro] Fetched %d posts from Reddit RSS.", len(posts))
        
        # Pass to Gemini
        return gemini_service.analyze_social_sentiment(posts)
    except Exception as exc:
        logger.warning("[macro] Social sentiment fetch failed: %s", exc)
        return "neutral"

def get_traffic_congestion(weather_rain_mm: float, transport_strike: bool) -> str:
    """
    Proxy: Rain + Strikes = Traffic.
    """
    if transport_strike or weather_rain_mm > 20.0:
        return "severe"
    elif weather_rain_mm > 0.0:
        return "moderate"
    return "normal"

def get_competitor_pricing(inflation_high: bool) -> str:
    """
    Proxy: High inflation forces discounts.
    """
    if inflation_high:
        return "discounted"
    return "normal"
