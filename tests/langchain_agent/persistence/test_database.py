"""
Tests for the database repository for LangChain Agent persistence.
"""
import os
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.langchain_agent.agent import DecisionChain, DecisionStep
from src.langchain_agent.persistence.database import (
    DEFAULT_DB_PATH,
    DatabaseSession,
    DecisionRepository,
    get_engine,
)
from src.langchain_agent.persistence.models import Base, ChainModel, StepModel


def test_get_engine_default_path():
    """Test getting an engine with the default path."""
    with patch("os.makedirs") as mock_makedirs:
        with patch("src.langchain_agent.persistence.database.create_engine") as mock_create_engine:
            with patch("src.langchain_agent.persistence.models.Base.metadata.create_all") as mock_create_all:
                # Configure mocks
                mock_engine = mock_create_engine.return_value
                
                # Call the function
                engine = get_engine()
                
                # Verify the calls
                mock_makedirs.assert_called_once_with(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)
                mock_create_engine.assert_called_once_with(f"sqlite:///{DEFAULT_DB_PATH}")
                mock_create_all.assert_called_once_with(mock_engine)
                
                # Verify the result
                assert engine == mock_engine


def test_get_engine_custom_path():
    """Test getting an engine with a custom path."""
    custom_path = "/tmp/test.db"
    
    with patch("os.makedirs") as mock_makedirs:
        with patch("src.langchain_agent.persistence.database.create_engine") as mock_create_engine:
            with patch("src.langchain_agent.persistence.models.Base.metadata.create_all") as mock_create_all:
                # Configure mocks
                mock_engine = mock_create_engine.return_value
                
                # Call the function
                engine = get_engine(custom_path)
                
                # Verify the calls
                mock_makedirs.assert_called_once_with(os.path.dirname(custom_path), exist_ok=True)
                mock_create_engine.assert_called_once_with(f"sqlite:///{custom_path}")
                mock_create_all.assert_called_once_with(mock_engine)
                
                # Verify the result
                assert engine == mock_engine


def test_database_session_context_manager(in_memory_db):
    """Test the DatabaseSession context manager."""
    # Create a DatabaseSession with the in-memory engine
    session_manager = DatabaseSession(engine=in_memory_db)
    
    # Use the context manager
    with session_manager as session:
        # Verify the session is active
        assert session is not None
        assert session.is_active
        
        # Test that we can use the session
        chain = ChainModel(
            chain_id="test-chain-id",
            title="Test Chain",
            context="Test context",
            status="in_progress"
        )
        session.add(chain)
        session.flush()
        
        # Verify the chain was added
        retrieved = session.query(ChainModel).filter_by(chain_id="test-chain-id").first()
        assert retrieved is not None
    
    # Verify the session is closed after the context
    assert session_manager.session is None


def test_database_session_exception_handling(in_memory_db):
    """Test the DatabaseSession handles exceptions properly."""
    # Create a DatabaseSession with the in-memory engine
    session_manager = DatabaseSession(engine=in_memory_db)
    
    # Use the context manager with an exception
    try:
        with session_manager as session:
            # Add something to the session
            chain = ChainModel(
                chain_id="test-chain-id",
                title="Test Chain",
                context="Test context",
                status="in_progress"
            )
            session.add(chain)
            session.flush()
            
            # Raise an exception
            raise ValueError("Test exception")
    except ValueError:
        pass
    
    # Verify the session is closed and rolled back
    assert session_manager.session is None
    
    # Verify nothing was committed
    # Create a new session to check
    Session = session_manager.session_factory
    with Session() as new_session:
        retrieved = new_session.query(ChainModel).filter_by(chain_id="test-chain-id").first()
        assert retrieved is None


