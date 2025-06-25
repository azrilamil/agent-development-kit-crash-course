import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from memory_agent.agent import memory_agent
from utils import call_agent_async

load_dotenv()

# ===== PART 1: Initialize Persistent Session Service =====
# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# ===== PART 2: Define Initial State =====
# This will only be used when creating a new session
initial_state = {
    "user_name": "Azril Amil",
    "reminders": [],
}


async def main_async():
    # Setup constants
    APP_NAME = "Memory Agent"
    USER_ID = "aiwithazril"

    # ===== PART 3: Session Management - Find or Create =====
    # Check for existing sessions for this user
    existing_sessions = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    # If there's an existing session, use it, otherwise create a new one
    if existing_sessions and existing_sessions.sessions:
        # Continue the most recent session
        session = existing_sessions.sessions[0]
        SESSION_ID = session.id
        print(f"Continuing existing session: {SESSION_ID}")

        # Ensure state has the required keys and update if necessary
        state_updated = False
        if "user_name" not in session.state:
            session.state["user_name"] = ""
            state_updated = True
        if "reminders" not in session.state:
            session.state["reminders"] = []
            state_updated = True

        if state_updated:
            await session_service.update_session(session)
            print("Session state updated with missing keys.")
    else:
        # Create a new session with a unique ID and initial state
        initial_state = {"user_name": "", "reminders": []}
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=None,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Agent Runner Setup =====
    # Create a runner with the memory agent
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to Memory Agent Chat!")
    print("Your reminders will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    asyncio.run(main_async())
