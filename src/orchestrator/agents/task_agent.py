"""
Task Agent - Handles todos, reminders, and task management
"""

from google.adk.agents import LlmAgent


def create_task_agent() -> LlmAgent:
    """
    Creates a task management agent.

    This agent handles:
    - Creating and managing todos
    - Setting reminders
    - Tracking task status
    - Task prioritization
    """
    return LlmAgent(
        name="TaskManager",
        model="gemini-2.0-flash-exp",
        description=(
            "A task management specialist that helps organize todos, set reminders, "
            "and track tasks. Use this agent when the user wants to create tasks, "
            "set reminders, check their todo list, or manage their schedule."
        ),
        instruction="""You are a proactive task management assistant.

Your capabilities:
- Create and organize todo items from voice commands
- Set reminders with natural language (e.g., "remind me tomorrow at 3pm")
- Track task completion and status
- Suggest task prioritization
- Provide task summaries

Always confirm task details before creating them. For voice interactions,
be concise and acknowledge task creation clearly.""",
        tools=[],  # Will add custom task tools later
    )
