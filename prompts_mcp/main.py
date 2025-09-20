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


class PromptsMCPServer:
    """MCP Server for serving prompts from a local directory using FastMCP."""

    def __init__(self) -> None:
        """Initialize server with environment variables and directory checks."""
        self.prompts_dir: Path | None = None
        self.app: FastMCP | None = None
        self.signal_count = 0
        self._initialize_server()

    def _initialize_server(self) -> None:
        """Initialize server with environment variables and directory checks."""
        # Directory containing prompts - must be set via PROMPTS_DIR
        # environment variable
        prompts_dir_env = os.getenv("PROMPTS_DIR")
        if not prompts_dir_env:
            logger.error(
                "PROMPTS_DIR environment variable is required. Please set "
                "PROMPTS_DIR to the path containing your prompt files"
            )
            sys.exit(1)

        self.prompts_dir = Path(prompts_dir_env).expanduser().resolve()

        # Check if PROMPTS_DIR exists, exit if it doesn't
        if not self.prompts_dir.exists():
            logger.error(
                "Prompts directory does not exist: %s. Please set "
                "PROMPTS_DIR environment variable to a valid path",
                self.prompts_dir,
            )
            sys.exit(1)

        # Create the FastMCP server
        self.app = FastMCP("prompts-mcp")

    def load_all_prompts(self) -> None:
        """Load all prompts from the prompts directory and register them
        individually."""
        prompt_count = 0
        if self.prompts_dir is None:
            logger.error("PROMPTS_DIR is not initialized")
            return

        # Copy instance variables to local variables for efficiency
        prompts_dir = self.prompts_dir
        log = logger

        for prompt_file in prompts_dir.glob("*.md"):
            if prompt_file.name == "README.md":
                continue

            try:
                prompt_data = load_prompt_file(prompt_file)

                # Register each prompt individually with FastMCP
                self.register_prompt(prompt_data)
                prompt_count += 1

            except (OSError, ValueError, UnicodeDecodeError) as e:
                log.error("Error loading prompt file %s: %s", prompt_file, e)

        log.info("Loaded %d prompts from %s", prompt_count, prompts_dir)

    def register_prompt(self, prompt_data: dict[str, Any]) -> None:
        """Register an individual prompt with FastMCP."""
        prompt_name = prompt_data["name"]
        prompt_content = prompt_data["content"]
        prompt_description = prompt_data["description"]

        # Create a prompt handler function for this specific prompt
        def create_prompt_handler(
            content: str, name: str, description: str
        ) -> None:
            if self.app is None:
                raise RuntimeError("FastMCP app is not initialized")

            # Define the prompt handler function first
            async def prompt_handler(
                arguments: dict[str, Any] | None = None,
            ) -> str:
                result = content
                # Add input if provided
                if arguments and "input" in arguments and arguments["input"]:
                    result += f"\n\n{arguments['input']}"
                return result

            # Register the prompt with FastMCP
            self.app.prompt(name=name, description=description)(prompt_handler)

        # Register the prompt
        create_prompt_handler(prompt_content, prompt_name, prompt_description)

    def signal_handler(self, _signum: int, _frame: Any) -> None:
        """Handle interrupt signals gracefully."""
        self.signal_count += 1

        if self.signal_count == 1:
            logger.info(
                "Received interrupt signal, shutting down gracefully..."
            )
            logger.info("Press Ctrl+C again to force exit")
            # Set up handler for second interrupt to force exit
            signal.signal(signal.SIGINT, lambda _s, _f: os._exit(1))
            signal.signal(signal.SIGTERM, lambda _s, _f: os._exit(1))
            # Use os._exit for clean shutdown without thread cleanup issues
            os._exit(0)
        else:
            logger.warning("Received second interrupt signal, forcing exit...")
            os._exit(1)


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
        if line.strip().startswith("#") and in_identity_section:
            break
        if in_identity_section and line.strip():
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


def main() -> None:
    """Main entry point for the MCP server."""
    # Create server instance
    server = PromptsMCPServer()

    logger.info("Starting prompts-mcp server with FastMCP")
    logger.info("Using prompts directory: %s", server.prompts_dir)

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, server.signal_handler)
    signal.signal(signal.SIGTERM, server.signal_handler)

    # Load all prompts
    server.load_all_prompts()

    # Run the server directly - signal handler will handle shutdown
    if server.app is None:
        logger.error("FastMCP app is not initialized")
        sys.exit(1)

    try:
        server.app.run()
    except (OSError, ValueError, RuntimeError) as e:
        logger.error("Server error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
