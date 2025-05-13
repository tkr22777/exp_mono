"""
LangChain Agent Repository Interfaces

This module defines the interfaces for repositories used by the LangChain Agent.
"""

from typing import List, Optional, Protocol

from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep


class DecisionChainRepository(Protocol):
    """Interface for decision chain repository."""
    
    def save_chain(self, chain: DecisionChain) -> str:
        """
        Save a decision chain.
        
        Args:
            chain: The decision chain to save
            
        Returns:
            The ID of the saved chain
        """
        ...
    
    def get_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Get a decision chain by ID.
        
        Args:
            chain_id: The ID of the chain to get
            
        Returns:
            The decision chain or None if not found
        """
        ...
    
    def get_recent_chains(self, limit: int = 10) -> List[DecisionChain]:
        """
        Get recent decision chains.
        
        Args:
            limit: Maximum number of chains to return
            
        Returns:
            List of decision chains
        """
        ...
    
    def delete_chain(self, chain_id: str) -> bool:
        """
        Delete a decision chain by ID.
        
        Args:
            chain_id: The ID of the chain to delete
            
        Returns:
            True if the chain was deleted, False otherwise
        """
        ... 