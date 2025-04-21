"""
Plan Creator Module

This module is responsible for creating processing plans for text analysis.
"""
from pydantic import BaseModel, Field


class ProcessingPlan(BaseModel):
    """Model representing a processing plan for text analysis."""

    title: str = Field(description="Title for the text processing plan")
    status: str = Field(default="planned", description="Status of the processing plan")


def create_plan(text: str) -> ProcessingPlan:
    """
    Create a processing plan based on the input text.

    Args:
        text: The input text to process

    Returns:
        A processing plan with minimal details
    """
    words = text.split()
    # Simple title extraction (first 5 words or less)
    title = " ".join(words[: min(5, len(words))]) + "..."

    plan = ProcessingPlan(
        title=title,
    )

    return plan
