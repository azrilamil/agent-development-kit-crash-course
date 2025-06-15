import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import root_agent

# Load environment variables from the .env file in the question_answering_agent directory
load_dotenv(dotenv_path="question_answering_agent/.env")


async def main():
    # Create a new session service to store state
    session_service_stateful = InMemorySessionService()

    initial_state = {
        "user_name": "Azril Amil",
        "user_preferences": """
            I like to play Pickleball, Disc Golf, and Tennis.
            My favorite food is Makanan Kampung.
            My favorite TV show is Game of Thrones.
            Loves it when people like and subscribe to his YouTube channel.
        """,
    }

    # Create a NEW session
    APP_NAME = "AZR Bot"
    USER_ID = "azril_amil"
    SESSION_ID = str(uuid.uuid4())
    
    stateful_session = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print("CREATED NEW SESSION:")
    print(f"\tSession ID: {SESSION_ID}")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Azril's favorite TV show?")]
    )

    # When running via `adk web`, the runner.run() is handled by the web server.
    # This loop is primarily for direct script execution testing.
    # We'll keep it here for that purpose but note its role changes with `adk web`.
    print("\n--- Running agent for direct script execution test ---")
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response (direct script): {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")
    session = await session_service_stateful.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # Log final Session state
    print("=== Final Session State ===")
    if session:
        for key, value in session.state.items():
            print(f"{key}: {value}")
    else:
        print(f"Session {SESSION_ID} not found after run.")


if __name__ == "__main__":
    asyncio.run(main())