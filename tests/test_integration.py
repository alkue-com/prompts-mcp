"""
Integration tests for prompts-mcp package.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the prompts-mcp package."""

    def test_end_to_end_prompt_loading(self):
        """Test complete end-to-end prompt loading workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create multiple prompt files
            prompt_files = [
                (
                    "system_prompt.md",
                    "# System Prompt\n\n# IDENTITY AND PURPOSE\nThis is a system prompt for testing.",
                ),
                (
                    "user_prompt.md",
                    "# User Prompt\n\n# IDENTITY AND PURPOSE\nThis is a user prompt for testing.",
                ),
                ("README.md", "# README\n\nThis should be ignored."),
            ]

            for filename, content in prompt_files:
                (prompts_dir / filename).write_text(content)

            # Mock the environment and PROMPTS_DIR
            with patch.dict(os.environ, {"PROMPTS_DIR": str(prompts_dir)}):
                with patch("prompts_mcp.main.PROMPTS_DIR", prompts_dir):
                    with patch("prompts_mcp.main.register_prompt") as mock_register:
                        # Test loading all prompts
                        from prompts_mcp.main import load_all_prompts

                        load_all_prompts()

                        # Should register 2 prompts (excluding README.md)
                        assert mock_register.call_count == 2

                        # Verify the registered prompts
                        calls = mock_register.call_args_list
                        registered_names = [call[0][0]["name"] for call in calls]
                        assert "system_prompt" in registered_names
                        assert "user_prompt" in registered_names
                        assert "README" not in registered_names

    def test_prompt_file_parsing_variations(self):
        """Test various prompt file formats and edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Test different prompt file formats
            test_cases = [
                {
                    "filename": "standard_prompt.md",
                    "content": """# Standard Prompt

# IDENTITY AND PURPOSE
This is a standard prompt with proper formatting.

# USAGE
Use this prompt for testing purposes.

# EXAMPLES
Here are some examples.
""",
                    "expected_title": "Standard Prompt",
                    "expected_description": "This is a standard prompt with proper formatting.",
                },
                {
                    "filename": "minimal_prompt.md",
                    "content": "Just a simple prompt without any sections.",
                    "expected_title": "Minimal Prompt",
                    "expected_description": "Just a simple prompt without any sections....",
                },
                {
                    "filename": "complex_formatting.md",
                    "content": """# Complex Formatting

# IDENTITY AND PURPOSE
This prompt has complex formatting
with multiple lines
and various content.

# USAGE
Usage instructions here.
""",
                    "expected_title": "Complex Formatting",
                    "expected_description": "This prompt has complex formatting with multiple lines and various content.",
                },
                {
                    "filename": "prompt_with_special_chars.md",
                    "content": """# Prompt With Special Chars

# IDENTITY AND PURPOSE
This prompt contains special characters: @#$%^&*()_+-=[]{}|;':\",./<>?

# USAGE
Use carefully.
""",
                    "expected_title": "Prompt With Special Chars",
                    "expected_description": "This prompt contains special characters: @#$%^&*()_+-=[]{}|;':\",./<>?",
                },
            ]

            for test_case in test_cases:
                prompt_file = prompts_dir / test_case["filename"]
                prompt_file.write_text(test_case["content"])

                from prompts_mcp.main import load_prompt_file

                result = load_prompt_file(prompt_file)

                assert result["name"] == test_case["filename"].replace(".md", "")
                assert result["title"] == test_case["expected_title"]
                assert result["description"] == test_case["expected_description"]
                assert result["content"] == test_case["content"]

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a mix of valid and invalid files
            valid_file = prompts_dir / "valid_prompt.md"
            valid_file.write_text("# Valid Prompt\n\nValid content.")

            # Create a file that will cause an error when read
            invalid_file = prompts_dir / "invalid_prompt.md"
            invalid_file.write_text("# Invalid Prompt\n\nInvalid content.")

            # Mock file reading to raise an error for the invalid file
            original_read_text = Path.read_text

            def mock_read_text(self, encoding=None):
                if self.name == "invalid_prompt.md":
                    raise PermissionError("Cannot read file")
                return original_read_text(self, encoding)

            with patch.object(Path, "read_text", mock_read_text):
                with patch("prompts_mcp.main.PROMPTS_DIR", prompts_dir):
                    with patch("prompts_mcp.main.register_prompt") as mock_register:
                        with patch("prompts_mcp.main.logger") as mock_logger:
                            from prompts_mcp.main import load_all_prompts

                            load_all_prompts()

                            # Should log error for invalid file
                            mock_logger.error.assert_called()

                            # Should still register the valid file
                            mock_register.assert_called_once()

    def test_large_prompt_files(self):
        """Test handling of large prompt files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a large prompt file
            large_content = (
                "# Large Prompt\n\n" + "This is a large prompt file. " * 1000
            )
            large_file = prompts_dir / "large_prompt.md"
            large_file.write_text(large_content)

            from prompts_mcp.main import load_prompt_file

            result = load_prompt_file(large_file)

            assert result["name"] == "large_prompt"
            assert result["title"] == "Large Prompt"
            assert len(result["content"]) > 10000  # Should handle large content
            assert result["content"] == large_content
