.PHONY: setup env check clean help install format lint test serve serve-dev

# Variables
PYTHON = python3
PORT ?= 5000
HOST ?= 0.0.0.0

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and create .env file"
	@echo "  make install     - Install all dependencies"
	@echo "  make env         - Create default .env file"
	@echo "  make check       - Run all code quality checks (lint, format)"
	@echo "  make clean       - Clean up generated files"
	@echo "  make test        - Run tests"
	@echo "  make serve       - Run the web server in production mode"
	@echo "    HOST=0.0.0.0                     - Host to bind to (optional)"
	@echo "    PORT=5000                        - Port to bind to (optional)"
	@echo "  make serve-dev   - Run the web server in development mode"
	@echo "    HOST=0.0.0.0                     - Host to bind to (optional)"
	@echo "    PORT=5000                        - Port to bind to (optional)"

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
		echo "FLASK_APP=src.server.app:create_app()" > .env && \
		echo "FLASK_ENV=development" >> .env && \
		echo "FLASK_DEBUG=1" >> .env && \
		echo "Created .env file."; \
	else \
		echo ".env file already exists"; \
	fi

# Linting
lint:
	@poetry run flake8 src *.py

# Formatting
format:
	@poetry run isort src *.py && poetry run black src *.py

# Run tests
test: install
	@echo "Running tests..."
	@poetry run pytest tests/ -v

# Code quality checks (combines all checks)
check: lint format

# Run the web server (production mode)
serve: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Starting web server on $(HOST):$(PORT)..."
	@poetry run gunicorn -b $(HOST):$(PORT) "src.server.app:create_app()"

# Run the web server (development mode)
serve-dev: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Starting development web server on $(HOST):$(PORT)..."
	@poetry run python server.py --host $(HOST) --port $(PORT) --debug

# Clean up
clean:
	@rm -rf __pycache__ src/__pycache__ src/**/__pycache__ \
		*.pyc src/*.pyc src/**/*.pyc \
		.pytest_cache .coverage .mypy_cache 
