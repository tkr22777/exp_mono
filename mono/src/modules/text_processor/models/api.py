"""
Text Processor API Models

This module contains the API models for the text processor.
"""

from typing import Optional
from pydantic import BaseModel, Field

from src.modules.text_processor.models.domain import ProcessingResult


class TextProcessRequest(BaseModel):
    """Request model for text processing."""
    text: str = Field(..., description="Text to process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class TextProcessResponse(BaseModel):
    """Response model for text processing."""
    success: bool = Field(default=True, description="Whether the request was successful")
    result: Optional[ProcessingResult] = Field(None, description="Processing result")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    
    @classmethod
    def from_result(cls, result: ProcessingResult) -> "TextProcessResponse":
        """Create a response from a processing result."""
        return cls(success=True, result=result, error=None)
    
    @classmethod
    def from_error(cls, error: str) -> "TextProcessResponse":
        """Create an error response."""
        return cls(success=False, result=None, error=error) 