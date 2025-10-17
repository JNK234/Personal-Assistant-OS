# ABOUTME: CLI interface providing REPL-style interactive chat with Claude
# ABOUTME: Handles user input, commands, and displays streaming responses

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .agent import chat, get_agent_info
from .session import (
    create_session_id,
    save_message,
    load_session,
    list_sessions,
    session_exists,
    get_session_info
)

console = Console()


def display_welcome():
    """Display welcome message and available commands."""
    welcome_text = """
# Welcome to Claude Agent SDK Chatbot!

A powerful CLI chatbot with session persistence and file operations.

**Available Commands:**
- `/new` - Start a new chat session
- `/resume <session_id>` - Resume an existing session
- `/sessions` - List all saved sessions
- `/info` - Show current session and agent information
- `/help` - Display this help message
- `/exit` or `/quit` - Exit the application

**Tips:**
- All conversations are automatically saved
- You can resume any previous session using `/resume`
- Claude can read, write, and edit files when you ask
    """
    console.print(Panel(Markdown(welcome_text), title="Claude Chatbot", border_style="blue"))


async def handle_command(command: str, current_session: str) -> tuple[str, bool]:
    """
    Handle special commands.

    Args:
        command: The command string (including leading /)
        current_session: Current session ID

    Returns:
        Tuple of (new_session_id, should_continue)
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    # Exit commands
    if cmd in ['/exit', '/quit']:
        console.print("\n[yellow]Goodbye![/yellow]")
        return current_session, False

    # Help command
    elif cmd == '/help':
        display_welcome()
        return current_session, True

    # New session command
    elif cmd == '/new':
        new_session = create_session_id()
        console.print(f"\n[green]✓ Started new session: {new_session}[/green]")
        return new_session, True

    # Resume session command
    elif cmd == '/resume':
        if len(parts) < 2:
            console.print("[red]✗ Usage: /resume <session_id>[/red]")
            return current_session, True

        session_id = parts[1]
        if not session_exists(session_id):
            console.print(f"[red]✗ Session '{session_id}' not found[/red]")
            console.print("Use /sessions to see available sessions")
            return current_session, True

        info = await get_session_info(session_id)
        console.print(f"\n[green]✓ Resumed session: {session_id}[/green]")
        console.print(f"  Messages: {info['message_count']}")
        console.print(f"  Last active: {info['last_message_at']}")
        return session_id, True

    # List sessions command
    elif cmd == '/sessions':
        sessions = list_sessions()
        if not sessions:
            console.print("\n[yellow]No sessions found[/yellow]")
            return current_session, True

        table = Table(title="Saved Sessions", show_header=True, header_style="bold cyan")
        table.add_column("Session ID", style="green")
        table.add_column("Created", style="blue")
        table.add_column("Messages", justify="right")
        table.add_column("Last Active", style="yellow")

        for session in sessions[:20]:  # Show last 20 sessions
            table.add_row(
                session['session_id'],
                session['created_at'][:19],
                str(session['message_count']),
                session['last_message_at'][:19]
            )

        console.print()
        console.print(table)
        if len(sessions) > 20:
            console.print(f"\n[dim]Showing 20 of {len(sessions)} sessions[/dim]")
        return current_session, True

    # Info command
    elif cmd == '/info':
        info = await get_agent_info()
        session_info = await get_session_info(current_session)

        console.print("\n[bold cyan]Current Session:[/bold cyan]")
        console.print(f"  ID: {current_session}")
        if session_info:
            console.print(f"  Messages: {session_info['message_count']}")
            console.print(f"  Created: {session_info['created_at'][:19]}")

        console.print("\n[bold cyan]Agent Configuration:[/bold cyan]")
        console.print(f"  Model: {info['model']}")
        console.print(f"  Permission Mode: {info['permission_mode']}")
        console.print(f"  Allowed Tools: {', '.join(info['allowed_tools'])}")
        return current_session, True

    # Unknown command
    else:
        console.print(f"[red]✗ Unknown command: {cmd}[/red]")
        console.print("Type /help to see available commands")
        return current_session, True


async def run_repl():
    """Main REPL loop for interactive chat."""
    # Display welcome message
    display_welcome()

    # Create initial session
    current_session = create_session_id()
    console.print(f"\n[dim]Session started: {current_session}[/dim]")

    # Main loop
    while True:
        try:
            # Get user input
            console.print()
            user_input = console.input(f"[bold blue][{current_session[:8]}] >[/bold blue] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith('/'):
                current_session, should_continue = await handle_command(user_input, current_session)
                if not should_continue:
                    break
                continue

            # Save user message
            await save_message(current_session, "user", user_input)

            # Get response from Claude
            console.print()
            response_parts = []

            try:
                async for chunk in chat(user_input, current_session, continue_session=True):
                    console.print(chunk, end="", highlight=False)
                    response_parts.append(chunk)
                    sys.stdout.flush()

                # Save assistant response
                full_response = "".join(response_parts)
                if full_response.strip():
                    await save_message(current_session, "assistant", full_response)

                console.print()  # New line after response

            except Exception as e:
                console.print(f"\n[red]✗ Error: {str(e)}[/red]")
                console.print("[yellow]Please check your API key and internet connection[/yellow]")

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Use /exit or /quit to exit properly[/yellow]")
            continue
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]✗ Unexpected error: {str(e)}[/red]")
            continue


def main():
    """Entry point for the CLI application."""
    try:
        asyncio.run(run_repl())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
