"""
Performance tests for prompts-mcp package.
"""

import concurrent.futures
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from prompts_mcp.main import PromptsMCPServer, load_prompt_file


@pytest.mark.slow
class TestPerformance:
    """Performance tests for the prompts-mcp package."""

    def test_load_prompt_file_performance(self, temp_prompts_dir: Any) -> None:
        """Test performance of loading individual prompt files."""
        prompt_file = temp_prompts_dir / "test_prompt_1.md"

        # Measure time for multiple loads

        start_time = time.time()
        for _ in range(100):
            load_prompt_file(prompt_file)
        end_time = time.time()

        # Should complete 100 loads in reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0

    def test_load_all_prompts_performance(self, temp_prompts_dir: Any) -> None:
        """Test performance of loading all prompts."""
        # Create multiple prompt files
        for i in range(50):
            prompt_file = temp_prompts_dir / f"prompt_{i}.md"
            prompt_file.write_text(f"# Prompt {i}\n\nContent for prompt {i}.")

        # Create test server instance

        server = PromptsMCPServer.__new__(PromptsMCPServer)
        server.prompts_dir = temp_prompts_dir
        server.app = None
        server.signal_count = 0

        # Mock the register_prompt method

        with patch.object(server, "register_prompt"):
            start_time = time.time()
            server.load_all_prompts()
            end_time = time.time()

            # Should complete loading 50 prompts in reasonable time
            # (< 2 seconds)
            assert (end_time - start_time) < 2.0

    def test_memory_usage_with_large_files(self) -> None:
        """Test memory usage with large prompt files."""

        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()

            # Create a large prompt file (1MB)
            large_content = "# Large Prompt\n\n" + "x" * (1024 * 1024)
            large_file = prompts_dir / "large_prompt.md"
            large_file.write_text(large_content)

            # Load the large file

            result = load_prompt_file(large_file)

            # Verify content is loaded correctly
            assert len(result["content"]) == len(large_content)
            assert result["name"] == "large_prompt"
            assert result["title"] == "Large Prompt"

    def test_concurrent_prompt_loading(self, temp_prompts_dir: Any) -> None:
        """Test concurrent loading of multiple prompt files."""

        # Create multiple prompt files
        prompt_files = []
        for i in range(20):
            prompt_file = temp_prompts_dir / f"concurrent_prompt_{i}.md"
            prompt_file.write_text(
                f"# Concurrent Prompt {i}\n\nContent for concurrent prompt {i}."
            )
            prompt_files.append(prompt_file)

        def load_single_prompt(prompt_file: Any) -> Any:
            return load_prompt_file(prompt_file)

        # Load prompts concurrently
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(load_single_prompt, pf) for pf in prompt_files
            ]
            results = [future.result() for future in futures]
        end_time = time.time()

        # Should complete concurrent loading in reasonable time
        assert (end_time - start_time) < 1.0
        assert len(results) == 20

        # Verify all results are correct
        for i, result in enumerate(results):
            assert result["name"] == f"concurrent_prompt_{i}"
            assert result["title"] == f"Concurrent Prompt {i}"
