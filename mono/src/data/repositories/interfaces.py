"""
Repository Interfaces

This module defines interfaces for data repositories using Protocol classes.
"""

from typing import Optional, Protocol

from src.modules.text_processor.models.domain import SessionState


class SessionRepository(Protocol):
    """Interface for session data repository."""
    
    def get_session(self, session_id: str) -> SessionState:
        """
        Get session state by ID, creating a new one if it doesn't exist.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session state
        """
        ...
    
    def save_session(self, session_id: str, state: SessionState) -> None:
        """
        Save session state.
        
        Args:
            session_id: Unique session identifier
            state: Session state to save
        """
        ...
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if the session was deleted, False if it didn't exist
        """
        ... 