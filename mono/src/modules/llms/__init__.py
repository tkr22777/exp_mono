"""LLMs package for AI client interactions."""

# Make the AI client and exceptions available at package level
from src.modules.llms.ai_client import (
    default_client,
    AIClientError,
    OpenAIError,
    GeminiError,
    DeepseekError,
    InvalidAPIKeyError,
)

__all__ = [
    "default_client",
    "AIClientError",
    "OpenAIError", 
    "GeminiError",
    "DeepseekError",
    "InvalidAPIKeyError",
]
