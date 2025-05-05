"""
Database Session and Repository Implementation

This module provides functionality for managing database sessions
and repository patterns for database operations.
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.langchain_agent.agent import DecisionChain, DecisionStep
from src.langchain_agent.persistence.models import Base, ChainModel, StepModel

# Default SQLite database location
DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), ".langchain_agent", "decisions.db"
)
T = TypeVar("T")


def get_engine(db_path: Optional[str] = None) -> Engine:
    """
    Get or create a SQLAlchemy engine.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        SQLAlchemy engine instance
    """
    # Use default path if not provided
    db_path = db_path or DEFAULT_DB_PATH

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create the engine
    engine = create_engine(f"sqlite:///{db_path}")

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    return engine


class DatabaseSession:
    """Context manager for database sessions."""

    def __init__(self, engine: Optional[Engine] = None, db_path: Optional[str] = None):
        """
        Initialize the database session.

        Args:
            engine: SQLAlchemy engine (optional)
            db_path: Path to the SQLite database file (optional)
        """
        self.engine = engine or get_engine(db_path)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        """
        Start a new session when entering the context.

        Returns:
            SQLAlchemy session
        """
        self.session = self.session_factory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the session when exiting the context.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if self.session is not None:
            if exc_type is not None:
                # If an exception occurred, rollback the session
                self.session.rollback()
            else:
                # Otherwise, commit the session
                self.session.commit()

            # Close the session
            self.session.close()
            self.session = None


class DecisionRepository:
    """Repository for managing decision chains and steps in the database."""

    def __init__(self, session: Session):
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def save_chain(self, chain: DecisionChain) -> ChainModel:
        """
        Save a decision chain to the database.

        Args:
            chain: The decision chain to save

        Returns:
            The saved chain model
        """
        # Check if the chain already exists
        db_chain = (
            self.session.query(ChainModel).filter_by(chain_id=chain.chain_id).first()
        )

        if db_chain:
            # Update existing chain
            db_chain.title = chain.title
            db_chain.context = chain.context
            db_chain.final_decision = chain.final_decision
            db_chain.status = chain.status
        else:
            # Create new chain
            db_chain = ChainModel.from_pydantic(chain)
            self.session.add(db_chain)
            self.session.flush()

        # Save steps
        for step in chain.steps:
            self.save_step(step, chain.chain_id)

        return db_chain

    def save_step(self, step: DecisionStep, chain_id: str) -> StepModel:
        """
        Save a decision step to the database.

        Args:
            step: The decision step to save
            chain_id: The ID of the parent chain

        Returns:
            The saved step model
        """
        # Check if the step already exists
        db_step = self.session.query(StepModel).filter_by(step_id=step.step_id).first()

        if db_step:
            # Update existing step
            db_step.reasoning = step.reasoning
            db_step.decision = step.decision
            db_step.next_actions = json.dumps(step.next_actions)
            db_step.meta_data = json.dumps(step.metadata)
        else:
            # Create new step
            db_step = StepModel.from_pydantic(step, chain_id)
            self.session.add(db_step)
            self.session.flush()

        return db_step

    def get_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Get a decision chain by ID.

        Args:
            chain_id: The ID of the chain to get

        Returns:
            The decision chain or None if not found
        """
        db_chain = self.session.query(ChainModel).filter_by(chain_id=chain_id).first()

        if db_chain:
            return db_chain.to_pydantic()

        return None

    def get_chains(self, limit: int = 10, offset: int = 0) -> List[DecisionChain]:
        """
        Get multiple decision chains with pagination.

        Args:
            limit: Maximum number of chains to return
            offset: Offset for pagination

        Returns:
            List of decision chains
        """
        db_chains = (
            self.session.query(ChainModel)
            .order_by(ChainModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [chain.to_pydantic() for chain in db_chains]

    def get_step(self, step_id: str) -> Optional[DecisionStep]:
        """
        Get a decision step by ID.

        Args:
            step_id: The ID of the step to get

        Returns:
            The decision step or None if not found
        """
        db_step = self.session.query(StepModel).filter_by(step_id=step_id).first()

        if db_step:
            return db_step.to_pydantic()

        return None

    def delete_chain(self, chain_id: str) -> bool:
        """
        Delete a decision chain by ID.

        Args:
            chain_id: The ID of the chain to delete

        Returns:
            True if the chain was deleted, False otherwise
        """
        db_chain = self.session.query(ChainModel).filter_by(chain_id=chain_id).first()

        if db_chain:
            self.session.delete(db_chain)
            return True

        return False
