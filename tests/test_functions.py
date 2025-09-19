"""
Unit tests for prompts_mcp.main module functions.

This module tests individual functions without importing the main module
that has side effects at import time.
"""

import os
import signal
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestLoadPromptFileFunction:
    """Test cases for the load_prompt_file function."""

    def test_load_prompt_file_with_identity_section(self):
        """Test loading a prompt file with IDENTITY section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_prompt_1.md"
            prompt_file.write_text("""# Test Prompt 1

# IDENTITY AND PURPOSE
This is a test prompt for unit testing purposes. It demonstrates the structure of a typical prompt file.

# USAGE
Use this prompt to test the prompts-mcp functionality.

# EXAMPLES
Here are some examples of how to use this prompt.
""")

            # Import and test the function directly
            from prompts_mcp.main import load_prompt_file
            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_1"
            assert result["title"] == "Test Prompt 1"
            assert "test prompt for unit testing purposes" in result["description"]
            assert result["content"].startswith("# Test Prompt 1")

    def test_load_prompt_file_without_identity_section(self):
        """Test loading a prompt file without IDENTITY section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_prompt_2.md"
            prompt_file.write_text("""# Test Prompt 2

This is another test prompt without the IDENTITY section.

Just a simple prompt for testing purposes.
""")

            from prompts_mcp.main import load_prompt_file
            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_2"
            assert result["title"] == "Test Prompt 2"
            assert "This is another test prompt without the IDENTITY section" in result["description"]
            assert result["content"].startswith("# Test Prompt 2")

    def test_load_prompt_file_with_underscores_in_name(self):
        """Test that underscores in filename are converted to spaces in title."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a file with underscores
            prompt_file = prompts_dir / "test_prompt_with_underscores.md"
            prompt_file.write_text("# Test Prompt\n\nSimple content.")

            from prompts_mcp.main import load_prompt_file
            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_with_underscores"
            assert result["title"] == "Test Prompt With Underscores"

    def test_load_prompt_file_empty_content(self):
        """Test loading a prompt file with empty content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "empty_prompt.md"
            prompt_file.write_text("")

            from prompts_mcp.main import load_prompt_file
            result = load_prompt_file(prompt_file)

            assert result["name"] == "empty_prompt"
            assert result["title"] == "Empty Prompt"
            assert result["description"] == ""
            assert result["content"] == ""

    def test_load_prompt_file_nonexistent_file(self):
        """Test loading a nonexistent prompt file raises FileNotFoundError."""
        nonexistent_file = Path("/nonexistent/prompt.md")

        from prompts_mcp.main import load_prompt_file
        with pytest.raises(FileNotFoundError):
            load_prompt_file(nonexistent_file)


@pytest.mark.unit
class TestLoadAllPromptsFunction:
    """Test cases for the load_all_prompts function."""

    @patch('prompts_mcp.main.register_prompt')
    @patch('prompts_mcp.main.PROMPTS_DIR')
    def test_load_all_prompts_success(self, mock_prompts_dir, mock_register_prompt):
        """Test successful loading of all prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create test files
            prompt1 = prompts_dir / "test_prompt_1.md"
            prompt1.write_text("# Test Prompt 1\n\nContent 1.")
            prompt2 = prompts_dir / "test_prompt_2.md"
            prompt2.write_text("# Test Prompt 2\n\nContent 2.")

            mock_prompts_dir.glob.return_value = [prompt1, prompt2]

            # Import and set up the module properly
            import prompts_mcp.main
            prompts_mcp.main.PROMPTS_DIR = mock_prompts_dir

            from prompts_mcp.main import load_all_prompts
            load_all_prompts()

            assert mock_register_prompt.call_count == 2

    @patch('prompts_mcp.main.register_prompt')
    @patch('prompts_mcp.main.PROMPTS_DIR')
    def test_load_all_prompts_skips_readme(self, mock_prompts_dir, mock_register_prompt):
        """Test that README.md files are skipped."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt1 = prompts_dir / "test_prompt_1.md"
            prompt1.write_text("# Test Prompt 1\n\nContent 1.")
            readme = prompts_dir / "README.md"
            readme.write_text("# README\n\nThis should be ignored.")

            mock_prompts_dir.glob.return_value = [prompt1, readme]

            # Import and set up the module properly
            import prompts_mcp.main
            prompts_mcp.main.PROMPTS_DIR = mock_prompts_dir

            from prompts_mcp.main import load_all_prompts
            load_all_prompts()

            assert mock_register_prompt.call_count == 1

    @patch('prompts_mcp.main.register_prompt')
    @patch('prompts_mcp.main.PROMPTS_DIR')
    @patch('prompts_mcp.main.logger')
    def test_load_all_prompts_handles_errors(self, mock_logger, mock_prompts_dir, mock_register_prompt):
        """Test that errors in loading individual prompts are handled gracefully."""
        mock_prompts_dir.glob.return_value = [Path("/nonexistent/prompt.md")]
        mock_register_prompt.side_effect = Exception("Test error")

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.PROMPTS_DIR = mock_prompts_dir

        from prompts_mcp.main import load_all_prompts
        load_all_prompts()

        mock_logger.error.assert_called_once()

    @patch('prompts_mcp.main.register_prompt')
    @patch('prompts_mcp.main.PROMPTS_DIR')
    def test_load_all_prompts_no_files(self, mock_prompts_dir, mock_register_prompt):
        """Test loading when no prompt files exist."""
        mock_prompts_dir.glob.return_value = []

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.PROMPTS_DIR = mock_prompts_dir

        from prompts_mcp.main import load_all_prompts
        load_all_prompts()

        mock_register_prompt.assert_not_called()


