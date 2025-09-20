## rc (2025-09-20)

### Feat

- **changelog**: add changelog file with unreleased refactor entry

### Fix

- **release**: reorder changelog generation before version bump

### Refactor

- reorganize dependency groups for better separation

## 1.4.1 (2025-09-20)

### Fix

- **deps**: move ruff from dev to test dependencies
- **dev**: simplify uv sync command to use --all-extras
- **dev**: update usage examples and remove debug logging

### Refactor

- **deps**: separate lint and test dependency groups
- migrate from optional-dependencies to dependency-groups
- **main**: remove unnecessary assert statements

## 1.4.0 (2025-09-20)

### Feat

- **release**: add PyPI credential support via .pypirc parsing
- **dev**: update setup workflow and rename install-dev to install

### Fix

- disable uv managed python and pin tool versions
- **dev**: support pytest arguments and improve help documentation
- **pyproject**: correct testpaths directory name

## 1.3.2 (2025-09-19)

### Fix

- **pyproject**: update author email and remove development status
- **dev**: add prompts_mcp.egg-info to clean targets

## 1.3.1 (2025-09-19)

## 1.3.0 (2025-09-19)

### Feat

- **release**: add dist directory clearing before build

### Fix

- **release**: add uv build step before publishing

## 1.2.2 (2025-09-19)

## 1.2.1 (2025-09-19)

## 1.2.0 (2025-09-19)

### Feat

- **build**: add testpypi index and switch to uv publish

## 1.1.0 (2025-09-19)

### Feat

- **release**: add Python release script to replace shell version
- **release**: add release script for automated version bumping and publishing
- add clean target and improve Makefile configuration
- add development tooling with ruff linting and makefile
- **testing**: add comprehensive test suite with coverage
- add graceful signal handling and version bump
- add development setup and improve configuration docs
- implement complete MCP server with FastMCP integration
- **prompts**: Add prompts

### Fix

- **pyproject**: lower Python requirement and update build system
- **dev**: add coverage.xml to cleanup and reorder cache dirs
- **main**: make PROMPTS_DIR environment variable required

### Refactor

- migrate pytest config from ini to pyproject.toml
- replace Makefile with dev.py and add CONTRIBUTING guide
- **main**: simplify prompt loading and improve type annotations
