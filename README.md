# prompts-mcp

This is an MCP (Model Context Protocol) server that serves prompts stored in a configurable directory (defaults to `prompts/`).

The prompts are accessible via any MCP-compatible client that supports server-provided prompts.

## Features

- Automatically discovers and loads all `.md` prompt files from the `prompts/` directory
- Extracts prompt descriptions from the "IDENTITY and PURPOSE" sections
- Provides proper MCP server interface with prompt listing and retrieval
- Supports input arguments for prompts
- Compatible with MCP-enabled clients
- Configurable prompts directory via environment variable

## Configuration

### Prompts Directory

By default, the server looks for prompts in the `prompts/` directory relative to the main script. You can customize this by setting the `PROMPTS_DIR` environment variable:

```bash
# Use a custom prompts directory
export PROMPTS_DIR="/path/to/your/prompts"
uv run main.py
```

The environment variable supports:
- Absolute paths: `/home/user/my-prompts`
- Relative paths: `../shared-prompts`
- Home directory expansion: `~/Documents/prompts`

If the `PROMPTS_DIR` environment variable is not set, it defaults to `./prompts/` in the same directory as the main script.

## Usage

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd prompts-mcp

# Install dependencies
uv sync
```

Or if you prefer to install globally:

```bash
uv pip install mcp
```

### Running the Server

```bash
uv run main.py
```

Or if you have the dependencies installed globally:

```bash
python main.py
```

The server will:
1. Scan the configured prompts directory (default: `prompts/`) for `.md` files
2. Parse and load all discovered prompts
3. Start an MCP server accessible via stdio

### Connecting from MCP Clients

To use this server with MCP-compatible clients (like Claude Desktop), add the following configuration to your `mcp.json` file:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "uv",
      "args": ["run", "/path/to/prompts-mcp/main.py"],
      "cwd": "/path/to/prompts-mcp"
    }
  }
}
```

Or if you have Python and dependencies installed globally:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "python",
      "args": ["/path/to/prompts-mcp/main.py"],
      "cwd": "/path/to/prompts-mcp"
    }
  }
}
```

#### Using a Custom Prompts Directory

To use a custom prompts directory, add the `PROMPTS_DIR` environment variable to your configuration:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "uv",
      "args": ["run", "/path/to/prompts-mcp/main.py"],
      "cwd": "/path/to/prompts-mcp",
      "env": {
        "PROMPTS_DIR": "/path/to/your/custom/prompts"
      }
    }
  }
}
```

Or with Python globally installed:

```json
{
  "mcpServers": {
    "prompts": {
      "command": "python",
      "args": ["/path/to/prompts-mcp/main.py"],
      "cwd": "/path/to/prompts-mcp",
      "env": {
        "PROMPTS_DIR": "/path/to/your/custom/prompts"
      }
    }
  }
}
```

Make sure to replace `/path/to/prompts-mcp` with the actual absolute path to your prompts-mcp directory.

**Note**: The exact location of the `mcp.json` configuration file depends on your MCP client. For Claude Desktop, it's typically located at:
- **macOS**: `~/Library/Application Support/Claude/mcp.json`
- **Windows**: `%APPDATA%\Claude\mcp.json`
