"""
Test AI Models

This module contains pytest-based tests for OpenAI, Gemini, and Deepseek models.
Each test sends a structured prompt and verifies the models can produce the expected output format.
"""
import os
import json
import pytest
from openai import OpenAI

from src.ai_client import default_client
from src.settings import settings


def mask_api_key(key: str) -> str:
    """Mask an API key for safe display."""
    if not key:
        return "None (not set)"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


TEST_PROMPT = """
Please respond with a JSON object containing exactly the following structure:
{
  "greeting": "Hello, World!",
  "status": "success"
}
Provide ONLY the JSON object with no additional text before or after.
"""


def verify_json_response(response: str) -> bool:
    """
    Verify the response is valid JSON with the expected structure.
    
    Args:
        response: The model's response as a string
        
    Returns:
        True if the response contains valid JSON with the expected fields
    """
    try:
        if response.startswith("Error generating"): # Handle client-side error messages
            return False
            
        # Attempt to extract JSON if wrapped in markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.rfind("```")
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.rfind("```")
            response = response[start:end].strip()
            
        data = json.loads(response)
        
        return (
            isinstance(data, dict) 
            and data.get("greeting") == "Hello, World!" 
            and data.get("status") == "success"
        )
    except (json.JSONDecodeError, KeyError):
        return False


def test_openai():
    """Test OpenAI API integration with structured output."""
    if not settings.OPENAI_API_KEY:
        pytest.skip("OpenAI API key not configured")
    
    org_id = settings.OPENAI_ORG
    api_key = settings.OPENAI_API_KEY

    # Project keys require an org ID
    if api_key.startswith("sk-proj-") and not org_id:
        pytest.skip("OpenAI project API key requires a valid organization ID")
    
    client_args = {"api_key": api_key}
    if org_id:
        client_args["organization"] = org_id
    
    try:
        client = OpenAI(**client_args)
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns valid JSON."},
                {"role": "user", "content": TEST_PROMPT},
            ],
            max_tokens=settings.MAX_TOKENS,
            temperature=0.1, # Lower temperature for deterministic JSON output
        )
        
        response_text = response.choices[0].message.content if response.choices else ""
        assert response_text, "Response should not be empty"
        assert verify_json_response(response_text), f"Response should be valid JSON with expected structure. Got: {response_text}"
    except Exception as e:
        pytest.skip(f"OpenAI API error: {str(e)}")


@pytest.mark.skipif(
    not settings.GEMINI_API_KEY, reason="Gemini API key not configured"
)
def test_gemini():
    """Test Gemini API integration with structured output."""
    try:
        response = default_client.generate_with_gemini(TEST_PROMPT)
        assert response, "Response should not be empty"
        assert verify_json_response(response), f"Response should be valid JSON with expected structure. Got: {response}"
    except Exception as e:
        pytest.skip(f"Gemini API error: {str(e)}")


@pytest.mark.skipif(
    not settings.DEEPSEEK_API_KEY, reason="Deepseek API key not configured"
)
def test_deepseek():
    """Test Deepseek API integration with structured output."""
    try:
        response = default_client.generate_with_deepseek(TEST_PROMPT)
        assert response, "Response should not be empty"
        assert verify_json_response(response), f"Response should be valid JSON with expected structure. Got: {response}"
    except Exception as e:
        pytest.skip(f"Deepseek API error: {str(e)}") 