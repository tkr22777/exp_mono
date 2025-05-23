"""
In-Memory Repository Implementations

This module implements in-memory repositories for the Text Processor.
"""

from typing import Dict

from src.modules.text_processor.models.domain import SessionState


class InMemorySessionRepository:
    """In-memory implementation of the session repository."""

    def __init__(self) -> None:
        """Initialize the repository with an empty storage dictionary."""
        self._storage: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        """
        Get session state by ID, creating a new one if it doesn't exist.

        Args:
            session_id: Unique session identifier

        Returns:
            Session state
        """
        if session_id not in self._storage:
            self._storage[session_id] = SessionState()
        return self._storage[session_id]

    def save_session(self, session_id: str, state: SessionState) -> None:
        """
        Save session state.

        Args:
            session_id: Unique session identifier
            state: Session state to save
        """
        self._storage[session_id] = state

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if the session was deleted, False if it didn't exist
        """
        if session_id in self._storage:
            del self._storage[session_id]
            return True
        return False
