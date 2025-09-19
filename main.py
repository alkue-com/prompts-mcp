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
    PROMPTS_DIR = Path(__file__).parent / "prompts"

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
    """Load all prompts from the prompts directory and store them for the prompt handler."""
    if not PROMPTS_DIR.exists():
        logger.warning(f"Prompts directory does not exist: {PROMPTS_DIR}")
        return

    prompt_count = 0
    for prompt_file in PROMPTS_DIR.glob("*.md"):
        if prompt_file.name == "README.md":
            continue

        try:
            prompt_data = load_prompt_file(prompt_file)

            # Store the prompt content for retrieval
            setattr(app, f"_prompt_content_{prompt_data['name']}", prompt_data["content"])
            setattr(app, f"_prompt_data_{prompt_data['name']}", prompt_data)
            prompt_count += 1

        except Exception as e:
            logger.error(f"Error loading prompt file {prompt_file}: {e}")

    logger.info(f"Loaded {prompt_count} prompts from {PROMPTS_DIR}")


# Custom prompt handler using the @app.prompt decorator
@app.prompt()
async def handle_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
    """Handle prompt requests."""
    # Get the stored prompt content
    content_attr = f"_prompt_content_{name}"
    if not hasattr(app, content_attr):
        raise ValueError(f"Prompt '{name}' not found")

    content = getattr(app, content_attr)

    # Add input if provided
    if arguments and "input" in arguments and arguments["input"]:
        content += f"\n\n{arguments['input']}"

    return content


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