def test_repository_save_chain_new(repository, sample_decision_chain):
    """Test saving a new chain with the repository."""
    # Save the chain
    db_chain = repository.save_chain(sample_decision_chain)
    
    # Verify the chain was saved
    assert db_chain.chain_id == sample_decision_chain.chain_id
    assert db_chain.title == sample_decision_chain.title
    assert db_chain.context == sample_decision_chain.context
    assert db_chain.final_decision == sample_decision_chain.final_decision
    assert db_chain.status == sample_decision_chain.status
    
    # Verify it was saved to the database
    retrieved = repository.session.query(ChainModel).filter_by(chain_id=sample_decision_chain.chain_id).first()
    assert retrieved is not None
    assert retrieved == db_chain
    
    # Verify the steps were saved
    step_count = repository.session.query(StepModel).filter_by(chain_id=sample_decision_chain.chain_id).count()
    assert step_count == len(sample_decision_chain.steps)


def test_repository_save_chain_update(repository, sample_decision_chain):
    """Test updating an existing chain with the repository."""
    # First save the chain
    repository.save_chain(sample_decision_chain)
    
    # Update the chain
    updated_chain = DecisionChain(
        chain_id=sample_decision_chain.chain_id,  # Same ID
        title="Updated Title",
        context="Updated context",
        steps=sample_decision_chain.steps,  # Same steps
        final_decision="Updated decision",
        status="updated"
    )
    
    # Save the updated chain
    db_chain = repository.save_chain(updated_chain)
    
    # Verify the chain was updated
    assert db_chain.chain_id == updated_chain.chain_id
    assert db_chain.title == updated_chain.title
    assert db_chain.context == updated_chain.context
    assert db_chain.final_decision == updated_chain.final_decision
    assert db_chain.status == updated_chain.status
    
    # Verify it was updated in the database
    retrieved = repository.session.query(ChainModel).filter_by(chain_id=updated_chain.chain_id).first()
    assert retrieved is not None
    assert retrieved.title == "Updated Title"
    assert retrieved.context == "Updated context"
    assert retrieved.final_decision == "Updated decision"
    assert retrieved.status == "updated"


def test_repository_save_step_new(repository, sample_decision_step):
    """Test saving a new step with the repository."""
    # First create a chain to link to
    chain = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        status="in_progress"
    )
    repository.session.add(chain)
    repository.session.flush()
    
    # Save the step
    db_step = repository.save_step(sample_decision_step, "test-chain-id")
    
    # Verify the step was saved
    assert db_step.step_id == sample_decision_step.step_id
    assert db_step.chain_id == "test-chain-id"
    assert db_step.step_number == sample_decision_step.step_number
    assert db_step.reasoning == sample_decision_step.reasoning
    assert db_step.decision == sample_decision_step.decision
    
    # Verify it was saved to the database
    retrieved = repository.session.query(StepModel).filter_by(step_id=sample_decision_step.step_id).first()
    assert retrieved is not None
    assert retrieved == db_step


def test_repository_save_step_update(repository, sample_decision_step):
    """Test updating an existing step with the repository."""
    # First create a chain to link to
    chain = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        status="in_progress"
    )
    repository.session.add(chain)
    repository.session.flush()
    
    # Save the step initially
    repository.save_step(sample_decision_step, "test-chain-id")
    
    # Update the step
    updated_step = DecisionStep(
        step_id=sample_decision_step.step_id,  # Same ID
        step_number=sample_decision_step.step_number,
        reasoning="Updated reasoning",
        decision="Updated decision",
        next_actions=["Updated action"],
        metadata={"updated": "value"}
    )
    
    # Save the updated step
    db_step = repository.save_step(updated_step, "test-chain-id")
    
    # Verify the step was updated
    assert db_step.reasoning == updated_step.reasoning
    assert db_step.decision == updated_step.decision
    
    # Verify it was updated in the database
    retrieved = repository.session.query(StepModel).filter_by(step_id=updated_step.step_id).first()
    assert retrieved is not None
    assert retrieved.reasoning == "Updated reasoning"
    assert retrieved.decision == "Updated decision"


def test_repository_get_chain(repository, sample_decision_chain):
    """Test getting a chain from the repository."""
    # First save the chain
    repository.save_chain(sample_decision_chain)
    
    # Get the chain
    retrieved_chain = repository.get_chain(sample_decision_chain.chain_id)
    
    # Verify the chain was retrieved
    assert isinstance(retrieved_chain, DecisionChain)
    assert retrieved_chain.chain_id == sample_decision_chain.chain_id
    assert retrieved_chain.title == sample_decision_chain.title
    assert retrieved_chain.context == sample_decision_chain.context
    assert retrieved_chain.final_decision == sample_decision_chain.final_decision
    assert retrieved_chain.status == sample_decision_chain.status
    assert len(retrieved_chain.steps) == len(sample_decision_chain.steps)


