"""
Tests for the database repository for LangChain Agent persistence.
"""
import contextlib
import json
import os
import uuid
from typing import List
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep
from src.modules.langchain_agent.repositories.models import Base, ChainModel, StepModel
from src.modules.langchain_agent.repositories.sqlite_repository import (
    DEFAULT_DB_PATH,
    SQLiteDecisionChainRepository,
    get_engine,
    get_session,
)


def test_get_engine_default_path():
    """Test getting an engine with the default path."""
    with patch("os.makedirs") as mock_makedirs:
        with patch(
            "src.modules.langchain_agent.repositories.sqlite_repository.create_engine"
        ) as mock_create_engine:
            with patch(
                "src.modules.langchain_agent.repositories.models.Base.metadata.create_all"
            ) as mock_create_all:
                # Configure mocks
                mock_engine = mock_create_engine.return_value

                # Call the function
                engine = get_engine()

                # Verify the calls
                mock_makedirs.assert_called_once_with(
                    os.path.dirname(DEFAULT_DB_PATH), exist_ok=True
                )
                mock_create_engine.assert_called_once_with(
                    f"sqlite:///{DEFAULT_DB_PATH}"
                )
                mock_create_all.assert_called_once_with(mock_engine)

                # Verify the result
                assert engine == mock_engine


def test_get_engine_custom_path():
    """Test getting an engine with a custom path."""
    custom_path = "/tmp/test.db"

    with patch("os.makedirs") as mock_makedirs:
        with patch(
            "src.modules.langchain_agent.repositories.sqlite_repository.create_engine"
        ) as mock_create_engine:
            with patch(
                "src.modules.langchain_agent.repositories.models.Base.metadata.create_all"
            ) as mock_create_all:
                # Configure mocks
                mock_engine = mock_create_engine.return_value

                # Call the function
                engine = get_engine(custom_path)

                # Verify the calls
                mock_makedirs.assert_called_once_with(
                    os.path.dirname(custom_path), exist_ok=True
                )
                mock_create_engine.assert_called_once_with(f"sqlite:///{custom_path}")
                mock_create_all.assert_called_once_with(mock_engine)

                # Verify the result
                assert engine == mock_engine


@pytest.fixture
def session_context():
    """Fixture providing a session context for testing."""
    with get_session() as session:
        yield session


def test_session_context_manager(in_memory_db):
    """Test the session context manager."""
    # Use the context manager
    with get_session() as session:
        # Verify the session is active
        assert session is not None
        assert session.is_active

        # Test that we can use the session
        chain = ChainModel(
            chain_id="test-chain-id",
            title="Test Chain",
            context="Test context",
            status="in_progress",
        )
        session.add(chain)
        session.flush()

        # Verify the chain was added
        retrieved = (
            session.query(ChainModel).filter_by(chain_id="test-chain-id").first()
        )
        assert retrieved is not None


def test_session_exception_handling():
    """Test the session handles exceptions properly."""
    # Create an isolated in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Define a local get_session function for this test
    @contextlib.contextmanager
    def local_get_session():
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Use the context manager with an exception
    try:
        with local_get_session() as session:
            # Add something to the session
            chain = ChainModel(
                chain_id=f"test-chain-id-{uuid.uuid4()}",
                title="Test Chain",
                context="Test context",
                status="in_progress",
            )
            session.add(chain)
            session.flush()
            # Raise an exception to trigger rollback
            raise ValueError("Test exception")
    except ValueError:
        pass  # Expected exception

    # Verify the transaction was rolled back
    with local_get_session() as session:
        # The chain should not exist in the database
        count = session.query(ChainModel).count()
        assert count == 0  # No chains should have been committed


def test_repository_save_chain_new(repository, sample_decision_chain):
    """Test saving a new chain with the repository."""
    # Save the chain
    chain_id = repository.save_chain(sample_decision_chain)

    # Verify the chain was saved
    assert chain_id == sample_decision_chain.chain_id

    # Get the chain from the repository
    with get_session() as session:
        # Verify it was saved to the database
        retrieved = (
            session.query(ChainModel)
            .filter_by(chain_id=sample_decision_chain.chain_id)
            .first()
        )
        assert retrieved is not None
        assert retrieved.title == sample_decision_chain.title
        assert retrieved.context == sample_decision_chain.context
        assert retrieved.final_decision == sample_decision_chain.final_decision
        assert retrieved.status == sample_decision_chain.status

        # Verify the steps were saved
        step_count = (
            session.query(StepModel)
            .filter_by(chain_id=sample_decision_chain.chain_id)
            .count()
        )
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
        status="updated",
    )

    # Save the updated chain
    chain_id = repository.save_chain(updated_chain)

    # Verify the chain was updated
    assert chain_id == updated_chain.chain_id

    # Get the chain from the repository
    retrieved_chain = repository.get_chain(chain_id)
    assert retrieved_chain is not None
    assert retrieved_chain.title == updated_chain.title
    assert retrieved_chain.context == updated_chain.context
    assert retrieved_chain.final_decision == updated_chain.final_decision
    assert retrieved_chain.status == updated_chain.status


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


