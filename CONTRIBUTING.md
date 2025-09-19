# Contributing

## Setup

Install development tools with [mise](https://mise.jdx.dev/):

    mise install

Set the `PROMPTS_DIR` environment variable:

    export PROMPTS_DIR="/path/to/your/prompts"

Run the server:

    uv run prompts-mcp

## Development

Use `dev.py` script to run common development tasks.

Run all the tasks below (install, format, lint, check, test) at once:

    python dev.py all

### Tasks

Install dependencies:

    python dev.py install

Format code:

    python dev.py format

Lint and fix code:

    python dev.py lint

Check code without fixing:

    python dev.py check

Run all tests:

    python dev.py test

Run only specific tests (takes `pytest` arguments):

    python dev.py test -m slow

## Testing

Use it in [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

    npx -y @modelcontextprotocol/inspector \
        uv --directory "$PWD" run prompts-mcp

Use it in [Goose CLI](https://block.github.io/goose/docs/quickstart):

    goose session --with-extension "uv --directory "$PWD" run prompts-mcp"

Use it in [VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_add-an-mcp-server) or [Cursor](https://cursor.com/docs/context/mcp#using-mcpjson) `mcp.json`:

```json
{
    "mcpServers": {
        "prompts-mcp": {
            "command": "uv",
            "args": ["--directory", "/path/to/repo", "run", "prompts-mcp"],
            "env": {
                "PROMPTS_DIR": "${env:PROMPTS_DIR}"
            }
        }
    }
}
```

## Release

Use `release.py` to build and publish the source dist and the wheel.

Build and publish to [TestPyPI](https://test.pypi.org/project/prompts-mcp/):

    python release.py rc

Build and publish to [PyPI](https://pypi.org/project/prompts-mcp/):

    python release.py
