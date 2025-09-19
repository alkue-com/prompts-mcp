#!/usr/bin/env python3
"""Development script - alternative to Makefile"""

import os
import shutil
import subprocess
import sys


def run_command(cmd, description=""):
    """Run a command and exit on failure."""
    if description:
        print(f"{description}...")

    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def clean():
    """Remove build files, cache files, and test caches."""
    print("Cleaning build artifacts...")

    # Directories to remove
    dirs_to_remove = [
        "build",
        "dist",
        "htmlcov",
        ".pytest_cache",
        ".ruff_cache",
        "prompts_mcp.egg-info",
    ]

    # Files to remove
    files_to_remove = [".coverage", "coverage.xml"]

    # Remove directories
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")

    # Remove files
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed file: {file_name}")

    # Remove __pycache__ directories recursively
    for root, dirs, _files in os.walk("."):
        for d in dirs[:]:  # Use slice to avoid modifying list while iterating
            if d == "__pycache__":
                cache_dir = os.path.join(root, d)
                shutil.rmtree(cache_dir)
                print(f"Removed cache directory: {cache_dir}")
                dirs.remove(d)  # Remove from dirs to avoid descending into it

    # Remove .pyc and .pyo files
    for root, _dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".pyc", ".pyo")):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removed file: {file_path}")

    print("Clean completed!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python dev.py <command> [args...]")
        print("")
        print("Commands:")
        print("  install      Install Python dependencies")
        print("  format       Format code with ruff")
        print("  lint         Lint and fix code with ruff")
        print("  check        Check code without fixing")
        print("  test         Run tests (accepts pytest arguments)")
        print("  clean        Clean build artifacts")
        print("  all          Run all checks")
        print("")
        print("Examples:")
        print("  python dev.py test                     # Run all tests")
        print("  python dev.py test -m unit             # Run unit tests")
        print(
            "  python dev.py test tests/test_main.py  # Run specific test file"
        )
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "install": (
            "uv sync --extra dev --extra test --no-managed-python && "
            "uv run pre-commit install --hook-type pre-commit "
            "--hook-type commit-msg",
            "Installing Python dependencies",
        ),
        "format": ("uv run ruff format .", "Formatting code"),
        "lint": ("uv run ruff check . --fix", "Linting code"),
        "check": ("uv run ruff check .", "Checking code"),
        "clean": (None, "Cleaning build artifacts"),  # Handled by function
    }

    if command == "all":
        print("Running all checks...")
        for cmd_name in ["install", "format", "lint", "check", "test"]:
            if cmd_name == "test":
                # For 'all' command, run tests without additional arguments
                run_command("uv run pytest", "Running tests")
            else:
                cmd, desc = commands[cmd_name]
                run_command(cmd, desc)
    elif command == "clean":
        clean()  # Special case - use function instead of command
    elif command == "test":
        # Handle test command with pytest arguments
        pytest_args = sys.argv[2:] if len(sys.argv) > 2 else []
        pytest_cmd = (
            "uv run pytest " + " ".join(pytest_args)
            if pytest_args
            else "uv run pytest"
        )
        run_command(pytest_cmd, "Running tests")
    elif command in commands:
        cmd, desc = commands[command]
        run_command(cmd, desc)
    else:
        print(f"Unknown command: {command}")
        print(
            "Available commands: install, format, lint, check, test, clean, all"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
