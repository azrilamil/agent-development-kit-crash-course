#!/usr/bin/env python3
"""
Test script for the improved stock analyst agent with multiple data sources.
Run this to test the rate limiting improvements and alternative APIs.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sub_agents.stock_analyst.agent import (
    get_stock_price, 
    clear_stock_cache, 
    get_cache_info,
    test_data_sources
)

def test_basic_functionality():
    """Test basic stock price functionality."""
    print("=== Testing Basic Functionality ===\n")
    
    # Test 1: Normal stock lookup
    print("Test 1: Fetching MSFT stock price...")
    result = get_stock_price("MSFT")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Price: ${result['price']}")
        print(f"Source: {result['source']}")
        print(f"Timestamp: {result['timestamp']}")
    else:
        print(f"Error: {result['error_message']}")
    print()
    
    # Test 2: Same stock again (should use cache)
    print("Test 2: Fetching MSFT again (should use cache)...")
    result = get_stock_price("MSFT")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Price: ${result['price']}")
        print(f"Source: {result['source']} (should be 'cache')")
    print()
    
    # Test 3: Different stock
    print("Test 3: Fetching AAPL stock price...")
    result = get_stock_price("AAPL")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Price: ${result['price']}")
        print(f"Source: {result['source']}")
    print()


def test_cache_functionality():
    """Test cache-related functionality."""
    print("=== Testing Cache Functionality ===\n")
    
    # Get cache info
    print("Current cache info:")
    cache_info = get_cache_info()
    print(f"Cache size: {cache_info['cache_size']}")
    print(f"Alternative sources available: {cache_info['alternative_sources_available']}")
    
    if cache_info['cached_stocks']:
        print("Cached stocks:")
        for ticker, info in cache_info['cached_stocks'].items():
            print(f"  {ticker}: ${info['price']} ({info['source']}, {info['age_minutes']} min old)")
    print()
    
    # Clear cache
    print("Clearing cache...")
    clear_result = clear_stock_cache()
    print(f"Clear result: {clear_result['message']}")
    
    # Verify cache is empty
    cache_info = get_cache_info()
    print(f"Cache size after clear: {cache_info['cache_size']}")
    print()


def test_alternative_sources():
    """Test alternative data sources."""
    print("=== Testing Alternative Data Sources ===\n")
    
    print("Testing all APIs with AAPL...")
    try:
        results = test_data_sources("AAPL")
        
        for api_name, result in results.items():
            print(f"\n{api_name.upper()}:")
            print(f"  Status: {result['status']}")
            if result['status'] == 'success':
                print(f"  Price: ${result['price']}")
                print(f"  Source: {result['source']}")
            else:
                print(f"  Error: {result['error_message']}")
    
    except Exception as e:
        print(f"Error testing alternative sources: {e}")
    print()


def test_multiple_stocks():
    """Test fetching multiple stocks to see fallback behavior."""
    print("=== Testing Multiple Stocks ===\n")
    
    tickers = ["MSFT", "AAPL", "GOOGL", "TSLA", "AMZN"]
    
    for i, ticker in enumerate(tickers):
        print(f"Request {i+1}: Fetching {ticker}...")
        result = get_stock_price(ticker)
        print(f"  Status: {result['status']}")
        if result['status'] == 'success':
            print(f"  Price: ${result['price']}")
            print(f"  Source: {result['source']}")
        else:
            print(f"  Error: {result['error_message']}")
        print()
        
        # Small delay between requests to be respectful to APIs
        if i < len(tickers) - 1:  # Don't sleep after the last request
            time.sleep(1)


def test_invalid_ticker():
    """Test behavior with invalid ticker."""
    print("=== Testing Invalid Ticker ===\n")
    
    print("Testing invalid ticker 'INVALID_XYZ'...")
    result = get_stock_price("INVALID_XYZ")
    print(f"Status: {result['status']}")
    print(f"Error: {result.get('error_message', 'No error message')}")
    if 'suggestion' in result:
        print(f"Suggestion: {result['suggestion']}")
    print()


def run_comprehensive_test():
    """Run all tests in sequence."""
    print("Stock Analyst Agent - Comprehensive Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        print("=" * 50)
        
        test_cache_functionality()
        print("=" * 50)
        
        test_alternative_sources()
        print("=" * 50)
        
        test_multiple_stocks()
        print("=" * 50)
        
        test_invalid_ticker()
        print("=" * 50)
        
        print("✅ All tests completed!")
        
        # Final cache summary
        print("\nFinal cache summary:")
        cache_info = get_cache_info()
        print(f"Total cached stocks: {cache_info['cache_size']}")
        if cache_info['cached_stocks']:
            for ticker, info in cache_info['cached_stocks'].items():
                print(f"  {ticker}: ${info['price']} from {info['source']}")
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Run comprehensive test suite")
    print("2. Test basic functionality only")
    print("3. Test alternative sources only")
    print("4. Test cache functionality only")
    
    try:
        choice = input("\nEnter choice (1-4) or press Enter for comprehensive test: ").strip()
        
        if choice == "2":
            test_basic_functionality()
        elif choice == "3":
            test_alternative_sources()
        elif choice == "4":
            test_cache_functionality()
        else:
            run_comprehensive_test()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()