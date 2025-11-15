"""
Voice-First CLI for the Personal Assistant using Google ADK Orchestrator
"""

import asyncio
import os
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from .orchestrator import VoiceOrchestrator
from .session import (
    create_session_id,
    save_message,
    load_session,
    list_sessions,
    get_session_info,
)

# Load environment variables
load_dotenv()

console = Console()


class VoiceCLI:
    """
    Voice-first command-line interface for the personal assistant.
    """

    def __init__(self):
        self.orchestrator: Optional[VoiceOrchestrator] = None
        self.session_id: Optional[str] = None
        self.running = True

        # Check for Google API key
        if not os.getenv("GOOGLE_API_KEY"):
            console.print(
                "[red]Error: GOOGLE_API_KEY not found in environment variables.[/red]"
            )
            console.print(
                "Get your API key from: https://aistudio.google.com/apikey"
            )
            sys.exit(1)

    async def start(self):
        """Start the voice CLI."""
        self.show_welcome()

        # Create a new session
        self.session_id = create_session_id()
        self.orchestrator = VoiceOrchestrator(session_id=self.session_id)

        console.print(
            f"[green]Started new voice session: {self.session_id}[/green]\n"
        )

        await self.repl()

    def show_welcome(self):
        """Display welcome message."""
        welcome = """
# 🎙️ Voice-First Personal Assistant

Powered by Google ADK Multi-Agent Orchestrator

**Available Commands:**
- `/voice` - Start voice mode (coming soon)
- `/new` - Start a new session
- `/resume <id>` - Resume a session
- `/sessions` - List all sessions
- `/info` - Show orchestrator info
- `/help` - Show this help
- `/exit` or `/quit` - Exit

**Agents Available:**
- 📧 EmailAssistant - Gmail operations
- ✅ TaskManager - Todos and reminders
- 💬 GeneralAssistant - Conversation and search

Type your message or command to begin!
        """
        console.print(Panel(Markdown(welcome), title="Welcome", border_style="blue"))

    async def repl(self):
        """Run the Read-Eval-Print Loop."""
        while self.running:
            try:
                # Get user input
                prompt_text = f"[{self.session_id}] > "
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: console.input(prompt_text)
                )

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    await self.handle_command(user_input)
                else:
                    await self.handle_message(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit to quit[/yellow]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")

    async def handle_command(self, command: str):
        """Handle CLI commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None

        if cmd in ["/exit", "/quit"]:
            console.print("[yellow]Goodbye! 👋[/yellow]")
            self.running = False

        elif cmd == "/new":
            self.session_id = create_session_id()
            self.orchestrator = VoiceOrchestrator(session_id=self.session_id)
            console.print(f"[green]New session started: {self.session_id}[/green]")

        elif cmd == "/resume":
            if not args:
                console.print("[red]Usage: /resume <session_id>[/red]")
                return

            session_data = await load_session(args)
            if session_data:
                self.session_id = args
                self.orchestrator = VoiceOrchestrator(session_id=self.session_id)
                console.print(f"[green]Resumed session: {args}[/green]")
                console.print(
                    f"[dim]Loaded {len(session_data['messages'])} messages[/dim]"
                )
            else:
                console.print(f"[red]Session not found: {args}[/red]")

        elif cmd == "/sessions":
            sessions = await list_sessions()
            if sessions:
                console.print("\n[bold]Available Sessions:[/bold]")
                for session in sessions:
                    info = await get_session_info(session["session_id"])
                    console.print(
                        f"  • {session['session_id']} "
                        f"({info['message_count']} messages, "
                        f"last: {info['last_activity']})"
                    )
                console.print()
            else:
                console.print("[dim]No sessions found[/dim]")

        elif cmd == "/info":
            if self.orchestrator:
                info = self.orchestrator.get_session_info()
                console.print("\n[bold]Orchestrator Info:[/bold]")
                console.print(f"  Session: {info['session_id']}")
                console.print(f"  Model: {info['model']}")
                console.print(f"  Coordinator: {info['agents']['coordinator']}")
                console.print("  Sub-agents:")
                for agent in info["agents"]["sub_agents"]:
                    console.print(f"    - {agent}")
                console.print()
            else:
                console.print("[red]No active orchestrator[/red]")

        elif cmd == "/voice":
            console.print(
                "[yellow]Voice mode coming soon! "
                "Will integrate with Gemini Live API for real-time audio.[/yellow]"
            )

        elif cmd == "/help":
            self.show_welcome()

        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")

    async def handle_message(self, message: str):
        """Handle user message through orchestrator."""
        if not self.orchestrator:
            console.print("[red]No active orchestrator. Use /new to start.[/red]")
            return

        # Save user message
        await save_message(self.session_id, "user", message)

        # Process through orchestrator
        console.print()
        response_text = ""

        try:
            async for chunk in self.orchestrator.process_message(message, stream=True):
                console.print(chunk, end="")
                sys.stdout.flush()
                response_text += chunk

            console.print("\n")

            # Save assistant response
            await save_message(self.session_id, "assistant", response_text.strip())

        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")


async def main():
    """Main entry point."""
    cli = VoiceCLI()
    await cli.start()


if __name__ == "__main__":
    asyncio.run(main())
