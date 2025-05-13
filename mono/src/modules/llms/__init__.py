"""LLMs package for AI client interactions."""

# Make the AI client available at package level
from src.modules.llms.ai_client import default_client

__all__ = ["default_client"]
