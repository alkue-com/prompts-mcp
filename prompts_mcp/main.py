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


def _is_signal_available(signal_name: str) -> bool:
    """Check if a signal is available on the current platform."""
    return hasattr(signal, signal_name)


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

    def _validate_prompts_directory(self) -> Path | None:
        """Validate that prompts directory is initialized and return it."""
        if self.prompts_dir is None:
            logger.error("PROMPTS_DIR is not initialized")
            return None
        return self.prompts_dir

    def _should_skip_file(self, prompt_file: Path) -> bool:
        """Check if a prompt file should be skipped."""
        return prompt_file.name == "README.md"

    def _load_single_prompt(self, prompt_file: Path) -> dict[str, Any] | None:
        """Load a single prompt file and return its data."""
        try:
            return load_prompt_file(prompt_file)
        except (OSError, ValueError, UnicodeDecodeError) as e:
            logger.error("Error loading prompt file %s: %s", prompt_file, e)
            return None

    def load_all_prompts(self) -> None:
        """Load all prompts from the prompts directory and register them
        individually."""
        prompt_count = 0
        prompts_dir = self._validate_prompts_directory()

        if prompts_dir is None:
            return

        for prompt_file in prompts_dir.glob("*.md"):
            if self._should_skip_file(prompt_file):
                continue

            prompt_data = self._load_single_prompt(prompt_file)
            if prompt_data is not None:
                self.register_prompt(prompt_data)
                prompt_count += 1

        logger.info("Loaded %d prompts from %s", prompt_count, prompts_dir)

    def _validate_app_initialization(self) -> None:
        """Validate that FastMCP app is initialized."""
        if self.app is None:
            raise RuntimeError("FastMCP app is not initialized")

    def _create_prompt_handler(self, content: str) -> Any:
        """Create a prompt handler function for the given content."""

        async def prompt_handler(
            arguments: dict[str, Any] | None = None,
        ) -> str:
            result = content
            # Add input if provided
            if arguments and "input" in arguments and arguments["input"]:
                result += f"\n\n{arguments['input']}"
            return result

        return prompt_handler

    def register_prompt(self, prompt_data: dict[str, Any]) -> None:
        """Register an individual prompt with FastMCP."""
        prompt_name = prompt_data["name"]
        prompt_content = prompt_data["content"]
        prompt_description = prompt_data["description"]

        self._validate_app_initialization()
        prompt_handler = self._create_prompt_handler(prompt_content)

        # Register the prompt with FastMCP
        assert self.app is not None  # Validated in _validate_app_initialization
        self.app.prompt(name=prompt_name, description=prompt_description)(
            prompt_handler
        )

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
            # SIGTERM is not available on all platforms (e.g., Windows)
            if _is_signal_available("SIGTERM"):
                signal.signal(signal.SIGTERM, lambda _s, _f: os._exit(1))
            # Use os._exit for clean shutdown without thread cleanup issues
            os._exit(0)
        else:
            logger.warning("Received second interrupt signal, forcing exit...")
            os._exit(1)


def _extract_title_from_filename(prompt_path: Path) -> str:
    """Extract title from filename converting _ to spaces."""
    return prompt_path.stem.replace("_", " ").title()


def _extract_description_from_identity_section(lines: list[str]) -> str:
    """Extract description from IDENTITY AND PURPOSE section."""
    description = ""
    in_identity_section = False

    for line in lines:
        if line.strip().upper().startswith("# IDENTITY AND PURPOSE"):
            in_identity_section = True
            continue
        if line.strip().startswith("#") and in_identity_section:
            break
        if in_identity_section and line.strip():
            description += line.strip() + " "

    return description.strip()


def _extract_fallback_description(lines: list[str]) -> str:
    """Extract fallback description from first non-empty line."""
    for line in lines:
        if line.strip() and not line.startswith("#"):
            return line.strip()[:100] + "..."
    return ""


def _extract_description_from_content(content: str) -> str:
    """Extract description from prompt content."""
    lines = content.split("\n")

    # Try to extract from IDENTITY AND PURPOSE section first
    description = _extract_description_from_identity_section(lines)

    # If no description found, use fallback
    if not description:
        description = _extract_fallback_description(lines)

    return description


def load_prompt_file(prompt_path: Path) -> dict[str, Any]:
    """Load and parse a prompt file."""
    try:
        # Try UTF-8 first, fall back to system default if needed
        content = prompt_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fall back to system default encoding if UTF-8 fails
        try:
            content = prompt_path.read_text()
        except UnicodeDecodeError:
            # Last resort: read as bytes and decode with errors='replace'
            content = prompt_path.read_bytes().decode("utf-8", errors="replace")

    title = _extract_title_from_filename(prompt_path)
    description = _extract_description_from_content(content)

    return {
        "name": prompt_path.stem,
        "title": title,
        "description": description,
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
    # SIGTERM is not available on all platforms (e.g., Windows)
    if _is_signal_available("SIGTERM"):
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
