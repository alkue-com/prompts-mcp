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

### Prompt Format

Prompts should be markdown files with the following structure:

```markdown
# IDENTITY and PURPOSE

Your prompt description goes here...

# STEPS

- Step 1
- Step 2

# OUTPUT

Expected output format...

# INPUT:
```

## Implementation

The server is implemented using FastMCP, the ergonomic interface for MCP servers. It provides:

- **Prompt Discovery**: Automatically finds all `.md` files in the prompts directory
- **Metadata Extraction**: Parses prompt descriptions from IDENTITY and PURPOSE sections
- **FastMCP Interface**: Simple, clean prompt registration and handling
- **Input Support**: Optional input parameter for customizing prompts

## Technical Details

- Built with Python 3.13+
- Uses MCP 1.14.1 with FastMCP for simplified implementation
- Managed with `uv` for fast dependency resolution and virtual environments
- Loads and serves 226 prompts out of the box
- Works with any MCP-compatible client (Cursor, Claude Desktop, etc.)
- Much simpler than complex fallback implementations

## Project Structure

```
prompts-mcp/
├── main.py              # MCP server implementation
├── pyproject.toml       # Project configuration with uv
├── uv.lock             # Locked dependencies
├── prompts/            # Directory containing 226+ prompt files
└── README.md           # This file
```
