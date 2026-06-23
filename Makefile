.PHONY: test test-all lint clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  test        - Run all tests"
	@echo "  test-all    - Run all tests with verbose output"
	@echo "  lint        - Run code linting"
	@echo "  clean       - Clean up cache files"
	@echo "  help        - Show this help message"

# Run all tests
test:
	@echo "🧪 Running Radio Thermostat Test Suite..."
	pytest --cov=custom_components/radiotherm

# Run all tests with verbose output
test-all:
	@echo "🧪 Running Radio Thermostat Test Suite (Verbose)..."
	pytest -v --cov=custom_components/radiotherm

# Run linting
lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 custom_components/radiotherm/ tests/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not found. Install with: pip install flake8"; \
	fi
	@if command -v black >/dev/null 2>&1; then \
		black --check --diff custom_components/radiotherm/ tests/; \
	else \
		echo "black not found. Install with: pip install black"; \
	fi

# Clean up cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
