# Python Experiment with LangChain

Text processing system with LangChain-based decision making, CLI and web interfaces.

## Core Components

- Text processor with planning and execution steps
- LangChain agent for multi-step reasoning
- SQLAlchemy-based persistence layer
- CLI interface and RESTful API
- Web interface with decision chain visualization

## Setup

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env  # Then edit with your API keys
```

## CLI Usage

```bash
# Basic text processing
poetry run python python_experiment.py --text "Your text"

# With LangChain and persistence
poetry run python python_experiment.py --text "Your text" --use-langchain --persist

# View chains
poetry run python python_experiment.py --list-recent
poetry run python python_experiment.py --chain-id "chain_id"
```

## Server

```bash
# Development mode
make serve-dev [HOST=127.0.0.1] [PORT=8080]

# Production mode
make serve
```

## API Endpoints

```
POST /api/process           # Process text
GET /api/chains             # List chains
GET /api/chains/{chain_id}  # Get chain details
```

## Integration

```python
# Basic usage
from src.modules.langchain_agent.api import process_with_langchain
chain, results = process_with_langchain("Your text")

# With persistence
from src.modules.langchain_agent.api import create_persistent_agent
agent = create_persistent_agent()
chain, chain_id = agent.process_text_with_persistence("Your text")
```

## Development Notes

### Module Structure
- Business logic is in `src/modules/langchain_agent/services`
- Domain models are in `src/modules/langchain_agent/models/domain.py`
- API models are in `src/modules/langchain_agent/models/api.py`
- Repository interfaces are in `src/modules/langchain_agent/repositories/interfaces.py`
- SQLite implementation is in `src/modules/langchain_agent/repositories/sqlite_repository.py`
- SQLAlchemy models are in `src/modules/langchain_agent/repositories/models.py`

The Text Processor module follows a similar structure:
- Business logic is in `src/modules/text_processor/service.py`
- Domain models are in `src/modules/text_processor/models/domain.py`
- API models are in `src/modules/text_processor/models/api.py`
- Repository interfaces are in `src/modules/text_processor/repositories/interfaces.py`
- In-memory implementation is in `src/modules/text_processor/repositories/memory_repositories.py`

### Migration Status
The LangChain Agent module has been successfully migrated from `src/langchain_agent` to `src/modules/langchain_agent`.

- ✅ All imports in the main codebase have been updated
- ✅ The module structure follows best practices for separating business logic from infrastructure
- ✅ The module is working correctly in the application
- ✅ All tests are passing

The Text Processor repositories have been migrated from `src/data/repositories` to `src/modules/text_processor/repositories`.

- ✅ Backward compatibility is maintained for existing code
- ✅ The module structure is consistent with other modules
- ✅ All tests are passing

### Known Issues
- Some type errors are still present but are being ignored via mypy.ini configuration
- The test suite has been updated to match the new module structure

## License

MIT 