# Changelog

All notable changes to this project will be documented in this file.

We use [PEP 440](https://peps.python.org/pep-0440/) version scheme and
do [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

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

## 1.5.2rc2 (2025-09-21)

### Refactor

- **dev**: extract helper functions from clean and main

## 1.5.2rc1 (2025-09-21)

### Fix

- **release**: add check=False to subprocess.run calls
- **dev**: add mypy_cache to clean directories
- **dev**: remove obsolete egg-info directory from clean targets
- **pyproject**: remove tag_format and changelog_incremental config

### Refactor

- **tests**: extract shared test utilities and optimize imports
- **main**: convert global functions to class-based architecture
- **dev**: consolidate mypy check into check command

### Perf

- **main**: optimize load_all_prompts with local variable caching

## 1.5.1 (2025-09-20)

### Refactor

- **release**: simplify cz bump commands and reorganize config
- **release**: consolidate changelog generation into bump command
