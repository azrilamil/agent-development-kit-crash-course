from datetime import datetime
import requests
import time

# Import configuration
try:
    from .config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, POLYGON_API_KEY, DEBUG_MODE
except ImportError:
    # Fallback if config not available
    ALPHA_VANTAGE_API_KEY = None
    FINNHUB_API_KEY = None
    POLYGON_API_KEY = None
    DEBUG_MODE = True


def get_stock_price_alpha_vantage(ticker: str) -> dict:
    """Fetch stock price using Alpha Vantage API (5 calls/minute free tier)"""
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "your_alpha_vantage_key_here":
        return {"status": "error", "ticker": ticker, "error_message": "Alpha Vantage API key not configured"}
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        if DEBUG_MODE:
            print(f"Fetching {ticker} from Alpha Vantage...")
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            price_str = quote.get("05. price", "")
            if price_str:
                price = float(price_str)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    "status": "success",
                    "ticker": ticker,
                    "price": price,
                    "timestamp": timestamp,
                    "source": "alpha_vantage"
                }
        
        # Check for API limit message
        if "Note" in data:
            return {
                "status": "error", 
                "ticker": ticker, 
                "error_message": "Alpha Vantage API limit reached (5 calls/minute)"
            }
        
        return {"status": "error", "ticker": ticker, "error_message": "Invalid response from Alpha Vantage"}
            
    except Exception as e:
        return {"status": "error", "ticker": ticker, "error_message": f"Alpha Vantage error: {str(e)}"}


def get_stock_price_finnhub(ticker: str) -> dict:
    """Fetch stock price using Finnhub API (60 calls/minute free tier)"""
    if not FINNHUB_API_KEY or FINNHUB_API_KEY == "your_finnhub_key_here":
        return {"status": "error", "ticker": ticker, "error_message": "Finnhub API key not configured"}
    
    url = "https://finnhub.io/api/v1/quote"
    params = {
        "symbol": ticker,
        "token": FINNHUB_API_KEY
    }
    
    try:
        if DEBUG_MODE:
            print(f"Fetching {ticker} from Finnhub...")
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "c" in data and data["c"] and data["c"] > 0:  # "c" is current price
            price = float(data["c"])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "status": "success",
                "ticker": ticker,
                "price": price,
                "timestamp": timestamp,
                "source": "finnhub"
            }
        else:
            return {"status": "error", "ticker": ticker, "error_message": "Invalid ticker or no data from Finnhub"}
            
    except Exception as e:
        return {"status": "error", "ticker": ticker, "error_message": f"Finnhub error: {str(e)}"}


def get_stock_price_polygon(ticker: str) -> dict:
    """Fetch stock price using Polygon.io API (5 calls/minute free tier)"""
    if not POLYGON_API_KEY or POLYGON_API_KEY == "your_polygon_key_here":
        return {"status": "error", "ticker": ticker, "error_message": "Polygon API key not configured"}
    
    # Get previous trading day's close (most recent available)
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
    params = {
        "apikey": POLYGON_API_KEY
    }
    
    try:
        if DEBUG_MODE:
            print(f"Fetching {ticker} from Polygon.io...")
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            price = float(result["c"])  # "c" is close price
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "status": "success",
                "ticker": ticker,
                "price": price,
                "timestamp": timestamp,
                "source": "polygon"
            }
        else:
            return {"status": "error", "ticker": ticker, "error_message": "Invalid ticker or no data from Polygon"}
            
    except Exception as e:
        return {"status": "error", "ticker": ticker, "error_message": f"Polygon error: {str(e)}"}


def get_stock_price_with_fallbacks(ticker: str) -> dict:
    """
    Try multiple APIs in order of preference:
    1. Finnhub (highest rate limit - 60/min)
    2. Alpha Vantage (5/min)
    3. Polygon (5/min)
    """
    
    # Try Finnhub first (highest rate limit)
    result = get_stock_price_finnhub(ticker)
    if result["status"] == "success":
        return result
    
    if DEBUG_MODE:
        print(f"Finnhub failed for {ticker}, trying Alpha Vantage...")
    
    # Try Alpha Vantage
    result = get_stock_price_alpha_vantage(ticker)
    if result["status"] == "success":
        return result
    
    if DEBUG_MODE:
        print(f"Alpha Vantage failed for {ticker}, trying Polygon...")
    
    # Try Polygon as last resort
    result = get_stock_price_polygon(ticker)
    if result["status"] == "success":
        return result
    
    # All APIs failed
    return {
        "status": "error",
        "ticker": ticker,
        "error_message": "All alternative APIs failed or reached rate limits",
        "suggestion": "Please try again in a few minutes"
    }


def test_all_apis(ticker: str = "AAPL") -> dict:
    """Test all APIs to see which ones are working"""
    results = {}
    
    print(f"Testing all APIs with {ticker}...")
    
    # Test Alpha Vantage
    print("\n--- Testing Alpha Vantage ---")
    results["alpha_vantage"] = get_stock_price_alpha_vantage(ticker)
    
    time.sleep(1)  # Small delay between API calls
    
    # Test Finnhub
    print("\n--- Testing Finnhub ---")
    results["finnhub"] = get_stock_price_finnhub(ticker)
    
    time.sleep(1)
    
    # Test Polygon
    print("\n--- Testing Polygon ---")
    results["polygon"] = get_stock_price_polygon(ticker)
    
    return results