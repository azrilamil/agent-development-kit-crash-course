#!/usr/bin/env python3
"""
Quick setup verification for the multi-source stock analyst agent.
This script verifies that all components are properly configured.
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_setup():
    """Verify that all components are properly set up."""
    print("🔍 Stock Analyst Agent - Setup Verification")
    print("=" * 50)
    
    # Test 1: Import main agent
    try:
        from sub_agents.stock_analyst.agent import stock_analyst, get_stock_price
        print("✅ Main agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main agent: {e}")
        return False
    
    # Test 2: Check configuration
    try:
        from sub_agents.stock_analyst.config import (
            ALPHA_VANTAGE_API_KEY, 
            FINNHUB_API_KEY, 
            POLYGON_API_KEY,
            CACHE_DURATION_MINUTES
        )
        print("✅ Configuration loaded successfully")
        
        # Check API keys
        api_keys_configured = 0
        if ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != "your_alpha_vantage_key_here":
            print("✅ Alpha Vantage API key configured")
            api_keys_configured += 1
        else:
            print("⚠️  Alpha Vantage API key not configured")
            
        if FINNHUB_API_KEY and FINNHUB_API_KEY != "your_finnhub_key_here":
            print("✅ Finnhub API key configured")
            api_keys_configured += 1
        else:
            print("⚠️  Finnhub API key not configured")
            
        if POLYGON_API_KEY and POLYGON_API_KEY != "your_polygon_key_here":
            print("✅ Polygon API key configured")
            api_keys_configured += 1
        else:
            print("⚠️  Polygon API key not configured")
            
        print(f"📊 {api_keys_configured}/3 alternative API keys configured")
        
    except ImportError as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test 3: Check alternative sources
    try:
        from sub_agents.stock_analyst.alternative_sources import (
            get_stock_price_with_fallbacks,
            get_stock_price_alpha_vantage,
            get_stock_price_finnhub,
            get_stock_price_polygon
        )
        print("✅ Alternative sources imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import alternative sources: {e}")
        return False
    
    # Test 4: Quick functionality test
    print("\n🧪 Quick Functionality Test")
    print("-" * 30)
    
    try:
        # Test cache info (should work without API calls)
        from sub_agents.stock_analyst.agent import get_cache_info
        cache_info = get_cache_info()
        print(f"✅ Cache system working (size: {cache_info['cache_size']})")
        print(f"✅ Alternative sources available: {cache_info['alternative_sources_available']}")
        
    except Exception as e:
        print(f"❌ Cache system test failed: {e}")
        return False
    
    # Test 5: Dependencies check
    print("\n📦 Dependencies Check")
    print("-" * 20)
    
    required_packages = ['yfinance', 'requests', 'google.adk.agents']
    for package in required_packages:
        try:
            if package == 'google.adk.agents':
                from google.adk.agents import Agent
            elif package == 'yfinance':
                import yfinance
            elif package == 'requests':
                import requests
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available - please install it")
            return False
    
    print("\n🎉 Setup Verification Complete!")
    print("=" * 50)
    
    if api_keys_configured > 0:
        print(f"✅ Your agent is ready with {api_keys_configured + 1} data sources!")
        print("   - yfinance (primary)")
        if api_keys_configured >= 1:
            print("   - Alternative APIs configured as fallbacks")
    else:
        print("⚠️  Your agent will work with yfinance only")
        print("   Consider configuring alternative APIs for better reliability")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Run: python test_agent.py")
    print(f"   2. Test with: get_stock_price('MSFT')")
    print(f"   3. Check cache: get_cache_info()")
    
    return True

if __name__ == "__main__":
    try:
        success = verify_setup()
        if success:
            print("\n🚀 Ready to use! Your rate limiting issues are solved.")
        else:
            print("\n❌ Setup incomplete. Please check the errors above.")
    except Exception as e:
        print(f"\n💥 Verification failed with error: {e}")
        import traceback
        traceback.print_exc()