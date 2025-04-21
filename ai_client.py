"""
AI Client Module

This module provides functionality to interact with external AI language models.
"""
import os
from typing import Optional

import dotenv
from openai import OpenAI

# Load environment variables from the .env file
if os.path.exists(".env"):
    dotenv.load_dotenv(".env")


class AIClient:
    """Client for interacting with external AI models."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI client.

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env var.
        """
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        # Get model settings from environment variables or use defaults
        self.model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
        self.max_tokens = int(os.environ.get("MAX_TOKENS", "150"))
        self.temperature = float(os.environ.get("TEMPERATURE", "0.7"))

    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the AI model based on the given prompt.

        Args:
            prompt: The text prompt to send to the AI model
            max_tokens: Maximum number of tokens in the response (overrides env setting)

        Returns:
            The AI model's response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
            )

            # Extract the response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            return "No response generated."

        except Exception as e:
            return f"Error generating AI response: {str(e)}"


# Create a singleton instance
default_client = AIClient()
