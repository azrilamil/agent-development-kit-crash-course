#!/usr/bin/env python3
"""
Simple script to run the greeting agent interactively using proper async handling.
"""

import asyncio
import sys
import os

# Add the greeting_agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'greeting_agent'))

from greeting_agent.agent import root_agent

async def run_agent_interactive():
    print("🤖 Starting Greeting Agent...")
    print("Type 'quit' or 'exit' to stop the agent.\n")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            # Run the agent with the user input using run_async
            print("Agent: ", end="", flush=True)
            
            response_generator = root_agent.run_async(user_input)
            full_response = ""
            
            async for chunk in response_generator:
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after response
            print()  # Extra line for spacing
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    asyncio.run(run_agent_interactive())