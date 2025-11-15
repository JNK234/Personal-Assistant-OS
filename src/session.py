# ABOUTME: Session persistence management for conversation history
# ABOUTME: Handles saving, loading, and managing chat sessions in JSON format

import json
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import SESSIONS_DIR


def create_session_id() -> str:
    """
    Generate a unique session ID based on current timestamp.

    Returns:
        Session ID in format: YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_session_path(session_id: str) -> Path:
    """
    Get the file path for a session.

    Args:
        session_id: The session identifier

    Returns:
        Path object pointing to the session file
    """
    return SESSIONS_DIR / f"{session_id}.json"


async def save_message(session_id: str, role: str, content: str) -> None:
    """
    Append a message to a session file.

    Args:
        session_id: The session identifier
        role: Message role ('user' or 'assistant')
        content: The message content
    """
    session_path = get_session_path(session_id)

    # Load existing session or create new one
    if session_path.exists():
        async with aiofiles.open(session_path, 'r') as f:
            data = json.loads(await f.read())
    else:
        data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

    # Append new message
    data["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    # Save back to file
    async with aiofiles.open(session_path, 'w') as f:
        await f.write(json.dumps(data, indent=2))


async def load_session(session_id: str) -> list[dict]:
    """
    Load all messages from a session.

    Args:
        session_id: The session identifier

    Returns:
        List of message dictionaries with 'role', 'content', and 'timestamp'

    Raises:
        FileNotFoundError: If session doesn't exist
    """
    session_path = get_session_path(session_id)

    if not session_path.exists():
        raise FileNotFoundError(f"Session '{session_id}' not found")

    async with aiofiles.open(session_path, 'r') as f:
        data = json.loads(await f.read())

    return data["messages"]


async def list_sessions() -> list[dict]:
    """
    List all available sessions with metadata.

    Returns:
        List of dictionaries containing session metadata:
        - session_id: The session identifier
        - created_at: Session creation timestamp
        - message_count: Number of messages in the session
        - last_message_at: Timestamp of last message
    """
    sessions = []

    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            async with aiofiles.open(session_file, 'r') as f:
                data = json.loads(await f.read())

            sessions.append({
                "session_id": data["session_id"],
                "created_at": data["created_at"],
                "message_count": len(data["messages"]),
                "last_message_at": data["messages"][-1]["timestamp"] if data["messages"] else data["created_at"]
            })
        except (json.JSONDecodeError, KeyError):
            # Skip invalid session files
            continue

    # Sort by last message time, most recent first
    sessions.sort(key=lambda x: x["last_message_at"], reverse=True)

    return sessions


def session_exists(session_id: str) -> bool:
    """
    Check if a session exists.

    Args:
        session_id: The session identifier

    Returns:
        True if session exists, False otherwise
    """
    return get_session_path(session_id).exists()


async def get_session_info(session_id: str) -> Optional[dict]:
    """
    Get metadata about a specific session.

    Args:
        session_id: The session identifier

    Returns:
        Dictionary with session metadata or None if not found
    """
    session_path = get_session_path(session_id)

    if not session_path.exists():
        return None

    async with aiofiles.open(session_path, 'r') as f:
        data = json.loads(await f.read())

    return {
        "session_id": data["session_id"],
        "created_at": data["created_at"],
        "message_count": len(data["messages"]),
        "last_message_at": data["messages"][-1]["timestamp"] if data["messages"] else data["created_at"]
    }
