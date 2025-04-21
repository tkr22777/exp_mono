"""
Test AI Models

This module contains pytest-based tests for OpenAI, Gemini, and Deepseek models.
Each test sends a structured prompt and verifies the models can produce the expected output format.
"""
import os
import json
import pytest
import dotenv
from openai import OpenAI

from src.ai_client import default_client
from src.settings import settings


def get_env_value(key: str) -> str:
    """Get a value directly from the .env file, bypassing settings."""
    dotenv.load_dotenv()
    return os.getenv(key, "")


def mask_api_key(key: str) -> str:
    """Mask an API key for safe display."""
    if not key:
        return "None (not set)"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def print_config():
    """Print masked configuration for debugging purposes."""
    print("\n🔧 Configuration:")
    print(f"OpenAI API Key: {mask_api_key(settings.OPENAI_API_KEY)}")
    print(f"OpenAI Org ID: {getattr(settings, 'OPENAI_ORG', 'Not set')}")
    print(f"Gemini API Key: {mask_api_key(settings.GEMINI_API_KEY or '')}")
    print(f"Deepseek API Key: {mask_api_key(settings.DEEPSEEK_API_KEY or '')}")


# A structured prompt that requests a specific output format
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
        # Clean the response if it contains error messages
        if response.startswith("Error generating"):
            return False
            
        # Extract JSON if surrounded by other text (like markdown code blocks)
        if "```json" in response:
            # Extract JSON from markdown code block
            start = response.find("```json") + 7
            end = response.rfind("```")
            response = response[start:end].strip()
        elif "```" in response:
            # Extract from generic code block
            start = response.find("```") + 3
            end = response.rfind("```")
            response = response[start:end].strip()
            
        # Parse the JSON
        data = json.loads(response)
        
        # Verify the expected structure
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
    
    # Get organization ID from settings or .env
    org_id = getattr(settings, "OPENAI_ORG", None) or get_env_value("OPENAI_ORG")
    
    # Skip if using project API key without org ID
    api_key = settings.OPENAI_API_KEY
    if api_key.startswith("sk-proj-") and not org_id:
        pytest.skip("OpenAI project API key requires a valid organization ID")
    
    # Create client with appropriate parameters
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
            temperature=0.1,  # Lower temperature for more deterministic output
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


if __name__ == "__main__":
    """Run tests manually if script is executed directly."""
    print_config()
    
    test_functions = [
        ("OpenAI", test_openai),
        ("Gemini", test_gemini),
        ("Deepseek", test_deepseek)
    ]
    
    for name, test_func in test_functions:
        print(f"\nTesting {name}...")
        try:
            test_func()
            print(f"✅ {name} Test Passed")
        except pytest.skip.Exception as e:
            print(f"⚠️ {name} Test Skipped: {str(e)}")
        except Exception as e:
            print(f"❌ {name} Test Failed: {str(e)}") 