@pytest.mark.unit
class TestRegisterPromptFunction:
    """Test cases for the register_prompt function."""

    @patch('prompts_mcp.main.app')
    def test_register_prompt_success(self, mock_app):
        """Test successful prompt registration."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content."
        }

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.app = mock_app

        from prompts_mcp.main import register_prompt
        register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert decorator_call[1]["description"] == "A test prompt for unit testing"

    @patch('prompts_mcp.main.app')
    def test_register_prompt_with_input_argument(self, mock_app):
        """Test that the registered prompt handler accepts input arguments."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content."
        }

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func):
            return func

        mock_app.prompt.return_value = mock_decorator

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.app = mock_app

        from prompts_mcp.main import register_prompt
        register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert decorator_call[1]["description"] == "A test prompt for unit testing"

    @patch('prompts_mcp.main.app')
    def test_register_prompt_without_input_argument(self, mock_app):
        """Test that the registered prompt handler works without input arguments."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content."
        }

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func):
            return func

        mock_app.prompt.return_value = mock_decorator

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.app = mock_app

        from prompts_mcp.main import register_prompt
        register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert decorator_call[1]["description"] == "A test prompt for unit testing"

    @patch('prompts_mcp.main.app')
    def test_register_prompt_with_empty_input(self, mock_app):
        """Test that empty input doesn't modify the result."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content."
        }

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func):
            return func

        mock_app.prompt.return_value = mock_decorator

        # Import and set up the module properly
        import prompts_mcp.main
        prompts_mcp.main.app = mock_app

        from prompts_mcp.main import register_prompt
        register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert decorator_call[1]["description"] == "A test prompt for unit testing"


@pytest.mark.unit
class TestSignalHandlerFunction:
    """Test cases for the signal_handler function."""

    @patch('prompts_mcp.main.logger')
    @patch('os._exit')
    def test_signal_handler_first_interrupt(self, mock_exit, mock_logger):
        """Test handling of first interrupt signal."""
        # Reset global signal count
        import prompts_mcp.main
        prompts_mcp.main.signal_count = 0
        prompts_mcp.main.logger = mock_logger

        from prompts_mcp.main import signal_handler
        signal_handler(signal.SIGINT, None)

        # Check that the first log message was called
        mock_logger.info.assert_any_call("Received interrupt signal, shutting down gracefully...")
        mock_exit.assert_called_once_with(0)

    @patch('prompts_mcp.main.logger')
    @patch('os._exit')
    def test_signal_handler_second_interrupt(self, mock_exit, mock_logger):
        """Test handling of second interrupt signal."""
        # Set signal count to 1 to simulate second interrupt
        import prompts_mcp.main
        prompts_mcp.main.signal_count = 1
        prompts_mcp.main.logger = mock_logger

        from prompts_mcp.main import signal_handler
        signal_handler(signal.SIGINT, None)

        mock_logger.warning.assert_called_with("Received second interrupt signal, forcing exit...")
        mock_exit.assert_called_once_with(1)

    @patch('signal.signal')
    @patch('os._exit')
    def test_signal_handler_sets_up_second_handler(self, mock_exit, mock_signal):
        """Test that signal handler sets up handler for second interrupt."""
        import prompts_mcp.main
        prompts_mcp.main.signal_count = 0

        from prompts_mcp.main import signal_handler
        signal_handler(signal.SIGINT, None)

        # Should set up new signal handlers
        assert mock_signal.call_count >= 2
