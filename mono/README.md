# Python Experiment with LangChain

Text processing system with LangChain-based decision making, CLI and web interfaces.

## Requirements

- Python 3.12+
- Poetry for dependency management

## Core Components

- Text processor with planning and execution steps
- LangChain agent for multi-step reasoning
- SQLAlchemy-based persistence layer
- CLI interface and RESTful API
- Web interface with decision chain visualization

## Setup

```bash
python --version  # Ensure Python 3.12+
poetry install
cp .env.example .env  # Edit with your API keys
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
make serve-dev [HOST=127.0.0.1] [PORT=8080]  # Development
make serve  # Production
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

## Architecture

### Module Structure
- `src/modules/langchain_agent`: Multi-step reasoning agent
  - `services/`: Business logic
  - `models/`: Domain and API models
  - `repositories/`: Persistence interfaces and implementations
- `src/modules/text_processor`: Text processing functionality
  - `service.py`: Core business logic
  - `models/`: Domain and API models
  - `repositories/`: Session storage interfaces and implementations
- `src/server/`: Flask application with REST API and Socket.IO

## License

MIT 