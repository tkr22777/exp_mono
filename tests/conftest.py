"""
Test configuration and fixtures for pytest.
"""
import pytest
from langchain_core.language_models import BaseLanguageModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.langchain_agent.agent import DecisionChain, DecisionStep, LangChainAgent
from src.langchain_agent.persistence.database import DecisionRepository
from src.langchain_agent.persistence.models import Base


class MockLLM(BaseLanguageModel):
    """Mock LLM for testing purposes."""
    
    # Add a model config to allow extra fields
    model_config = {"extra": "allow"}
    
    def __init__(self, responses=None):
        """Initialize with predefined responses."""
        super().__init__()
        self._responses = responses or ["This is a mock response"]
        self._invocations = []
    
    def invoke(self, input_data, **kwargs):
        """Mock invoke method that returns predefined responses."""
        self._invocations.append(input_data)
        return self._responses.pop(0) if self._responses else "Default mock response"
    
    def generate(self, prompts, **kwargs):
        """Mock generate method for compatibility."""
        return [self.invoke(prompt) for prompt in prompts]
    
    # Add required abstract methods
    def predict(self, text, **kwargs):
        """Required abstract method."""
        return self.invoke(text, **kwargs)
    
    def predict_messages(self, messages, **kwargs):
        """Required abstract method."""
        return self.invoke(messages, **kwargs)
    
    def generate_prompt(self, prompts, **kwargs):
        """Required abstract method."""
        return self.generate(prompts, **kwargs)
    
    async def apredict(self, text, **kwargs):
        """Required abstract method."""
        return self.predict(text, **kwargs)
    
    async def apredict_messages(self, messages, **kwargs):
        """Required abstract method."""
        return self.predict_messages(messages, **kwargs)
    
    async def agenerate_prompt(self, prompts, **kwargs):
        """Required abstract method."""
        return self.generate_prompt(prompts, **kwargs)
    
    async def ainvoke(self, input, **kwargs):
        """Required abstract method."""
        return self.invoke(input, **kwargs)
    
    async def agenerate(self, prompts, **kwargs):
        """Required abstract method."""
        return self.generate(prompts, **kwargs)
    
    @property
    def metadata(self):
        """Required property."""
        return {"name": "MockLLM"}


@pytest.fixture
def mock_llm():
    """Fixture providing a mock LLM."""
    return MockLLM([
        "Initial analysis of the text.",
        "Refinement of the analysis with alternatives.",
        "Final decision based on analysis."
    ])


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
def repository(db_session):
    """Fixture providing a repository with in-memory database session."""
    return DecisionRepository(db_session)


@pytest.fixture
def sample_decision_step():
    """Fixture providing a sample decision step."""
    return DecisionStep(
        step_id="test-step-id",
        step_number=1,
        reasoning="Test reasoning",
        decision="Test decision",
        next_actions=["Action 1", "Action 2"],
        metadata={"key": "value"}
    )


@pytest.fixture
def sample_decision_chain():
    """Fixture providing a sample decision chain."""
    step1 = DecisionStep(
        step_id="step-1",
        step_number=1,
        reasoning="Initial reasoning",
        decision="Initial decision",
        next_actions=["Next step"]
    )
    
    step2 = DecisionStep(
        step_id="step-2",
        step_number=2,
        reasoning="Secondary reasoning",
        decision="Final decision",
        next_actions=[]
    )
    
    return DecisionChain(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context for decision chain",
        steps=[step1, step2],
        final_decision="The final decision",
        status="completed"
    )


@pytest.fixture
def agent_with_mock_llm(mock_llm):
    """Fixture providing a LangChainAgent with a mock LLM."""
    # Create a minimal agent with mocked components
    agent = LangChainAgent(llm=mock_llm, verbose=False)
    
    # Create a mock agent_executor as a simple dictionary with an invoke method
    mock_agent_executor = {
        "invoke": lambda input_data: {"output": mock_llm.invoke(input_data["input"])}
    }
    
    # Replace the agent's executor with our mock
    agent.agent = mock_agent_executor
    
    return agent 
