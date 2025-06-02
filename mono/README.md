# Python Experiment with LangChain

Text processing system with LangChain-based decision making and web interface.

## Requirements

- Python 3.12+
- Poetry for dependency management

## Core Components

- Text processor with two-step transformation (intent analysis + execution)
- LangChain agent for multi-step reasoning
- SQLAlchemy-based persistence layer
- RESTful API and web interface
- Web interface with decision chain visualization
- **MCP Server**: Model Context Protocol server for AI tool integration

## MCP Server

The MCP (Model Context Protocol) server provides standardized tool access for AI applications:

**Available Tools:**
- `calculate`: Safe mathematical expression evaluator
- `text_stats`: Text analysis (word count, character count, etc.)
- `system_info`: Basic system information
- `format_text`: Text formatting (upper, lower, title, etc.)

**Usage:**
```bash
make mcp-help     # Show MCP commands
make mcp-server   # Run server (stdio mode)
make mcp-client   # Run interactive client
```

**Integration Example:**
```python
from src.mcp_server import SimpleMCPServer
server = SimpleMCPServer()
server.run_stdio()
```

## Setup

```bash
python --version  # Ensure Python 3.12+
poetry install
cp .env.example .env  # Edit with your API keys
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

## Text Transformation Process

The text processor uses a sophisticated two-step approach for transformations:

1. **Intent Analysis**: Analyzes user input to understand transformation intent
2. **Transformation Execution**: Applies precise changes based on analyzed intent

This approach improves accuracy by separating understanding from execution.

## Integration

```python
# Basic usage
from src.modules.langchain_agent.api import process_with_langchain
chain, results = process_with_langchain("Your text")

# With persistence
from src.modules.langchain_agent.api import create_persistent_agent
agent = create_persistent_agent()
chain, chain_id = agent.process_text_with_persistence("Your text")

# Text transformation
from src.modules.text_processor.service import TextProcessorService
processor = TextProcessorService(session_repo, ai_client)
result = processor.process_text("a blue car", session_id)  # Establish state
result = processor.process_text("make it red", session_id)  # Transform
```

## Architecture

### Module Structure
- `src/modules/langchain_agent`: Multi-step reasoning agent
  - `services/`: Business logic
  - `models/`: Domain and API models
  - `repositories/`: Persistence interfaces and implementations
- `src/modules/text_processor`: Text processing functionality
  - `service.py`: Core business logic with two-step transformation
  - `models/`: Domain and API models
  - `repositories/`: Session storage interfaces and implementations
- `src/server/`: Flask application with REST API and Socket.IO

## License

MIT 