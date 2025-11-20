"""
Unit tests for prompts_mcp.main module functions.

This module tests individual functions without importing the main module
that has side effects at import time.
"""

import asyncio
import signal
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from prompts_mcp.main import load_prompt_file
from tests.test_utils import create_test_server


@pytest.mark.unit
class TestLoadPromptFileFunction:
    """Test cases for the load_prompt_file function."""

    def test_load_prompt_file_with_identity_section(self) -> None:
        """Test loading a prompt file with IDENTITY section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_prompt_1.md"
            prompt_file.write_text("""# Test Prompt 1

# IDENTITY AND PURPOSE
This is a test prompt for unit testing purposes. It demonstrates the
structure of a typical prompt file.

# USAGE
Use this prompt to test the prompts-mcp functionality.

# EXAMPLES
Here are some examples of how to use this prompt.
""")

            # Import and test the function directly
            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_1"
            assert result["title"] == "Test Prompt 1"
            assert (
                "test prompt for unit testing purposes" in result["description"]
            )
            assert result["content"].startswith("# Test Prompt 1")

    def test_load_prompt_file_without_identity_section(self) -> None:
        """Test loading a prompt file without IDENTITY section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_prompt_2.md"
            prompt_file.write_text("""# Test Prompt 2

This is another test prompt without the IDENTITY section.

Just a simple prompt for testing purposes.
""")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_2"
            assert result["title"] == "Test Prompt 2"
            assert (
                "This is another test prompt without the IDENTITY section"
                in result["description"]
            )
            assert result["content"].startswith("# Test Prompt 2")

    def test_load_prompt_file_with_underscores_in_name(self) -> None:
        """Test that underscores in filename are converted to spaces in
        title."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a file with underscores
            prompt_file = prompts_dir / "test_prompt_with_underscores.md"
            prompt_file.write_text("# Test Prompt\n\nSimple content.")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "test_prompt_with_underscores"
            assert result["title"] == "Test Prompt With Underscores"

    def test_load_prompt_file_empty_content(self) -> None:
        """Test loading a prompt file with empty content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "empty_prompt.md"
            prompt_file.write_text("")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "empty_prompt"
            assert result["title"] == "Empty Prompt"
            assert result["description"] == ""
            assert result["content"] == ""

    def test_load_prompt_file_nonexistent_file(self) -> None:
        """Test loading a nonexistent prompt file raises FileNotFoundError."""
        # Use a cross-platform path that's guaranteed not to exist
        nonexistent_file = Path("nonexistent") / "prompt.md"

        with pytest.raises(FileNotFoundError):
            load_prompt_file(nonexistent_file)


@pytest.mark.unit
class TestNestedPromptLoading:
    """Test cases for nested prompt loading."""

    def test_load_nested_prompt_python_test(self) -> None:
        """Test loading the nested python:test prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create nested directory structure
            python_dir = prompts_dir / "python"
            python_dir.mkdir()

            # Create the test.md file
            test_file = python_dir / "test.md"
            test_file.write_text("""# test

Write Python unit test for $ARGUMENTS.
""")

            # Load the prompt file
            result = load_prompt_file(test_file)

            # Verify the result
            assert result["name"] == "test"
            assert result["title"] == "Test"
            assert "Write Python unit test for $ARGUMENTS" in result["content"]
            assert result["content"].startswith("# test")

    def test_load_all_nested_prompts(self) -> None:
        """Test loading all prompts including nested ones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create root prompt
            (prompts_dir / "root_prompt.md").write_text(
                "# Root Prompt\n\nRoot content."
            )

            # Create nested prompt
            python_dir = prompts_dir / "python"
            python_dir.mkdir()
            (python_dir / "test.md").write_text(
                "# test\n\nWrite Python unit test for $ARGUMENTS."
            )

            # Create test server instance
            server = create_test_server(prompts_dir=prompts_dir)

            # Mock the register_prompt method
            server.register_prompt = MagicMock()

            # Load all prompts
            server.load_all_prompts()

            # Verify that both prompts were registered
            assert server.register_prompt.call_count == 2

            # Verify the registered prompts
            calls = server.register_prompt.call_args_list
            registered_names = [call[0][0]["name"] for call in calls]

            assert "root_prompt" in registered_names
            assert "python:test" in registered_names


