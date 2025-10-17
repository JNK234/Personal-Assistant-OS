# ABOUTME: Claude Agent SDK wrapper for chat interactions
# ABOUTME: Handles streaming responses and session management

from typing import AsyncGenerator, Optional
from claude_agent_sdk import query, ClaudeAgentOptions
from pathlib import Path

from .config import (
    MODEL_NAME,
    ALLOWED_TOOLS,
    SYSTEM_PROMPT,
    PERMISSION_MODE
)


async def chat(
    prompt: str,
    session_id: Optional[str] = None,
    continue_session: bool = False
) -> AsyncGenerator[str, None]:
    """
    Send a message to Claude and yield response tokens as they arrive.

    Args:
        prompt: User's message
        session_id: Optional session ID for persistence
        continue_session: Whether to continue a previous session

    Yields:
        Text chunks from Claude's response, including tool usage information
    """
    # Configure agent options
    options = ClaudeAgentOptions(
        model=MODEL_NAME,
        allowed_tools=ALLOWED_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        permission_mode=PERMISSION_MODE,
        cwd=Path.cwd(),  # Use current working directory
    )

    # Send query and stream responses
    async for message in query(prompt=prompt, options=options):
        # Get the message type name
        message_type = type(message).__name__

        # Only process ResultMessage which contains the final response
        if message_type == 'ResultMessage':
            # Extract the result text from the ResultMessage
            if hasattr(message, 'result') and message.result:
                yield message.result

        # Handle AssistantMessage for streaming chunks
        elif message_type == 'AssistantMessage':
            if hasattr(message, 'message') and hasattr(message.message, 'content'):
                for block in message.message.content:
                    block_type = type(block).__name__
                    if block_type == 'TextBlock' and hasattr(block, 'text'):
                        yield block.text
            elif hasattr(message, 'text'):
                yield message.text

        # Skip SystemMessage and other internal messages
        # These are for debugging/metadata and not user-facing content


async def get_agent_info() -> dict:
    """
    Get information about the agent configuration.

    Returns:
        Dictionary with agent configuration details
    """
    return {
        "model": MODEL_NAME,
        "allowed_tools": ALLOWED_TOOLS,
        "permission_mode": PERMISSION_MODE,
        "system_prompt_length": len(SYSTEM_PROMPT) if SYSTEM_PROMPT else 0
    }
