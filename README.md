# prompts-mcp

Model Context Protocol (MCP) server of Markdown based prompts.

Serves prompts for any MCP-compatible client from a directory of Markdown files.

## Usage

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

Prompt naming: `_`'s in file name are converted to spaces and `.md` is dropped.

The server will exit with an error if `PROMPTS_DIR` is not set
or if the directory doesn't exist.

## Development

Roughly 100% coded by AI. See `CONTRIBUTING.md` for local setup.
