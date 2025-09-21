# Changelog

All notable changes to this project will be documented in this file.

We use [PEP 440](https://peps.python.org/pep-0440/) version scheme and
do [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

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
