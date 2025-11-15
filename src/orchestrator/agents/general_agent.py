"""
General Agent - Handles conversation, memory recall, and general questions
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search


def create_general_agent() -> LlmAgent:
    """
    Creates a general-purpose conversational agent.

    This agent handles:
    - General conversation
    - Information retrieval via web search
    - Memory and context awareness
    - Answering questions
    """
    return LlmAgent(
        name="GeneralAssistant",
        model="gemini-2.0-flash-exp",
        description=(
            "A friendly conversational assistant that can chat, answer questions, "
            "and search the web for information. Use this agent for general queries, "
            "casual conversation, and information lookup."
        ),
        instruction="""You are a helpful, friendly personal assistant.

Your capabilities:
- Engage in natural, warm conversation
- Answer questions using your knowledge or web search
- Remember context from the conversation
- Provide concise, accurate responses

Keep responses brief and conversational for voice interactions.
Always be helpful and proactive.""",
        tools=[google_search],
    )