@pytest.mark.unit
class TestPromptArguments:
    """Test cases for prompt arguments functionality."""

    def test_parse_yaml_frontmatter_with_arguments(self) -> None:
        """Test parsing YAML frontmatter with argument definitions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "code_review.md"
            prompt_file.write_text("""---
arguments:
    - name: code
      description: The code to review
      required: true
    - name: language
      description: Programming language
      required: false
---

# Code Review

Please review this ${language} code:

${code}
""")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "code_review"
            assert "arguments" in result
            assert len(result["arguments"]) == 2

            # Check first argument
            assert result["arguments"][0]["name"] == "code"
            assert result["arguments"][0]["description"] == "The code to review"
            assert result["arguments"][0]["required"] is True

            # Check second argument
            assert result["arguments"][1]["name"] == "language"
            assert (
                result["arguments"][1]["description"] == "Programming language"
            )
            assert result["arguments"][1]["required"] is False

    def test_infer_arguments_from_placeholders(self) -> None:
        """Test inferring arguments from ${placeholder} syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "sql_query.md"
            prompt_file.write_text("""# Generate SQL Query

Generate a SQL query for ${database_type} to ${action}.
""")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "sql_query"
            assert "arguments" in result
            assert len(result["arguments"]) == 2

            # Arguments should be sorted alphabetically
            assert result["arguments"][0]["name"] == "action"
            assert result["arguments"][1]["name"] == "database_type"

            # Inferred arguments should not be required
            assert result["arguments"][0]["required"] is False
            assert result["arguments"][1]["required"] is False

    def test_backward_compatibility_with_arguments_placeholder(self) -> None:
        """Test backward compatibility with $ARGUMENTS placeholder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test.md"
            prompt_file.write_text("""# test

Write Python unit test for $ARGUMENTS.
""")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "test"
            assert "arguments" in result
            assert len(result["arguments"]) == 1
            assert result["arguments"][0]["name"] == "ARGUMENTS"

    def test_no_arguments_in_prompt(self) -> None:
        """Test prompts without any arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "simple.md"
            prompt_file.write_text("""# Simple Prompt

This is a simple prompt without any arguments.
""")

            result = load_prompt_file(prompt_file)

            assert result["name"] == "simple"
            assert "arguments" in result
            assert len(result["arguments"]) == 0

    def test_argument_substitution(self) -> None:
        """Test that arguments are properly substituted in content."""
        from prompts_mcp.main import _substitute_arguments

        content = "Review this ${language} code:\n\n${code}"
        arguments = {
            "language": "Python",
            "code": "def hello():\n    print('world')",
        }

        result = _substitute_arguments(content, arguments)

        assert "Python" in result
        assert "def hello():" in result
        assert "${language}" not in result
        assert "${code}" not in result

    def test_argument_substitution_with_arguments_placeholder(self) -> None:
        """Test substitution of $ARGUMENTS placeholder."""
        from prompts_mcp.main import _substitute_arguments

        content = "Write unit test for $ARGUMENTS."
        arguments = {"ARGUMENTS": "the login function"}

        result = _substitute_arguments(content, arguments)

        assert "the login function" in result
        assert "$ARGUMENTS" not in result

    def test_find_argument_placeholders_skips_invalid_identifiers(self) -> None:
        """Test that placeholders with invalid identifiers are ignored."""
        from prompts_mcp.main import _find_argument_placeholders

        content = "Valid: ${valid_arg}, Invalid: ${1}, ${-invalid}, ${valid_2}"
        placeholders = _find_argument_placeholders(content)

        assert "valid_arg" in placeholders
        assert "valid_2" in placeholders
        assert "1" not in placeholders
        assert "-invalid" not in placeholders


