.PHONY: setup env check clean help install format lint test serve serve-dev supabase-install supabase-login supabase-link supabase-push supabase-reset supabase-diff supabase-seed supabase-status supabase-start supabase-stop supabase-restart supabase-local-db supabase-new-migration

# Variables
PYTHON = python3
PORT ?= 5000
HOST ?= 0.0.0.0
MIGRATION_NAME ?= migration

# Include .env file if it exists
-include .env

# Default values if not set in .env
SUPABASE_PROJECT_ID ?= your-project-id
SUPABASE_DB_PASSWORD ?= your-password

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
	@echo ""
	@echo "Supabase Commands:"
	@echo "  make supabase-install   - Install Supabase CLI"
	@echo "  make supabase-login     - Login to Supabase CLI"
	@echo "  make supabase-link      - Link local project to Supabase project"
	@echo "  make supabase-push      - Push migrations to Supabase database"
	@echo "  make supabase-reset     - Reset Supabase database and apply migrations"
	@echo "  make supabase-diff      - Generate a migration from database changes"
	@echo "    MIGRATION_NAME=feature_name      - Name for the migration (optional)"
	@echo "  make supabase-seed      - Apply seed data to database"
	@echo "  make supabase-status    - Check status of migrations"
	@echo "  make supabase-start     - Start local Supabase services"
	@echo "  make supabase-stop      - Stop local Supabase services"
	@echo "  make supabase-restart   - Restart local Supabase services"
	@echo "  make supabase-local-db  - Connect to local Supabase PostgreSQL database"
	@echo "  make supabase-new-migration - Create a new Supabase migration"

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

# Supabase CLI commands

# Install Supabase CLI
supabase-install:
	@echo "Installing Supabase CLI..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install -g supabase; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install supabase/tap/supabase; \
	else \
		echo "Neither npm nor brew found. Please install Node.js or Homebrew first, or follow installation instructions at https://supabase.com/docs/guides/cli"; \
		exit 1; \
	fi
	@echo "Verifying installation..."
	@supabase --version

# Login to Supabase CLI
supabase-login:
	@echo "Logging in to Supabase..."
	@supabase login
	@echo "If login was successful, you can see your projects with 'supabase projects list'"

# Link local project to Supabase project
supabase-link:
	@echo "Linking to Supabase project..."
	@if [ -z "$(SUPABASE_PROJECT_ID)" ] || [ "$(SUPABASE_PROJECT_ID)" = "your-project-id" ]; then \
		echo "Error: SUPABASE_PROJECT_ID not set in .env file"; \
		exit 1; \
	fi
	@if [ -z "$(SUPABASE_DB_PASSWORD)" ] || [ "$(SUPABASE_DB_PASSWORD)" = "your-password" ]; then \
		echo "Error: SUPABASE_DB_PASSWORD not set in .env file"; \
		exit 1; \
	fi
	@supabase link --project-ref $(SUPABASE_PROJECT_ID) --password $(SUPABASE_DB_PASSWORD)

# Push migrations to Supabase database
supabase-push:
	@echo "Pushing migrations to Supabase database..."
	@supabase db push

# Reset Supabase database and apply migrations
supabase-reset:
	@echo "Resetting Supabase database (this will delete all data)..."
	@read -p "Are you sure? (y/n) " confirm && [ $$confirm = "y" ] || exit 1
	@supabase db reset

# Generate a migration from database changes
supabase-diff:
	@echo "Generating migration from database changes..."
	@supabase db diff --use-migra -f $(MIGRATION_NAME)

# Apply seed data to database
supabase-seed:
	@echo "Applying seed data to database..."
	@supabase db execute --file supabase/seed.sql

# Check status of migrations
supabase-status:
	@echo "Checking status of migrations..."
	@supabase migration list

# Start local Supabase services
supabase-start:
	@echo "Starting local Supabase services..."
	@supabase start

# Stop local Supabase services
supabase-stop:
	@echo "Stopping local Supabase services..."
	@supabase stop

# Restart local Supabase services
supabase-restart:
	@echo "Restarting local Supabase services..."
	@supabase stop || true
	@supabase start

# Connect to local Supabase PostgreSQL database
supabase-local-db:
	@echo "Connecting to local Supabase PostgreSQL database..."
	@supabase db connect

# Create a new Supabase migration
supabase-new-migration:
	@echo "Creating new empty migration file..."
	@if [ -z "$(MIGRATION_NAME)" ]; then \
		echo "Error: Please provide a migration name with MIGRATION_NAME=your_migration_name"; \
		exit 1; \
	fi
	@timestamp=$$(date +%Y%m%d%H%M%S) && \
	filename="supabase/migrations/$${timestamp}_$(MIGRATION_NAME).sql" && \
	echo "-- Migration: $(MIGRATION_NAME)" > $$filename && \
	echo "-- Created at: $$(date)" >> $$filename && \
	echo "" >> $$filename && \
	echo "-- Enter your SQL commands here" >> $$filename && \
	echo "Created migration file: $$filename"
