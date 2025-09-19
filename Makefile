.DEFAULT_GOAL := all
.PHONY: install-dev format lint check test clean all

# Install development dependencies
install-dev:
	uv pip install -e ".[dev,test]"

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

# Clean build files, cache files, and test caches
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Run all checks (format, lint, test)
all: install-dev format lint check test
