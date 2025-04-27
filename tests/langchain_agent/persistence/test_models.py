"""
Tests for the SQLAlchemy models used in the LangChain Agent persistence module.
"""
import json

import pytest
from sqlalchemy import inspect

from src.langchain_agent.agent import DecisionChain, DecisionStep
from src.langchain_agent.persistence.models import (
    Base,
    ChainModel,
    StepModel,
    get_or_create,
)


def test_chain_model_creation(db_session):
    """Test creating a ChainModel instance."""
    chain_model = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        status="in_progress"
    )
    
    db_session.add(chain_model)
    db_session.flush()
    
    # Verify it was saved correctly
    retrieved = db_session.query(ChainModel).filter_by(chain_id="test-chain-id").first()
    assert retrieved is not None
    assert retrieved.chain_id == "test-chain-id"
    assert retrieved.title == "Test Chain"
    assert retrieved.context == "Test context"
    assert retrieved.status == "in_progress"
    assert retrieved.final_decision is None
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None


def test_step_model_creation(db_session):
    """Test creating a StepModel instance."""
    # First create a chain to reference
    chain_model = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        status="in_progress"
    )
    db_session.add(chain_model)
    db_session.flush()
    
    # Now create a step
    step_model = StepModel(
        step_id="test-step-id",
        chain_id="test-chain-id",
        step_number=1,
        reasoning="Test reasoning",
        decision="Test decision",
        next_actions=json.dumps(["Action 1", "Action 2"]),
        meta_data=json.dumps({"key": "value"})
    )
    
    db_session.add(step_model)
    db_session.flush()
    
    # Verify it was saved correctly
    retrieved = db_session.query(StepModel).filter_by(step_id="test-step-id").first()
    assert retrieved is not None
    assert retrieved.step_id == "test-step-id"
    assert retrieved.chain_id == "test-chain-id"
    assert retrieved.step_number == 1
    assert retrieved.reasoning == "Test reasoning"
    assert retrieved.decision == "Test decision"
    assert json.loads(retrieved.next_actions) == ["Action 1", "Action 2"]
    assert json.loads(retrieved.meta_data) == {"key": "value"}
    assert retrieved.created_at is not None
    
    # Verify relationship
    assert retrieved.chain == chain_model


def test_chain_model_to_pydantic(db_session, sample_decision_step):
    """Test converting a ChainModel to a Pydantic model."""
    # Create a chain with steps
    chain_model = ChainModel(
        chain_id="test-chain-id",
        title="Test Chain",
        context="Test context",
        final_decision="Final decision",
        status="completed"
    )
    db_session.add(chain_model)
    db_session.flush()
    
    # Create steps
    step_model = StepModel(
        step_id=sample_decision_step.step_id,
        chain_id="test-chain-id",
        step_number=sample_decision_step.step_number,
        reasoning=sample_decision_step.reasoning,
        decision=sample_decision_step.decision,
        next_actions=json.dumps(sample_decision_step.next_actions),
        meta_data=json.dumps(sample_decision_step.metadata)
    )
    db_session.add(step_model)
    db_session.flush()
    
    # Convert to Pydantic model
    pydantic_chain = chain_model.to_pydantic()
    
    # Verify the conversion
    assert isinstance(pydantic_chain, DecisionChain)
    assert pydantic_chain.chain_id == "test-chain-id"
    assert pydantic_chain.title == "Test Chain"
    assert pydantic_chain.context == "Test context"
    assert pydantic_chain.final_decision == "Final decision"
    assert pydantic_chain.status == "completed"
    assert len(pydantic_chain.steps) == 1
    
    # Verify the step conversion
    step = pydantic_chain.steps[0]
    assert isinstance(step, DecisionStep)
    assert step.step_id == sample_decision_step.step_id
    assert step.step_number == sample_decision_step.step_number
    assert step.reasoning == sample_decision_step.reasoning
    assert step.decision == sample_decision_step.decision
    assert step.next_actions == sample_decision_step.next_actions
    assert step.metadata == sample_decision_step.metadata


