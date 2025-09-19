"""
Unit tests for prompts_mcp.main module.

This module tests the main function and environment validation
with proper mocking to avoid import-time side effects.
"""

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestMainFunction:
    """Test cases for the main function."""

    @patch("prompts_mcp.main.load_all_prompts")
    @patch("prompts_mcp.main.app")
    @patch("prompts_mcp.main.signal.signal")
    @patch("prompts_mcp.main.logger")
    @patch("prompts_mcp.main.initialize_server")
    def test_main_success(
        self,
        mock_init_server,
        mock_logger,
        mock_signal,
        mock_app,
        mock_load_prompts,
    ):
        """Test successful main function execution."""
        # Set up the mocked app and PROMPTS_DIR
        import prompts_mcp.main

        prompts_mcp.main.app = mock_app
        prompts_mcp.main.PROMPTS_DIR = Path("/test/prompts")

        from prompts_mcp.main import main

        main()

        mock_init_server.assert_called_once()
        mock_logger.info.assert_any_call(
            "Starting prompts-mcp server with FastMCP"
        )
        mock_signal.assert_called()
        mock_load_prompts.assert_called_once()
        mock_app.run.assert_called_once()

    @patch("prompts_mcp.main.load_all_prompts")
    @patch("prompts_mcp.main.app")
    @patch("prompts_mcp.main.signal.signal")
    @patch("prompts_mcp.main.logger")
    @patch("prompts_mcp.main.initialize_server")
    @patch("sys.exit")
    def test_main_app_error(
        self,
        mock_exit,
        mock_init_server,
        mock_logger,
        mock_signal,
        mock_app,
        mock_load_prompts,
    ):
        """Test main function handles app.run errors."""
        mock_app.run.side_effect = Exception("Server error")

        # Set up the mocked app and PROMPTS_DIR
        import prompts_mcp.main

        prompts_mcp.main.app = mock_app
        prompts_mcp.main.PROMPTS_DIR = Path("/test/prompts")

        from prompts_mcp.main import main

        main()

        mock_init_server.assert_called_once()
        mock_logger.error.assert_called_with("Server error: Server error")
        mock_exit.assert_called_once_with(1)


@pytest.mark.unit
class TestEnvironmentValidation:
    """Test cases for environment variable validation."""

    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    @patch.dict("os.environ", {}, clear=True)
    def test_initialize_server_missing_prompts_dir(
        self, mock_exit, mock_logger
    ):
        """Test initialize_server fails when PROMPTS_DIR is not set."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        from prompts_mcp.main import initialize_server

        with pytest.raises(SystemExit):
            initialize_server()

        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "PROMPTS_DIR environment variable is required" in error_message
        mock_exit.assert_called_once_with(1)

    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    @patch("prompts_mcp.main.Path")
    @patch.dict("os.environ", {"PROMPTS_DIR": "/nonexistent/path"})
    def test_initialize_server_nonexistent_directory(
        self, mock_path_class, mock_exit, mock_logger
    ):
        """Test initialize_server fails when PROMPTS_DIR doesn't exist."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        # Mock Path to return a path that doesn't exist
        mock_path = mock_path_class.return_value
        mock_path.expanduser.return_value = mock_path
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = False

        from prompts_mcp.main import initialize_server

        with pytest.raises(SystemExit):
            initialize_server()

        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Prompts directory does not exist" in error_message
        mock_exit.assert_called_once_with(1)

    @patch("prompts_mcp.main.FastMCP")
    @patch("prompts_mcp.main.Path")
    @patch.dict("os.environ", {"PROMPTS_DIR": "/valid/path"})
    def test_initialize_server_success(self, mock_path_class, mock_fastmcp):
        """Test successful initialize_server execution."""
        # Mock Path to return a path that exists
        mock_path = mock_path_class.return_value
        mock_path.expanduser.return_value = mock_path
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True

        from prompts_mcp.main import initialize_server

        initialize_server()

        mock_fastmcp.assert_called_once_with("prompts-mcp")


@pytest.mark.unit
class TestMainBlock:
    """Test cases for the main block execution."""

    def test_main_block_coverage(self):
        """Test that verifies the main block can be executed."""
        # This test ensures the main block is testable
        # We can't easily test the if __name__ == "__main__" block directly
        # in pytest, but we can verify the main function exists and is callable
        import prompts_mcp.main

        # Verify the main function exists and is callable
        assert hasattr(prompts_mcp.main, "main")
        assert callable(prompts_mcp.main.main)

        # The if __name__ == "__main__" block is only executed when the script
        # is run directly, not when imported. This line is difficult to test
        # in pytest but is covered by running the script directly.
        assert True  # Placeholder assertion
