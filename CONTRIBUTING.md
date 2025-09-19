# Contributing

You can use your favorite Python version manager (asdf, pyenv, ...) as long
as it follows `.python-version`.

Install [pre-commit](https://pre-commit.com/) if it is not already installed.

Install pre-commit hooks in your git working copy:

    pre-commit install --hook-type pre-commit --hook-type commit-msg

## Setup

Install dependencies:

    uv sync

Set the `PROMPTS_DIR` environment variable:

    export PROMPTS_DIR="/path/to/your/prompts"

Run the server:

    uv run prompts-mcp

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

## Testing

Run all checks (install-dev, format, lint, check, test):

    python dev.py all

Use [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

    npx -y @modelcontextprotocol/inspector \
        uv --directory "$PWD" run prompts-mcp

Test in e.g. [Goose CLI](https://block.github.io/goose/docs/quickstart) (fast):

    goose session --with-extension "uvx --from "$PWD" prompts-mcp"

Test in e.g. [VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) `mcp.json` (slower):

```json
{
    "mcpServers": {
        "prompts-mcp": {
            "command": "uvx",
            "args": ["--from", "/path/to/repo", "prompts-mcp"],
            "env": {
                "PROMPTS_DIR": "${env:PROMPTS_DIR}"
            }
        }
    }
}
```

## Publish

Build and publish to [TestPyPI](https://test.pypi.org/project/prompts-mcp/):

    python release.py rc

Build and pubish to [PyPI](https://pypi.org/project/prompts-mcp/):

    python release.py
