# Contributing

## Setup

Install dependencies:

   uv sync

Set the PROMPTS_DIR environment variable:

   export PROMPTS_DIR="/path/to/your/prompts"

Run the server:

   uv run prompts-mcp

## Development

This project includes a `dev.py` script that provides common development tasks.

Install development dependencies:

    python dev.py install-dev

Format code with ruff:

    python dev.py format

Lint and fix code with ruff:

    python dev.py lint

Check code without fixing:

    python dev.py check

Run all tests:

    python dev.py test

Clean build artifacts and cache files:

    python dev.py clean

Run all checks (install-dev, format, lint, check, test):

    python dev.py all

## Testing

Run all tests:

    uv run pytest

Run unit tests only:

    uv run pytest -m unit

Run integration tests only:

    uv run pytest -m integration

Run performance tests only:

    uv run pytest -m slow