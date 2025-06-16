from datetime import datetime, timedelta
import time
import random

import yfinance as yf
from google.adk.agents import Agent

# Import configuration
try:
    from .config import *
except ImportError:
    # Fallback configuration if config.py is not available
    CACHE_DURATION_MINUTES = 5
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1
    DEBUG_MODE = True
    LOG_CACHE_HITS = True

# Import alternative sources
try:
    from .alternative_sources import get_stock_price_with_fallbacks, test_all_apis
    ALTERNATIVE_SOURCES_AVAILABLE = True
except ImportError:
    ALTERNATIVE_SOURCES_AVAILABLE = False
    if DEBUG_MODE:
        print("Alternative sources not available")

# Simple in-memory cache for stock prices
_stock_cache = {}

def get_stock_price(ticker: str) -> dict:
    """Retrieves current stock price with caching, retry logic, and alternative sources."""
    if DEBUG_MODE:
        print(f"--- Tool: get_stock_price called for {ticker} ---")
    
    # Check cache first
    cache_key = ticker.upper()
    current_time = datetime.now()
    
    if cache_key in _stock_cache:
        cached_data = _stock_cache[cache_key]
        cache_time = cached_data['cached_at']
        if current_time - cache_time < timedelta(minutes=CACHE_DURATION_MINUTES):
            if LOG_CACHE_HITS and DEBUG_MODE:
                print(f"Returning cached data for {ticker}")
            return {
                "status": "success",
                "ticker": ticker,
                "price": cached_data['price'],
                "timestamp": cached_data['timestamp'],
                "source": "cache"
            }
    
    # Try yfinance first with retry logic
    yfinance_result = _try_yfinance(ticker)
    if yfinance_result["status"] == "success":
        # Cache successful result
        _cache_result(cache_key, yfinance_result, current_time)
        return yfinance_result
    
    # If yfinance fails and alternative sources are available, try them
    if ALTERNATIVE_SOURCES_AVAILABLE:
        if DEBUG_MODE:
            print(f"yfinance failed for {ticker}, trying alternative sources...")
        
        alt_result = get_stock_price_with_fallbacks(ticker)
        if alt_result["status"] == "success":
            # Cache successful result from alternative source
            _cache_result(cache_key, alt_result, current_time)
            return alt_result
        else:
            # Both yfinance and alternatives failed
            return {
                "status": "error",
                "ticker": ticker,
                "error_message": f"All data sources failed for {ticker}. yfinance error: {yfinance_result.get('error_message', 'Unknown')}. Alternative sources error: {alt_result.get('error_message', 'Unknown')}",
                "suggestion": "Please try again in a few minutes as this might be temporary rate limiting across multiple providers."
            }
    else:
        # Only yfinance available and it failed
        return yfinance_result


