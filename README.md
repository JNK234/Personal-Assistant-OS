# Claude Agent SDK CLI Chatbot

A Python-based interactive CLI chatbot powered by Claude Agent SDK with session persistence and file operation capabilities.

## Features

- **Interactive REPL Interface**: Chat with Claude in a terminal
- **Session Persistence**: Conversations are automatically saved and can be resumed
- **File Operations**: Claude can read, write, and edit files when needed
- **Streaming Responses**: Real-time response streaming for better UX
- **Simple Architecture**: Clean, modular design that's easy to understand and extend

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Anthropic API Key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd personal-assistant-os
```

2. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

Start the chatbot:
```bash
uv run chatbot
```

Or alternatively:
```bash
uv run python -m src.cli
```

### Available Commands

- `/new` - Start a new chat session
- `/resume <session_id>` - Resume an existing session
- `/sessions` - List all saved sessions
- `/help` - Display available commands
- `/exit` or `/quit` - Exit the application

### Examples

**Basic Chat:**
```
[20250117_143022] > Hello! What can you do?

Hi! I'm Claude, and I can help you with various tasks...
```

**File Operations:**
```
[20250117_143022] > Read the README.md file

Let me read that file for you.
[Using tool: Read with input: {"file_path": "README.md"}]

Here's the content of README.md:
...
```

**Resume Session:**
```
[20250117_143022] > /resume 20250117_140000

Resumed session: 20250117_140000
Previous messages loaded: 12

[20250117_140000] > Continue our previous discussion...
```

## Project Structure

```
claude-chatbot/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore patterns
├── src/
│   ├── __init__.py             # Package marker
│   ├── config.py               # Configuration & environment
│   ├── agent.py                # Claude Agent SDK wrapper
│   ├── session.py              # Session persistence logic
│   └── cli.py                  # Main entry point & REPL
└── sessions/                    # Stored conversations (gitignored)
```

## Extension for Web Applications

The architecture is designed to be framework-agnostic. The `agent.py` module can be easily integrated into web frameworks like FastAPI or Flask:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from src.agent import chat

app = FastAPI()

@app.post("/chat")
async def web_chat(message: str, session_id: str = None):
    async def generate():
        async for chunk in chat(message, session_id):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## License

MIT
