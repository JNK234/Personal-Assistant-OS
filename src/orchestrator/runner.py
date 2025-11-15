"""
ADK Runtime Integration - Proper async agent execution
"""

import asyncio
from typing import AsyncGenerator, List, Dict, Any
from google.adk.agents import LlmAgent


class AgentRunner:
    """
    Simple runner for executing ADK agents asynchronously.

    This provides a lightweight wrapper around ADK agents for async execution.
    """

    def __init__(self, agent: LlmAgent):
        """
        Initialize the runner with an agent.

        Args:
            agent: The ADK agent to run
        """
        self.agent = agent
        self.conversation_history: List[Dict[str, str]] = []

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
            # Simulate agent processing
            # In a full ADK implementation, this would use the agent's run method
            # with proper session management and tool execution

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

        This is a simplified implementation. In production, you would:
        1. Use ADK's proper runtime/session management
        2. Execute tools if the agent requests them
        3. Handle sub-agent delegation
        4. Manage conversation state

        Args:
            message: User message

        Returns:
            Agent response
        """
        # For now, provide intelligent routing based on message content
        agent_name = self.agent.name.lower()

        # Simple intent detection for demonstration
        message_lower = message.lower()

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
                    f"sending, and searching emails."
                )
            elif any(
                word in message_lower
                for word in ["task", "todo", "remind", "reminder", "schedule"]
            ):
                return (
                    f"I'll route that to the Task Manager. "
                    f"You asked: '{message}'. "
                    f"The Task Agent will help you create todos, set reminders, "
                    f"and manage your schedule."
                )
            else:
                return (
                    f"I'll route that to the General Assistant. "
                    f"You asked: '{message}'. "
                    f"The General Agent will help with conversation, questions, "
                    f"and information lookup."
                )

        elif "email" in agent_name:
            return (
                f"[EmailAgent] Processing: '{message}'. "
                f"I can help with reading emails, sending messages, "
                f"and searching your inbox. "
                f"(Gmail API integration pending)"
            )

        elif "task" in agent_name:
            return (
                f"[TaskAgent] Processing: '{message}'. "
                f"I can help with creating todos, setting reminders, "
                f"and tracking tasks. "
                f"(Task management system pending)"
            )

        elif "general" in agent_name:
            return (
                f"[GeneralAgent] Processing: '{message}'. "
                f"I can chat, answer questions, and search the web. "
                f"How can I help you today?"
            )

        else:
            return f"Received: '{message}'. Agent: {self.agent.name}"

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
