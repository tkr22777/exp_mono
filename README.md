# Python Text Processing with AI

A Python application that processes text using multiple AI language model providers.

## Requirements

- Python 3.9+
- Poetry

## Quick Start

```bash
# Setup and run
make setup
make run TEXT="Your custom text to analyze"

# Run tests
make test
```

## Architecture

- **Core Components**:
  - `ai_client.py`: Multi-provider abstraction (OpenAI, Gemini, Deepseek)
  - `settings.py`: Environment-based configuration using pydantic-settings
  - `text_processor.py`: Two-step processing workflow
  - `plan_creator.py`: Text analysis planning

- **Supported AI Models**:
  - OpenAI GPT (required)
  - Google Gemini
  - Deepseek

## Configuration

Create a `.env` file with your API keys (generated from `.env.example`):

```
# Required
OPENAI_API_KEY=your_key
OPENAI_ORG=org-id_for_project_keys

# Optional
GEMINI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

Model parameters can also be configured in the `.env` file.

## Available Commands

```bash
# Core commands
make run [TEXT="..."] [NAME="..."]  # Run text processor with default AI model

# Testing commands
make test                           # Run all API tests with pytest
make debug-keys                     # Display API keys (masked) for verification

# Development commands
make check                          # Run all code quality checks
make fix-format                     # Fix formatting issues
make clean                          # Clean up generated files
```

## Key Implementation Details

- Poetry-based dependency management with fixed version for `google-generativeai`
- Pydantic-based configuration with runtime validation
- Centralized environment setup with fallback mechanisms
- Type-safe API client implementations with error handling
- Test suite with automatic API key validation

## Troubleshooting

- Python version compatibility issues: Ensure Python 3.9+ is used
- Lock file problems: Run `poetry lock --no-update` manually
- API Authentication: Verify correct API keys and permissions
- OpenAI Project API keys: Make sure you specify the organization ID in your .env file
- If an API fails: Check the test results and your API keys 