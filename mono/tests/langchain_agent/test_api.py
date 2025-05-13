"""
Tests for the LangChain Agent API.
"""
from unittest.mock import patch

import pytest

from src.langchain_agent.api import (
    LangChainDecisionResult,
    _convert_to_result,
    process_with_langchain,
)


def test_langchain_decision_result():
    """Test creating a LangChainDecisionResult model."""
    result = LangChainDecisionResult(
        title="Test Title",
        final_decision="Test Decision",
        step_count=2,
        context="Test Context",
        chain_id="test-chain-id",
    )

    assert result.title == "Test Title"
    assert result.final_decision == "Test Decision"
    assert result.step_count == 2
    assert result.context == "Test Context"
    assert result.chain_id == "test-chain-id"


def test_convert_to_result(sample_decision_chain):
    """Test converting a DecisionChain to a LangChainDecisionResult."""
    result = _convert_to_result(sample_decision_chain)

    assert result.title == sample_decision_chain.title
    assert result.final_decision == sample_decision_chain.final_decision
    assert result.step_count == len(sample_decision_chain.steps)
    assert result.context == sample_decision_chain.context
    assert result.chain_id == sample_decision_chain.chain_id


def test_convert_to_result_no_final_decision(sample_decision_chain):
    """Test converting a DecisionChain with no final decision."""
    # Create a chain with no final decision
    sample_decision_chain.final_decision = None

    result = _convert_to_result(sample_decision_chain)

    assert result.final_decision == "No final decision reached"


@patch("src.langchain_agent.api.create_agent")
def test_process_with_langchain(
    mock_create_agent, agent_with_mock_llm, sample_decision_chain, monkeypatch
):
    """Test processing text with the LangChain agent through the API."""
    # Set up the mock agent to return our sample chain
    mock_agent = agent_with_mock_llm
    monkeypatch.setattr(mock_agent, "process_text", lambda _: sample_decision_chain)
    mock_create_agent.return_value = mock_agent

    # Call the API function
    chain, result = process_with_langchain("Test input")

    # Verify the mock was called
    mock_create_agent.assert_called_once()

    # Verify the results
    assert chain == sample_decision_chain
    assert result.title == sample_decision_chain.title
    assert result.final_decision == sample_decision_chain.final_decision
    assert result.step_count == len(sample_decision_chain.steps)
    assert result.context == sample_decision_chain.context
    assert result.chain_id == sample_decision_chain.chain_id
