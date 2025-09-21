#!/usr/bin/env python3
"""Release script for building dists and publishing them to PyPI.

Logic for getting uv publish to read credentials from ~/.pypirc by bulletmark.
See: https://github.com/bulletmark/uv-publish/blob/main/uv_publish.py
"""

import shlex
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


def get_current_branch() -> str:
    """Get the current git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("Error: Failed to get current branch")
        sys.exit(1)
    return result.stdout.strip()


def check_working_tree_clean() -> None:
    """Check if the working tree has uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "-s"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("Error: Failed to check git status")
        sys.exit(1)

    # Check for actual changes (non-empty lines with content)
    changes = [
        line for line in result.stdout.strip().split("\n") if line.strip()
    ]
    if changes:
        print("Error: Working tree has changes: Stash, commit or reset first")
        print("Changes detected:")
        for change in changes:
            print(f"  {change}")
        sys.exit(1)


def clear_dist_directory() -> None:
    """Clear the dist/ directory if it exists."""
    dist_path = Path("dist")
    if dist_path.exists():
        print("Clearing dist/ directory...")
        shutil.rmtree(dist_path)
        print("dist/ directory cleared")
    else:
        print("dist/ directory does not exist, skipping clear")


def _load_pypi_config(repository: str) -> ConfigParser:
    """Load PyPI configuration from .pypirc or use defaults."""
    config = ConfigParser()
    config.read_string(DEFAULT_CONFIG)
    if PYPIRC.exists():
        config.read(PYPIRC)

    # Ensure the requested repository section exists
    if repository not in config:
        raise ValueError(
            f"Repository '{repository}' not found in configuration"
        )

    return config


def _add_token_auth(opts: list[str], password: str) -> None:
    """Add token authentication to options."""
    if password:
        opts.append(f"--token={password}")


def _add_username_auth(
    opts: list[str], user: str, password: str | None
) -> None:
    """Add username/password authentication to options."""
    opts.append(f"--username={user}")
    if password:
        opts.append(f"--password={password}")


def _add_repository_url(opts: list[str], url: str | None) -> None:
    """Add repository URL to options if not empty."""
    if url and opts:
        opts.append(f"--publish-url={url}")


def build_uv_publish_command(repository: str = "pypi") -> list[str]:
    """Build uv publish command with credentials from .pypirc."""
    config = _load_pypi_config(repository)
    settings = config[repository]
    opts: list[str] = []

    if user := settings.get("username"):
        password = settings.get("password")

        if "__token__" in user:
            if password:
                _add_token_auth(opts, password)
        else:
            _add_username_auth(opts, user, password)

        url = settings.get("repository")
        _add_repository_url(opts, url)

    return ["uv", "publish"] + opts


def _check_uv_available() -> None:
    """Check if uv is available and exit with error if not."""
    if not shutil.which("uv"):
        print("Error: 'uv' command not found. Please install uv first.")
        print(
            "Visit https://docs.astral.sh/uv/getting-started/installation/ "
            "for installation instructions."
        )
        sys.exit(1)


def parse_arguments() -> tuple[str | None, str | None]:
    """Parse command line arguments.

    Returns:
        tuple: (prerelease_type, publish_index)
    """
    args = sys.argv[1:]
    prerelease_type = None
    publish_index = None
    i = 0
    while i < len(args):
        if args[i] == "--publish":
            if i + 1 >= len(args):
                print("Error: --publish requires an index name")
                print("Example: --publish pypi")
                sys.exit(1)
            publish_index = args[i + 1]
            i += 1  # Skip the index name
        elif args[i] in ["alpha", "beta", "rc"]:
            prerelease_type = args[i]
        i += 1
    return prerelease_type, publish_index


def validate_release_environment() -> None:
    """Validate that we're in a proper state for releasing."""
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


def run_bump_command(bump_cmd: list[str], publish_index: str | None) -> bool:
    """Run bump command and handle 'no commits found' error.

    Returns:
        bool: True if bump succeeded or no commits found with publish enabled,
            False if no commits found without publish enabled.
    """
    bump_result = subprocess.run(bump_cmd, check=False)
    if bump_result.returncode == 3:
        print("No commits found for bumping, continuing with current version")
        if not publish_index:
            print("Skipping publish (use --publish <index> to enable)")
            return False
    elif bump_result.returncode != 0:
        print(f"Bump command failed with exit code {bump_result.returncode}")
        sys.exit(bump_result.returncode)
    return True


def run_publish_command(publish_index: str | None) -> None:
    """Run publish command if publish_index is specified."""
    if publish_index:
        publish_cmd = build_uv_publish_command(publish_index)
        print(f"Publishing to {publish_index}...")
        print(f"Running: {' '.join(publish_cmd)}")
        result = subprocess.run(publish_cmd, check=False)
        if result.returncode != 0:
            print(f"Publish failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    else:
        print("Skipping publish (use --publish <index> to enable)")


def run_prerelease(prerelease_type: str, publish_index: str | None) -> None:
    """Run prerelease process."""
    print(f"Creating pre-release ({prerelease_type})")

    # Run bump command
    bump_cmd = [
        "uv",
        "run",
        "cz",
        "bump",
        "--prerelease",
        prerelease_type,
        "--yes",
    ]

    # Run bump command and handle errors
    if not run_bump_command(bump_cmd, publish_index):
        return

    # Run build command
    run_command("uv build", "Building package")

    # Run publish command
    run_publish_command(publish_index)


def run_release(publish_index: str | None) -> None:
    """Run regular release process."""
    # Run bump command
    bump_cmd = ["uv", "run", "cz", "bump", "--yes"]

    # Run bump command and handle errors
    if not run_bump_command(bump_cmd, publish_index):
        return

    # Run build command
    run_command("uv build", "Building package")

    # Run publish command
    run_publish_command(publish_index)


def main() -> None:
    """Main entry point for the release script."""
    # Check if uv is available before doing anything else
    _check_uv_available()

    prerelease_type, publish_index = parse_arguments()
    validate_release_environment()
    if prerelease_type:
        run_prerelease(prerelease_type, publish_index)
    else:
        run_release(publish_index)


if __name__ == "__main__":
    main()
