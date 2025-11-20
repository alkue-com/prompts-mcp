# Changelog

All notable changes to this project will be documented in this file.

We use [PEP 440](https://peps.python.org/pep-0440/) version scheme and
do [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## 1.7.0 (2025-11-20)

### Feat

- **prompts_mcp**: support prompt arguments with YAML frontmatter
- **prompts_mcp**: support nested prompt files with colon-separated names

### Fix

- **prompts_mcp**: remove leading slash from prompt names and update input argument usage
- **pyproject**: rename commit dependency group to git
- add uv availability check to dev and release scripts
- **ci**: remove v prefix from git tag verification

### Refactor

- simplify subprocess calls and remove bandit config
- **release**: require index parameter for publish option
- **release**: extract functions and add optional publish flag

## 1.6.0 (2025-09-21)

## 1.6.0rc1 (2025-09-21)

### Feat

- add command chaining support for cross-platform execution

### Fix

- **release**: add --yes flag to cz bump commands
- **release**: improve working tree status detection and error output
- **workflows**: add release workflow with RC creation testing
- **dev**: use shlex.split for proper Windows command parsing
- improve Windows cross-platform compatibility
- **config**: add repository validation and enable ruff rules

### Refactor

- **dev**: replace os path operations with pathlib
