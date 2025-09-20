# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## 1.5.0 (2025-09-20)

### Feat

- **changelog**: add changelog file with unreleased refactor entry

### Fix

- **release**: reorder changelog generation before version bump

### Refactor

- **changelog**: add incremental generation and standardize format
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
