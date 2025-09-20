#!/usr/bin/env python3
"""Release script for building dists and publishing them to PyPI.

Logic for getting uv publish to read credentials from ~/.pypirc by bulletmark.
See: https://github.com/bulletmark/uv-publish/blob/main/uv_publish.py
"""

import os
import shutil
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path

PYPIRC = Path.home() / ".pypirc"

DEFAULT_CONFIG = """
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/

[testpypi]
repository = https://test.pypi.org/legacy/
"""


def run_command(cmd: str, description: str = "") -> None:
    """Run a command and exit on failure."""
    if description:
        print(f"{description}...")

    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def get_current_branch() -> str:
    """Get the current git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error: Failed to get current branch")
        sys.exit(1)
    return result.stdout.strip()


def check_working_tree_clean() -> None:
    """Check if the working tree has uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "-s"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error: Failed to check git status")
        sys.exit(1)

    if result.stdout.strip():
        print("Error: Working tree has changes: Stash, commit or reset first")
        sys.exit(1)


def clear_dist_directory() -> None:
    """Clear the dist/ directory if it exists."""
    dist_path = "dist"
    if os.path.exists(dist_path):
        print("Clearing dist/ directory...")
        shutil.rmtree(dist_path)
        print("dist/ directory cleared")
    else:
        print("dist/ directory does not exist, skipping clear")


def build_uv_publish_command(repository: str = "pypi") -> list[str]:
    """Build uv publish command with credentials from .pypirc."""
    config = ConfigParser()
    config.read_string(DEFAULT_CONFIG)
    if PYPIRC.exists():
        config.read(PYPIRC)

    settings = config[repository]
    opts = []

    if user := settings.get("username"):
        password = settings.get("password")

        if "__token__" in user:
            if password:
                opts.append(f"--token={password}")
        else:
            opts.append(f"--username={user}")
            if password:
                opts.append(f"--password={password}")

        url = settings.get("repository")
        if url and opts:
            opts.append(f"--publish-url={url}")

    return ["uv", "publish"] + opts


def main() -> None:
    prerelease_type = sys.argv[1] if len(sys.argv) > 1 else None

    # Check if we're on main or master branch
    branch = get_current_branch()
    if branch not in ["main", "master"]:
        print(
            "Error: Releases must be created from trunk, "
            "run this script in main/master."
        )
        sys.exit(1)

    # Check if working tree is clean
    check_working_tree_clean()

    # Clear dist directory before building
    clear_dist_directory()

    if prerelease_type:
        print(f"Creating pre-release ({prerelease_type})")

        # Run bump command
        bump_cmd = ["uv", "run", "cz", "bump", "--prerelease", prerelease_type]
        run_command(" ".join(bump_cmd), "Creating pre-release")

        # Run build command
        run_command("uv build", "Building package")

        # Run publish command with testpypi credentials
        publish_cmd = build_uv_publish_command("testpypi")
        print("Publishing to testpypi...")
        print(f"Running: {' '.join(publish_cmd)}")
        result = subprocess.run(publish_cmd)
        if result.returncode != 0:
            print(f"Publish failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    else:
        # Run bump command
        bump_cmd = ["uv", "run", "cz", "bump"]
        run_command(" ".join(bump_cmd), "Creating release")

        # Run build command
        run_command("uv build", "Building package")

        # Run publish command with pypi credentials
        publish_cmd = build_uv_publish_command("pypi")
        print("Publishing to PyPI...")
        print(f"Running: {' '.join(publish_cmd)}")
        result = subprocess.run(publish_cmd)
        if result.returncode != 0:
            print(f"Publish failed with exit code {result.returncode}")
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
