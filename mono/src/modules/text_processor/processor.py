"""
Text Processor Module

This module contains functionality for text processing using an LLM with minimal context.
The implementation demonstrates a simple conversational workflow where:
1. Only the last response from the LLM is stored in the session state
2. This last response is included in the next prompt to provide minimal context
3. The system message guides the LLM to perform as a calculator for demo purposes
"""
from typing import Optional

from src.modules.text_processor import get_text_processor_service


def process_text(text: str, session_id: Optional[str] = None) -> str:
    """
    Process text using an LLM with minimal context

    Args:
        text: The input text to process
        session_id: Session identifier for tracking the conversation history

    Returns:
        The generated response text
    """
    # Get the text processor service
    service = get_text_processor_service()

    # Process the text and return the response
    result = service.process_text(text, session_id)
    return result.response
