"""
Voice Orchestrator Engine - Main coordinator using Google ADK
"""

import os
from typing import AsyncGenerator, Optional, List, Dict
from google.adk.agents import LlmAgent

from .agents import create_email_agent, create_task_agent, create_general_agent


class VoiceOrchestrator:
    """
    Main orchestrator that coordinates specialized agents using Google ADK.

    This orchestrator uses an LLM-based coordinator that intelligently routes
    requests to specialized sub-agents based on user intent.
    """

    def __init__(self, session_id: Optional[str] = None, history: Optional[List[Dict]] = None):
        """
        Initialize the voice orchestrator.

        Args:
            session_id: Optional session ID for conversation persistence
            history: Optional conversation history to restore context
        """
        self.session_id = session_id
        self._initial_history = history or []

        # Create specialized agents
        self.email_agent = create_email_agent()
        self.task_agent = create_task_agent()
        self.general_agent = create_general_agent()

        # Create the main coordinator agent
        self.coordinator = self._create_coordinator()

    def _create_coordinator(self) -> LlmAgent:
        """
        Create the main coordinator agent that routes to sub-agents.

        Returns:
            LlmAgent configured as a coordinator
        """
        return LlmAgent(
            name="VoiceCoordinator",
            model="gemini-2.0-flash-exp",
            description=(
                "I am your personal voice assistant coordinator. "
                "I intelligently route your requests to specialized agents "
                "for email, tasks, or general assistance."
            ),
            instruction="""You are the primary coordinator for a voice-first personal assistant.

Your role is to:
1. Listen to user requests
2. Understand their intent
3. Route to the appropriate specialist agent:
   - EmailAssistant: for email operations (reading, sending, searching)
   - TaskManager: for todos, reminders, and task management
   - GeneralAssistant: for conversation, questions, and general queries

4. Synthesize responses from sub-agents into natural voice-friendly output

Guidelines for voice interactions:
- Be concise and clear
- Avoid long paragraphs - use short sentences
- Confirm actions before executing them (especially emails, tasks)
- Acknowledge understanding ("Got it", "Sure thing", etc.)
- Be proactive and helpful

When routing:
- Email keywords: email, gmail, send, inbox, message, reply, compose
- Task keywords: todo, task, remind, reminder, schedule, appointment
- General: everything else (chat, questions, search, help)

Always maintain context across the conversation and remember what the user has said.""",
            sub_agents=[
                self.email_agent,
                self.task_agent,
                self.general_agent,
            ],
        )

    async def process_message(
        self, message: str, stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Process a message through the orchestrator.

        Args:
            message: User message to process
            stream: Whether to stream the response

        Yields:
            Response chunks from the agent
        """
        try:
            # Use the agent runner for async execution
            from .runner import AgentRunner

            if not hasattr(self, "_runner"):
                self._runner = AgentRunner(self.coordinator)

                # Load initial history if available
                if self._initial_history:
                    self._runner.conversation_history = self._initial_history.copy()

            # Run the coordinator and stream results
            async for chunk in self._runner.run(message, stream=stream):
                yield chunk

        except Exception as e:
            yield f"Sorry, I encountered an error: {str(e)}"

    def get_session_info(self) -> dict:
        """
        Get information about the current orchestrator session.

        Returns:
            Dictionary with session information
        """
        return {
            "session_id": self.session_id,
            "agents": {
                "coordinator": self.coordinator.name,
                "sub_agents": [
                    self.email_agent.name,
                    self.task_agent.name,
                    self.general_agent.name,
                ],
            },
            "model": self.coordinator.model,
        }
