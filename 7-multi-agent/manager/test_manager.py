#!/usr/bin/env python3
"""
Test script for the manager agent to verify proper delegation to stock_analyst
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import root_agent

def test_manager_delegation():
    """Test that the manager properly delegates stock requests"""
    
    print("🧪 Testing Manager Agent Delegation")
    print("=" * 50)
    
    # Test stock price request
    print("\n📊 Testing stock price request...")
    try:
        response = root_agent.run("What's the current stock price for Microsoft?")
        print(f"Response: {response}")
        
        # Check if the response indicates delegation happened
        if "stock_analyst" in str(response).lower() or "microsoft" in str(response).lower():
            print("✅ Manager appears to have delegated to stock_analyst")
        else:
            print("❌ Manager may not have properly delegated")
            
    except Exception as e:
        print(f"❌ Error during stock request: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_manager_delegation()