def test_chain_model_from_pydantic(sample_decision_chain):
    """Test creating a ChainModel from a Pydantic model."""
    # Convert to SQLAlchemy model
    sqlalchemy_chain = ChainModel.from_pydantic(sample_decision_chain)
    
    # Verify the conversion
    assert sqlalchemy_chain.chain_id == sample_decision_chain.chain_id
    assert sqlalchemy_chain.title == sample_decision_chain.title
    assert sqlalchemy_chain.context == sample_decision_chain.context
    assert sqlalchemy_chain.final_decision == sample_decision_chain.final_decision
    assert sqlalchemy_chain.status == sample_decision_chain.status
    
    # Steps are added separately


def test_step_model_to_pydantic(db_session, sample_decision_step):
    """Test converting a StepModel to a Pydantic model."""
    # Create a step model
    step_model = StepModel(
        step_id=sample_decision_step.step_id,
        chain_id="test-chain-id",
        step_number=sample_decision_step.step_number,
        reasoning=sample_decision_step.reasoning,
        decision=sample_decision_step.decision,
        next_actions=json.dumps(sample_decision_step.next_actions),
        meta_data=json.dumps(sample_decision_step.metadata)
    )
    
    # Convert to Pydantic model
    pydantic_step = step_model.to_pydantic()
    
    # Verify the conversion
    assert isinstance(pydantic_step, DecisionStep)
    assert pydantic_step.step_id == sample_decision_step.step_id
    assert pydantic_step.step_number == sample_decision_step.step_number
    assert pydantic_step.reasoning == sample_decision_step.reasoning
    assert pydantic_step.decision == sample_decision_step.decision
    assert pydantic_step.next_actions == sample_decision_step.next_actions
    assert pydantic_step.metadata == sample_decision_step.metadata


def test_step_model_from_pydantic(sample_decision_step):
    """Test creating a StepModel from a Pydantic model."""
    # Convert to SQLAlchemy model
    sqlalchemy_step = StepModel.from_pydantic(sample_decision_step, "test-chain-id")
    
    # Verify the conversion
    assert sqlalchemy_step.step_id == sample_decision_step.step_id
    assert sqlalchemy_step.chain_id == "test-chain-id"
    assert sqlalchemy_step.step_number == sample_decision_step.step_number
    assert sqlalchemy_step.reasoning == sample_decision_step.reasoning
    assert sqlalchemy_step.decision == sample_decision_step.decision
    assert json.loads(sqlalchemy_step.next_actions) == sample_decision_step.next_actions
    assert json.loads(sqlalchemy_step.meta_data) == sample_decision_step.metadata


def test_get_or_create_existing(db_session):
    """Test get_or_create with an existing instance."""
    # Create a model first
    chain = ChainModel(
        chain_id="existing-id",
        title="Existing Chain",
        context="Existing context",
        status="in_progress"
    )
    db_session.add(chain)
    db_session.flush()
    
    # Use get_or_create to retrieve it
    result = get_or_create(
        db_session,
        ChainModel,
        defaults={"title": "New Title"},
        chain_id="existing-id"
    )
    
    # Verify we got the existing one
    assert result.chain_id == "existing-id"
    assert result.title == "Existing Chain"  # Not updated from defaults


def test_get_or_create_new(db_session):
    """Test get_or_create with a new instance."""
    # Use get_or_create to create a new instance
    result = get_or_create(
        db_session,
        ChainModel,
        defaults={
            "title": "New Chain",
            "context": "New context",
            "status": "in_progress"
        },
        chain_id="new-id"
    )
    
    # Verify a new instance was created
    assert result.chain_id == "new-id"
    assert result.title == "New Chain"
    assert result.context == "New context"
    assert result.status == "in_progress"
    
    # Verify it was saved to the database
    retrieved = db_session.query(ChainModel).filter_by(chain_id="new-id").first()
    assert retrieved is not None
    assert retrieved == result 