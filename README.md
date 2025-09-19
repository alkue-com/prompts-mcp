# prompts-mcp

This is an MCP (Model Context Protocol) server that serves prompts stored in a directory specified by the `PROMPTS_DIR` environment variable.

The prompts are accessible via any MCP-compatible client that supports server-provided prompts.

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

The exact location of the `mcp.json` configuration file depends on your MCP client.

### Configuration

The `PROMPTS_DIR` environment variable is **required** and must be set to the path containing your `.md` files.

The server will exit with an error if `PROMPTS_DIR` is not set or if the directory doesn't exist.

## Development

See `CONTRIBUTING.md` for that.
