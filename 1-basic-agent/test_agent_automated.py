#!/usr/bin/env python3
"""
Automated test script for the greeting agent using proper async handling.
"""

import asyncio
import sys
import os

# Add the greeting_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'greeting_agent'))

from greeting_agent.agent import root_agent

async def test_agent_automated():
    print("🤖 Testing Greeting Agent with Automated Inputs...")
    print("=" * 60)
    
    # Test cases
    test_inputs = [
        "Hello!",
        "My name is John",
        "Hi there, I'm Sarah",
        "Good morning",
        "How do you greet someone in Spanish?"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}:")
        print(f"User: {user_input}")
        
        try:
            print("Agent: ", end="", flush=True)
            
            response_generator = root_agent.run_async(user_input)
            full_response = ""
            
            async for chunk in response_generator:
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after response
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_agent_automated())