# prompts-mcp

MCP (Model Context Protocol) server that provides prompts from a directory.

The prompts are Markdown files and named after their file name.

## Usage

The prompts are available for any MCP-compatible chat client that supports
[server-provided prompts](https://modelcontextprotocol.io/docs/learn/server-concepts#how-prompts-work).

**Configure your client** (e.g. Claude Desktop) by adding to your `mcp json`:

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

The exact location of the `mcp.json` configuration file depends on your client.

### Configuration

The `PROMPTS_DIR` environment variable is **required** and must be set to
a path containing all your `.md` files you want to serve as prompts.

The server will exit with an error if `PROMPTS_DIR` is not set
or if the directory doesn't exist.

## Development

Roughly 100% coded by AI. See `CONTRIBUTING.md` for local setup.
