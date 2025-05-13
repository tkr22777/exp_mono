"""
Test configuration and fixtures for pytest.
"""
import pytest
from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import Generation, LLMResult
from langchain_core.runnables import Runnable
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.modules.langchain_agent import Base
from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep
from src.modules.langchain_agent.repositories.sqlite_repository import SQLiteDecisionChainRepository
from src.modules.langchain_agent.services.agent_service import LangChainAgentService


class MockLLM(Runnable):
    """Simple mock LLM for testing purposes."""

    def __init__(self, responses: Optional[List[str]] = None):
        """Initialize with predefined responses."""
        self.responses = responses or ["This is a mock response"]
        self.invocations = []

    def invoke(self, input_data: Any, **kwargs: Any) -> str:
        """Mock invoke method that returns predefined responses."""
        self.invocations.append(input_data)
        return self.responses.pop(0) if self.responses else "Default mock response"
    
    def batch(self, inputs: List[Any], **kwargs: Any) -> List[str]:
        """Process multiple inputs in a batch."""
        return [self.invoke(input_data, **kwargs) for input_data in inputs]
    
    async def ainvoke(self, input_data: Any, **kwargs: Any) -> str:
        """Async version of invoke."""
        return self.invoke(input_data, **kwargs)
    
    async def abatch(self, inputs: List[Any], **kwargs: Any) -> List[str]:
        """Async version of batch."""
        return self.batch(inputs, **kwargs)

    # Add property for compatibility
    @property
    def metadata(self) -> Dict[str, str]:
        """Required property."""
        return {"name": "MockLLM"}


@pytest.fixture
def mock_llm():
    """Fixture providing a mock LLM."""
    return MockLLM(
        [
            "Initial analysis of the text.",
            "Refinement of the analysis with alternatives.",
            "Final decision based on analysis.",
        ]
    )


@pytest.fixture
def in_memory_db():
    """Fixture providing an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(in_memory_db):
    """Fixture providing a database session with in-memory database."""
    Session = sessionmaker(bind=in_memory_db)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository():
    """Fixture providing a repository with in-memory database."""
    # Using None as db_path will use the in-memory database for testing
    return SQLiteDecisionChainRepository(db_path=None)


@pytest.fixture
def sample_decision_step():
    """Fixture providing a sample decision step."""
    return DecisionStep(
        step_id="test-step-id",
        step_number=1,
        reasoning="Test reasoning",
        decision="Test decision",
        next_actions=["Action 1", "Action 2"],
        metadata={"key": "value"},
    )


@pytest.fixture
def sample_decision_chain():
    """Fixture providing a sample decision chain."""
    step1 = DecisionStep(
        step_id="step-1",
        step_number=1,
        reasoning="Initial reasoning",
        decision="Initial decision",
        next_actions=["Next step"],
    )

    step2 = DecisionStep(
        step_id="step-2",
        step_number=2,
        reasoning="Secondary reasoning",
        decision="Final decision",
        next_actions=[],
    )

    return DecisionChain(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context for decision chain",
        steps=[step1, step2],
        final_decision="The final decision",
        status="completed",
    )


@pytest.fixture
def agent_with_mock_llm(mock_llm, repository):
    """Fixture providing a LangChainAgent with a mock LLM."""
    # Create a minimal agent with mocked components
    agent = LangChainAgentService(repository=repository, llm=mock_llm, verbose=False)

    # Create a simple mock executor that directly uses the mock LLM
    class MockSimpleLLMExecutor:
        def __init__(self, llm):
            self.llm = llm

        def invoke(self, input_data):
            # Get the response from the mock LLM
            response = self.llm.invoke(input_data.get("input", ""))

            # Handle case where response is an AIMessage or other message type
            if hasattr(response, "content"):
                response = response.content

            # Return the output in the expected format
            return {"output": response}

    # Replace the agent's executor with our mock
    agent.agent = MockSimpleLLMExecutor(mock_llm)

    return agent
