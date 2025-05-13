"""
Tests for the LangChain Agent implementation.
"""
import pytest

from src.langchain_agent.agent import (
    DecisionChain,
    DecisionStep,
    LangChainAgent,
    create_agent,
)


def test_decision_step_creation():
    """Test creating a decision step."""
    step = DecisionStep(
        step_number=1,
        reasoning="Test reasoning",
        decision="Test decision",
        next_actions=["Action 1", "Action 2"],
        metadata={"key": "value"},
    )

    assert step.step_id is not None
    assert step.step_number == 1
    assert step.reasoning == "Test reasoning"
    assert step.decision == "Test decision"
    assert len(step.next_actions) == 2
    assert step.metadata["key"] == "value"


def test_decision_chain_creation():
    """Test creating a decision chain."""
    chain = DecisionChain(
        title="Test Chain",
        context="Test context",
        steps=[],
        final_decision=None,
        status="in_progress",
    )

    assert chain.chain_id is not None
    assert chain.title == "Test Chain"
    assert chain.context == "Test context"
    assert len(chain.steps) == 0
    assert chain.final_decision is None
    assert chain.status == "in_progress"


def test_agent_initialization(mock_llm):
    """Test initializing the LangChain agent."""
    agent = LangChainAgent(llm=mock_llm, verbose=False)

    assert agent.llm == mock_llm
    assert agent.verbose is False
    assert agent.message_history is not None
    assert agent.agent is not None
    assert agent.active_chain is None


def test_create_decision_chain(agent_with_mock_llm, monkeypatch):
    """Test creating a decision chain."""
    # Mock the title generation
    monkeypatch.setattr(
        "src.modules.llms.ai_client.default_client.generate_response",
        lambda _: "Generated Title",
    )

    agent = agent_with_mock_llm
    chain = agent.create_decision_chain("Test context")

    assert chain.title == "Generated Title"
    assert chain.context == "Test context"
    assert len(chain.steps) == 0
    assert chain.status == "in_progress"
    assert agent.active_chain == chain


def test_add_decision_step(agent_with_mock_llm):
    """Test adding a step to the decision chain."""
    agent = agent_with_mock_llm
    chain = agent.create_decision_chain("Test context", title="Test Chain")

    step = agent.add_decision_step(
        reasoning="Test reasoning", decision="Test decision", next_actions=["Action 1"]
    )

    assert step.step_number == 1
    assert step.reasoning == "Test reasoning"
    assert step.decision == "Test decision"
    assert len(step.next_actions) == 1
    assert step in agent.active_chain.steps


def test_add_decision_step_no_active_chain(agent_with_mock_llm):
    """Test adding a step without an active chain raises an error."""
    agent = agent_with_mock_llm

    with pytest.raises(ValueError, match="No active decision chain"):
        agent.add_decision_step(
            reasoning="Test reasoning",
            decision="Test decision",
            next_actions=["Action 1"],
        )


def test_complete_decision_chain(agent_with_mock_llm):
    """Test completing the decision chain."""
    agent = agent_with_mock_llm
    agent.create_decision_chain("Test context", title="Test Chain")

    completed_chain = agent.complete_decision_chain("Final decision")

    assert completed_chain.final_decision == "Final decision"
    assert completed_chain.status == "completed"
    assert agent.active_chain is None


def test_complete_decision_chain_no_active_chain(agent_with_mock_llm):
    """Test completing without an active chain raises an error."""
    agent = agent_with_mock_llm

    with pytest.raises(ValueError, match="No active decision chain"):
        agent.complete_decision_chain("Final decision")


def test_process_text(agent_with_mock_llm, monkeypatch):
    """Test processing text through the decision chain."""
    # Mock the title generation
    monkeypatch.setattr(
        "src.modules.llms.ai_client.default_client.generate_response",
        lambda _: "Generated Title",
    )

    agent = agent_with_mock_llm
    chain = agent.process_text("Test input text")

    assert chain.title == "Generated Title"
    assert chain.context == "Test input text"
    assert len(chain.steps) == 2
    assert chain.final_decision is not None
    assert chain.status == "completed"


def test_create_agent():
    """Test the create_agent factory function."""
    agent = create_agent()

    assert isinstance(agent, LangChainAgent)
    assert agent.verbose is True
