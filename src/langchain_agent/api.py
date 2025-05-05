"""
LangChain Agent API

This module provides a simple API for using the LangChain decision-making agent
from other parts of the application.
"""
from typing import Dict, Tuple

from pydantic import BaseModel, Field

from src.langchain_agent.agent import DecisionChain, LangChainAgent, create_agent


class LangChainDecisionResult(BaseModel):
    """Model representing the results of the LangChain decision-making process."""

    title: str = Field(description="Title for the decision process")
    final_decision: str = Field(description="The final decision reached")
    step_count: int = Field(description="Number of steps in the decision process")
    context: str = Field(description="Original context for the decision")
    chain_id: str = Field(description="Unique identifier for the decision chain")


def _convert_to_result(chain: DecisionChain) -> LangChainDecisionResult:
    """
    Convert a DecisionChain to a LangChainDecisionResult.

    Args:
        chain: The decision chain to convert

    Returns:
        A LangChainDecisionResult summarizing the decision chain
    """
    return LangChainDecisionResult(
        title=chain.title,
        final_decision=chain.final_decision or "No final decision reached",
        step_count=len(chain.steps),
        context=chain.context,
        chain_id=chain.chain_id,
    )


def process_with_langchain(text: str) -> Tuple[DecisionChain, LangChainDecisionResult]:
    """
    Process text using the LangChain decision-making agent.

    This function creates a decision chain based on the input text,
    processes it through multiple steps, and returns both the full chain
    and a simplified result.

    Args:
        text: The input text to process

    Returns:
        A tuple containing the full decision chain and a simplified result
    """
    # Create the agent
    agent = create_agent()

    # Process the text
    chain = agent.process_text(text)

    # Convert to result
    result = _convert_to_result(chain)

    return chain, result
