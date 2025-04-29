# Define all phony targets
.PHONY: setup env check clean help install format lint test serve serve-dev \
	supabase-% # All supabase targets are marked as phony

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
	@echo
	@echo "Development commands:"
	@echo "  make setup       - Install dependencies and create .env file"
	@echo "  make install     - Install all dependencies"
	@echo "  make env         - Create default .env file"
	@echo "  make check       - Run all code quality checks (lint, format)"
	@echo "  make clean       - Clean up generated files"
	@echo "  make test        - Run tests"
	@echo
	@echo "Server commands:"
	@echo "  make serve       - Run the web server in production mode"
	@echo "  make serve-dev   - Run the web server in development mode"
	@echo "      HOST=0.0.0.0 - Host to bind to (default: 0.0.0.0)"
	@echo "      PORT=5000    - Port to bind to (default: 5000)"
	@echo
	@echo "Supabase commands:"
	@echo "  make supabase-install  - Install Supabase CLI"
	@echo "  make supabase-init     - Initialize Supabase project"
	@echo "  make supabase-login    - Login to Supabase"
	@echo "  make supabase-link     - Link to existing Supabase project"
	@echo "  make supabase-push     - Push migrations to Supabase"
	@echo "  make supabase-reset    - Reset database and apply migrations"
	@echo "  make supabase-diff     - Generate migration from database changes"
	@echo "      MIGRATION_NAME=feature_name - Name for migration (default: migration)"
	@echo "  make supabase-seed     - Apply seed data to database"
	@echo "  make supabase-status   - Check migrations status"
	@echo "  make supabase-start    - Start local Supabase services"
	@echo "  make supabase-stop     - Stop local Supabase services"
	@echo "  make supabase-restart  - Restart local Supabase services"
	@echo "  make supabase-local-db - Connect to local PostgreSQL database"
	@echo "  make supabase-new-migration - Create new migration file"

# Development commands
setup: install env

install:
	@echo "Installing dependencies..."
	@if [ -f pyproject.toml ]; then \
		if [ -f poetry.lock ] && ! poetry check --lock > /dev/null 2>&1; then \
			poetry lock || echo "⚠️ Lock file update failed, continuing anyway"; \
		elif [ ! -f poetry.lock ]; then \
			poetry lock || echo "⚠️ Lock file generation failed, continuing anyway"; \
		fi; \
		poetry install || echo "❌ Installation failed"; \
	else \
		echo "❌ pyproject.toml not found"; exit 1; \
	fi

lint:
	@poetry run flake8 src *.py

format:
	@poetry run isort src *.py && poetry run black src *.py

test: install
	@echo "Running tests..."
	@poetry run pytest tests/ -v

check: lint format

# Server commands
serve: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Starting web server on $(HOST):$(PORT)..."
	@poetry run gunicorn -b $(HOST):$(PORT) "src.server.app:create_app()"

serve-dev: install
	@if [ ! -f .env ]; then $(MAKE) env; fi
	@echo "Starting development web server on $(HOST):$(PORT)..."
	@poetry run python server.py --host $(HOST) --port $(PORT) --debug

clean:
	@rm -rf __pycache__ src/__pycache__ src/**/__pycache__ \
		*.pyc src/*.pyc src/**/*.pyc \
		.pytest_cache .coverage .mypy_cache

# Supabase commands
supabase-install:
	@echo "Installing Supabase CLI..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install -g supabase; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install supabase/tap/supabase; \
	else \
		echo "Neither npm nor brew found. Please install Node.js or Homebrew."; exit 1; \
	fi
	@echo "Verifying installation..." && supabase --version

supabase-login:
	@echo "Logging in to Supabase..."
	@supabase login
	@echo "If login was successful, you can see your projects with 'supabase projects list'"

supabase-link:
	@echo "Linking to Supabase project..."
	@if [ -z "$(SUPABASE_PROJECT_ID)" ] || [ "$(SUPABASE_PROJECT_ID)" = "your-project-id" ] || \
	   [ -z "$(SUPABASE_DB_PASSWORD)" ] || [ "$(SUPABASE_DB_PASSWORD)" = "your-password" ]; then \
		echo "Error: SUPABASE_PROJECT_ID and SUPABASE_DB_PASSWORD must be set in .env file"; exit 1; \
	fi
	@supabase link --project-ref $(SUPABASE_PROJECT_ID) --password $(SUPABASE_DB_PASSWORD)

supabase-push:
	@echo "Pushing migrations to Supabase database..."
	@supabase db push

supabase-reset:
	@echo "Resetting Supabase database (this will delete all data)..."
	@read -p "Are you sure? (y/n) " confirm && [ $$confirm = "y" ] || exit 1
	@supabase db reset

supabase-diff:
	@echo "Generating migration from database changes..."
	@supabase db diff --use-migra -f $(MIGRATION_NAME)

supabase-seed:
	@echo "Applying seed data to database..."
	@supabase db execute --file supabase/seed.sql

supabase-status:
	@echo "Checking status of migrations..."
	@supabase migration list

supabase-start:
	@echo "Starting local Supabase services..."
	@supabase start

supabase-stop:
	@echo "Stopping local Supabase services..."
	@supabase stop

supabase-restart:
	@echo "Restarting local Supabase services..."
	@supabase stop || true
	@supabase start

supabase-local-db:
	@echo "Connecting to local Supabase PostgreSQL database..."
	@supabase db connect

supabase-new-migration:
	@echo "Creating new empty migration file..."
	@if [ -z "$(MIGRATION_NAME)" ]; then \
		echo "Error: Please provide a migration name with MIGRATION_NAME=your_migration_name"; exit 1; \
	fi
	@timestamp=$$(date +%Y%m%d%H%M%S) && \
	filename="supabase/migrations/$${timestamp}_$(MIGRATION_NAME).sql" && \
	echo "-- Migration: $(MIGRATION_NAME)" > $$filename && \
	echo "-- Created at: $$(date)" >> $$filename && \
	echo "" >> $$filename && \
	echo "-- Enter your SQL commands here" >> $$filename && \
	echo "Created migration file: $$filename"

supabase-init:
	@echo "Initializing Supabase project..."
	@supabase init
	@if [ -f supabase/config.toml ] && [ ! -z "$(SUPABASE_PROJECT_ID)" ] && [ ! -z "$(SUPABASE_URL)" ]; then \
		sed -i '' "s/your-project-id/$(SUPABASE_PROJECT_ID)/g" supabase/config.toml && \
		sed -i '' "s|https://your-project-id.supabase.co|$(SUPABASE_URL)|g" supabase/config.toml && \
		sed -i '' "s|db.your-project-id.supabase.co|db.$(SUPABASE_PROJECT_ID).supabase.co|g" supabase/config.toml && \
		echo "Supabase project initialized successfully."; \
	else \
		echo "Initialization complete. Please update supabase/config.toml manually."; \
	fi
