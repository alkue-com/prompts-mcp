#!/usr/bin/env python3
"""
MCP Server for serving prompts from a local directory using FastMCP.

This server provides prompts from the prompts/ directory as MCP prompts,
making them accessible to any MCP-compatible client.
"""

import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompts-mcp")

# Global variable to track signal count
signal_count = 0

# Global variables that will be initialized in main()
PROMPTS_DIR: Path | None = None
app: FastMCP | None = None


def initialize_server():
    """Initialize the server with environment variables and directory checks."""
    global PROMPTS_DIR, app

    # Directory containing prompts - must be set via PROMPTS_DIR
    # environment variable
    prompts_dir_env = os.getenv("PROMPTS_DIR")
    if not prompts_dir_env:
        logger.error(
            "PROMPTS_DIR environment variable is required. Please set "
            "PROMPTS_DIR to the path containing your prompt files"
        )
        sys.exit(1)

    PROMPTS_DIR = Path(prompts_dir_env).expanduser().resolve()

    # Check if PROMPTS_DIR exists, exit if it doesn't
    if not PROMPTS_DIR.exists():
        logger.error(
            f"Prompts directory does not exist: {PROMPTS_DIR}. Please set "
            "PROMPTS_DIR environment variable to a valid path"
        )
        sys.exit(1)

    # Create the FastMCP server
    app = FastMCP("prompts-mcp")


def load_prompt_file(prompt_path: Path) -> dict[str, Any]:
    """Load and parse a prompt file."""
    content = prompt_path.read_text(encoding="utf-8")

    # Extract title from filename (remove .md extension and convert
    # underscores to spaces)
    title = prompt_path.stem.replace("_", " ").title()

    # Parse the content to extract description
    lines = content.split("\n")
    description = ""

    # Look for IDENTITY and PURPOSE section to extract description
    in_identity_section = False
    for line in lines:
        if line.strip().upper().startswith("# IDENTITY AND PURPOSE"):
            in_identity_section = True
            continue
        elif line.strip().startswith("#") and in_identity_section:
            break
        elif in_identity_section and line.strip():
            description += line.strip() + " "

    # If no description found, use first non-empty line
    if not description.strip():
        for line in lines:
            if line.strip() and not line.startswith("#"):
                description = line.strip()[:100] + "..."
                break

    return {
        "name": prompt_path.stem,
        "title": title,
        "description": description.strip(),
        "content": content,
    }


def load_all_prompts():
    """Load all prompts from the prompts directory and register them
    individually."""
    prompt_count = 0
    for prompt_file in PROMPTS_DIR.glob("*.md"):
        if prompt_file.name == "README.md":
            continue

        try:
            prompt_data = load_prompt_file(prompt_file)

            # Register each prompt individually with FastMCP
            register_prompt(prompt_data)
            prompt_count += 1

        except Exception as e:
            logger.error(f"Error loading prompt file {prompt_file}: {e}")

    logger.info(f"Loaded {prompt_count} prompts from {PROMPTS_DIR}")


def register_prompt(prompt_data: dict[str, Any]):
    """Register an individual prompt with FastMCP."""
    prompt_name = prompt_data["name"]
    prompt_content = prompt_data["content"]
    prompt_description = prompt_data["description"]

    # Create a prompt handler function for this specific prompt
    def create_prompt_handler(content: str, name: str, description: str):
        @app.prompt(name=name, description=description)
        async def prompt_handler(
            arguments: dict[str, Any] | None = None,
        ) -> str:
            result = content
            # Add input if provided
            if arguments and "input" in arguments and arguments["input"]:
                result += f"\n\n{arguments['input']}"
            return result

        return prompt_handler

    # Register the prompt
    create_prompt_handler(prompt_content, prompt_name, prompt_description)


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global signal_count
    signal_count += 1

    if signal_count == 1:
        logger.info("Received interrupt signal, shutting down gracefully...")
        logger.info("Press Ctrl+C again to force exit")
        # Set up handler for second interrupt to force exit
        signal.signal(signal.SIGINT, lambda s, f: os._exit(1))
        signal.signal(signal.SIGTERM, lambda s, f: os._exit(1))
        # Use os._exit for clean shutdown without thread cleanup issues
        os._exit(0)
    else:
        logger.warning("Received second interrupt signal, forcing exit...")
        os._exit(1)


def main():
    """Main entry point for the MCP server."""
    # Initialize server first
    initialize_server()

    logger.info("Starting prompts-mcp server with FastMCP")
    logger.info(f"Using prompts directory: {PROMPTS_DIR}")

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load all prompts
    load_all_prompts()

    # Run the server directly - signal handler will handle shutdown
    try:
        app.run()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
