# Voice-First Personal Assistant - Setup Guide

## Overview

This project now includes a **voice-first, low-latency multi-agent orchestrator** powered by Google's Agent Development Kit (ADK).

## Architecture

```
Voice Orchestrator (Coordinator)
├── Email Assistant (Gmail operations)
├── Task Manager (Todos & reminders)
└── General Assistant (Chat & search)
```

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy the key

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### 4. Run the Voice Assistant

```bash
uv run voice-assistant
```

Or:

```bash
python -m src.voice_cli
```

## Available Commands

### CLI Commands

- `/voice` - Start voice mode (streaming audio - coming soon)
- `/new` - Start a new session
- `/resume <id>` - Resume a previous session
- `/sessions` - List all saved sessions
- `/info` - Show orchestrator information
- `/help` - Show help message
- `/exit` or `/quit` - Exit the application

### Natural Language

Just type naturally! The orchestrator will route your request to the right agent:

**Email Operations:**
- "Check my email"
- "Send an email to John"
- "Search for emails from last week"

**Task Management:**
- "Add a todo: buy groceries"
- "Remind me to call mom tomorrow"
- "Show my tasks"

**General Chat:**
- "What's the weather like?"
- "Tell me about quantum computing"
- "How do I cook pasta?"

## Architecture Details

### Agents

1. **VoiceCoordinator** (Main orchestrator)
   - Routes requests to specialized agents
   - Uses `gemini-2.0-flash-exp` model
   - Manages conversation context

2. **EmailAssistant**
   - Handles Gmail operations
   - Read, send, search emails
   - Requires confirmation before sending

3. **TaskManager**
   - Manages todos and reminders
   - Natural language task creation
   - Task tracking and scheduling

4. **GeneralAssistant**
   - General conversation
   - Web search integration
   - Information lookup

### Voice Streaming (Coming Soon)

The system includes a `VoiceStreamer` class for bidirectional audio streaming with Gemini Live API:

- Low-latency voice input → text transcription
- Text → voice output
- Bidirectional streaming for natural conversation
- Voice activity detection (VAD)

## Development

### Project Structure

```
src/
├── orchestrator/           # Multi-agent orchestrator
│   ├── engine.py          # Main coordinator
│   ├── runner.py          # Async agent execution
│   └── agents/            # Specialized agents
│       ├── email_agent.py
│       ├── task_agent.py
│       └── general_agent.py
├── voice/                  # Voice I/O (streaming)
│   └── streaming.py
├── voice_cli.py           # Voice CLI interface
├── cli.py                 # Original CLI (Claude)
└── session.py             # Session persistence
```

### Adding New Agents

Create a new agent in `src/orchestrator/agents/`:

```python
from google.adk.agents import LlmAgent

def create_my_agent() -> LlmAgent:
    return LlmAgent(
        name="MyAgent",
        model="gemini-2.0-flash-exp",
        description="What this agent does",
        instruction="Detailed instructions for the agent",
        tools=[],  # Add tools here
    )
```

Then add it to the coordinator in `engine.py`:

```python
self.my_agent = create_my_agent()

self.coordinator = LlmAgent(
    # ...
    sub_agents=[
        self.email_agent,
        self.task_agent,
        self.general_agent,
        self.my_agent,  # Add here
    ],
)
```

## Roadmap

- [x] Multi-agent orchestrator with ADK
- [x] Email agent structure
- [x] Task agent structure
- [x] General assistant agent
- [x] CLI interface
- [ ] Gmail API integration
- [ ] Task persistence system
- [ ] Voice streaming (Gemini Live API)
- [ ] Voice activity detection
- [ ] Web UI for voice chat
- [ ] Calendar integration
- [ ] Mobile app

## Troubleshooting

### "GOOGLE_API_KEY not found"

Make sure you've:
1. Created a `.env` file (copy from `.env.example`)
2. Added your Google API key
3. The key is valid and active

### Import errors

Run:
```bash
uv sync
```

Or reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Session errors

Sessions are stored in `sessions/` directory. If you encounter errors:

```bash
rm -rf sessions/
```

Then restart the application.

## Learn More

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)
- [Google ADK Python](https://github.com/google/adk-python)

## License

MIT
