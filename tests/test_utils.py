"""
Shared utility functions for tests.
"""

from pathlib import Path
from typing import Any

from prompts_mcp.main import PromptsMCPServer


def create_test_server(prompts_dir: Path | None = None, app: Any = None) -> Any:
    """Create a test server instance with mocked dependencies."""
    # Create a mock server instance
    server = PromptsMCPServer.__new__(PromptsMCPServer)
    server.prompts_dir = prompts_dir
    server.app = app
    server.signal_count = 0

    return server
