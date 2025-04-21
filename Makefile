.PHONY: setup env check clean help run lint format type-check install test debug-keys

# Variables
PYTHON = python3
TEXT ?= "This is some example text to process and analyze. It has multiple sentences! How many? Let's find out."
NAME ?= "World"
SRC_DIR = src
TEST_DIR = tests

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and create .env file"
	@echo "  make install     - Install all dependencies"
	@echo "  make env         - Create default .env file"
	@echo "  make run         - Run the text processor with options:"
	@echo "    TEXT=\"Your text\"                - Text to process (optional)"
	@echo "    NAME=\"Your name\"                - Custom greeting name (optional)"
	@echo "  make test        - Run all API tests using pytest"
	@echo "  make debug-keys  - Display API keys in masked format for verification"
	@echo "  make check       - Run all code quality checks (lint, format, type-check)"
	@echo "  make clean       - Clean up generated files"

# Setup the development environment and create env file
setup: install env

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

# Create environment file
env:
	@if [ ! -f .env ]; then \
		cp .env.example .env && echo "Created .env file. Edit it to add your API keys."; \
	else \
		echo ".env file already exists"; \
	fi

# Run the experiment
run: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@poetry run python python_experiment.py --name $(NAME) --text="$(TEXT)" || echo "❌ Execution failed"

# Test all AI models
test: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Running API tests..."
	@poetry run pytest $(TEST_DIR)/test_ai_models.py -v || echo "❌ Some tests failed or were skipped"

# Debug API keys
debug-keys: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Displaying masked API keys for verification..."
	@poetry run python -c "from tests.test_ai_models import print_config; print_config()"

# Linting
lint:
	@poetry run flake8 $(SRC_DIR)/*.py $(TEST_DIR)/*.py *.py

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
	poetry run flake8 $(SRC_DIR)/*.py $(TEST_DIR)/*.py *.py; \
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

# Clean up
clean:
	@rm -rf __pycache__ $(SRC_DIR)/__pycache__ $(TEST_DIR)/__pycache__ *.pyc $(SRC_DIR)/*.pyc $(TEST_DIR)/*.pyc .pytest_cache .coverage .mypy_cache 