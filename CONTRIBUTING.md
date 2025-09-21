# Contributing

Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
if not already present.

## Development

Set the `PROMPTS_DIR` environment variable (macOS & Linux distros):

    export PROMPTS_DIR="/path/to/your/prompts"

On Windows:

    set PROMPTS_DIR=C:\path\to\your\prompts

Run the server:

    uv run prompts-mcp

Use `dev.py` for development tasks. Run without arguments for list of all tasks.

To run all the tasks (sync, format, lint, check, test) at once:

    uv run dev.py all

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

Run `release.py` to bump version, do changelog, build packages and publish them.

**Note:** The script looks for PyPI credentials in user's `.pypirc`.

Build and publish to [TestPyPI](https://test.pypi.org/project/prompts-mcp/):

    uv run release.py rc

Build and publish to [PyPI](https://pypi.org/project/prompts-mcp/):

    uv run release.py
