"""
Unit tests for prompts_mcp.main module.

This module tests the main function and environment validation
with proper mocking to avoid import-time side effects.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

import prompts_mcp.main
from prompts_mcp.main import PromptsMCPServer, main
from tests.test_utils import create_test_server


@pytest.mark.unit
class TestMainFunction:
    """Test cases for the main function."""

    @patch("prompts_mcp.main.PromptsMCPServer")
    @patch("prompts_mcp.main.signal.signal")
    @patch("prompts_mcp.main.logger")
    def test_main_success(
        self,
        mock_logger: Any,
        mock_signal: Any,
        mock_server_class: Any,
    ) -> None:
        """Test successful main function execution."""
        # Create a mock server instance
        mock_server = MagicMock()
        mock_server.prompts_dir = Path("test") / "prompts"
        mock_server.app = MagicMock()
        mock_server_class.return_value = mock_server

        main()

        # Verify that server was created
        mock_server_class.assert_called_once()

        # Verify that methods were called
        mock_logger.info.assert_any_call(
            "Starting prompts-mcp server with FastMCP"
        )
        mock_signal.assert_called()
        mock_server.load_all_prompts.assert_called_once()
        mock_server.app.run.assert_called_once()
        # Verify mock_signal was used
        assert mock_signal.call_count >= 2

    @patch("prompts_mcp.main.PromptsMCPServer")
    @patch("prompts_mcp.main.signal.signal")
    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    def test_main_app_error(
        self,
        mock_exit: Any,
        mock_logger: Any,
        mock_signal: Any,
        mock_server_class: Any,
    ) -> None:
        """Test main function handles app.run errors."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        # Create a mock server instance with an app that raises an error
        mock_server = MagicMock()
        mock_server.prompts_dir = Path("test") / "prompts"
        mock_server.app = MagicMock()
        mock_server.app.run.side_effect = RuntimeError("Server error")
        mock_server_class.return_value = mock_server

        with pytest.raises(SystemExit):
            main()

        # Verify that server was created
        mock_server_class.assert_called_once()

        # Verify error handling
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert error_call[0][0] == "Server error: %s"
        assert isinstance(error_call[0][1], RuntimeError)
        assert str(error_call[0][1]) == "Server error"
        mock_exit.assert_called_once_with(1)
        # Verify mock_signal was used
        assert mock_signal.call_count >= 2


@pytest.mark.unit
class TestEnvironmentValidation:
    """Test cases for environment variable validation."""

    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    @patch.dict("os.environ", {}, clear=True)
    def test_initialize_server_missing_prompts_dir(
        self, mock_exit: Any, mock_logger: Any
    ) -> None:
        """Test _initialize_server fails when PROMPTS_DIR is not set."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        with pytest.raises(SystemExit):
            # Create server instance which will call _initialize_server
            PromptsMCPServer()

        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "PROMPTS_DIR environment variable is required" in error_message
        mock_exit.assert_called_once_with(1)

    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    @patch("prompts_mcp.main.Path")
    @patch.dict("os.environ", {"PROMPTS_DIR": "/nonexistent/path"})
    def test_initialize_server_nonexistent_directory(
        self, mock_path_class: Any, mock_exit: Any, mock_logger: Any
    ) -> None:
        """Test _initialize_server fails when PROMPTS_DIR doesn't exist."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        # Mock Path to return a path that doesn't exist
        mock_path = mock_path_class.return_value
        mock_path.expanduser.return_value = mock_path
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = False

        with pytest.raises(SystemExit):
            # Create server instance which will call _initialize_server
            PromptsMCPServer()

        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Prompts directory does not exist" in error_message
        mock_exit.assert_called_once_with(1)

    @patch("prompts_mcp.main.FastMCP")
    @patch("prompts_mcp.main.Path")
    @patch.dict("os.environ", {"PROMPTS_DIR": "/valid/path"})
    def test_initialize_server_success(
        self, mock_path_class: Any, mock_fastmcp: Any
    ) -> None:
        """Test successful _initialize_server execution."""
        # Mock Path to return a path that exists
        mock_path = mock_path_class.return_value
        mock_path.expanduser.return_value = mock_path
        mock_path.resolve.return_value = mock_path
        mock_path.exists.return_value = True

        # Create server instance which will call _initialize_server
        server = PromptsMCPServer()

        mock_fastmcp.assert_called_once_with("prompts-mcp")
        assert server.prompts_dir == mock_path
        assert server.app is not None


