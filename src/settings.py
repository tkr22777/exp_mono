"""
Settings Module

This module provides a centralized place for all application settings
using Pydantic for validation and type safety.
"""
import sys
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- OpenAI --- 
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_ORG: Optional[str] = Field(
        None, description="OpenAI organization ID (required for project API keys)"
    )
    MODEL_NAME: str = Field("gpt-3.5-turbo", description="OpenAI model name")
    MAX_TOKENS: int = Field(150, description="Maximum tokens for OpenAI responses")
    TEMPERATURE: float = Field(
        0.7, description="Temperature for OpenAI response generation"
    )

    # --- Google Gemini --- 
    GEMINI_API_KEY: Optional[str] = Field(
        None, description="Google Gemini API key (optional)"
    )
    GEMINI_MODEL: str = Field(
        "models/gemini-1.5-flash-001", description="Google Gemini model name"
    )
    GEMINI_TEMPERATURE: float = Field(
        0.15, description="Temperature for Gemini response generation"
    )

    # --- Deepseek --- 
    DEEPSEEK_API_KEY: Optional[str] = Field(
        None, description="Deepseek API key (optional)"
    )
    DEEPSEEK_MODEL: str = Field("deepseek-chat", description="Deepseek model name")
    DEEPSEEK_SYSTEM_PROMPT: str = Field(
        "You are a helpful assistant. Provide concise and accurate responses.",
        description="System prompt for Deepseek",
    )

    @field_validator("TEMPERATURE", "GEMINI_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate that temperature is within the valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {v}")
        return v

# Singleton instance for the application
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Check your .env file to make sure it contains the required values.")
    sys.exit(1) 