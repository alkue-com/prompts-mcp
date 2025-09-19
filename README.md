# prompts-mcp

This is an MCP (Model Context Protocol) server that serves prompts stored in the `prompts/` directory.

The prompts are accessible via any MCP-compatible client that supports server-provided prompts.

## Features

- Automatically discovers and loads all `.md` prompt files from the `prompts/` directory
- Extracts prompt descriptions from the "IDENTITY and PURPOSE" sections
- Provides proper MCP server interface with prompt listing and retrieval
- Supports input arguments for prompts
- Compatible with MCP-enabled clients

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
1. Scan the `prompts/` directory for `.md` files
2. Parse and load all discovered prompts
3. Start an MCP server accessible via stdio
