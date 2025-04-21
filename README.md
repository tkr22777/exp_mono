# Python Text Processing with AI

A simple Python application that processes text using AI capabilities.

## Quick Start

```bash
# Setup project and create .env file
make setup

# Run with default settings
make run
```

## Setup

```bash
# Install dependencies and create .env file
make setup

# Or just create .env file if dependencies are already installed
make env
```

After setup, **edit the `.env` file to add your OpenAI API key**.

## Running the Application

```bash
# Run with default text
make run

# Process custom text
make run TEXT="Your text to analyze"

# Set custom name for greeting
make run NAME="Your Name"

# Enable detailed output
make run VERBOSE=1

# Combine options
make run TEXT="Analyze this text." NAME="Alice" VERBOSE=1
```

## Code Quality

```bash
# Run all code quality checks at once
# (flake8, isort, black, mypy)
make check

# Automatically fix formatting issues
make fix-format
```

The `check` command runs all code quality tools and provides a clear report of which checks passed or failed.

## Maintenance Commands

```bash
# Clean up generated files
make clean

# Show all available commands
make help
```

For more information on each command, run `make help`. 