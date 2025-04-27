"""
Persistence API for LangChain Agent

This module provides a simple API for persisting and retrieving LangChain
decision chains and steps from a database.
"""
import os
from typing import List, Optional, Tuple

from src.langchain_agent.agent import DecisionChain, DecisionStep, LangChainAgent
from src.langchain_agent.persistence.database import (
    DatabaseSession,
    DecisionRepository,
    get_engine,
)


def save_decision_chain(chain: DecisionChain, db_path: Optional[str] = None) -> str:
    """
    Save a decision chain to the database.
    
    Args:
        chain: The decision chain to save
        db_path: Path to the SQLite database file (optional)
        
    Returns:
        The ID of the saved chain
    """
    with DatabaseSession(db_path=db_path) as session:
        repository = DecisionRepository(session)
        db_chain = repository.save_chain(chain)
        return db_chain.chain_id


def get_decision_chain(chain_id: str, db_path: Optional[str] = None) -> Optional[DecisionChain]:
    """
    Get a decision chain by ID.
    
    Args:
        chain_id: The ID of the chain to get
        db_path: Path to the SQLite database file (optional)
        
    Returns:
        The decision chain or None if not found
    """
    with DatabaseSession(db_path=db_path) as session:
        repository = DecisionRepository(session)
        return repository.get_chain(chain_id)


def get_recent_chains(limit: int = 10, db_path: Optional[str] = None) -> List[DecisionChain]:
    """
    Get recent decision chains.
    
    Args:
        limit: Maximum number of chains to return
        db_path: Path to the SQLite database file (optional)
        
    Returns:
        List of decision chains
    """
    with DatabaseSession(db_path=db_path) as session:
        repository = DecisionRepository(session)
        return repository.get_chains(limit=limit)


def delete_decision_chain(chain_id: str, db_path: Optional[str] = None) -> bool:
    """
    Delete a decision chain by ID.
    
    Args:
        chain_id: The ID of the chain to delete
        db_path: Path to the SQLite database file (optional)
        
    Returns:
        True if the chain was deleted, False otherwise
    """
    with DatabaseSession(db_path=db_path) as session:
        repository = DecisionRepository(session)
        result = repository.delete_chain(chain_id)
        return result


class PersistentLangChainAgent(LangChainAgent):
    """
    LangChain agent with persistence capabilities.
    
    This agent extends the standard LangChainAgent with the ability
    to persist decision chains and steps to a database.
    """
    
    def __init__(self, *args, db_path: Optional[str] = None, **kwargs):
        """
        Initialize the persistent LangChain agent.
        
        Args:
            *args: Arguments to pass to the parent class
            db_path: Path to the SQLite database file (optional)
            **kwargs: Keyword arguments to pass to the parent class
        """
        super().__init__(*args, **kwargs)
        self.db_path = db_path
    
    def save_active_chain(self) -> Optional[str]:
        """
        Save the active decision chain to the database.
        
        Returns:
            The ID of the saved chain or None if no active chain
        """
        if not self.active_chain:
            return None
        
        return save_decision_chain(self.active_chain, self.db_path)
    
    def load_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Load a decision chain from the database.
        
        Args:
            chain_id: The ID of the chain to load
            
        Returns:
            The loaded decision chain or None if not found
        """
        chain = get_decision_chain(chain_id, self.db_path)
        
        if chain:
            self.active_chain = chain
            
        return chain
    
    def process_text_with_persistence(self, text: str) -> Tuple[DecisionChain, str]:
        """
        Process text with persistence.
        
        This method processes the text using the standard process_text method
        and then persists the resulting chain to the database.
        
        Args:
            text: The input text to process
            
        Returns:
            A tuple containing the decision chain and its ID
        """
        chain = self.process_text(text)
        chain_id = save_decision_chain(chain, self.db_path)
        return chain, chain_id


def create_persistent_agent(db_path: Optional[str] = None, **kwargs) -> PersistentLangChainAgent:
    """
    Create a persistent LangChain agent.
    
    Args:
        db_path: Path to the SQLite database file (optional)
        **kwargs: Additional keyword arguments for the agent
        
    Returns:
        A configured PersistentLangChainAgent instance
    """
    return PersistentLangChainAgent(db_path=db_path, **kwargs) 