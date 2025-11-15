"""
ADK Runtime Integration - Async agent execution with Google ADK

NOTE: This is currently a simplified implementation that uses keyword-based routing.
For production use, this should be replaced with proper ADK agent execution using
Google's Agent runtime and session management.
"""

import asyncio
import os
from typing import AsyncGenerator, List, Dict, Any
from google.adk.agents import LlmAgent
import google.generativeai as genai


class AgentRunner:
    """
    Runner for executing ADK agents asynchronously.

    This provides async execution of Google ADK agents with conversation history
    and streaming support.

    NOTE: Current implementation uses simplified routing logic. For full ADK
    integration, use google.adk.Runtime with proper session management.
    """

    def __init__(self, agent: LlmAgent):
        """
        Initialize the runner with an agent.

        Args:
            agent: The ADK agent to run
        """
        self.agent = agent
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize Google Generative AI
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(agent.model)
        else:
            self._model = None

    async def run(
        self, user_message: str, stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Run the agent with a user message.

        Args:
            user_message: Message from the user
            stream: Whether to stream the response

        Yields:
            Response chunks from the agent
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            response = await self._execute_agent(user_message)

            # Add assistant response to history
            self.conversation_history.append(
                {"role": "assistant", "content": response}
            )

            if stream:
                # Stream word by word for voice-friendly output
                words = response.split()
                for i, word in enumerate(words):
                    # Add space except for last word
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
            else:
                yield response

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            yield error_msg

    async def _execute_agent(self, message: str) -> str:
        """
        Execute the agent with the message.

        Uses Google Gemini API if available, falls back to mock routing otherwise.

        Args:
            message: User message

        Returns:
            Agent response
        """
        # Try to use real Gemini API if configured
        if self._model:
            try:
                # Build context from agent's instruction and history
                system_prompt = self.agent.instruction if hasattr(self.agent, 'instruction') else ""

                # Format conversation history for Gemini
                chat_history = []
                for msg in self.conversation_history[-10:]:  # Last 10 messages for context
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

                # Add system prompt as first user message if present
                if system_prompt:
                    prompt = f"{system_prompt}\n\nUser: {message}"
                else:
                    prompt = message

                # Generate response using Gemini
                response = await asyncio.to_thread(
                    self._model.generate_content,
                    prompt
                )

                return response.text

            except Exception as e:
                # Fall back to mock mode if API fails
                return await self._mock_agent_response(message, error=str(e))

        # Fall back to mock mode if no API key
        return await self._mock_agent_response(message)

    async def _mock_agent_response(self, message: str, error: str = None) -> str:
        """
        Provide mock responses based on keyword routing.

        This is a fallback when real ADK execution is not available.

        Args:
            message: User message
            error: Optional error message to include

        Returns:
            Mock response
        """
        agent_name = self.agent.name.lower()
        message_lower = message.lower()

        error_note = f"\n\n(Note: Using mock mode{f' due to: {error}' if error else ''})" if error else ""

        if "coordinator" in agent_name:
            # Route to appropriate sub-agent based on keywords
            if any(
                word in message_lower
                for word in ["email", "gmail", "send", "inbox", "message"]
            ):
                return (
                    f"I'll route that to the Email Assistant. "
                    f"You asked: '{message}'. "
                    f"The Email Agent will handle operations like reading, "
                    f"sending, and searching emails.{error_note}"
                )
            elif any(
                word in message_lower
                for word in ["task", "todo", "remind", "reminder", "schedule"]
            ):
                return (
                    f"I'll route that to the Task Manager. "
                    f"You asked: '{message}'. "
                    f"The Task Agent will help you create todos, set reminders, "
                    f"and manage your schedule.{error_note}"
                )
            else:
                return (
                    f"I'll route that to the General Assistant. "
                    f"You asked: '{message}'. "
                    f"The General Agent will help with conversation, questions, "
                    f"and information lookup.{error_note}"
                )

        elif "email" in agent_name:
            return (
                f"[EmailAgent] Processing: '{message}'. "
                f"I can help with reading emails, sending messages, "
                f"and searching your inbox. "
                f"(Gmail API integration pending){error_note}"
            )

        elif "task" in agent_name:
            return (
                f"[TaskAgent] Processing: '{message}'. "
                f"I can help with creating todos, setting reminders, "
                f"and tracking tasks. "
                f"(Task management system pending){error_note}"
            )

        elif "general" in agent_name:
            return (
                f"[GeneralAgent] Processing: '{message}'. "
                f"I can chat, answer questions, and search the web. "
                f"How can I help you today?{error_note}"
            )

        else:
            return f"Received: '{message}'. Agent: {self.agent.name}{error_note}"

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of messages
        """
        return self.conversation_history

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
