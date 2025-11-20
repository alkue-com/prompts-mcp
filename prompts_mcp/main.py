"""
MCP Server for serving prompts from a local directory using FastMCP.

This server provides prompts from the prompts/ directory as MCP prompts,
making them accessible to any MCP-compatible client.
"""

import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompts-mcp")


def _is_signal_available(signal_name: str) -> bool:
    """Check if a signal is available on the current platform."""
    return hasattr(signal, signal_name)


class PromptsMCPServer:
    """MCP Server for serving prompts from a local directory using FastMCP."""

    def __init__(self) -> None:
        """Initialize server with environment variables and directory checks."""
        self.prompts_dir: Path | None = None
        self.app: FastMCP | None = None
        self.signal_count = 0
        self._initialize_server()

    def _initialize_server(self) -> None:
        """Initialize server with environment variables and directory checks."""
        # Directory containing prompts - must be set via PROMPTS_DIR
        # environment variable
        prompts_dir_env = os.getenv("PROMPTS_DIR")
        if not prompts_dir_env:
            logger.error(
                "PROMPTS_DIR environment variable is required. Please set "
                "PROMPTS_DIR to the path containing your prompt files"
            )
            sys.exit(1)

        self.prompts_dir = Path(prompts_dir_env).expanduser().resolve()

        # Check if PROMPTS_DIR exists, exit if it doesn't
        if not self.prompts_dir.exists():
            logger.error(
                "Prompts directory does not exist: %s. Please set "
                "PROMPTS_DIR environment variable to a valid path",
                self.prompts_dir,
            )
            sys.exit(1)

        # Create the FastMCP server
        self.app = FastMCP("prompts-mcp")

    def _validate_prompts_directory(self) -> Path | None:
        """Validate that prompts directory is initialized and return it."""
        if self.prompts_dir is None:
            logger.error("PROMPTS_DIR is not initialized")
            return None
        return self.prompts_dir

    def _should_skip_file(self, prompt_file: Path) -> bool:
        """Check if a prompt file should be skipped."""
        return prompt_file.name == "README.md"

    def _load_single_prompt(
        self, prompt_file: Path, prompts_dir: Path
    ) -> dict[str, Any] | None:
        """Load a single prompt file and return its data."""
        try:
            # Calculate name based on relative path
            rel_path = prompt_file.relative_to(prompts_dir)
            if len(rel_path.parts) == 1:
                name = prompt_file.stem
            else:
                # Join all parent parts with :
                parent_str = ":".join(rel_path.parent.parts)
                name = f"{parent_str}:{prompt_file.stem}"

            return load_prompt_file(prompt_file, name)
        except (OSError, ValueError, UnicodeDecodeError) as e:
            logger.error("Error loading prompt file %s: %s", prompt_file, e)
            return None

    def load_all_prompts(self) -> None:
        """Load all prompts from the prompts directory and register them
        individually."""
        prompt_count = 0
        prompts_dir = self._validate_prompts_directory()

        if prompts_dir is None:
            return

        for prompt_file in prompts_dir.rglob("*.md"):
            if self._should_skip_file(prompt_file):
                continue

            prompt_data = self._load_single_prompt(prompt_file, prompts_dir)
            if prompt_data is not None:
                self.register_prompt(prompt_data)
                prompt_count += 1

        logger.info("Loaded %d prompts from %s", prompt_count, prompts_dir)

    def _validate_app_initialization(self) -> None:
        """Validate that FastMCP app is initialized."""
        if self.app is None:
            raise RuntimeError("FastMCP app is not initialized")

    def _create_prompt_handler(
        self, content: str, arguments: list[dict[str, Any]]
    ) -> Any:
        """Create a prompt handler for content and arguments."""
        # Strip YAML frontmatter from content for the actual prompt
        _, content_without_frontmatter = _parse_yaml_frontmatter(content)

        # Create handler based on whether arguments are present
        if not arguments:
            return self._create_simple_handler(content_without_frontmatter)
        return self._create_dynamic_args_handler(
            content_without_frontmatter, arguments
        )

    def _create_simple_handler(self, content: str) -> Any:
        """Create a simple handler without arguments."""

        async def prompt_handler(
            input: str | None = None,  # noqa: A002
        ) -> str:
            result = content
            if input:
                result += f"\n\n{input}"
            return result

        return prompt_handler

    def _create_dynamic_args_handler(
        self, content: str, arguments: list[dict[str, Any]]
    ) -> Any:
        """Create a handler with dynamic argument parameters."""
        import inspect
        from typing import Annotated

        # Create parameter list for the function signature
        params = []
        annotations = {}

        # Add each argument as a parameter
        for arg in arguments:
            arg_name = arg["name"]
            arg_desc = arg["description"]
            is_required = arg.get("required", False)

            # Create parameter with annotation
            if is_required:
                # Required parameter (no default)
                param = inspect.Parameter(
                    arg_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[str, arg_desc],
                )
            else:
                # Optional parameter (with default)
                param = inspect.Parameter(
                    arg_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default="",
                    annotation=Annotated[str, arg_desc],
                )
            params.append(param)
            annotations[arg_name] = Annotated[str, arg_desc]

        # Create the handler function
        async def handler(**kwargs: str) -> str:  # noqa: ANN401
            result = _substitute_arguments(content, kwargs)
            if "input" in kwargs and kwargs["input"]:
                result += f"\n\n{kwargs['input']}"
            return result

        # Update the function signature and annotations
        handler.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
        handler.__annotations__ = annotations

        return handler

    def register_prompt(self, prompt_data: dict[str, Any]) -> None:
        """Register an individual prompt with FastMCP."""
        prompt_name = prompt_data["name"]
        prompt_content = prompt_data["content"]
        prompt_description = prompt_data["description"]
        prompt_arguments = prompt_data.get("arguments", [])

        self._validate_app_initialization()
        prompt_handler = self._create_prompt_handler(
            prompt_content, prompt_arguments
        )

        # Register the prompt with FastMCP
        if self.app is None:
            raise RuntimeError("FastMCP app is not initialized")
        self.app.prompt(name=prompt_name, description=prompt_description)(
            prompt_handler
        )

    def signal_handler(self, _signum: int, _frame: Any) -> None:
        """Handle interrupt signals gracefully."""
        self.signal_count += 1

        if self.signal_count == 1:
            logger.info(
                "Received interrupt signal, shutting down gracefully..."
            )
            logger.info("Press Ctrl+C again to force exit")
            # Set up handler for second interrupt to force exit
            signal.signal(signal.SIGINT, lambda _s, _f: os._exit(1))
            # SIGTERM is not available on all platforms (e.g., Windows)
            if _is_signal_available("SIGTERM"):
                signal.signal(signal.SIGTERM, lambda _s, _f: os._exit(1))
            # Use os._exit for clean shutdown without thread cleanup issues
            os._exit(0)
        else:
            logger.warning("Received second interrupt signal, forcing exit...")
            os._exit(1)


