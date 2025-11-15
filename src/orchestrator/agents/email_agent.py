"""
Email Agent - Handles Gmail operations
"""

from google.adk.agents import LlmAgent


def create_email_agent() -> LlmAgent:
    """
    Creates an email management agent.

    This agent handles:
    - Reading emails
    - Composing and sending emails
    - Searching inbox
    - Email summarization
    """
    return LlmAgent(
        name="EmailAssistant",
        model="gemini-2.0-flash-exp",
        description=(
            "An email management specialist that helps with Gmail operations. "
            "Use this agent when the user wants to read, send, search, or manage emails. "
            "Keywords: email, gmail, send, inbox, message, reply"
        ),
        instruction="""You are an email management assistant with access to Gmail.

Your capabilities:
- Read and summarize recent emails
- Compose and send emails with user approval
- Search through inbox
- Provide email summaries and insights
- Draft replies and responses

IMPORTANT: Always confirm before sending emails. For voice interactions,
read email content clearly and ask for explicit confirmation before any send operation.

Be concise in summaries but thorough in content when needed.""",
        tools=[],  # Will add Gmail tools later
    )
