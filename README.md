# prompts-mcp

This MCP (Model Context Protocol) server provides prompts from an
user specified directory. The prompts are plain-text Markdown (`.md`) files.

The prompts are then accessible via any MCP-compatible client that supports
[server-provided prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts).

## Usage

**Configure your MCP client** (e.g., Claude Desktop) by adding to your `mcp json`:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "uvx",
      "args": ["prompts-mcp"],
      "env": {
        "PROMPTS_DIR": "/path/to/your/prompts"
      }
    }
  }
}
```

The exact location of the `mcp.json` configuration file depends on your
MCP client.

### Configuration

The `PROMPTS_DIR` environment variable is **required** and must be set to
the path containing your `.md` files.

The server will exit with an error if `PROMPTS_DIR` is not set,
or if the directory doesn't exist.

## Development

See `CONTRIBUTING.md` for local setup.