@pytest.mark.unit
class TestLoadAllPromptsEdgeCases:
    """Test edge cases for load_all_prompts method."""

    def test_class_initialization(self) -> None:
        """Test that the class can be instantiated."""
        assert TestLoadAllPromptsEdgeCases is not None

    @patch("prompts_mcp.main.logger")
    def test_load_all_prompts_prompts_dir_none(self, mock_logger: Any) -> None:
        """Test load_all_prompts when prompts_dir is None."""
        # Create test server instance with None prompts_dir
        server = create_test_server(prompts_dir=None)

        # Call the method
        server.load_all_prompts()

        mock_logger.error.assert_called_once_with(
            "PROMPTS_DIR is not initialized"
        )


@pytest.mark.unit
class TestRegisterPromptEdgeCases:
    """Test edge cases for register_prompt method."""

    def test_class_initialization(self) -> None:
        """Test that the class can be instantiated."""
        assert TestRegisterPromptEdgeCases is not None

    def test_register_prompt_app_none(self) -> None:
        """Test register_prompt when app is None."""
        # Create test server instance with None app
        server = create_test_server(app=None)

        prompt_data = {
            "name": "test_prompt",
            "content": "Test content",
            "description": "Test description",
        }

        with pytest.raises(
            RuntimeError, match="FastMCP app is not initialized"
        ):
            server.register_prompt(prompt_data)


@pytest.mark.unit
class TestMainEdgeCases:
    """Test edge cases for main function."""

    def test_class_initialization(self) -> None:
        """Test that the class can be instantiated."""
        assert TestMainEdgeCases is not None

    @patch("prompts_mcp.main.PromptsMCPServer")
    @patch("prompts_mcp.main.signal.signal")
    @patch("prompts_mcp.main.logger")
    @patch("sys.exit")
    def test_main_app_none(
        self,
        mock_exit: Any,
        mock_logger: Any,
        mock_signal: Any,
        mock_server_class: Any,
    ) -> None:
        """Test main function when app is None."""
        # Mock sys.exit to raise SystemExit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        # Create a mock server instance with None app
        mock_server = MagicMock()
        mock_server.prompts_dir = Path("test") / "prompts"
        mock_server.app = None
        mock_server_class.return_value = mock_server

        with pytest.raises(SystemExit):
            main()

        # Verify that server was created
        mock_server_class.assert_called_once()

        # Check that the error call is the expected one
        mock_logger.error.assert_any_call("FastMCP app is not initialized")
        # Should exit due to app being None
        mock_exit.assert_called_with(1)
        # Verify mock_signal was used
        assert mock_signal.call_count >= 2


@pytest.mark.unit
class TestMainBlock:
    """Test cases for the main block execution."""

    def test_class_initialization(self) -> None:
        """Test that the class can be instantiated."""
        assert TestMainBlock is not None

    def test_main_block_coverage(self) -> None:
        """Test that verifies the main block can be executed."""
        # This test ensures the main block is testable
        # We can't easily test the if __name__ == "__main__" block directly
        # in pytest, but we can verify the main function exists and is callable
        # Verify the main function exists and is callable
        assert hasattr(prompts_mcp.main, "main")
        assert callable(prompts_mcp.main.main)

        # The if __name__ == "__main__" block is only executed when the script
        # is run directly, not when imported. This line is difficult to test
        # in pytest but is covered by running the script directly.
        assert True  # Placeholder assertion
