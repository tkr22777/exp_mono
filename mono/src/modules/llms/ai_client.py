"""
AI Client Module

This module provides functionality to interact with external AI language models.
"""
import logging
from typing import Dict, List, Optional, Union

import google.generativeai as genai
from openai import OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from src.utils.settings import settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Initialize Gemini if API key is available
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Define Message type for clarity
Message = Dict[str, str]  # Contains 'role' and 'content' keys


class AIClient:
    """Client for interacting with external AI models."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI client.

        Args:
            api_key: OpenAI API key. If not provided, will use the one from settings.
        """
        openai_key = api_key or settings.OPENAI_API_KEY
        openai_org = getattr(settings, "OPENAI_ORG", None)

        if openai_key.startswith("sk-proj-"):
            if not openai_org:
                logger.warning(
                    "Using a project API key but no organization ID is set. This may cause authentication issues."
                )
            else:
                logger.info(
                    f"Using OpenAI project API key with organization ID: {openai_org}"
                )

        client_args = {"api_key": openai_key}
        if openai_org:
            client_args["organization"] = openai_org

        self.client = OpenAI(**client_args)

        self.model_name = settings.MODEL_NAME
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    def generate_response(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the AI model based on the given prompt or messages.

        Args:
            prompt: The text prompt to send to the AI model
            messages: A list of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum number of tokens in the response (overrides setting)

        Returns:
            The AI model's response as a string
        """
        try:
            # Convert prompt to messages format if messages not provided
            if messages is None:
                if prompt is None:
                    raise ValueError("Either prompt or messages must be provided")

                # Use default system message with prompt
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            else:
                # If no system message is included, add the default one
                has_system_message = any(
                    msg.get("role") == "system" for msg in messages
                )
                if not has_system_message:
                    messages.insert(
                        0, {"role": "system", "content": "You are a helpful assistant."}
                    )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            return "No response generated."

        except Exception as e:
            return f"Error generating AI response: {str(e)}"

    def generate_with_gemini(self, input_data: str) -> str:
        """
        Make an API call to Google's Gemini AI model.

        Args:
            input_data: The input prompt for the model

        Returns:
            The generated response from Gemini

        Raises:
            ValueError: If the Gemini API key is not configured
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key not found in settings. "
                "Please add GEMINI_API_KEY to your .env file."
            )

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)

            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            # Handle different versions of the Gemini API for generation config
            try:
                generation_config = genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=250,
                )
            except TypeError:
                generation_config = genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                )

            response = model.generate_content(
                input_data, generation_config=generation_config
            )

            return response.text
        except Exception as e:
            return f"Error generating Gemini response: {str(e)}"

    @retry(
        stop=stop_after_attempt(1),  # Initial attempt + retries combined
        wait=wait_fixed(0.2),  # Wait 0.2 second between retries
        retry=retry_if_exception_type(Exception),
    )
    def generate_with_deepseek(self, prompt: str) -> str:
        """
        Generate a response using Deepseek's API.

        Args:
            prompt: The input prompt for the model

        Returns:
            The generated response from Deepseek

        Raises:
            ValueError: If the Deepseek API key is not configured
        """
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError(
                "Deepseek API key not found in settings. "
                "Please add DEEPSEEK_API_KEY to your .env file."
            )

        system_prompt = settings.DEEPSEEK_SYSTEM_PROMPT

        try:
            client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
            )

            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating Deepseek response: {str(e)}"


default_client = AIClient()
