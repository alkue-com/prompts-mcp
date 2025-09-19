"""
Test fixtures and configuration for prompts-mcp tests.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary directory with sample prompt files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        prompts_dir = Path(temp_dir) / "prompts"
        prompts_dir.mkdir()

        # Create sample prompt files
        sample_prompt_1 = prompts_dir / "test_prompt_1.md"
        sample_prompt_1.write_text("""# Test Prompt 1

# IDENTITY AND PURPOSE
This is a test prompt for unit testing purposes. It demonstrates the structure of a typical prompt file.

# USAGE
Use this prompt to test the prompts-mcp functionality.

# EXAMPLES
Here are some examples of how to use this prompt.
""")

        sample_prompt_2 = prompts_dir / "test_prompt_2.md"
        sample_prompt_2.write_text("""# Test Prompt 2

This is another test prompt without the IDENTITY section.

Just a simple prompt for testing purposes.
""")

        sample_prompt_3 = prompts_dir / "README.md"
        sample_prompt_3.write_text("""# README

This is a README file that should be ignored during prompt loading.
""")

        yield prompts_dir


@pytest.fixture
def mock_fastmcp():
    """Mock FastMCP server for testing."""
    mock_app = MagicMock()
    mock_app.prompt = MagicMock()
    return mock_app


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    test_prompts_path = Path(__file__).parent / "test_prompts"
    with patch.dict(os.environ, {"PROMPTS_DIR": str(test_prompts_path)}):
        yield


@pytest.fixture
def sample_prompt_data():
    """Sample prompt data for testing."""
    return {
        "name": "test_prompt",
        "title": "Test Prompt",
        "description": "A test prompt for unit testing",
        "content": "# Test Prompt\n\nThis is a test prompt content."
    }


@pytest.fixture
def mock_signal():
    """Mock signal handling for testing."""
    with patch('signal.signal') as mock_signal_func:
        yield mock_signal_func


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch('prompts_mcp.main.logger') as mock_log:
        yield mock_log