def _extract_title_from_filename(prompt_path: Path) -> str:
    """Extract title from filename converting _ to spaces."""
    return prompt_path.stem.replace("_", " ").title()


def _extract_description_from_identity_section(lines: list[str]) -> str:
    """Extract description from IDENTITY AND PURPOSE section."""
    description = ""
    in_identity_section = False

    for line in lines:
        if line.strip().upper().startswith("# IDENTITY AND PURPOSE"):
            in_identity_section = True
            continue
        if line.strip().startswith("#") and in_identity_section:
            break
        if in_identity_section and line.strip():
            description += line.strip() + " "

    return description.strip()


def _extract_fallback_description(lines: list[str]) -> str:
    """Extract fallback description from first non-empty line."""
    for line in lines:
        if line.strip() and not line.startswith("#"):
            return line.strip()[:100] + "..."
    return ""


def _extract_description_from_content(content: str) -> str:
    """Extract description from prompt content."""
    lines = content.split("\n")

    # Try to extract from IDENTITY AND PURPOSE section first
    description = _extract_description_from_identity_section(lines)

    # If no description found, use fallback
    if not description:
        description = _extract_fallback_description(lines)

    return description


def _parse_yaml_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from content.

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    import re

    # Check if content starts with YAML frontmatter (---)
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    yaml_content = match.group(1)
    remaining_content = match.group(2)

    try:
        import yaml

        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter or {}, remaining_content
    except (yaml.YAMLError, ImportError):
        # If YAML parsing fails, return empty dict and original content
        return {}, content


