"""
Repository Module

This module provides factory functions for creating repositories.
"""

from src.data.repositories.interfaces import SessionRepository
from src.data.repositories.memory_repositories import InMemorySessionRepository

# Singleton instances
_session_repository: SessionRepository = InMemorySessionRepository()


def get_session_repository() -> SessionRepository:
    """
    Get the session repository instance.
    
    Returns:
        Session repository instance
    """
    return _session_repository 