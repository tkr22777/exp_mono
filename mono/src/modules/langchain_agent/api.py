"""
LangChain Agent API

This module provides a simple API for using the LangChain Agent.
"""

from typing import Optional, Tuple

from src.modules.langchain_agent import (
    DecisionChain,
    LangChainDecisionResult,
    get_langchain_agent_service,
)
from src.modules.langchain_agent.repositories import get_decision_chain_repository


def process_with_langchain(text: str) -> Tuple[DecisionChain, LangChainDecisionResult]:
    """
    Process text using the LangChain agent.

    Args:
        text: The input text to process

    Returns:
        A tuple containing the decision chain and the result
    """
    service = get_langchain_agent_service()
    chain = service.process_text(text)
    result = LangChainDecisionResult.from_domain(chain)
    return chain, result


def create_persistent_agent(
    db_path: Optional[str] = None, **kwargs
) -> "PersistentLangChainAgent":
    """
    Create a persistent LangChain agent.

    This is a compatibility function for the old API.

    Args:
        db_path: Path to the SQLite database file
        **kwargs: Additional keyword arguments for the agent

    Returns:
        A wrapper around the LangChain agent service
    """
    service = get_langchain_agent_service(db_path=db_path, **kwargs)
    return PersistentLangChainAgent(service)


def get_decision_chain(
    chain_id: str, db_path: Optional[str] = None
) -> Optional[DecisionChain]:
    """
    Get a decision chain by ID.

    Args:
        chain_id: The ID of the chain to get
        db_path: Path to the SQLite database file

    Returns:
        The decision chain or None if not found
    """
    repository = get_decision_chain_repository(db_path=db_path)
    return repository.get_chain(chain_id)


def get_recent_chains(limit: int = 10, db_path: Optional[str] = None):
    """
    Get recent decision chains.

    Args:
        limit: Maximum number of chains to return
        db_path: Path to the SQLite database file

    Returns:
        List of decision chains
    """
    repository = get_decision_chain_repository(db_path=db_path)
    return repository.get_recent_chains(limit=limit)


class PersistentLangChainAgent:
    """
    Wrapper around LangChainAgentService for backward compatibility.
    """

    def __init__(self, service):
        """
        Initialize the wrapper.

        Args:
            service: The LangChain agent service
        """
        self.service = service

    def process_text(self, text: str) -> DecisionChain:
        """
        Process text using the LangChain agent.

        Args:
            text: The input text to process

        Returns:
            The generated decision chain
        """
        return self.service.process_text(text)

    def process_text_with_persistence(self, text: str) -> Tuple[DecisionChain, str]:
        """
        Process text and persist the decision chain.

        Args:
            text: The input text to process

        Returns:
            A tuple containing the decision chain and its ID
        """
        return self.service.process_text_with_persistence(text)

    def load_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Load a decision chain from the database.

        Args:
            chain_id: The ID of the chain to load

        Returns:
            The loaded decision chain or None if not found
        """
        return self.service.get_chain(chain_id)
