"""
Tests for the Text Processor API models.
"""
import pytest
from pydantic import ValidationError

from src.modules.text_processor.models.api import (
    TextProcessRequest,
    TextProcessResponse,
)
from src.modules.text_processor.models.domain import ProcessingResult


class TestTextProcessRequest:
    """Tests for the TextProcessRequest class."""

    def test_valid_request_creation(self):
        """Test creating a valid request."""
        request = TextProcessRequest(text="Test text")

        assert request.text == "Test text"
        assert request.session_id is None

    def test_request_with_session_id(self):
        """Test creating a request with a session ID."""
        request = TextProcessRequest(text="Test text", session_id="test-session-id")

        assert request.text == "Test text"
        assert request.session_id == "test-session-id"

    def test_missing_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            TextProcessRequest()  # Missing text


class TestTextProcessResponse:
    """Tests for the TextProcessResponse class."""

    def test_default_initialization(self):
        """Test initializing with default values."""
        response = TextProcessResponse()

        assert response.success is True
        assert response.result is None
        assert response.error is None

    def test_custom_initialization(self):
        """Test initializing with custom values."""
        result = ProcessingResult(
            response="Test response", session_id="test-session-id"
        )
        response = TextProcessResponse(success=True, result=result)

        assert response.success is True
        assert response.result == result
        assert response.error is None

    def test_error_initialization(self):
        """Test initializing with an error."""
        response = TextProcessResponse(success=False, error="Test error")

        assert response.success is False
        assert response.result is None
        assert response.error == "Test error"

    def test_from_result_factory_method(self):
        """Test the from_result factory method."""
        result = ProcessingResult(
            response="Test response", session_id="test-session-id"
        )
        response = TextProcessResponse.from_result(result)

        assert response.success is True
        assert response.result == result
        assert response.error is None

    def test_from_error_factory_method(self):
        """Test the from_error factory method."""
        error = "Test error"
        response = TextProcessResponse.from_error(error)

        assert response.success is False
        assert response.result is None
        assert response.error == error
