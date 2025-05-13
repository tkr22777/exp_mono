"""
Database Models for LangChain Agent

This module defines SQLAlchemy models for persisting decision chains and steps.
"""
import datetime
import json
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, declarative_base, relationship

from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep

Base = declarative_base()
T = TypeVar("T")


class ChainModel(Base):
    """SQLAlchemy model for persisting decision chains."""

    __tablename__ = "decision_chains"

    id = Column(Integer, primary_key=True)
    chain_id = Column(String(36), unique=True, index=True)
    title = Column(String(255), nullable=False)
    context = Column(Text, nullable=False)
    final_decision = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationship with steps
    steps = relationship(
        "StepModel", back_populates="chain", cascade="all, delete-orphan"
    )

    def to_pydantic(self) -> DecisionChain:
        """
        Convert the SQLAlchemy model to a Pydantic model.

        Returns:
            DecisionChain: A Pydantic model instance
        """
        return DecisionChain(
            chain_id=self.chain_id,
            title=self.title,
            context=self.context,
            final_decision=self.final_decision,
            status=self.status,
            steps=[step.to_pydantic() for step in self.steps],
        )

    @classmethod
    def from_pydantic(cls, chain: DecisionChain) -> "ChainModel":
        """
        Create a SQLAlchemy model from a Pydantic model.

        Args:
            chain: The Pydantic model to convert

        Returns:
            ChainModel: A SQLAlchemy model instance
        """
        return cls(
            chain_id=chain.chain_id,
            title=chain.title,
            context=chain.context,
            final_decision=chain.final_decision,
            status=chain.status,
            # Steps are added separately to avoid recursive creation
        )


class StepModel(Base):
    """SQLAlchemy model for persisting decision steps."""

    __tablename__ = "decision_steps"

    id = Column(Integer, primary_key=True)
    step_id = Column(String(36), unique=True, index=True)
    chain_id = Column(
        String(36), ForeignKey("decision_chains.chain_id"), nullable=False
    )
    step_number = Column(Integer, nullable=False)
    reasoning = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)
    next_actions = Column(Text, nullable=False)  # Stored as JSON
    meta_data = Column(Text, nullable=False)  # Stored as JSON (renamed from metadata)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship with chain
    chain = relationship("ChainModel", back_populates="steps")

    def to_pydantic(self) -> DecisionStep:
        """
        Convert the SQLAlchemy model to a Pydantic model.

        Returns:
            DecisionStep: A Pydantic model instance
        """
        return DecisionStep(
            step_id=self.step_id,
            step_number=self.step_number,
            reasoning=self.reasoning,
            decision=self.decision,
            next_actions=json.loads(self.next_actions),
            metadata=json.loads(self.meta_data),  # Convert meta_data back to metadata
        )

    @classmethod
    def from_pydantic(cls, step: DecisionStep, chain_id: str) -> "StepModel":
        """
        Create a SQLAlchemy model from a Pydantic model.

        Args:
            step: The Pydantic model to convert
            chain_id: The ID of the parent chain

        Returns:
            StepModel: A SQLAlchemy model instance
        """
        return cls(
            step_id=step.step_id,
            chain_id=chain_id,
            step_number=step.step_number,
            reasoning=step.reasoning,
            decision=step.decision,
            next_actions=json.dumps(step.next_actions),
            meta_data=json.dumps(step.metadata),  # Store metadata as meta_data
        )


def get_or_create(
    session: Session,
    model: Type[T],
    defaults: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> T:
    """
    Get an existing instance or create a new one.

    Args:
        session: SQLAlchemy session
        model: The model class
        defaults: Default values for new instances
        **kwargs: Filters for the query

    Returns:
        An instance of the model
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance

    params = {**kwargs}
    if defaults:
        params.update(defaults)
    instance = model(**params)
    session.add(instance)
    session.flush()
    return instance 