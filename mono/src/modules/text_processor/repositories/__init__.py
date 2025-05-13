"""
Text Processor Repository Module

This module provides factory functions for creating repositories.
"""

from src.modules.text_processor.repositories.interfaces import SessionRepository
from src.modules.text_processor.repositories.memory_repositories import InMemorySessionRepository

# Singleton instance
_session_repository: SessionRepository = InMemorySessionRepository()


def get_session_repository() -> SessionRepository:
    """
    Get the session repository instance.
    
    Returns:
        Session repository instance
    """
    return _session_repository 