def _extract_arguments_from_frontmatter(
    frontmatter: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract argument definitions from YAML frontmatter.

    Returns:
        List of argument definitions with name, description, and required fields
    """
    if "arguments" not in frontmatter:
        return []

    arguments = frontmatter["arguments"]
    if not isinstance(arguments, list):
        return []

    return [
        {
            "name": arg["name"],
            "description": arg.get("description", ""),
            "required": arg.get("required", False),
        }
        for arg in arguments
        if isinstance(arg, dict) and "name" in arg
    ]


def _find_argument_placeholders(content: str) -> set[str]:
    """Find all argument placeholders in content.

    Supports both ${arg_name} and $ARGUMENTS syntax.

    Returns:
        Set of argument names found in the content
    """
    import re

    # Find ${arg_name} style placeholders
    placeholders = set(re.findall(r"\$\{(\w+)\}", content))

    # Check for $ARGUMENTS placeholder
    if "$ARGUMENTS" in content:
        placeholders.add("ARGUMENTS")

    return placeholders


def _substitute_arguments(content: str, arguments: dict[str, str]) -> str:
    """Substitute argument placeholders with actual values.

    Args:
        content: The prompt content with placeholders
        arguments: Dictionary of argument name to value mappings

    Returns:
        Content with placeholders replaced by actual values
    """

    result = content

    # Replace ${arg_name} style placeholders
    for arg_name, arg_value in arguments.items():
        placeholder = f"${{{arg_name}}}"
        result = result.replace(placeholder, arg_value)

    # Handle $ARGUMENTS placeholder (backward compatibility)
    if "ARGUMENTS" in arguments:
        result = result.replace("$ARGUMENTS", arguments["ARGUMENTS"])

    return result


def load_prompt_file(
    prompt_path: Path, name: str | None = None
) -> dict[str, Any]:
    """Load and parse a prompt file."""
    try:
        # Try UTF-8 first, fall back to system default if needed
        content = prompt_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fall back to system default encoding if UTF-8 fails
        try:
            content = prompt_path.read_text()
        except UnicodeDecodeError:
            # Last resort: read as bytes and decode with errors='replace'
            content = prompt_path.read_bytes().decode("utf-8", errors="replace")

    # Parse YAML frontmatter if present
    frontmatter, content_without_frontmatter = _parse_yaml_frontmatter(content)

    # Extract arguments from frontmatter
    arguments = _extract_arguments_from_frontmatter(frontmatter)

    # If no arguments defined in frontmatter, infer from placeholders
    if not arguments:
        placeholders = _find_argument_placeholders(content_without_frontmatter)
        arguments = [
            {
                "name": placeholder,
                "description": f"Value for {placeholder}",
                "required": False,
            }
            for placeholder in sorted(placeholders)
        ]

    title = _extract_title_from_filename(prompt_path)
    description = _extract_description_from_content(content_without_frontmatter)

    return {
        "name": name or prompt_path.stem,
        "title": title,
        "description": description,
        "content": content,  # Keep original content with frontmatter
        "arguments": arguments,
    }


def main() -> None:
    """Main entry point for the MCP server."""
    # Create server instance
    server = PromptsMCPServer()

    logger.info("Starting prompts-mcp server with FastMCP")
    logger.info("Using prompts directory: %s", server.prompts_dir)

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, server.signal_handler)
    # SIGTERM is not available on all platforms (e.g., Windows)
    if _is_signal_available("SIGTERM"):
        signal.signal(signal.SIGTERM, server.signal_handler)

    # Load all prompts
    server.load_all_prompts()

    # Run the server directly - signal handler will handle shutdown
    if server.app is None:
        logger.error("FastMCP app is not initialized")
        sys.exit(1)

    try:
        server.app.run()
    except (OSError, ValueError, RuntimeError) as e:
        logger.error("Server error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