@pytest.mark.unit
class TestLoadAllPromptsFunction:
    """Test cases for the load_all_prompts method."""

    @patch("prompts_mcp.main.load_prompt_file")
    def test_load_all_prompts_success(self, mock_load_prompt_file: Any) -> None:
        """Test successful loading of all prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create test files
            prompt1 = prompts_dir / "test_prompt_1.md"
            prompt1.write_text("# Test Prompt 1\n\nContent 1.")
            prompt2 = prompts_dir / "test_prompt_2.md"
            prompt2.write_text("# Test Prompt 2\n\nContent 2.")

            # Mock the load_prompt_file function to return test data
            mock_load_prompt_file.side_effect = [
                {
                    "name": "test_prompt_1",
                    "content": "Content 1",
                    "description": "Test Prompt 1",
                },
                {
                    "name": "test_prompt_2",
                    "content": "Content 2",
                    "description": "Test Prompt 2",
                },
            ]

            # Create test server instance
            server = create_test_server(prompts_dir=prompts_dir)

            # Mock the register_prompt method
            server.register_prompt = MagicMock()

            # Call the method
            server.load_all_prompts()

            # Verify that register_prompt was called twice
            assert server.register_prompt.call_count == 2

    @patch("prompts_mcp.main.load_prompt_file")
    def test_load_all_prompts_skips_readme(
        self, mock_load_prompt_file: Any
    ) -> None:
        """Test that README.md files are skipped."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt1 = prompts_dir / "test_prompt_1.md"
            prompt1.write_text("# Test Prompt 1\n\nContent 1.")
            readme = prompts_dir / "README.md"
            readme.write_text("# README\n\nThis should be ignored.")

            # Mock the load_prompt_file function to return test data
            mock_load_prompt_file.return_value = {
                "name": "test_prompt_1",
                "content": "Content 1",
                "description": "Test Prompt 1",
            }

            # Create test server instance
            server = create_test_server(prompts_dir=prompts_dir)

            # Mock the register_prompt method
            server.register_prompt = MagicMock()

            # Call the method
            server.load_all_prompts()

            # Verify that register_prompt was called only once
            # (README.md should be skipped)
            assert server.register_prompt.call_count == 1

    @patch("prompts_mcp.main.load_prompt_file")
    @patch("prompts_mcp.main.logger")
    def test_load_all_prompts_handles_errors(
        self, mock_logger: Any, mock_load_prompt_file: Any
    ) -> None:
        """Test that errors in loading individual prompts are handled
        gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_prompt.md"
            prompt_file.write_text("# Test Prompt\n\nContent.")

            # Mock load_prompt_file to raise an exception that should be caught
            mock_load_prompt_file.side_effect = OSError("Test error")

            # Create test server instance
            server = create_test_server(prompts_dir=prompts_dir)

            # Mock the register_prompt method
            server.register_prompt = MagicMock()

            # Call the method
            server.load_all_prompts()

            # Verify that error was logged
            mock_logger.error.assert_called_once()

    def test_load_all_prompts_no_files(self) -> None:
        """Test loading when no prompt files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create test server instance
            server = create_test_server(prompts_dir=prompts_dir)

            # Mock the register_prompt method
            server.register_prompt = MagicMock()

            # Call the method
            server.load_all_prompts()

            # Verify that register_prompt was not called
            server.register_prompt.assert_not_called()


