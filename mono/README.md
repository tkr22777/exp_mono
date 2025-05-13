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
from src.langchain_agent.api import process_with_langchain
chain, results = process_with_langchain("Your text")

# With persistence
from src.langchain_agent.persistence.api import create_persistent_agent
agent = create_persistent_agent()
chain, chain_id = agent.process_text_with_persistence("Your text")
```

## License

MIT 