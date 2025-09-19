# prompts-mcp

This is an MCP (Model Context Protocol) server that serves prompts stored in a directory specified by the `PROMPTS_DIR` environment variable.

The prompts are accessible via any MCP-compatible client that supports server-provided prompts.

## Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set the PROMPTS_DIR environment variable:**
   ```bash
   export PROMPTS_DIR="/path/to/your/prompts"
   ```

3. **Run the server:**
   ```bash
   uv run prompts-mcp
   ```

4. **Configure your MCP client** (e.g., Claude Desktop) by adding to your `mcp.json`:
   ```json
   {
     "mcpServers": {
       "prompts": {
         "command": "uv",
         "args": ["run", "prompts-mcp"],
         "cwd": "/path/to/prompts-mcp",
         "env": {
           "PROMPTS_DIR": "/path/to/your/prompts"
         }
       }
     }
   }
   ```

Replace `/path/to/prompts-mcp` with the actual absolute path to your prompts-mcp directory, and `/path/to/your/prompts` with the actual path to your prompts directory.

## Configuration

### Required: PROMPTS_DIR Environment Variable

The `PROMPTS_DIR` environment variable is **required** and must be set to the path containing your prompt files:

```bash
export PROMPTS_DIR="/path/to/your/prompts"
uv run prompts-mcp
```

You must also set it in your MCP client configuration:

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

**Important**: The prompts directory must exist and contain `.md` files. The server will exit with an error if `PROMPTS_DIR` is not set or if the directory doesn't exist.

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
