ad#!/usr/bin/env python3
"""
Simple script to run the greeting agent interactively.
"""

import asyncio
from agent import root_agent

async def main():
    print("🤖 Starting Greeting Agent...")
    print("Type 'quit' or 'exit' to stop the agent.\n")
    
    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
                
            # Run the agent with the user input using run_async
            response_generator = root_agent.run_async(user_input)
            
            print("Agent: ", end="", flush=True)
            async for chunk in response_generator:
                print(chunk, end="", flush=True)
            print()  # New line after response
            print()
            
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    asyncio.run(main())