def _try_yfinance(ticker: str) -> dict:
    """Try to get stock price using yfinance with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            if DEBUG_MODE:
                print(f"yfinance attempt {attempt + 1} for {ticker}")
            
            # Add exponential backoff with jitter
            if attempt > 0:
                delay = min(BASE_RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1), 30)
                if DEBUG_MODE:
                    print(f"Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
            
            # Fetch stock data
            stock = yf.Ticker(ticker)
            current_price = None
            
            # Method 1: Try info (most comprehensive but can be rate limited)
            try:
                info = stock.info
                current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Info method failed: {str(e)}")
            
            # Method 2: Try recent history if info fails
            if current_price is None:
                try:
                    hist = stock.history(period="1d", interval="1m")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        if DEBUG_MODE:
                            print(f"Got price from 1-minute history: {current_price}")
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"1-minute history method failed: {str(e)}")
            
            # Method 3: Try daily history
            if current_price is None:
                try:
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        if DEBUG_MODE:
                            print(f"Got price from daily history: {current_price}")
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Daily history method failed: {str(e)}")
            
            # Method 4: Try 5-day history as last resort
            if current_price is None:
                try:
                    hist = stock.history(period="5d")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        if DEBUG_MODE:
                            print(f"Got price from 5-day history: {current_price}")
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"5-day history method failed: {str(e)}")
            
            if current_price is None:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "status": "error",
                        "error_message": f"Could not fetch price for {ticker} from yfinance after {MAX_RETRIES} attempts.",
                    }
                continue
            
            # Success!
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "status": "success",
                "ticker": ticker,
                "price": current_price,
                "timestamp": timestamp,
                "source": "yfinance"
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            if DEBUG_MODE:
                print(f"yfinance attempt {attempt + 1} failed: {str(e)}")
            
            # Check if it's a rate limiting error
            if any(keyword in error_msg for keyword in ['rate limit', 'too many requests', '429', 'quota', 'exceeded']):
                if attempt == MAX_RETRIES - 1:
                    return {
                        "status": "error",
                        "error_message": f"yfinance rate limit exceeded for {ticker}.",
                    }
                # Continue to retry with exponential backoff
                continue
            else:
                # For other errors, return immediately
                return {
                    "status": "error",
                    "error_message": f"yfinance error for {ticker}: {str(e)}",
                }
    
    return {
        "status": "error",
        "error_message": f"yfinance failed for {ticker} after {MAX_RETRIES} attempts",
    }


def _cache_result(cache_key: str, result: dict, current_time: datetime):
    """Cache a successful result."""
    _stock_cache[cache_key] = {
        'price': result['price'],
        'timestamp': result['timestamp'],
        'cached_at': current_time,
        'source': result['source']
    }


def clear_stock_cache():
    """Clear the stock price cache - useful for testing or manual refresh."""
    global _stock_cache
    _stock_cache.clear()
    if DEBUG_MODE:
        print("Stock price cache cleared")
    return {"status": "success", "message": "Cache cleared successfully"}


def get_cache_info():
    """Get information about the current cache state."""
    cache_info = {}
    current_time = datetime.now()
    
    for ticker, data in _stock_cache.items():
        age_minutes = (current_time - data['cached_at']).total_seconds() / 60
        cache_info[ticker] = {
            'price': data['price'],
            'timestamp': data['timestamp'],
            'source': data.get('source', 'unknown'),
            'age_minutes': round(age_minutes, 1),
            'expires_in_minutes': round(CACHE_DURATION_MINUTES - age_minutes, 1)
        }
    
    return {
        "status": "success",
        "cache_size": len(_stock_cache),
        "cache_duration_minutes": CACHE_DURATION_MINUTES,
        "alternative_sources_available": ALTERNATIVE_SOURCES_AVAILABLE,
        "cached_stocks": cache_info
    }


def test_data_sources(ticker: str = "AAPL"):
    """Test all available data sources for a given ticker."""
    if not ALTERNATIVE_SOURCES_AVAILABLE:
        return {"status": "error", "message": "Alternative sources not available"}
    
    return test_all_apis(ticker)


# Create the root agent
stock_analyst = Agent(
    name="stock_analyst",
    model="gemini-2.0-flash",
    description="An intelligent stock market assistant with multiple data sources and advanced rate limiting protection.",
    instruction="""
    You are a helpful stock market assistant that helps users track their stocks of interest.
    
    When asked about stock prices:
    1. Use the get_stock_price tool to fetch the latest price for the requested stock(s)
    2. Format the response to show each stock's current price and the time it was fetched
    3. If a stock price couldn't be fetched, explain this to the user and suggest they try again in 2-3 minutes
    4. If you get cached data (indicated by "source": "cache"), you can mention that the price is from recent cache
    5. Be patient and understanding when rate limits occur - this is normal for free financial data APIs
    
    Advanced features:
    - Stock prices are automatically cached for 5 minutes to reduce API calls
    - The system uses multiple data sources: yfinance (primary), Finnhub, Alpha Vantage, and Polygon.io
    - Intelligent retry logic with exponential backoff
    - Automatic fallback to alternative APIs when primary source fails
    - You can use clear_stock_cache() to force fresh data if needed
    - Use get_cache_info() to see what's currently cached
    - Use test_data_sources() to check which APIs are working
    
    Data source information:
    - yfinance: Primary source (Yahoo Finance)
    - Finnhub: 60 calls/minute (backup)
    - Alpha Vantage: 5 calls/minute (backup)
    - Polygon.io: 5 calls/minute (backup)
    
    Important notes:
    - Always be helpful and explain any limitations or delays to the user
    - If rate limits are encountered across all sources, suggest waiting 2-3 minutes
    - Cached data is perfectly fine for most use cases and helps avoid rate limits
    - Different sources may show slightly different prices due to timing and data feeds
    
    Example response format:
    "Here are the current stock prices:
    - MSFT: $420.50 (updated at 2024-04-21 16:30:00) [yfinance]
    - AAPL: $185.25 (updated at 2024-04-21 16:28:00) [cached from finnhub]
    - GOOGL: $175.80 (updated at 2024-04-21 16:30:00) [alpha_vantage - fallback used]"
    
    If you encounter rate limiting errors across all sources, be empathetic and explain that this is temporary.
    """,
    tools=[get_stock_price, clear_stock_cache, get_cache_info, test_data_sources],
)