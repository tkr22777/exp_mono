"""LLMs package for AI client interactions."""

# Make the AI client and exceptions available at package level
from src.modules.llms.ai_client import (
    AIClientError,
    DeepseekError,
    GeminiError,
    InvalidAPIKeyError,
    OpenAIError,
    default_client,
)

__all__ = [
    "default_client",
    "AIClientError",
    "OpenAIError",
    "GeminiError",
    "DeepseekError",
    "InvalidAPIKeyError",
]
