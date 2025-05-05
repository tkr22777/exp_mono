.PHONY: setup check clean help run lint format type-check install test serve serve-dev

# Variables
PYTHON = python3
TEXT ?= This is some example text to process and analyze. It has multiple sentences! How many? Let's find out.
NAME ?= World
SRC_DIR = src
TEST_DIR = tests
PORT ?= 5000
HOST ?= 0.0.0.0
TIMEOUT ?= 300

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies"
	@echo "  make install     - Install all dependencies"
	@echo "  make run         - Run the text processor with options:"
	@echo "    TEXT=\"Your text\"                - Text to process (optional)"
	@echo "    NAME=\"Your name\"                - Custom greeting name (optional)"
	@echo "  make test        - Run all API tests using pytest"
	@echo "  make check       - Run all code quality checks (lint, format, type-check)"
	@echo "  make clean       - Clean up generated files"
	@echo "  make serve       - Run the web server in production mode"
	@echo "    HOST=0.0.0.0                     - Host to bind to (optional)"
	@echo "    PORT=5000                        - Port to bind to (optional)"
	@echo "    TIMEOUT=300                      - Gunicorn worker timeout in seconds (optional)"
	@echo "  make serve-dev   - Run the web server in development mode"
	@echo "    HOST=0.0.0.0                     - Host to bind to (optional)"
	@echo "    PORT=5000                        - Port to bind to (optional)"

# Setup the development environment
setup: install

# Install dependencies with Poetry
install:
	@echo "Installing dependencies..."
	@if [ -f pyproject.toml ]; then \
		if [ -f poetry.lock ]; then \
			if ! poetry check --lock > /dev/null 2>&1; then \
				poetry lock || echo "⚠️ Lock file update failed, continuing anyway"; \
			fi; \
		else \
			poetry lock || echo "⚠️ Lock file generation failed, continuing anyway"; \
		fi; \
		poetry install || echo "❌ Installation failed"; \
	else \
		echo "❌ pyproject.toml not found"; \
		exit 1; \
	fi

# Run the experiment
run: install
	@poetry run python python_experiment.py --name "$(NAME)" --text "$(TEXT)" || echo "❌ Execution failed"

# Test all AI models
test: install
	@echo "Running API tests..."
	@poetry run pytest $(TEST_DIR) -v || echo "❌ Some tests failed or were skipped"

# Linting
lint:
	@poetry run flake8 $(SRC_DIR) $(TEST_DIR) *.py

# Formatting
format:
	@poetry run isort $(SRC_DIR) $(TEST_DIR) *.py && poetry run black $(SRC_DIR) $(TEST_DIR) *.py

# Type checking
type-check:
	@poetry run mypy $(SRC_DIR) $(TEST_DIR) *.py

# Code quality checks (combines all checks)
check:
	@failures=0; \
	echo "Running code quality checks..."; \
	poetry run flake8 $(SRC_DIR) $(TEST_DIR) *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ Flake8"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ Flake8"; \
	fi; \
	poetry run isort --check-only $(SRC_DIR) $(TEST_DIR) *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ isort"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ isort"; \
	fi; \
	poetry run black --check $(SRC_DIR) $(TEST_DIR) *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ black"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ black"; \
	fi; \
	poetry run mypy $(SRC_DIR) $(TEST_DIR) *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ mypy"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ mypy"; \
	fi; \
	if [ $$failures -gt 0 ]; then \
		echo "❌ $$failures check(s) failed"; \
		exit 1; \
	else \
		echo "✅ All checks passed"; \
	fi

# Automatically fix formatting issues
fix-format:
	@poetry run isort $(SRC_DIR) $(TEST_DIR) *.py && poetry run black $(SRC_DIR) $(TEST_DIR) *.py && echo "✅ Formatting fixed"

# Run the web server (production mode)
serve: install
	@echo "Starting web server on $(HOST):$(PORT) with timeout $(TIMEOUT)s..."
	@poetry run gunicorn -b $(HOST):$(PORT) --timeout $(TIMEOUT) "src.server.app:create_app()" || echo "❌ Server failed to start"

# Run the web server (development mode)
serve-dev: install
	@echo "Starting development web server on $(HOST):$(PORT)..."
	@poetry run python server.py --host $(HOST) --port $(PORT) --debug || echo "❌ Server failed to start"

# Clean up
clean:
	@rm -rf __pycache__ $(SRC_DIR)/__pycache__ $(TEST_DIR)/__pycache__ \
		$(SRC_DIR)/**/__pycache__ $(TEST_DIR)/**/__pycache__ \
		*.pyc $(SRC_DIR)/*.pyc $(TEST_DIR)/*.pyc $(SRC_DIR)/**/*.pyc $(TEST_DIR)/**/*.pyc \
		.pytest_cache .coverage .mypy_cache 