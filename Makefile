.PHONY: format lint check test install-dev

# Install development dependencies
install-dev:
	pip install -e ".[dev,test]"

# Format code with ruff
format:
	ruff format .

# Lint and fix code with ruff
lint:
	ruff check . --fix

# Check code without fixing
check:
	ruff check .

# Run tests
test:
	pytest

# Run all checks (format, lint, test)
all: format lint test
