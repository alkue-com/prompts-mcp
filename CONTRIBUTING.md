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

Use `release.py` to bump version, update `CHANGELOG.md` and create a git tag.

If `--publish <index>` is given, the created `dist/` files are published there.

**Note:** The script looks for PyPI credentials in user's `.pypirc`.

Create release and publish it to [PyPI](https://pypi.org/project/prompts-mcp/):

    uv run release.py --publish pypi

You may distribute pre-release versions e.g.:

    uv run release.py alpha --publish testpypi
    uv run release.py beta --publish testpypi
    uv run release.py rc --publish pypi
