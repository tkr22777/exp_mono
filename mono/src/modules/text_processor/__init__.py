"""
Text Processor Module

This module provides functionality for processing text using AI models.
"""

from src.data.repositories import get_session_repository
from src.modules.llms.ai_client import default_client
from src.modules.text_processor.service import TextProcessorService

# Create a singleton instance of the text processor service
_text_processor_service = TextProcessorService(
    session_repository=get_session_repository(),
    ai_client=default_client
)


def get_text_processor_service() -> TextProcessorService:
    """
    Get the text processor service instance.
    
    Returns:
        Text processor service instance
    """
    return _text_processor_service