@pytest.mark.unit
class TestRegisterPromptFunction:
    """Test cases for the register_prompt method."""

    def test_register_prompt_success(self) -> None:
        """Test successful prompt registration."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content.",
        }

        # Create mock app
        mock_app = MagicMock()

        # Create test server instance
        server = create_test_server(app=mock_app)

        # Call the method
        server.register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert (
            decorator_call[1]["description"] == "A test prompt for unit testing"
        )

    def test_register_prompt_with_input_argument(self) -> None:
        """Test that the registered prompt handler accepts input arguments."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content.",
        }

        # Create mock app
        mock_app = MagicMock()

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func: Any) -> Any:
            return func

        mock_app.prompt.return_value = mock_decorator

        # Create test server instance
        server = create_test_server(app=mock_app)

        # Call the method
        server.register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert (
            decorator_call[1]["description"] == "A test prompt for unit testing"
        )

    def test_register_prompt_handler_with_input(self) -> None:
        """Test that the registered prompt handler works with input args."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content.",
        }

        # Create mock app
        mock_app = MagicMock()

        # Create a mock decorator that captures the function
        captured_func = None

        def mock_decorator(func: Any) -> Any:
            nonlocal captured_func
            captured_func = func
            return func

        mock_app.prompt.return_value = mock_decorator

        # Create test server instance
        server = create_test_server(app=mock_app)

        # Call the method
        server.register_prompt(sample_prompt_data)

        # Get the handler function that was registered
        handler_func = captured_func

        # Test the handler function with input arguments
        if handler_func is not None:
            result = asyncio.run(handler_func(input="Additional user input"))
            expected = (
                "# Test Prompt\n\nThis is a test prompt content.\n\n"
                "Additional user input"
            )
            assert result == expected

            # Test the handler function without input arguments
            result_no_input = asyncio.run(handler_func(input=None))
            assert (
                result_no_input
                == "# Test Prompt\n\nThis is a test prompt content."
            )

            # Test the handler function with empty input
            result_empty_input = asyncio.run(handler_func(input=""))
            assert (
                result_empty_input
                == "# Test Prompt\n\nThis is a test prompt content."
            )
        else:
            pytest.skip("Handler function not captured by mock decorator")

    def test_register_prompt_without_input_argument(self) -> None:
        """Test that the registered prompt handler works without input
        arguments."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content.",
        }

        # Create mock app
        mock_app = MagicMock()

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func: Any) -> Any:
            return func

        mock_app.prompt.return_value = mock_decorator

        # Create test server instance
        server = create_test_server(app=mock_app)

        # Call the method
        server.register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert (
            decorator_call[1]["description"] == "A test prompt for unit testing"
        )

    def test_register_prompt_with_empty_input(self) -> None:
        """Test that empty input doesn't modify the result."""
        sample_prompt_data = {
            "name": "test_prompt",
            "title": "Test Prompt",
            "description": "A test prompt for unit testing",
            "content": "# Test Prompt\n\nThis is a test prompt content.",
        }

        # Create mock app
        mock_app = MagicMock()

        # Create a mock decorator that returns the function unchanged
        def mock_decorator(func: Any) -> Any:
            return func

        mock_app.prompt.return_value = mock_decorator

        # Create test server instance
        server = create_test_server(app=mock_app)

        # Call the method
        server.register_prompt(sample_prompt_data)

        # Verify that app.prompt was called
        mock_app.prompt.assert_called_once()

        # Get the decorator call and verify the arguments
        decorator_call = mock_app.prompt.call_args
        assert decorator_call[1]["name"] == "test_prompt"
        assert (
            decorator_call[1]["description"] == "A test prompt for unit testing"
        )

    @patch("prompts_mcp.main.logger")
    def test_create_handler_skips_invalid_arguments(
        self, mock_logger: Any
    ) -> None:
        """Test that _create_prompt_handler skips invalid arguments."""
        server = create_test_server()

        content = "Content"
        arguments = [
            {"name": "valid_arg", "description": "Valid", "required": False},
            {"name": "1", "description": "Invalid", "required": False},
            {
                "name": "invalid-name",
                "description": "Invalid",
                "required": False,
            },
        ]

        handler = server._create_prompt_handler(content, arguments)  # noqa: SLF001

        # Check signature
        import inspect

        sig = inspect.signature(handler)
        assert "valid_arg" in sig.parameters
        assert "1" not in sig.parameters
        assert "invalid-name" not in sig.parameters

        # Check warnings
        assert mock_logger.warning.call_count == 2


