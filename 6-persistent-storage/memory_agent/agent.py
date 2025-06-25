from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def add_reminder(reminder: str, tool_context: ToolContext) -> dict:
    """Add a new reminder to the user's reminder list.

    Args:
        reminder: The reminder text to add
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(f"--- Tool: add_reminder called for '{reminder}' ---")

    # Get current reminders from state
    reminders = tool_context.state.get("reminders", [])

    # Add the new reminder
    reminders.append(reminder)

    # Update state with the new list of reminders
    tool_context.state["reminders"] = reminders

    return {
        "action": "add_reminder",
        "reminder": reminder,
        "message": f"Added reminder: {reminder}",
    }


def view_reminders(tool_context: ToolContext) -> dict:
    """View all current reminders.

    Args:
        tool_context: Context for accessing session state

    Returns:
        The list of reminders
    """
    print("--- Tool: view_reminders called ---")

    # Get reminders from state
    reminders = tool_context.state.get("reminders", [])

    return {"action": "view_reminders", "reminders": reminders, "count": len(reminders)}


def update_reminder(index: int, updated_text: str, tool_context: ToolContext) -> dict:
    """Update an existing reminder.

    Args:
        index: The 1-based index of the reminder to update
        updated_text: The new text for the reminder
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(
        f"--- Tool: update_reminder called for index {index} with '{updated_text}' ---"
    )

    # Get current reminders from state
    reminders = tool_context.state.get("reminders", [])

    # Check if the index is valid
    if not reminders or index < 1 or index > len(reminders):
        return {
            "action": "update_reminder",
            "status": "error",
            "message": f"Could not find reminder at position {index}. Currently there are {len(reminders)} reminders.",
        }

    # Update the reminder (adjusting for 0-based indices)
    old_reminder = reminders[index - 1]
    reminders[index - 1] = updated_text

    # Update state with the modified list
    tool_context.state["reminders"] = reminders

    return {
        "action": "update_reminder",
        "index": index,
        "old_text": old_reminder,
        "updated_text": updated_text,
        "message": f"Updated reminder {index} from '{old_reminder}' to '{updated_text}'",
    }


def delete_reminder(index: int, tool_context: ToolContext) -> dict:
    """Delete a reminder.

    Args:
        index: The 1-based index of the reminder to delete
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(f"--- Tool: delete_reminder called for index {index} ---")

    # Get current reminders from state
    reminders = tool_context.state.get("reminders", [])

    # Check if the index is valid
    if not reminders or index < 1 or index > len(reminders):
        return {
            "action": "delete_reminder",
            "status": "error",
            "message": f"Could not find reminder at position {index}. Currently there are {len(reminders)} reminders.",
        }

    # Remove the reminder (adjusting for 0-based indices)
    deleted_reminder = reminders.pop(index - 1)

    # Update state with the modified list
    tool_context.state["reminders"] = reminders

    return {
        "action": "delete_reminder",
        "index": index,
        "deleted_reminder": deleted_reminder,
        "message": f"Deleted reminder {index}: '{deleted_reminder}'",
    }


def update_user_name(name: str, tool_context: ToolContext) -> dict:
    """Update the user's name.

    Args:
        name: The new name for the user
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    print(f"--- Tool: update_user_name called with '{name}' ---")

    # Get current name from state
    old_name = tool_context.state.get("user_name", "")

    # Update the name in state
    tool_context.state["user_name"] = name

    return {
        "action": "update_user_name",
        "old_name": old_name,
        "new_name": name,
        "message": f"Updated your name to: {name}",
    }


# Create a simple persistent agent
root_agent = Agent(
    name="memory_agent",
    model="gemini-1.5-flash",
    description="A smart reminder agent with persistent memory",
    instruction="""
    You are a friendly reminder assistant that remembers users across conversations.

    The user's information is stored in state.
    - User's name: {user_name|} (if available)
    - Reminders: {reminders|[]}

    You can help users manage their reminders with the following capabilities:
    1. Add new reminders
    2. View existing reminders
    3. Update reminders
    4. Delete reminders
    5. Update the user's name

    Always be friendly and address the user by name if you know it. If you don't know their name yet,
    ask them for it and use the update_user_name tool to store it when they introduce themselves.

    **REMINDER MANAGEMENT GUIDELINES:**

    When dealing with reminders, you need to be smart about finding the right reminder:

    1. **Partial Matching**: If a user refers to a reminder with partial text, find the best match.
       Example: "delete the dentist one" should match "Dentist appointment on Tuesday"

    2. **Context Awareness**: Use context from the conversation to identify reminders.
       Example: If discussing meetings and user says "update the second one", refer to the second meeting-related reminder.

    3. **Fuzzy Matching**: Be flexible with variations in wording.
       Example: "grocery shopping" should match "buy groceries" or "go to the store"

    4. **Confirmation**: When there's ambiguity, show the user what you found and confirm before proceeding.
       Example: "I found 'Call mom at 3pm'. Is this the reminder you want to delete?"

    5. **Error Handling**: If no match is found, suggest viewing all reminders to help the user identify the correct one.

    Remember: Users often refer to reminders casually. Your job is to understand their intent and find the right reminder even with vague references.
    """,
    tools=[
        add_reminder,
        view_reminders,
        update_reminder,
        delete_reminder,
        update_user_name,
    ],
)
