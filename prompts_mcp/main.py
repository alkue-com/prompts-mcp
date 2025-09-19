#!/usr/bin/env python3
"""
MCP Server for serving prompts from a local directory using FastMCP.

This server provides prompts from the prompts/ directory as MCP prompts,
making them accessible to any MCP-compatible client.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompts-mcp")

# Directory containing prompts
# Can be overridden with PROMPTS_DIR environment variable
prompts_dir_env = os.getenv("PROMPTS_DIR")
if prompts_dir_env:
    PROMPTS_DIR = Path(prompts_dir_env).expanduser().resolve()
else:
    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Create the FastMCP server
app = FastMCP("prompts-mcp")


def load_prompt_file(prompt_path: Path) -> Dict[str, Any]:
    """Load and parse a prompt file."""
    content = prompt_path.read_text(encoding="utf-8")

    # Extract title from filename (remove .md extension and convert underscores to spaces)
    title = prompt_path.stem.replace("_", " ").title()

    # Parse the content to extract description
    lines = content.split('\n')
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
        "content": content
    }


def load_all_prompts():
    """Load all prompts from the prompts directory and register them individually."""
    if not PROMPTS_DIR.exists():
        logger.warning(f"Prompts directory does not exist: {PROMPTS_DIR}")
        return

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


def register_prompt(prompt_data: Dict[str, Any]):
    """Register an individual prompt with FastMCP."""
    prompt_name = prompt_data["name"]
    prompt_content = prompt_data["content"]
    prompt_description = prompt_data["description"]

    # Create a prompt handler function for this specific prompt
    def create_prompt_handler(content: str, name: str, description: str):
        @app.prompt(name=name, description=description)
        async def prompt_handler(arguments: Optional[Dict[str, Any]] = None) -> str:
            result = content
            # Add input if provided
            if arguments and "input" in arguments and arguments["input"]:
                result += f"\n\n{arguments['input']}"
            return result
        return prompt_handler

    # Register the prompt
    create_prompt_handler(prompt_content, prompt_name, prompt_description)


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting prompts-mcp server with FastMCP")
    logger.info(f"Using prompts directory: {PROMPTS_DIR}")

    # Load all prompts
    load_all_prompts()

    # Run the server
    app.run()


if __name__ == "__main__":
    main()
