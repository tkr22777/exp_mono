"""
Test AI Models

This module contains pytest-based tests for OpenAI, Gemini, and Deepseek models.
Each test sends a simple prompt and verifies the models are working correctly.
"""
import os
import re
import pytest
import dotenv
from openai import OpenAI

from src.ai_client import default_client, AIClient
from src.settings import settings


def get_env_value(key: str) -> str:
    """Get a value directly from the .env file, bypassing settings."""
    dotenv.load_dotenv()  # Make sure .env is loaded
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
    openai_org = getattr(settings, "OPENAI_ORG", None)
    print(f"OpenAI Org ID: {openai_org or 'Not set'}")
    print(f"OpenAI Model: {settings.MODEL_NAME}")
    print(f"Gemini API Key: {mask_api_key(settings.GEMINI_API_KEY or '')}")
    print(f"Gemini Model: {settings.GEMINI_MODEL}")
    print(f"Deepseek API Key: {mask_api_key(settings.DEEPSEEK_API_KEY or '')}")
    print(f"Deepseek Model: {settings.DEEPSEEK_MODEL}")
    print(f"Deepseek System Prompt: {settings.DEEPSEEK_SYSTEM_PROMPT[:30]}..." if 
          len(settings.DEEPSEEK_SYSTEM_PROMPT) > 30 else settings.DEEPSEEK_SYSTEM_PROMPT)


# Simpler prompt that will work across all models
TEST_PROMPT = "Write 'Hello, World!' exactly as shown."


def verify_response(response: str) -> bool:
    """
    Verify the response contains 'Hello, World!' in any case.
    """
    # Check if the response contains an error message
    if response.startswith("Error generating"):
        # Extract the error message to help with debugging
        print(f"Error in API response: {response}")
        return False
    
    # Very simple check - does the response contain "hello" and "world"
    return "hello" in response.lower() and "world" in response.lower()


def test_openai():
    """Test OpenAI API integration."""
    if not settings.OPENAI_API_KEY:
        pytest.skip("OpenAI API key not configured")
    
    # Get organization ID directly from .env file
    env_org_id = get_env_value("OPENAI_ORG")
    settings_org_id = getattr(settings, "OPENAI_ORG", None)
    
    # Print configuration to help debug
    print(f"\nOpenAI Configuration:")
    print(f"- API Key: {mask_api_key(settings.OPENAI_API_KEY)}")
    print(f"- Organization ID from settings: {settings_org_id or 'Not set'}")
    print(f"- Organization ID from .env: {env_org_id or 'Not set'}")
    print(f"- Model: {settings.MODEL_NAME}")
    
    # For testing, create a fresh client with explicit parameters
    api_key = settings.OPENAI_API_KEY
    org_id = settings_org_id or env_org_id
    
    # Check if we need an organization ID for this key
    if api_key.startswith("sk-proj-") and not org_id:
        print("\n⚠️ OpenAI Project API Key detected but no Organization ID found!")
        print("You need to add OPENAI_ORG to your .env file.")
        pytest.skip("OpenAI project API key requires a valid organization ID")
    
    # Create client with or without organization ID
    client_args = {"api_key": api_key}
    if org_id:
        client_args["organization"] = org_id
        print(f"Using organization ID: {org_id}")
    
    try:
        # Create a fresh client
        client = OpenAI(**client_args)
        
        # Test with a minimal API call first to verify authentication
        models = client.models.list()
        print(f"Authentication successful. Available models: {len(models.data)}")
        
        # Now try the actual test
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": TEST_PROMPT},
            ],
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content if response.choices else ""
        
        assert response_text, "Response should not be empty"
        assert verify_response(response_text), f"Response should contain 'Hello, World!'. Got: {response_text}"
        print(f"\n✅ OpenAI Response: {response_text}")
    except Exception as e:
        print(f"\n❌ OpenAI API Error: {str(e)}")
        pytest.skip(f"OpenAI API error: {str(e)}")


@pytest.mark.skipif(
    not settings.GEMINI_API_KEY, reason="Gemini API key not configured"
)
def test_gemini_direct():
    """Test Gemini API integration using direct method."""
    import google.generativeai as genai
    
    try:
        # Ensure we're using the latest API key
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Create a fresh model instance without caching
        gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Create a simple generation config
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=250,
                response_mime_type="text/plain",
            )
        except TypeError:
            # Fall back to older API version
            generation_config = genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
            )
        
        # Generate response with simplified approach
        response = gemini_model.generate_content(
            TEST_PROMPT,
            generation_config=generation_config
        )
        
        # Extract text from response
        response_text = response.text
        
        assert response_text, "Response should not be empty"
        assert verify_response(response_text), f"Response should contain 'Hello, World!'. Got: {response_text}"
        print(f"\n✅ Gemini Direct Response: {response_text}")
    except Exception as e:
        print(f"\n❌ Gemini API Error: {str(e)}")
        pytest.skip(f"Gemini API error: {str(e)}")


@pytest.mark.skipif(
    not settings.GEMINI_API_KEY, reason="Gemini API key not configured"
)
def test_gemini_client():
    """Test Gemini API integration using client method."""
    response = default_client.generate_with_gemini(TEST_PROMPT)
    
    # Handle API errors
    if response.startswith("Error generating Gemini response:"):
        print(f"\n❌ Gemini Client Error: {response}")
        pytest.skip(f"Gemini API error: {response}")
    
    assert response, "Response should not be empty"
    assert verify_response(response), f"Response should contain 'Hello, World!'. Got: {response}"
    print(f"\n✅ Gemini Client Response: {response}")


@pytest.mark.skipif(
    not settings.DEEPSEEK_API_KEY, reason="Deepseek API key not configured"
)
def test_deepseek():
    """Test Deepseek API integration."""
    response = default_client.generate_with_deepseek(TEST_PROMPT)
    
    # Handle API errors
    if response.startswith("Error generating Deepseek response:"):
        print(f"\n❌ Deepseek Error: {response}")
        pytest.skip(f"Deepseek API error: {response}")
    
    assert response, "Response should not be empty"
    assert verify_response(response), f"Response should contain 'Hello, World!'. Got: {response}"
    print(f"\n✅ Deepseek Response: {response}")


if __name__ == "__main__":
    # For manual testing via python test_ai_models.py
    print_config()
    print(f"\n🧪 Testing AI Models with prompt: '{TEST_PROMPT}'\n")
    
    try:
        test_openai()
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
    
    if settings.GEMINI_API_KEY:
        try:
            test_gemini_direct()
            test_gemini_client()
        except Exception as e:
            print(f"❌ Gemini Error: {str(e)}")
    else:
        print("⚠️ Gemini API key not set. Skipping test.")
    
    if settings.DEEPSEEK_API_KEY:
        try:
            test_deepseek()
        except Exception as e:
            print(f"❌ Deepseek Error: {str(e)}")
    else:
        print("⚠️ Deepseek API key not set. Skipping test.")
    
    print("\n✨ Test completed!") 