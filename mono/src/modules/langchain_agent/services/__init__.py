"""
LangChain Agent Service Module

This module provides factory functions for creating services.
"""

from typing import Optional

from langchain_core.language_models import BaseLanguageModel

from src.modules.langchain_agent.repositories import get_decision_chain_repository
from src.modules.langchain_agent.services.agent_service import LangChainAgentService


def get_langchain_agent_service(
    db_path: Optional[str] = None,
    llm: Optional[BaseLanguageModel] = None,
    verbose: bool = False,
    max_iterations: int = 5,
) -> LangChainAgentService:
    """
    Get the LangChain agent service instance.
    
    Args:
        db_path: Path to the SQLite database file
        llm: The language model to use
        verbose: Whether to print verbose output during execution
        max_iterations: Maximum number of iterations for the agent to run
        
    Returns:
        LangChain agent service instance
    """
    repository = get_decision_chain_repository(db_path)
    return LangChainAgentService(
        repository=repository,
        llm=llm,
        verbose=verbose,
        max_iterations=max_iterations,
    ) 