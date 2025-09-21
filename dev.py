#!/usr/bin/env python3
"""Script for common development tasks - alternative to Makefile"""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str = "") -> None:
    """Run a command and exit on failure."""
    if description:
        print(f"{description}...")

    print(f"Running: {cmd}")

    # Handle command chaining (&&) across platforms
    if "&&" in cmd:
        commands = [c.strip() for c in cmd.split("&&")]
        for i, sub_cmd in enumerate(commands):
            if i > 0:
                print(f"Running chained command: {sub_cmd}")
            run_single_command(sub_cmd)
    else:
        run_single_command(cmd)


def run_single_command(cmd: str) -> None:
    """Run a single command without chaining."""
    try:
        result = subprocess.run(shlex.split(cmd), check=False)
    except FileNotFoundError:
        print(f"Command not found: {cmd}")
        sys.exit(1)

    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def _remove_directories(dirs_to_remove: list[str]) -> None:
    """Remove specified directories if they exist."""
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")


def _remove_files(files_to_remove: list[str]) -> None:
    """Remove specified files if they exist."""
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            file_path.unlink()
            print(f"Removed file: {file_name}")


def _remove_pycache_directories() -> None:
    """Remove __pycache__ directories recursively."""
    for root, dirs, _files in os.walk("."):
        for d in dirs[:]:  # Use slice to avoid modifying list while iterating
            if d == "__pycache__":
                cache_dir = Path(root) / d
                shutil.rmtree(cache_dir)
                print(f"Removed cache directory: {cache_dir}")
                dirs.remove(d)  # Remove from dirs to avoid descending into it


def _remove_compiled_python_files() -> None:
    """Remove .pyc and .pyo files recursively."""
    for root, _dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".pyc", ".pyo")):
                file_path = Path(root) / file
                file_path.unlink()
                print(f"Removed file: {file_path}")


def clean() -> None:
    """Remove build files, cache files, and test caches."""
    print("Cleaning build artifacts...")

    # Directories to remove
    dirs_to_remove = [
        "dist",
        "htmlcov",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
    ]

    # Files to remove
    files_to_remove = [".coverage", "coverage.xml"]

    # Remove directories
    _remove_directories(dirs_to_remove)

    # Remove files
    _remove_files(files_to_remove)

    # Remove __pycache__ directories recursively
    _remove_pycache_directories()

    # Remove .pyc and .pyo files
    _remove_compiled_python_files()

    print("Clean completed!")


def _check_uv_available() -> None:
    """Check if uv is available and exit with error if not."""
    if not shutil.which("uv"):
        print("Error: 'uv' command not found. Please install uv first.")
        print(
            "Visit https://docs.astral.sh/uv/getting-started/installation/ "
            "for installation instructions."
        )
        sys.exit(1)


def _print_usage() -> None:
    """Print usage information and exit."""
    print("Usage: ./dev.py <command> [args...]")
    print("")
    print("Commands:")
    print("  sync         Sync dependencies")
    print("  format       Format code with ruff")
    print("  lint         Lint and fix code with ruff")
    print("  check        Run type checking with mypy")
    print("  test         Run tests (accepts pytest arguments)")
    print("")
    print("  all          Run all above")
    print("  clean        Clean build artifacts and cache files")
    print("")
    print("Examples:")
    print("  ./dev.py test                     # Run all tests")
    print("  ./dev.py test -m unit             # Run unit tests")
    print("  ./dev.py test tests/test_main.py  # Run specific test file")
    sys.exit(1)


def _get_commands() -> dict[str, tuple[str | None, str]]:
    """Get the available commands and their configurations."""
    return {
        "sync": (
            "uv sync --all-groups && "
            "uv run pre-commit install --hook-type pre-commit "
            "--hook-type commit-msg",
            "Syncing dependencies",
        ),
        "format": ("uv run ruff format .", "Formatting code"),
        "lint": ("uv run ruff check . --fix", "Linting code"),
        "check": ("uv run mypy .", "Running type checking"),
        "clean": (None, "Cleaning build artifacts"),  # Handled by function
    }


def _run_all_commands() -> None:
    """Run all available commands in sequence."""
    print("Running all checks...")
    commands = _get_commands()

    for cmd_name in ["sync", "format", "lint", "check", "test"]:
        if cmd_name == "test":
            # For 'all' command, run tests without additional arguments
            run_command("uv run pytest", "Running tests")
        else:
            cmd, desc = commands[cmd_name]
            if cmd is not None:
                run_command(cmd, desc)


def _run_test_command() -> None:
    """Handle test command with pytest arguments."""
    pytest_args = sys.argv[2:] if len(sys.argv) > 2 else []
    pytest_cmd = (
        "uv run pytest " + " ".join(pytest_args)
        if pytest_args
        else "uv run pytest"
    )
    run_command(pytest_cmd, "Running tests")


def _run_single_command(command: str) -> None:
    """Run a single command from the commands dictionary."""
    commands = _get_commands()

    if command in commands:
        cmd, desc = commands[command]
        if cmd is not None:
            run_command(cmd, desc)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: sync, format, lint, check, test, clean, all")
        sys.exit(1)


def main() -> None:
    """Main entry point for the development script."""
    # Check if uv is available before doing anything else
    _check_uv_available()

    if len(sys.argv) < 2:
        _print_usage()

    command = sys.argv[1]

    if command == "all":
        _run_all_commands()
    elif command == "clean":
        clean()  # Special case - use function instead of command
    elif command == "test":
        _run_test_command()
    else:
        _run_single_command(command)


if __name__ == "__main__":
    main()
