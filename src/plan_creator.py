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
    # Extract a title from the text (first 5 words or less)
    words = text.split()
    title = " ".join(words[: min(5, len(words))]) + "..."

    plan = ProcessingPlan(
        title=title,
    )

    return plan