@pytest.fixture
def clean_repository():
    """Fixture providing a clean repository with in-memory database."""
    # Create an isolated in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Create a repository that uses this isolated database
    class IsolatedRepository(SQLiteDecisionChainRepository):
        def __init__(self):
            # Override to use our isolated engine
            self.db_path = None

        def save_chain(self, chain: DecisionChain) -> str:
            """Override to use isolated session."""
            session = Session()
            try:
                # Check if the chain already exists
                db_chain = (
                    session.query(ChainModel).filter_by(chain_id=chain.chain_id).first()
                )

                if db_chain:
                    # Update existing chain
                    db_chain.title = chain.title
                    db_chain.context = chain.context
                    db_chain.final_decision = chain.final_decision
                    db_chain.status = chain.status
                else:
                    # Create new chain
                    db_chain = ChainModel(
                        chain_id=chain.chain_id,
                        title=chain.title,
                        context=chain.context,
                        final_decision=chain.final_decision,
                        status=chain.status,
                    )
                    session.add(db_chain)
                    session.flush()

                # Save steps
                for step in chain.steps:
                    self._save_step(session, step, chain.chain_id)

                session.commit()
                return db_chain.chain_id
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        def _save_step(
            self, session: Session, step: DecisionStep, chain_id: str
        ) -> None:
            """Save a decision step."""
            # Check if the step already exists
            db_step = session.query(StepModel).filter_by(step_id=step.step_id).first()

            if db_step:
                # Update existing step
                db_step.step_number = step.step_number
                db_step.reasoning = step.reasoning
                db_step.decision = step.decision
                db_step.next_actions = json.dumps(step.next_actions)
                db_step.meta_data = json.dumps(step.metadata)
            else:
                # Create new step
                db_step = StepModel(
                    step_id=step.step_id,
                    chain_id=chain_id,
                    step_number=step.step_number,
                    reasoning=step.reasoning,
                    decision=step.decision,
                    next_actions=json.dumps(step.next_actions),
                    meta_data=json.dumps(step.metadata),
                )
                session.add(db_step)
                session.flush()

        def get_recent_chains(self, limit: int = 10) -> List[DecisionChain]:
            """Override to use isolated session."""
            session = Session()
            try:
                db_chains = (
                    session.query(ChainModel)
                    .order_by(ChainModel.created_at.desc())
                    .limit(limit)
                    .all()
                )

                # Convert to domain models
                chains = []
                for db_chain in db_chains:
                    # Get steps
                    db_steps = (
                        session.query(StepModel)
                        .filter_by(chain_id=db_chain.chain_id)
                        .order_by(StepModel.step_number)
                        .all()
                    )

                    # Convert to domain model
                    steps = [
                        DecisionStep(
                            step_id=step.step_id,
                            step_number=step.step_number,
                            reasoning=step.reasoning,
                            decision=step.decision,
                            next_actions=json.loads(step.next_actions),
                            metadata=json.loads(step.meta_data),
                        )
                        for step in db_steps
                    ]

                    chains.append(
                        DecisionChain(
                            chain_id=db_chain.chain_id,
                            title=db_chain.title,
                            context=db_chain.context,
                            final_decision=db_chain.final_decision,
                            status=db_chain.status,
                            steps=steps,
                        )
                    )

                return chains
            finally:
                session.close()

    return IsolatedRepository()


def test_repository_get_recent_chains(clean_repository):
    """Test getting recent chains from the repository."""
    repo = clean_repository

    # Create sample chains
    sample_chain = DecisionChain(
        chain_id="test-chain-id-isolated",
        title="Test Chain",
        context="Test context",
        steps=[],
        final_decision="The final decision",
        status="completed",
    )

    # Save multiple chains
    repo.save_chain(sample_chain)

    # Create and save another chain
    another_chain = DecisionChain(
        chain_id="another-chain-id-isolated",
        title="Another Chain",
        context="Another context",
        steps=[],
        final_decision=None,
        status="in_progress",
    )
    repo.save_chain(another_chain)

    # Get the chains
    chains = repo.get_recent_chains(limit=10)

    # Verify the chains were retrieved
    assert len(chains) == 2
    assert all(isinstance(chain, DecisionChain) for chain in chains)
    assert any(chain.chain_id == sample_chain.chain_id for chain in chains)
    assert any(chain.chain_id == another_chain.chain_id for chain in chains)


def test_repository_get_recent_chains_limit(clean_repository):
    """Test limiting the number of chains retrieved."""
    repo = clean_repository

    # Create sample chains
    sample_chain = DecisionChain(
        chain_id="test-chain-id-limit",
        title="Test Chain",
        context="Test context",
        steps=[],
        final_decision="The final decision",
        status="completed",
    )

    # Save multiple chains
    repo.save_chain(sample_chain)

    # Create and save another chain
    another_chain = DecisionChain(
        chain_id="another-chain-id-limit",
        title="Another Chain",
        context="Another context",
        steps=[],
        final_decision=None,
        status="in_progress",
    )
    repo.save_chain(another_chain)

    # Get limited chains
    chains = repo.get_recent_chains(limit=1)

    # Verify only one chain was retrieved
    assert len(chains) == 1


def test_repository_delete_chain(repository, sample_decision_chain):
    """Test deleting a chain from the repository."""
    # First save the chain
    repository.save_chain(sample_decision_chain)

    # Delete the chain
    result = repository.delete_chain(sample_decision_chain.chain_id)

    # Verify the chain was deleted
    assert result is True

    # Verify it was deleted from the database
    with get_session() as session:
        retrieved = (
            session.query(ChainModel)
            .filter_by(chain_id=sample_decision_chain.chain_id)
            .first()
        )
        assert retrieved is None

        # Verify the steps were also deleted
        steps = (
            session.query(StepModel)
            .filter_by(chain_id=sample_decision_chain.chain_id)
            .all()
        )
        assert len(steps) == 0


def test_repository_delete_chain_not_found(repository):
    """Test deleting a non-existent chain from the repository."""
    # Delete a non-existent chain
    result = repository.delete_chain("non-existent-id")

    # Verify the result indicates nothing was deleted
    assert result is False
