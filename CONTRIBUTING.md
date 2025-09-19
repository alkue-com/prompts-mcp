# Contributing

## Setup

Install dependencies:

    uv sync

Set the `PROMPTS_DIR` environment variable:

    export PROMPTS_DIR="/path/to/your/prompts"

Run the server:

    uv run prompts-mcp

Use [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

    npx -y @modelcontextprotocol/inspector \
        uv --directory /this/path run prompts-mcp

## Development

Use `dev.py` script to run common development tasks.

Install development dependencies:

    python dev.py install-dev

Format code:

    python dev.py format

Lint and fix code:

    python dev.py lint

Check code without:

    python dev.py check

Run all tests:

    python dev.py test

Clean build artifacts and cache files:

    python dev.py clean

Run all checks (install-dev, format, lint, check, test):

    python dev.py all
