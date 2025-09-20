# Contributing

Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
if not already present.

## Development

### macOS & Linux distros

Set the `PROMPTS_DIR` environment variable:

    export PROMPTS_DIR="/path/to/your/prompts"

Run the server:

    uv run prompts-mcp

Use `./dev.py` for common tasks. Run without arguments for list of all tasks.

To run all the tasks (sync, format, lint, check, test) at once:

    ./dev.py all

### Windows

Set the `PROMPTS_DIR` environment variable:

    set PROMPTS_DIR=C:\path\to\your\prompts

Run the server:

    uv run prompts-mcp

Use `python dev.py` for common tasks. Run without arguments for list of all tasks.

To run all the tasks (sync, format, lint, check, test) at once:

    python dev.py all

### Test drive

Use it in [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

    npx -y @modelcontextprotocol/inspector \
        uv --directory "$PWD" run prompts-mcp

Use it in [Goose CLI](https://block.github.io/goose/docs/quickstart):

    goose session --with-extension "uv --directory "$PWD" run prompts-mcp"

Use it in [VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_add-an-mcp-server) or [Cursor](https://cursor.com/docs/context/mcp#using-mcpjson) by configuring `mcp.json`:

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

**Note:** The release script looks for PyPI credentials in `~/.pypirc`.

Build and publish to [TestPyPI](https://test.pypi.org/project/prompts-mcp/):

    ./release.py rc

Build and publish to [PyPI](https://pypi.org/project/prompts-mcp/):

    ./release.py
