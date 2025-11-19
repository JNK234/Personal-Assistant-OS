# CLAUDE.md - AI Assistant Developer Guide

This document provides comprehensive guidance for AI assistants (like Claude Code) working with the Personal Assistant OS codebase. It covers the codebase structure, development workflows, conventions, and known issues.

**Last Updated**: 2025-11-19

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Development Environment](#development-environment)
4. [Code Conventions](#code-conventions)
5. [Architecture Guide](#architecture-guide)
6. [Working with Sessions](#working-with-sessions)
7. [Known Issues & Gotchas](#known-issues--gotchas)
8. [Development Workflows](#development-workflows)
9. [Testing Guidelines](#testing-guidelines)
10. [File Reference](#file-reference)

---

## Project Overview

**Personal Assistant OS** is a voice-first, low-latency personal assistant with two distinct operational modes:

1. **Voice Assistant** - Google ADK multi-agent orchestrator (Primary focus)
2. **Claude Chatbot** - Claude Agent SDK with file operations (Legacy/Alternative)

### Key Features

- **Multi-Agent Orchestration**: Intelligent routing to specialized agents (Email, Task, General)
- **Voice-First Design**: Optimized for voice interactions with streaming responses
- **Session Persistence**: JSON-based conversation history
- **Async Architecture**: Built on asyncio for non-blocking operations
- **Low Latency**: Sub-500ms response times with streaming

### Technology Stack

- **Python**: 3.11+ (using modern type hints and async/await)
- **Package Manager**: `uv` (preferred) or pip
- **AI Frameworks**:
  - Google ADK (google-adk) for voice orchestrator
  - Claude Agent SDK (claude-agent-sdk) for chatbot
- **LLM Models**:
  - `gemini-2.0-flash-exp` for voice assistant
  - `claude-sonnet-4-20250514` for chatbot
- **Session Storage**: JSON files in `sessions/` directory
- **UI/UX**: Rich terminal UI with streaming output

---

## Repository Structure

```
Personal-Assistant-OS/
├── src/                          # Main application code
│   ├── __init__.py
│   ├── config.py                 # Configuration & environment variables
│   ├── session.py                # Session persistence (load/save/list)
│   ├── agent.py                  # Claude Agent SDK wrapper
│   ├── cli.py                    # Claude chatbot CLI (legacy)
│   ├── voice_cli.py              # Voice assistant CLI (primary)
│   └── orchestrator/             # Voice orchestrator components
│       ├── __init__.py
│       ├── engine.py             # VoiceOrchestrator - main coordinator
│       ├── runner.py             # AgentRunner - async execution
│       └── agents/               # Specialized agent definitions
│           ├── __init__.py
│           ├── email_agent.py    # EmailAssistant
│           ├── task_agent.py     # TaskManager
│           └── general_agent.py  # GeneralAssistant
├── sessions/                     # Session storage (gitignored)
│   └── *.json                    # Individual session files
├── .env.example                  # Environment variable template
├── pyproject.toml                # Project metadata & dependencies
├── uv.lock                       # Dependency lock file
├── README.md                     # User-facing documentation
├── VOICE_SETUP.md               # Voice assistant setup guide
├── CODE_REVIEW.md               # Comprehensive code review
├── IMPLEMENTATION_SUMMARY.md    # Implementation notes
└── CLAUDE.md                     # This file
```

### Important Directories

- **src/**: All Python source code
- **src/orchestrator/**: Voice assistant orchestrator logic
- **src/orchestrator/agents/**: Individual agent implementations
- **sessions/**: Persisted conversation history (auto-created, gitignored)

---

## Development Environment

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or pip
- Google API Key (for voice assistant)
- Anthropic API Key (optional, for Claude chatbot)

### Setup

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install dependencies**:
```bash
uv sync
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Required environment variables**:
```env
# For Voice Assistant (required)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# For Claude Chatbot (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Running the Application

**Voice Assistant** (primary):
```bash
uv run voice-assistant
# OR
python -m src.voice_cli
```

**Claude Chatbot** (alternative):
```bash
uv run chatbot
# OR
python -m src.cli
```

---

## Code Conventions

### File Headers

Many files include `# ABOUTME:` comments at the top describing their purpose:

```python
# ABOUTME: Session persistence management for conversation history
# ABOUTME: Handles saving, loading, and managing chat sessions in JSON format
```

**Convention for AI Assistants**: When creating new files, add ABOUTME comments to help with codebase navigation.

### Type Hints

All functions use modern Python type hints:

```python
async def load_session(session_id: str) -> list[dict]:
    """Load all messages from a session."""
    ...

def create_email_agent() -> LlmAgent:
    """Create the email assistant agent."""
    ...
```

**Convention**: Always include type hints for function parameters and return values.

### Async/Await Patterns

The codebase uses async/await extensively:

- **Session I/O**: All session operations are async (uses `aiofiles`)
- **Agent Processing**: Message processing is async with streaming
- **CLI Loops**: REPL loops use async/await

**Important**: Mixing sync and async incorrectly is a common source of bugs (see Known Issues).

### Docstrings

Functions use Google-style docstrings:

```python
async def save_message(session_id: str, role: str, content: str) -> None:
    """
    Append a message to a session file.

    Args:
        session_id: The session identifier
        role: Message role ('user' or 'assistant')
        content: The message content
    """
    ...
```

### Module Exports

Modules use `__all__` in `__init__.py`:

```python
# src/orchestrator/agents/__init__.py
from .email_agent import create_email_agent
from .task_agent import create_task_agent
from .general_agent import create_general_agent

__all__ = [
    'create_email_agent',
    'create_task_agent',
    'create_general_agent',
]
```

---

## Architecture Guide

### Two-Mode Architecture

The application supports two distinct modes:

1. **Voice Assistant Mode** (`src/voice_cli.py`):
   - Uses Google ADK multi-agent orchestrator
   - Primary mode for voice-first interactions
   - Routes to specialized agents (Email, Task, General)

2. **Claude Chatbot Mode** (`src/cli.py`):
   - Uses Claude Agent SDK
   - Legacy/alternative mode
   - Single-agent architecture

### Voice Orchestrator Architecture

```
User Input
    ↓
voice_cli.py (REPL)
    ↓
VoiceOrchestrator (engine.py)
    ↓
AgentRunner (runner.py)
    ↓
├─→ EmailAssistant (agents/email_agent.py)
├─→ TaskManager (agents/task_agent.py)
└─→ GeneralAssistant (agents/general_agent.py)
    ↓
Response Stream
```

### Key Components

#### VoiceOrchestrator (src/orchestrator/engine.py)

**Purpose**: Main coordinator that manages specialized agents

**Key Methods**:
- `__init__(session_id, history)`: Initialize with optional session context
- `process_message(message, stream=True)`: Process user input and stream response
- `get_session_info()`: Get metadata about current session

**Location**: `src/orchestrator/engine.py:12-136`

#### AgentRunner (src/orchestrator/runner.py)

**Purpose**: Async execution wrapper for agents

**Key Methods**:
- `run(message, stream=True)`: Execute agent with message and stream results
- Maintains conversation history

**Note**: Currently uses keyword-based routing as a temporary implementation (see Known Issues).

**Location**: `src/orchestrator/runner.py:25-145`

#### Session Management (src/session.py)

**Purpose**: Persist conversation history to JSON files

**Key Functions**:
- `create_session_id()`: Generate timestamp-based session ID
- `save_message(session_id, role, content)`: Append message to session
- `load_session(session_id)`: Load all messages from session
- `list_sessions()`: List all available sessions with metadata
- `session_exists(session_id)`: Check if session exists

**Storage Format**:
```json
{
  "session_id": "20250119_143022",
  "created_at": "2025-01-19T14:30:22.123456",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-01-19T14:30:22.123456"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2025-01-19T14:30:25.789012"
    }
  ]
}
```

**Location**: `src/session.py:1-165`

### Agent Creation Pattern

Each specialized agent follows this pattern:

```python
from google.adk.agents import LlmAgent

def create_<agent>_agent() -> LlmAgent:
    return LlmAgent(
        name="AgentName",
        model="gemini-2.0-flash-exp",
        description="Brief description for coordinator",
        instruction="Detailed behavior instructions",
        tools=[],  # Agent-specific tools
    )
```

**Locations**:
- Email: `src/orchestrator/agents/email_agent.py`
- Task: `src/orchestrator/agents/task_agent.py`
- General: `src/orchestrator/agents/general_agent.py`

---

## Working with Sessions

### Session Lifecycle

1. **Creation**: When user starts new conversation
   ```python
   session_id = create_session_id()  # "20250119_143022"
   ```

2. **Saving Messages**: After each user/assistant exchange
   ```python
   await save_message(session_id, "user", user_message)
   await save_message(session_id, "assistant", assistant_response)
   ```

3. **Resuming**: Loading previous conversation
   ```python
   messages = await load_session(session_id)
   orchestrator = VoiceOrchestrator(session_id=session_id, history=messages)
   ```

4. **Listing**: Viewing all sessions
   ```python
   sessions = await list_sessions()
   # Returns list sorted by last_message_at (most recent first)
   ```

### Session File Location

- Directory: `sessions/` (auto-created)
- Format: `{session_id}.json`
- Example: `sessions/20250119_143022.json`
- **Gitignored**: Session files are never committed

### Important Session Details

- **Session IDs**: Format `YYYYMMDD_HHMMSS` (timestamp-based)
- **Async Operations**: All session I/O is async (uses aiofiles)
- **Error Handling**: Missing sessions raise `FileNotFoundError`
- **Sorting**: Sessions listed by `last_message_at` (newest first)

---

## Known Issues & Gotchas

### Critical Bugs (From CODE_REVIEW.md)

#### Bug #1: Async/Sync Mismatch in list_sessions()

**Location**: `src/session.py:94` and `src/voice_cli.py:146`

**Problem**: `list_sessions()` is declared as async but implemented synchronously.

**Current Code**:
```python
# src/session.py:94 - Declared as async
async def list_sessions() -> list[dict]:
    sessions = []
    for session_file in SESSIONS_DIR.glob("*.json"):  # Sync file I/O!
        # ...
```

**Status**: FIXED in session.py (now properly async with aiofiles)

**For AI Assistants**: When working with session functions, ensure async/await consistency.

#### Bug #2: Type Mismatch in load_session()

**Location**: `src/voice_cli.py:134-140`

**Problem**: `load_session()` returns `list[dict]` but code expects dict with 'messages' key.

**Current Code**:
```python
# load_session returns: list[dict] (just the messages array)
session_data = await load_session(args)
# But code tries to access: session_data['messages']  # ERROR!
```

**Fix Required**: Use `len(session_data)` instead of `len(session_data['messages'])`

**For AI Assistants**: Check function return types carefully. `load_session()` returns the messages array directly, not a dict containing messages.

### Architectural Issues

#### Dead Code: ADK Agents Not Actually Executed

**Location**: `src/orchestrator/runner.py:69-145`

**Problem**: Agents are created but never actually executed via ADK runtime. Instead, the code uses hardcoded keyword matching:

```python
# Current implementation (simplified)
if any(word in message_lower for word in ["email", "gmail", ...]):
    return "I'll route that to the Email Assistant..."  # Hardcoded!
```

**What's Missing**: Actual ADK agent execution (agent.run(), agent.query(), etc.)

**Impact**: ~200+ lines of agent definition code that isn't used for actual AI routing.

**For AI Assistants**:
- If asked to "improve agent routing", the real task is implementing ADK execution
- Don't add more keywords to the hardcoded matching - implement real ADK integration
- See `IMPLEMENTATION_SUMMARY.md` for full context

#### Session History Not Integrated with AgentRunner

**Location**: `src/orchestrator/runner.py:25`

**Problem**: AgentRunner maintains in-memory conversation history separate from persisted sessions:

```python
class AgentRunner:
    def __init__(self, agent: LlmAgent):
        self.conversation_history: List[Dict[str, str]] = []  # In-memory only!
```

**Impact**: When resuming a session, the orchestrator starts with empty history (no context).

**For AI Assistants**: When implementing session resume, ensure:
1. Load history from JSON: `messages = await load_session(session_id)`
2. Pass to orchestrator: `VoiceOrchestrator(session_id=session_id, history=messages)`
3. Orchestrator populates runner history: `self._runner.conversation_history = messages.copy()`

### Code Quality Issues

#### Massive Code Duplication

**Files**: `src/cli.py` (217 lines) vs `src/voice_cli.py` (222 lines)

**Problem**: ~180 lines duplicated between both CLI implementations:
- REPL loop structure (~50 lines)
- Command parsing (~80 lines)
- Welcome messages (~20 lines)
- Session management (~30 lines)

**For AI Assistants**: If asked to refactor, consider creating:
- `BaseCLI` class with shared functionality
- Specialized `ClaudeCLI` and `VoiceCLI` subclasses
- Shared command parser module

#### Print Statements vs. Logging

**Location**: Various files (especially `src/voice/streaming.py`)

**Problem**: Uses `print()` instead of proper logging:
```python
print("[Voice] Connected to Gemini Live API")  # Bad
```

**Preferred**:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("[Voice] Connected to Gemini Live API")  # Good
```

**For AI Assistants**: When adding new features, use `logging` module, not `print()`.

---

## Development Workflows

### Making Changes to Agent Behavior

1. **Edit Agent Definition**:
   ```bash
   # Edit the relevant agent file
   src/orchestrator/agents/email_agent.py  # For email agent
   src/orchestrator/agents/task_agent.py   # For task agent
   src/orchestrator/agents/general_agent.py # For general agent
   ```

2. **Modify the create_*_agent() function**:
   ```python
   def create_email_agent() -> LlmAgent:
       return LlmAgent(
           name="EmailAssistant",
           instruction="Updated instructions here...",
           # ... other params
       )
   ```

3. **Test Changes**:
   ```bash
   uv run voice-assistant
   # Test with relevant queries
   ```

### Adding a New Agent

1. **Create agent file**: `src/orchestrator/agents/new_agent.py`
   ```python
   from google.adk.agents import LlmAgent

   def create_new_agent() -> LlmAgent:
       return LlmAgent(
           name="NewAgent",
           model="gemini-2.0-flash-exp",
           description="What this agent does",
           instruction="Detailed behavior instructions",
           tools=[],
       )
   ```

2. **Export from __init__.py**: `src/orchestrator/agents/__init__.py`
   ```python
   from .new_agent import create_new_agent

   __all__ = [
       # ... existing agents
       'create_new_agent',
   ]
   ```

3. **Register in orchestrator**: `src/orchestrator/engine.py`
   ```python
   from .agents import create_new_agent  # Add import

   class VoiceOrchestrator:
       def __init__(self, ...):
           # ...
           self.new_agent = create_new_agent()

           self.coordinator = LlmAgent(
               # ...
               sub_agents=[
                   # ... existing agents
                   self.new_agent,
               ],
           )
   ```

4. **Add routing logic**: `src/orchestrator/runner.py`
   ```python
   # Add keywords for routing
   if any(word in message_lower for word in ["new", "keywords"]):
       # Route to new agent
   ```

### Working with Dependencies

**Adding Dependencies**:
```bash
# Add to pyproject.toml [dependencies] section
uv add package-name

# Or manually edit pyproject.toml then:
uv sync
```

**Removing Dependencies**:
```bash
uv remove package-name

# Or manually edit pyproject.toml then:
uv sync
```

**Lock File**: `uv.lock` is auto-generated. Commit it to ensure reproducible builds.

### Git Workflow

**Branch Naming**: Follow pattern `claude/<description>-<session-id>`
- Example: `claude/voice-agent-orchestrator-plan-016vs6qY6bf41CXsXAEXTjE4`

**Commit Messages**: Use conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

**Example**:
```bash
git add .
git commit -m "fix: resolve async/sync mismatch in list_sessions"
git push -u origin claude/fix-session-bugs-<session-id>
```

---

## Testing Guidelines

### Manual Testing

**Test Session Management**:
```python
# Test in Python REPL
import asyncio
from src.session import create_session_id, save_message, load_session, list_sessions

async def test():
    sid = create_session_id()
    await save_message(sid, "user", "Hello")
    await save_message(sid, "assistant", "Hi!")
    messages = await load_session(sid)
    print(messages)
    sessions = await list_sessions()
    print(sessions)

asyncio.run(test())
```

**Test Voice Orchestrator**:
```python
import asyncio
from src.orchestrator import VoiceOrchestrator

async def test():
    orch = VoiceOrchestrator()
    async for chunk in orch.process_message("Check my email"):
        print(chunk, end='', flush=True)

asyncio.run(test())
```

### Common Test Scenarios

1. **New Session Creation**:
   - Start app, send message
   - Verify session file created in `sessions/`
   - Check JSON structure matches expected format

2. **Session Resume**:
   - Load existing session
   - Verify message history displays
   - Send new message, verify it's appended

3. **Agent Routing**:
   - Test email keywords: "check my email"
   - Test task keywords: "add todo"
   - Test general: "what's the weather"
   - Verify appropriate agent responses

4. **Error Handling**:
   - Resume non-existent session (should show error)
   - Invalid session ID format
   - Missing .env file

---

## File Reference

### Core Files

| File | Purpose | Key Functions/Classes | Lines |
|------|---------|----------------------|-------|
| `src/config.py` | Configuration & env vars | `ANTHROPIC_API_KEY`, `SESSIONS_DIR`, `ALLOWED_TOOLS` | 50 |
| `src/session.py` | Session persistence | `save_message()`, `load_session()`, `list_sessions()` | 165 |
| `src/agent.py` | Claude Agent SDK wrapper | Agent initialization and chat | ~200 |
| `src/cli.py` | Claude chatbot CLI | `main()`, REPL loop | 217 |
| `src/voice_cli.py` | Voice assistant CLI | `main()`, REPL loop, commands | 222 |

### Orchestrator Files

| File | Purpose | Key Functions/Classes | Lines |
|------|---------|----------------------|-------|
| `src/orchestrator/engine.py` | Main coordinator | `VoiceOrchestrator` | 136 |
| `src/orchestrator/runner.py` | Async execution | `AgentRunner` | ~145 |
| `src/orchestrator/agents/email_agent.py` | Email agent | `create_email_agent()` | ~40 |
| `src/orchestrator/agents/task_agent.py` | Task agent | `create_task_agent()` | ~40 |
| `src/orchestrator/agents/general_agent.py` | General agent | `create_general_agent()` | ~40 |

### Documentation Files

| File | Purpose | For |
|------|---------|-----|
| `README.md` | User documentation | End users |
| `VOICE_SETUP.md` | Voice setup guide | End users |
| `CODE_REVIEW.md` | Comprehensive code review | Developers |
| `IMPLEMENTATION_SUMMARY.md` | Implementation notes | Developers |
| `CLAUDE.md` | This file | AI Assistants |

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, scripts |
| `uv.lock` | Dependency lock file (auto-generated) |
| `.env.example` | Environment variable template |
| `.env` | Actual environment variables (gitignored) |
| `.gitignore` | Git ignore patterns |

---

## Quick Reference Commands

### Running the Application
```bash
# Voice assistant (primary)
uv run voice-assistant

# Claude chatbot (alternative)
uv run chatbot

# Direct Python execution
python -m src.voice_cli
python -m src.cli
```

### Dependency Management
```bash
# Install all dependencies
uv sync

# Add new dependency
uv add package-name

# Remove dependency
uv remove package-name
```

### Session Management
```bash
# List session files
ls sessions/

# View session content
cat sessions/20250119_143022.json

# Delete all sessions (fresh start)
rm -rf sessions/
```

### Development
```bash
# Run Python REPL with src in path
uv run python

# Check Python version
python --version  # Should be 3.11+

# Verify uv installation
uv --version
```

---

## AI Assistant Best Practices

### When Working with This Codebase

1. **Always check CODE_REVIEW.md first**: It documents known bugs and issues
2. **Use async/await correctly**: Don't mix sync and async operations
3. **Maintain type hints**: Add type annotations to all new functions
4. **Test session operations**: Session bugs are common - test thoroughly
5. **Follow ABOUTME convention**: Add file headers to new files
6. **Use logging, not print**: Import `logging` for output
7. **Consider code duplication**: Check if functionality exists before adding
8. **Update documentation**: Keep CLAUDE.md and README.md in sync
9. **Session context matters**: Remember to pass history when resuming
10. **Read function return types**: Especially for session functions

### Common Pitfalls to Avoid

- **Don't** assume `load_session()` returns a dict with 'messages' key (it returns the list directly)
- **Don't** mix sync and async in session operations
- **Don't** add more hardcoded keywords to runner.py (implement real ADK instead)
- **Don't** use `print()` for logging (use `logging` module)
- **Don't** forget to update both CLI files if making shared changes (or refactor to reduce duplication)
- **Don't** commit session files (they're gitignored for privacy)

### When Asked To...

**"Fix the session bugs"**: See Known Issues section, bugs #1 and #2
**"Add a new agent"**: Follow "Adding a New Agent" in Development Workflows
**"Improve agent routing"**: Implement real ADK execution, not more keywords
**"Refactor CLIs"**: Create BaseCLI class to reduce duplication
**"Add logging"**: Replace `print()` with `logging` module
**"Resume session context"**: Ensure history is passed to AgentRunner

---

## Additional Resources

- **Google ADK Documentation**: https://google.github.io/adk-docs/
- **Claude Agent SDK**: Anthropic's SDK for building agents
- **uv Documentation**: https://github.com/astral-sh/uv
- **Python Async/Await**: https://docs.python.org/3/library/asyncio.html

---

**Maintained by**: AI assistants working on this codebase
**Version**: 1.0
**Last Updated**: 2025-11-19
