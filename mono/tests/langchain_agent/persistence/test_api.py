"""
Tests for the persistence API for LangChain Agent.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.modules.langchain_agent.api import (
    PersistentLangChainAgent,
    create_persistent_agent,
    get_decision_chain,
    get_recent_chains,
)
from src.modules.langchain_agent.models.domain import DecisionChain


@patch("src.modules.langchain_agent.api.get_decision_chain_repository")
def test_get_decision_chain(mock_get_repository, sample_decision_chain):
    """Test getting a decision chain using the API."""
    # Set up mocks
    mock_repository = MagicMock()
    mock_get_repository.return_value = mock_repository
    mock_repository.get_chain.return_value = sample_decision_chain

    # Call the function
    result = get_decision_chain(sample_decision_chain.chain_id, db_path="/test/path.db")

    # Verify the calls
    mock_get_repository.assert_called_once_with(db_path="/test/path.db")
    mock_repository.get_chain.assert_called_once_with(sample_decision_chain.chain_id)

    # Verify the result
    assert result == sample_decision_chain


@patch("src.modules.langchain_agent.api.get_decision_chain_repository")
def test_get_recent_chains(mock_get_repository, sample_decision_chain):
    """Test getting recent decision chains using the API."""
    # Set up mocks
    mock_repository = MagicMock()
    mock_get_repository.return_value = mock_repository
    mock_repository.get_recent_chains.return_value = [sample_decision_chain]

    # Call the function
    result = get_recent_chains(limit=5, db_path="/test/path.db")

    # Verify the calls
    mock_get_repository.assert_called_once_with(db_path="/test/path.db")
    mock_repository.get_recent_chains.assert_called_once_with(limit=5)

    # Verify the result
    assert result == [sample_decision_chain]


def test_persistent_langchain_agent_init():
    """Test initializing a PersistentLangChainAgent."""
    # Create a mock service
    mock_service = MagicMock()

    # Create the agent
    agent = PersistentLangChainAgent(mock_service)

    # Verify the attributes
    assert agent.service == mock_service


def test_persistent_agent_load_chain(sample_decision_chain):
    """Test loading a chain into a PersistentLangChainAgent."""
    # Create a mock service
    mock_service = MagicMock()
    mock_service.get_chain.return_value = sample_decision_chain

    # Create an agent
    agent = PersistentLangChainAgent(mock_service)

    # Call the method
    result = agent.load_chain(sample_decision_chain.chain_id)

    # Verify the calls
    mock_service.get_chain.assert_called_once_with(sample_decision_chain.chain_id)

    # Verify the result
    assert result == sample_decision_chain


def test_persistent_agent_load_chain_not_found():
    """Test loading a non-existent chain."""
    # Create a mock service
    mock_service = MagicMock()
    mock_service.get_chain.return_value = None

    # Create an agent
    agent = PersistentLangChainAgent(mock_service)

    # Call the method
    result = agent.load_chain("non-existent-id")

    # Verify the calls
    mock_service.get_chain.assert_called_once_with("non-existent-id")

    # Verify the result
    assert result is None


def test_persistent_agent_process_text_with_persistence(sample_decision_chain):
    """Test processing text with persistence."""
    # Create a mock service
    mock_service = MagicMock()
    mock_service.process_text_with_persistence.return_value = (
        sample_decision_chain,
        sample_decision_chain.chain_id,
    )

    # Create an agent
    agent = PersistentLangChainAgent(mock_service)

    # Call the method
    chain, chain_id = agent.process_text_with_persistence("Test input")

    # Verify the calls
    mock_service.process_text_with_persistence.assert_called_once_with("Test input")

    # Verify the result
    assert chain == sample_decision_chain
    assert chain_id == sample_decision_chain.chain_id


@patch("src.modules.langchain_agent.api.get_langchain_agent_service")
def test_create_persistent_agent(mock_get_service):
    """Test creating a persistent agent."""
    # Configure mock
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    # Call the function
    agent = create_persistent_agent(db_path="/test/path.db")

    # Verify the calls
    mock_get_service.assert_called_once_with(db_path="/test/path.db")

    # Verify the result
    assert isinstance(agent, PersistentLangChainAgent)
    assert agent.service == mock_service
