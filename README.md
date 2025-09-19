# prompts-mcp

Model Context Protocol (MCP) server of Markdown based prompts.

Serves a directory of Markdown files as prompts to a chat session.

Works with any MCP client supporting server-side prompts.

## Usage

**Configure your client** (e.g. Claude Desktop) by adding to your `mcp.json`:

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

The location of the `mcp.json` file depends on your client and operating system.

### Configuration

Set `PROMPTS_DIR` to a path containing the `.md` files you want to serve as
prompts.

⚠️: The server will exit with an error if `PROMPTS_DIR` is not set
or if the directory does not exist.

Prompt naming: `_`'s in file names are converted to spaces and `.md` is dropped.

## Development

About 100% coded by AI. See `CONTRIBUTING.md` for local setup.
