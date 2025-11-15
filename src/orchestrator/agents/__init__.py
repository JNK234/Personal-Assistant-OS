"""
Specialized agents for the orchestrator
"""

from .email_agent import create_email_agent
from .task_agent import create_task_agent
from .general_agent import create_general_agent

__all__ = [
    "create_email_agent",
    "create_task_agent",
    "create_general_agent",
]
