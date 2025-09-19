# prompts-mcp

This is an MCP (Model Context Protocol) server that serves prompts stored in a configurable directory (defaults to `prompts/`).

The prompts are accessible via any MCP-compatible client that supports server-provided prompts.

## Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the server:**
   ```bash
   uv run prompts-mcp
   ```

3. **Configure your MCP client** (e.g., Claude Desktop) by adding to your `mcp.json`:
   ```json
   {
     "mcpServers": {
       "prompts": {
         "command": "uv",
         "args": ["run", "prompts-mcp"],
         "cwd": "/path/to/prompts-mcp"
       }
     }
   }
   ```

Replace `/path/to/prompts-mcp` with the actual absolute path to your prompts-mcp directory.

## Features

- Automatically discovers and loads all `.md` prompt files from the `prompts/` directory
- Extracts prompt descriptions from the "IDENTITY and PURPOSE" sections
- Provides proper MCP server interface with prompt listing and retrieval
- Supports input arguments for prompts
- Compatible with MCP-enabled clients
- Configurable prompts directory via environment variable

## Configuration

### Custom Prompts Directory

To use a custom prompts directory, set the `PROMPTS_DIR` environment variable:

```bash
export PROMPTS_DIR="/path/to/your/prompts"
uv run prompts-mcp
```

Or add it to your MCP client configuration:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "uv",
      "args": ["run", "prompts-mcp"],
      "cwd": "/path/to/prompts-mcp",
      "env": {
        "PROMPTS_DIR": "/path/to/your/custom/prompts"
      }
    }
  }
}
```

The environment variable supports:
- Absolute paths: `/home/user/my-prompts`
- Relative paths: `../shared-prompts`
- Home directory expansion: `~/Documents/prompts`

**Note**: The exact location of the `mcp.json` configuration file depends on your MCP client. For Claude Desktop, it's typically located at:
- **macOS**: `~/Library/Application Support/Claude/mcp.json`
- **Windows**: `%APPDATA%\Claude\mcp.json`

## Testing

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest -m unit

# Run integration tests only
uv run pytest -m integration

# Run performance tests only
uv run pytest -m slow

# Run with coverage
uv run pytest --cov=prompts_mcp --cov-report=html
```
