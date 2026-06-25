.PHONY: test test-all venv format lint clean help

VENV = .venv
BIN = $(VENV)/bin

# Use virtual environment binaries if they exist, otherwise fallback to system commands
PYTEST = $(if $(wildcard $(BIN)/pytest),$(BIN)/pytest,pytest)
FLAKE8 = $(if $(wildcard $(BIN)/flake8),$(BIN)/flake8,flake8)
BLACK = $(if $(wildcard $(BIN)/black),$(BIN)/black,black)
ISORT = $(if $(wildcard $(BIN)/isort),$(BIN)/isort,isort)
MYPY = $(if $(wildcard $(BIN)/mypy),$(BIN)/mypy,mypy)
BANDIT = $(if $(wildcard $(BIN)/bandit),$(BIN)/bandit,bandit)

# Default target
help:
	@echo "Available commands:"
	@echo "  venv        - Create virtual environment and install dependencies via uv"
	@echo "  test        - Run all tests"
	@echo "  test-all    - Run all tests with verbose output"
	@echo "  format      - Auto-format code and imports"
	@echo "  lint        - Run code linting (flake8, black, isort, mypy, bandit)"
	@echo "  clean       - Clean up cache and virtual environment files"
	@echo "  help        - Show this help message"

# Create virtual environment and install dependencies using uv
venv:
	@echo "🚀 Creating virtual environment..."
	uv venv
	@echo "📦 Installing dependencies..."
	uv pip install -r requirements.txt -e .[dev]

# Run all tests
test:
	@echo "🧪 Running Radio Thermostat Test Suite..."
	$(PYTEST) --cov=custom_components/radiotherm

# Run all tests with verbose output
test-all:
	@echo "🧪 Running Radio Thermostat Test Suite (Verbose)..."
	$(PYTEST) -v --cov=custom_components/radiotherm

# Run formatting
format:
	@echo "🧹 Formatting code..."
	@if [ -f "$(BIN)/isort" ]; then \
		$(ISORT) --profile=black custom_components/radiotherm/ tests/; \
	elif command -v isort >/dev/null 2>&1; then \
		isort --profile=black custom_components/radiotherm/ tests/; \
	else \
		echo "isort not found. Run 'make venv' or 'pip install isort'"; \
	fi
	@if [ -f "$(BIN)/black" ]; then \
		$(BLACK) custom_components/radiotherm/ tests/; \
	elif command -v black >/dev/null 2>&1; then \
		black custom_components/radiotherm/ tests/; \
	else \
		echo "black not found. Run 'make venv' or 'pip install black'"; \
	fi

# Run linting
lint:
	@echo "🔍 Running code linting..."
	@if [ -f "$(BIN)/flake8" ]; then \
		$(FLAKE8) custom_components/radiotherm/ tests/ --max-line-length=88 --extend-ignore=E203,W503; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 custom_components/radiotherm/ tests/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not found. Run 'make venv' or 'pip install flake8'"; \
	fi
	@if [ -f "$(BIN)/black" ]; then \
		$(BLACK) --check --diff custom_components/radiotherm/ tests/; \
	elif command -v black >/dev/null 2>&1; then \
		black --check --diff custom_components/radiotherm/ tests/; \
	else \
		echo "black not found. Run 'make venv' or 'pip install black'"; \
	fi
	@if [ -f "$(BIN)/isort" ]; then \
		$(ISORT) --profile=black --check --diff custom_components/radiotherm/ tests/; \
	elif command -v isort >/dev/null 2>&1; then \
		isort --profile=black --check --diff custom_components/radiotherm/ tests/; \
	else \
		echo "isort not found. Run 'make venv' or 'pip install isort'"; \
	fi
	@if [ -f "$(BIN)/mypy" ]; then \
		$(MYPY) custom_components/radiotherm/; \
	elif command -v mypy >/dev/null 2>&1; then \
		mypy custom_components/radiotherm/; \
	else \
		echo "mypy not found. Run 'make venv' or 'pip install mypy'"; \
	fi
	@if [ -f "$(BIN)/bandit" ]; then \
		$(BANDIT) -r custom_components/radiotherm/; \
	elif command -v bandit >/dev/null 2>&1; then \
		bandit -r custom_components/radiotherm/; \
	else \
		echo "bandit not found. Run 'make venv' or 'pip install bandit'"; \
	fi

# Clean up cache files
clean:
	@echo "🧹 Cleaning up cache and virtual environment files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	rm -rf $(VENV)
