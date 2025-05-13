"""
SQLite Repository Implementation

This module provides a SQLite-based implementation of the repository interfaces.
"""

import json
import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.modules.langchain_agent.repositories.models import Base, ChainModel, StepModel
from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep


# Default SQLite database location
DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), ".langchain_agent", "decisions.db"
)


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


@contextmanager
def get_session(db_path: Optional[str] = None) -> Iterator[Session]:
    """
    Get a database session as a context manager.

    Args:
        db_path: Path to the SQLite database file

    Yields:
        SQLAlchemy session
    """
    engine = get_engine(db_path)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class SQLiteDecisionChainRepository:
    """SQLite implementation of the decision chain repository."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    def save_chain(self, chain: DecisionChain) -> str:
        """
        Save a decision chain.
        
        Args:
            chain: The decision chain to save
            
        Returns:
            The ID of the saved chain
        """
        with get_session(self.db_path) as session:
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

            return db_chain.chain_id
    
    def _save_step(self, session: Session, step: DecisionStep, chain_id: str) -> None:
        """
        Save a decision step.
        
        Args:
            session: SQLAlchemy session
            step: The decision step to save
            chain_id: The ID of the parent chain
        """
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
    
    def get_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Get a decision chain by ID.
        
        Args:
            chain_id: The ID of the chain to get
            
        Returns:
            The decision chain or None if not found
        """
        with get_session(self.db_path) as session:
            db_chain = session.query(ChainModel).filter_by(chain_id=chain_id).first()
            
            if not db_chain:
                return None
            
            # Get steps
            db_steps = (
                session.query(StepModel)
                .filter_by(chain_id=chain_id)
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
            
            return DecisionChain(
                chain_id=db_chain.chain_id,
                title=db_chain.title,
                context=db_chain.context,
                final_decision=db_chain.final_decision,
                status=db_chain.status,
                steps=steps,
            )
    
    def get_recent_chains(self, limit: int = 10) -> List[DecisionChain]:
        """
        Get recent decision chains.
        
        Args:
            limit: Maximum number of chains to return
            
        Returns:
            List of decision chains
        """
        with get_session(self.db_path) as session:
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
    
    def delete_chain(self, chain_id: str) -> bool:
        """
        Delete a decision chain by ID.
        
        Args:
            chain_id: The ID of the chain to delete
            
        Returns:
            True if the chain was deleted, False otherwise
        """
        with get_session(self.db_path) as session:
            # Delete steps first
            session.query(StepModel).filter_by(chain_id=chain_id).delete()
            
            # Delete chain
            result = session.query(ChainModel).filter_by(chain_id=chain_id).delete()
            
            return result > 0 