def test_repository_get_chain_not_found(repository):
    """Test getting a non-existent chain from the repository."""
    # Get a non-existent chain
    retrieved_chain = repository.get_chain("non-existent-id")
    
    # Verify nothing was retrieved
    assert retrieved_chain is None


def test_repository_get_chains(repository, sample_decision_chain):
    """Test getting multiple chains from the repository."""
    # Save multiple chains
    repository.save_chain(sample_decision_chain)
    
    # Create and save another chain
    another_chain = DecisionChain(
        chain_id="another-chain-id",
        title="Another Chain",
        context="Another context",
        steps=[],
        final_decision=None,
        status="in_progress"
    )
    repository.save_chain(another_chain)
    
    # Get the chains
    chains = repository.get_chains(limit=10)
    
    # Verify the chains were retrieved
    assert len(chains) == 2
    assert all(isinstance(chain, DecisionChain) for chain in chains)
    assert any(chain.chain_id == sample_decision_chain.chain_id for chain in chains)
    assert any(chain.chain_id == another_chain.chain_id for chain in chains)


def test_repository_get_chains_limit(repository, sample_decision_chain):
    """Test limiting the number of chains retrieved."""
    # Save multiple chains
    repository.save_chain(sample_decision_chain)
    
    # Create and save another chain
    another_chain = DecisionChain(
        chain_id="another-chain-id",
        title="Another Chain",
        context="Another context",
        steps=[],
        final_decision=None,
        status="in_progress"
    )
    repository.save_chain(another_chain)
    
    # Get limited chains
    chains = repository.get_chains(limit=1)
    
    # Verify only one chain was retrieved
    assert len(chains) == 1


def test_repository_get_step(repository, sample_decision_step):
    """Test getting a step from the repository."""
    # First create a chain to link to
    chain = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        status="in_progress"
    )
    repository.session.add(chain)
    repository.session.flush()
    
    # Save the step
    repository.save_step(sample_decision_step, "test-chain-id")
    
    # Get the step
    retrieved_step = repository.get_step(sample_decision_step.step_id)
    
    # Verify the step was retrieved
    assert isinstance(retrieved_step, DecisionStep)
    assert retrieved_step.step_id == sample_decision_step.step_id
    assert retrieved_step.step_number == sample_decision_step.step_number
    assert retrieved_step.reasoning == sample_decision_step.reasoning
    assert retrieved_step.decision == sample_decision_step.decision
    assert retrieved_step.next_actions == sample_decision_step.next_actions
    assert retrieved_step.metadata == sample_decision_step.metadata


def test_repository_get_step_not_found(repository):
    """Test getting a non-existent step from the repository."""
    # Get a non-existent step
    retrieved_step = repository.get_step("non-existent-id")
    
    # Verify nothing was retrieved
    assert retrieved_step is None


def test_repository_delete_chain(repository, sample_decision_chain):
    """Test deleting a chain from the repository."""
    # First save the chain
    repository.save_chain(sample_decision_chain)
    
    # Delete the chain
    result = repository.delete_chain(sample_decision_chain.chain_id)
    
    # Verify the chain was deleted
    assert result is True
    
    # Verify it was deleted from the database
    retrieved = repository.session.query(ChainModel).filter_by(chain_id=sample_decision_chain.chain_id).first()
    assert retrieved is None
    
    # Verify the steps were also deleted (cascade)
    steps = repository.session.query(StepModel).filter_by(chain_id=sample_decision_chain.chain_id).all()
    assert len(steps) == 0


def test_repository_delete_chain_not_found(repository):
    """Test deleting a non-existent chain from the repository."""
    # Delete a non-existent chain
    result = repository.delete_chain("non-existent-id")
    
    # Verify the result indicates nothing was deleted
    assert result is False 
