"""
LangChain Agent Repository Module

This module provides factory functions for creating repositories.
"""

from typing import Optional

from src.modules.langchain_agent.repositories.interfaces import DecisionChainRepository
from src.modules.langchain_agent.repositories.models import Base
from src.modules.langchain_agent.repositories.sqlite_repository import (
    SQLiteDecisionChainRepository,
)

# Singleton instance
_decision_chain_repository: Optional[DecisionChainRepository] = None


def get_decision_chain_repository(
    db_path: Optional[str] = None,
) -> DecisionChainRepository:
    """
    Get the decision chain repository instance.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        Decision chain repository instance
    """
    global _decision_chain_repository

    if _decision_chain_repository is None:
        _decision_chain_repository = SQLiteDecisionChainRepository(db_path)

    return _decision_chain_repository
