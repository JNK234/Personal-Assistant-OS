# ABOUTME: Configuration management for the Claude chatbot application
# ABOUTME: Loads environment variables and defines application settings

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment. "
        "Please create a .env file with your API key. "
        "See .env.example for reference."
    )

# Model Configuration
MODEL_NAME = "claude-sonnet-4-20250514"

# Tool Configuration
# List of tools the agent is allowed to use
ALLOWED_TOOLS = [
    'Read',      # Read files (text, images, PDFs, notebooks)
    'Write',     # Create or overwrite files
    'Edit',      # Perform exact string replacements
    'Glob',      # Fast file pattern matching
    'Grep',      # Powerful search with regex
    'Bash',      # Execute bash commands
    'WebFetch',  # Fetch and process web content
    'WebSearch', # Search the web
]

# Session Configuration
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)  # Create sessions directory if it doesn't exist

# Optional System Prompt
# Can be customized via environment variable or modified here
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful AI assistant. You can read and write files, "
    "execute commands, and browse the web to help users with their tasks."
)

# Permission Mode
# Options: "auto", "manual", "never"
# "auto" - Automatically approve tool usage
# "manual" - Ask for approval before using tools
# "never" - Never use tools
PERMISSION_MODE = "bypassPermissions"