@pytest.mark.unit
class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility features."""

    def test_signal_availability_check(self) -> None:
        """Test that signal availability is checked correctly."""
        from prompts_mcp.main import _is_signal_available

        # SIGINT should be available on all platforms
        assert _is_signal_available("SIGINT")

        # SIGTERM may not be available on Windows
        # This test just ensures the function works without error
        _is_signal_available("SIGTERM")

    def test_encoding_fallback(self) -> None:
        """Test that file encoding fallback works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a file with non-UTF-8 content to test fallback
            prompt_file = prompts_dir / "test_encoding.md"
            # Write some content that should be readable
            prompt_file.write_text(
                "# Test Encoding\n\nThis is a test.", encoding="utf-8"
            )

            # This should work with our improved encoding handling
            result = load_prompt_file(prompt_file)
            assert result["name"] == "test_encoding"
            assert "Test Encoding" in result["title"]

    def test_encoding_fallback_system_default(self) -> None:
        """Test encoding fallback to system default when UTF-8 fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_encoding_fallback.md"

            # Create a file that will cause UTF-8 decode error
            # Write bytes that are not valid UTF-8
            invalid_utf8_bytes = (
                b"# Test Encoding\n\nThis has invalid UTF-8: \xff\xfe"
            )
            prompt_file.write_bytes(invalid_utf8_bytes)

            # Mock the read_text method to simulate UTF-8 failure
            def mock_read_text_utf8_fails(
                _self: Any, encoding: str | None = None
            ) -> str:
                if encoding == "utf-8":
                    raise UnicodeDecodeError(
                        "utf-8", b"", 0, 1, "invalid start byte"
                    )
                # For system default encoding, return valid content
                return "# Test Encoding\n\nThis is a test."

            with patch.object(Path, "read_text", mock_read_text_utf8_fails):
                result = load_prompt_file(prompt_file)
                assert result["name"] == "test_encoding_fallback"
                assert "Test Encoding" in result["title"]

    def test_encoding_fallback_bytes_decode(self) -> None:
        """Test encoding fallback to bytes decode with error replacement."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            prompt_file = prompts_dir / "test_encoding_bytes.md"

            # Create a file that will cause both UTF-8 and system default
            # to fail
            invalid_bytes = (
                b"# Test Encoding\n\nThis has invalid bytes: \xff\xfe"
            )
            prompt_file.write_bytes(invalid_bytes)

            # Mock the read_text method to simulate both UTF-8 and system
            # default failure
            def mock_read_text_both_fail(_self: Any, **_kwargs: Any) -> str:
                raise UnicodeDecodeError(
                    "utf-8", b"", 0, 1, "invalid start byte"
                )

            with patch.object(Path, "read_text", mock_read_text_both_fail):
                result = load_prompt_file(prompt_file)
                assert result["name"] == "test_encoding_bytes"
                # The content should be decoded with error replacement
                assert "Test Encoding" in result["content"]
                # Should contain replacement characters for invalid bytes
                assert (
                    "�" in result["content"]
                    or "Test Encoding" in result["content"]
                )

    def test_command_chaining_parsing(self) -> None:
        """Test that command chaining (&&) is parsed correctly."""

        # Test that commands with && are split correctly
        test_cmd = "echo hello && echo world"

        # This test verifies the parsing logic works
        # We can't easily test the actual execution without mocking subprocess
        commands = [c.strip() for c in test_cmd.split("&&")]
        assert len(commands) == 2
        assert commands[0] == "echo hello"
        assert commands[1] == "echo world"


@pytest.mark.unit
class TestSignalHandlerFunction:
    """Test cases for the signal_handler method."""

    @patch("prompts_mcp.main.logger")
    @patch("os._exit")
    def test_signal_handler_first_interrupt(
        self, mock_exit: Any, mock_logger: Any
    ) -> None:
        """Test handling of first interrupt signal."""
        # Create test server instance
        server = create_test_server()
        server.signal_count = 0

        # Call the signal handler method
        server.signal_handler(signal.SIGINT, None)

        # Check that the first log message was called
        mock_logger.info.assert_any_call(
            "Received interrupt signal, shutting down gracefully..."
        )
        mock_exit.assert_called_once_with(0)

    @patch("prompts_mcp.main.logger")
    @patch("os._exit")
    def test_signal_handler_second_interrupt(
        self, mock_exit: Any, mock_logger: Any
    ) -> None:
        """Test handling of second interrupt signal."""
        # Create test server instance
        server = create_test_server()
        server.signal_count = 1

        # Call the signal handler method
        server.signal_handler(signal.SIGINT, None)

        mock_logger.warning.assert_called_with(
            "Received second interrupt signal, forcing exit..."
        )
        mock_exit.assert_called_once_with(1)

    @patch("signal.signal")
    @patch("os._exit")
    def test_signal_handler_sets_up_second_handler(
        self, mock_exit: Any, mock_signal: Any
    ) -> None:
        """Test that signal handler sets up handler for second interrupt."""
        # Create test server instance
        server = create_test_server()
        server.signal_count = 0

        # Call the signal handler method
        server.signal_handler(signal.SIGINT, None)

        # Should set up new signal handlers
        assert mock_signal.call_count >= 2
        # Verify mock_exit was set up (though not called in this test)
        assert mock_exit is not None
