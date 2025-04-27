# Python Experiment with LangChain

A CLI application that processes text using a multi-step approach with AI assistance and LangChain-based decision making.

## Features

- **Text Processing**: Standard two-step text processing with planning and execution
- **LangChain Decision Making**: Multi-step reasoning and decision making using LangChain
- **Persistent Storage**: Database storage of decision chains and intermediate steps
- **CLI Interface**: Simple command-line interface for all functionalities

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   # Optional: Add other API keys
   # GEMINI_API_KEY=your_gemini_api_key
   # DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

## Usage

### Basic Text Processing

Process text with the standard two-step approach:

```bash
python python_experiment.py --text "Your text to process goes here"
```

### LangChain Decision Making

Use LangChain for multi-step decision making:

```bash
python python_experiment.py --text "Your text to process goes here" --use-langchain
```

### Persistent Storage

Save the decision chain to the database:

```bash
python python_experiment.py --text "Your text to process goes here" --use-langchain --persist
```

### View Recent Decision Chains

List recently saved decision chains:

```bash
python python_experiment.py --list-recent
```

### Load a Specific Decision Chain

Load and display a specific decision chain by ID:

```bash
python python_experiment.py --chain-id "chain_id_here"
```

## Project Structure

- `python_experiment.py`: Main CLI application
- `src/`: Source code directory
  - `text_processor.py`: Core text processing functionality
  - `planner/`: Planning functionality
  - `llms/`: LLM client implementations
  - `langchain_agent/`: LangChain decision-making agent
    - `agent.py`: Core agent implementation
    - `api.py`: API for using the agent
    - `persistence/`: Database persistence functionality
      - `models.py`: SQLAlchemy database models
      - `database.py`: Database session management
      - `api.py`: API for persistence operations

## LangChain Agent Module

The LangChain Agent module implements a decision-making agent using LangChain with the following components:

1. **Decision Models**: `DecisionStep` and `DecisionChain` to model the decision-making process
2. **Agent Implementation**: `LangChainAgent` for multi-step reasoning
3. **Persistence Layer**: SQLAlchemy models and database operations for storing decision chains
4. **Persistence API**: Simple API for persisting and retrieving decision chains

### Using the LangChain Agent in Your Code

You can use the LangChain Agent in your own Python code:

```python
from src.langchain_agent.api import process_with_langchain

# Process text and get results
chain, results = process_with_langchain("Your text to process")

# Access the final decision
final_decision = results.final_decision

# Access individual steps
for step in chain.steps:
    print(f"Step {step.step_number}: {step.decision}")
```

### Using Persistence

To use persistence in your code:

```python
from src.langchain_agent.persistence.api import create_persistent_agent

# Create a persistent agent
agent = create_persistent_agent()

# Process text and save the chain
chain, chain_id = agent.process_text_with_persistence("Your text to process")

# Later, load the chain
loaded_chain = agent.load_chain(chain_id)
```

## License

MIT 