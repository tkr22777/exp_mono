.PHONY: setup env check clean help run lint format type-check

# Variables
PYTHON = python3
TEXT ?= "This is some example text to process and analyze. It has multiple sentences! How many? Let's find out."
NAME ?= "World"
VERBOSE ?= 0

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and create .env file"
	@echo "  make env         - Create default .env file"
	@echo "  make run         - Run the text processor with options:"
	@echo "    TEXT=\"Your text\"                - Text to process (optional)"
	@echo "    NAME=\"Your name\"                - Custom greeting name (optional)"
	@echo "    VERBOSE=1                       - Show detailed output (optional)"
	@echo "  make check       - Run all code quality checks (lint, format, type-check)"
	@echo "  make clean       - Clean up generated files"

# Setup the development environment and create env file
setup:
	@echo "Setting up Poetry environment..."
	poetry install
	@$(MAKE) env

# Create environment file
env:
	@echo "Creating environment file..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it to add your OpenAI API key."; \
	else \
		echo ".env file already exists."; \
	fi

# Run the experiment
run:
	@echo "Running with environment file: .env"
	@if [ ! -f .env ]; then \
		echo "Environment file .env not found!"; \
		echo "Creating default environment file..."; \
		$(MAKE) env; \
	fi
	@echo "Processing text with AI..."
	poetry run python python_experiment.py --name $(NAME) --text $(TEXT) $(if $(filter 1,$(VERBOSE)),--verbose,)

# Linting
lint:
	@echo "Running flake8..."
	poetry run flake8 *.py

# Formatting
format:
	@echo "Formatting with isort and black..."
	poetry run isort *.py
	poetry run black *.py

# Type checking
type-check:
	@echo "Running mypy..."
	poetry run mypy *.py

# Code quality checks (combines all checks)
check:
	@echo "Running all code quality checks..."
	@echo "-------------------------------"
	@failures=0; \
	echo "Running flake8..."; \
	poetry run flake8 *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ Flake8 check failed!"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ Flake8 check passed!"; \
	fi; \
	echo "-------------------------------"; \
	echo "Running isort..."; \
	poetry run isort --check-only *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ isort check failed!"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ isort check passed!"; \
	fi; \
	echo "-------------------------------"; \
	echo "Running black..."; \
	poetry run black --check *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ black check failed!"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ black check passed!"; \
	fi; \
	echo "-------------------------------"; \
	echo "Running mypy..."; \
	poetry run mypy *.py; \
	if [ $$? -ne 0 ]; then \
		echo "❌ Type check failed!"; \
		failures=$$((failures+1)); \
	else \
		echo "✅ Type check passed!"; \
	fi; \
	echo "-------------------------------"; \
	if [ $$failures -gt 0 ]; then \
		echo "❌ Code quality checks: $$failures check(s) failed!"; \
		exit 1; \
	else \
		echo "✅ All code quality checks passed!"; \
	fi

# Automatically fix formatting issues
fix-format:
	@echo "Fixing formatting issues with isort and black..."
	poetry run isort *.py
	poetry run black *.py
	@echo "✅ Formatting fixed!"

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .mypy_cache 