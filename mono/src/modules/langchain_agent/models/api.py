"""
LangChain Agent API Models

This module defines the API models for the LangChain Agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep


class ProcessTextRequest(BaseModel):
    """Request model for processing text with LangChain Agent."""
    
    text: str = Field(..., description="The text to process")
    persist: bool = Field(default=False, description="Whether to persist the decision chain")


class DecisionStepResponse(BaseModel):
    """Response model for a decision step."""
    
    step_number: int = Field(..., description="The sequence number of this step")
    reasoning: str = Field(..., description="The reasoning behind this step")
    decision: str = Field(..., description="The decision made in this step")
    next_actions: List[str] = Field(
        default_factory=list, description="Next actions to take based on this decision"
    )
    
    @classmethod
    def from_domain(cls, step: DecisionStep) -> "DecisionStepResponse":
        """Create a response model from a domain model."""
        return cls(
            step_number=step.step_number,
            reasoning=step.reasoning,
            decision=step.decision,
            next_actions=step.next_actions,
        )


class LangChainDecisionResult(BaseModel):
    """Result of processing text with LangChain Agent."""
    
    chain_id: str = Field(..., description="The ID of the decision chain")
    title: str = Field(..., description="Title for this decision chain")
    final_decision: Optional[str] = Field(
        None, description="The final decision reached at the end of the chain"
    )
    step_count: int = Field(..., description="The number of steps in the decision chain")
    
    @classmethod
    def from_domain(cls, chain: DecisionChain) -> "LangChainDecisionResult":
        """Create a result model from a domain model."""
        final_decision = chain.final_decision
        if final_decision is None:
            final_decision = "No final decision reached"
            
        return cls(
            chain_id=chain.chain_id,
            title=chain.title,
            final_decision=final_decision,
            step_count=len(chain.steps),
        )


class ProcessTextResponse(BaseModel):
    """Response model for processing text with LangChain Agent."""
    
    success: bool = Field(default=True, description="Whether the request was successful")
    result: Optional[LangChainDecisionResult] = Field(None, description="The result of processing")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    
    @classmethod
    def from_chain(cls, chain: DecisionChain) -> "ProcessTextResponse":
        """Create a response from a decision chain."""
        return cls(
            success=True,
            result=LangChainDecisionResult.from_domain(chain),
            error=None,
        )
    
    @classmethod
    def from_error(cls, error: str) -> "ProcessTextResponse":
        """Create an error response."""
        return cls(
            success=False,
            result=None,
            error=error,
        ) 