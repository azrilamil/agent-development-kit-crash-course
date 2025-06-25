#!/usr/bin/env python3
"""
Simple test script to demonstrate the greeting agent functionality.
"""

import asyncio
from agent import root_agent

async def test_agent():
    print("🤖 Testing Greeting Agent...")
    print("=" * 50)
    
    # Test cases
    test_inputs = [
        "Hello!",
        "My name is John",
        "Hi there, I'm Sarah",
        "Good morning"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}:")
        print(f"User: {user_input}")
        
        try:
            # Run the agent with the user input using run_async
            response_generator = root_agent.run_async(user_input)
            
            print("Agent: ", end="", flush=True)
            async for chunk in response_generator:
                print(chunk, end="", flush=True)
            print()  # New line after response
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_agent())