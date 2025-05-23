"""
Text Processor Domain Models

This module contains the domain models for the text processor.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a conversation."""

    role: str = Field(
        ..., description="Role of the message sender (system, user, assistant)"
    )
    content: str = Field(..., description="Content of the message")


class SessionState(BaseModel):
    """State of a text processing session."""

    last_response: str = Field(
        default="", description="Last response from the assistant"
    )
    history: List[Message] = Field(
        default_factory=list, description="Conversation history"
    )


class ProcessingResult(BaseModel):
    """Result of text processing."""

    response: str = Field(..., description="Generated response text")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
