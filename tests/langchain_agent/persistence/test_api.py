"""
Tests for the persistence API for LangChain Agent.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.langchain_agent.agent import DecisionChain
from src.langchain_agent.persistence.api import (
    PersistentLangChainAgent,
    create_persistent_agent,
    delete_decision_chain,
    get_decision_chain,
    get_recent_chains,
    save_decision_chain,
)


@patch("src.langchain_agent.persistence.api.DatabaseSession")
def test_save_decision_chain(mock_db_session, sample_decision_chain):
    """Test saving a decision chain using the API."""
    # Set up mocks
    mock_session = MagicMock()
    mock_repository = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_session
    mock_repository.save_chain.return_value.chain_id = sample_decision_chain.chain_id

    with patch(
        "src.langchain_agent.persistence.api.DecisionRepository",
        return_value=mock_repository,
    ):
        # Call the function
        result = save_decision_chain(sample_decision_chain, db_path="/test/path.db")

        # Verify the calls
        mock_db_session.assert_called_once_with(db_path="/test/path.db")
        mock_repository.save_chain.assert_called_once_with(sample_decision_chain)

        # Verify the result
        assert result == sample_decision_chain.chain_id


@patch("src.langchain_agent.persistence.api.DatabaseSession")
def test_get_decision_chain(mock_db_session, sample_decision_chain):
    """Test getting a decision chain using the API."""
    # Set up mocks
    mock_session = MagicMock()
    mock_repository = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_session
    mock_repository.get_chain.return_value = sample_decision_chain

    with patch(
        "src.langchain_agent.persistence.api.DecisionRepository",
        return_value=mock_repository,
    ):
        # Call the function
        result = get_decision_chain(
            sample_decision_chain.chain_id, db_path="/test/path.db"
        )

        # Verify the calls
        mock_db_session.assert_called_once_with(db_path="/test/path.db")
        mock_repository.get_chain.assert_called_once_with(
            sample_decision_chain.chain_id
        )

        # Verify the result
        assert result == sample_decision_chain


@patch("src.langchain_agent.persistence.api.DatabaseSession")
def test_get_recent_chains(mock_db_session, sample_decision_chain):
    """Test getting recent decision chains using the API."""
    # Set up mocks
    mock_session = MagicMock()
    mock_repository = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_session
    mock_repository.get_chains.return_value = [sample_decision_chain]

    with patch(
        "src.langchain_agent.persistence.api.DecisionRepository",
        return_value=mock_repository,
    ):
        # Call the function
        result = get_recent_chains(limit=5, db_path="/test/path.db")

        # Verify the calls
        mock_db_session.assert_called_once_with(db_path="/test/path.db")
        mock_repository.get_chains.assert_called_once_with(limit=5)

        # Verify the result
        assert result == [sample_decision_chain]


@patch("src.langchain_agent.persistence.api.DatabaseSession")
def test_delete_decision_chain(mock_db_session):
    """Test deleting a decision chain using the API."""
    # Set up mocks
    mock_session = MagicMock()
    mock_repository = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_session
    mock_repository.delete_chain.return_value = True

    with patch(
        "src.langchain_agent.persistence.api.DecisionRepository",
        return_value=mock_repository,
    ):
        # Call the function
        result = delete_decision_chain("test-chain-id", db_path="/test/path.db")

        # Verify the calls
        mock_db_session.assert_called_once_with(db_path="/test/path.db")
        mock_repository.delete_chain.assert_called_once_with("test-chain-id")

        # Verify the result
        assert result is True


@patch("src.langchain_agent.persistence.api.LangChainAgent.__init__")
def test_persistent_langchain_agent_init(mock_init):
    """Test initializing a PersistentLangChainAgent."""
    # Set up mock
    mock_init.return_value = None

    # Create the agent
    agent = PersistentLangChainAgent(verbose=True, db_path="/test/path.db")

    # Verify the calls
    mock_init.assert_called_once_with(verbose=True)

    # Verify the attributes
    assert agent.db_path == "/test/path.db"


def test_persistent_agent_save_active_chain(sample_decision_chain):
    """Test saving the active chain of a PersistentLangChainAgent."""
    # Create an agent with a mock
    agent = PersistentLangChainAgent()
    agent.active_chain = sample_decision_chain

    with patch("src.langchain_agent.persistence.api.save_decision_chain") as mock_save:
        # Configure mock
        mock_save.return_value = sample_decision_chain.chain_id

        # Call the method
        result = agent.save_active_chain()

        # Verify the calls
        mock_save.assert_called_once_with(sample_decision_chain, None)

        # Verify the result
        assert result == sample_decision_chain.chain_id


def test_persistent_agent_save_active_chain_no_active_chain():
    """Test saving when there's no active chain."""
    # Create an agent with no active chain
    agent = PersistentLangChainAgent()
    agent.active_chain = None

    # Call the method
    result = agent.save_active_chain()

    # Verify the result
    assert result is None


def test_persistent_agent_load_chain(sample_decision_chain):
    """Test loading a chain into a PersistentLangChainAgent."""
    # Create an agent
    agent = PersistentLangChainAgent()

    with patch("src.langchain_agent.persistence.api.get_decision_chain") as mock_get:
        # Configure mock
        mock_get.return_value = sample_decision_chain

        # Call the method
        result = agent.load_chain(sample_decision_chain.chain_id)

        # Verify the calls
        mock_get.assert_called_once_with(sample_decision_chain.chain_id, None)

        # Verify the result
        assert result == sample_decision_chain
        assert agent.active_chain == sample_decision_chain


def test_persistent_agent_load_chain_not_found():
    """Test loading a non-existent chain."""
    # Create an agent
    agent = PersistentLangChainAgent()

    with patch("src.langchain_agent.persistence.api.get_decision_chain") as mock_get:
        # Configure mock
        mock_get.return_value = None

        # Call the method
        result = agent.load_chain("non-existent-id")

        # Verify the calls
        mock_get.assert_called_once_with("non-existent-id", None)

        # Verify the result
        assert result is None
        assert agent.active_chain is None


def test_persistent_agent_process_text_with_persistence(sample_decision_chain):
    """Test processing text with persistence."""
    # Create an agent with mocks
    agent = PersistentLangChainAgent()

    with patch.object(agent, "process_text") as mock_process:
        with patch(
            "src.langchain_agent.persistence.api.save_decision_chain"
        ) as mock_save:
            # Configure mocks
            mock_process.return_value = sample_decision_chain
            mock_save.return_value = sample_decision_chain.chain_id

            # Call the method
            chain, chain_id = agent.process_text_with_persistence("Test input")

            # Verify the calls
            mock_process.assert_called_once_with("Test input")
            mock_save.assert_called_once_with(sample_decision_chain, None)

            # Verify the result
            assert chain == sample_decision_chain
            assert chain_id == sample_decision_chain.chain_id


@patch("src.langchain_agent.persistence.api.PersistentLangChainAgent")
def test_create_persistent_agent(mock_agent_class):
    """Test the create_persistent_agent factory function."""
    # Call the function
    agent = create_persistent_agent(db_path="/test/path.db", verbose=True)

    # Verify the calls
    mock_agent_class.assert_called_once_with(db_path="/test/path.db", verbose=True)

    # Verify the result
    assert agent == mock_agent_class.return_value
