"""
LangChain Agent Domain Models

This module defines the domain models for the LangChain Agent.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DecisionStep(BaseModel):
    """Model representing a single step in the decision process."""

    step_id: str = Field(default_factory=lambda: str(uuid4()))
    step_number: int = Field(description="The sequence number of this step")
    reasoning: str = Field(description="The reasoning behind this step")
    decision: str = Field(description="The decision made in this step")
    next_actions: List[str] = Field(
        default_factory=list, description="Next actions to take based on this decision"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for this step"
    )


class DecisionChain(BaseModel):
    """Model representing a chain of decision steps."""

    chain_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(description="Title for this decision chain")
    context: str = Field(description="The context that prompted this decision chain")
    steps: List[DecisionStep] = Field(
        default_factory=list, description="The steps in this decision chain"
    )
    final_decision: Optional[str] = Field(
        None, description="The final decision reached at the end of the chain"
    )
    status: str = Field(
        default="in_progress",
        description="Status of the decision chain (in_progress, completed, error)",
    )
