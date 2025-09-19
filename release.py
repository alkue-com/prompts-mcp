#!/usr/bin/env python3
"""Release script - Python equivalent of release.sh"""

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


def get_current_branch():
    """Get the current git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error: Failed to get current branch")
        sys.exit(1)
    return result.stdout.strip()


def check_working_tree_clean():
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


def clear_dist_directory():
    """Clear the dist/ directory if it exists."""
    dist_path = "dist"
    if os.path.exists(dist_path):
        print("Clearing dist/ directory...")
        shutil.rmtree(dist_path)
        print("dist/ directory cleared")
    else:
        print("dist/ directory does not exist, skipping clear")


def main():
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
        cmd = (
            f'uvx --from commitizen cz bump --prerelease "{prerelease_type}" '
            f"--allow-no-commit && uv build && uv publish --index testpypi"
        )
        run_command(cmd, "Creating pre-release and publishing to testpypi")
    else:
        cmd = (
            "uvx --from commitizen cz bump --allow-no-commit && "
            "uv build && uv publish"
        )
        run_command(cmd, "Creating release and publishing to PyPI")


if __name__ == "__main__":
    main()
