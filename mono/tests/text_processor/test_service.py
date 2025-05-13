"""
Tests for the TextProcessorService.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.modules.text_processor.models.domain import ProcessingResult, SessionState, Message
from src.modules.text_processor.service import TextProcessorService


@pytest.fixture
def mock_session_repository():
    """Fixture providing a mock session repository."""
    repo = MagicMock()
    repo.get_session.return_value = SessionState()
    return repo


@pytest.fixture
def mock_ai_client():
    """Fixture providing a mock AI client."""
    client = MagicMock()
    client.generate_response.return_value = "Mock AI response"
    return client


@pytest.fixture
def text_processor_service(mock_session_repository, mock_ai_client):
    """Fixture providing a TextProcessorService with mock dependencies."""
    return TextProcessorService(
        session_repository=mock_session_repository,
        ai_client=mock_ai_client
    )


class TestTextProcessorService:
    """Tests for the TextProcessorService class."""

    def test_initialization(self, text_processor_service, mock_session_repository, mock_ai_client):
        """Test that the service initializes correctly with dependencies."""
        assert text_processor_service.session_repository == mock_session_repository
        assert text_processor_service.ai_client == mock_ai_client

    def test_is_valid_number_valid_input(self, text_processor_service):
        """Test is_valid_number with valid inputs."""
        assert text_processor_service.is_valid_number("42") is True
        assert text_processor_service.is_valid_number("3.14") is True
        assert text_processor_service.is_valid_number("-10") is True
        assert text_processor_service.is_valid_number("  42  ") is True  # Test with whitespace

    def test_is_valid_number_invalid_input(self, text_processor_service):
        """Test is_valid_number with invalid inputs."""
        assert text_processor_service.is_valid_number("not a number") is False
        assert text_processor_service.is_valid_number("42a") is False
        assert text_processor_service.is_valid_number("") is False

    def test_process_text_empty_input(self, text_processor_service):
        """Test process_text with empty input."""
        result = text_processor_service.process_text("")
        assert isinstance(result, ProcessingResult)
        assert result.response == "Please enter a number."
        assert result.session_id is None

    def test_process_text_with_session(self, text_processor_service, mock_ai_client):
        """Test process_text with a session ID."""
        session_id = "test-session-id"
        result = text_processor_service.process_text("42", session_id)
        
        assert isinstance(result, ProcessingResult)
        assert result.response == "Mock AI response"
        assert result.session_id == session_id
        mock_ai_client.generate_response.assert_called_once()

    def test_generate_llm_response_invalid_number(self, text_processor_service, mock_ai_client):
        """Test _generate_llm_response with invalid number."""
        response = text_processor_service._generate_llm_response("not a number")
        assert response == "Please provide a valid number."
        mock_ai_client.generate_response.assert_not_called()

    def test_generate_llm_response_valid_number(self, text_processor_service, mock_ai_client):
        """Test _generate_llm_response with valid number."""
        response = text_processor_service._generate_llm_response("42")
        assert response == "Mock AI response"
        mock_ai_client.generate_response.assert_called_once()

    def test_generate_llm_response_with_session(self, text_processor_service, mock_session_repository):
        """Test _generate_llm_response with a session ID."""
        session_id = "test-session-id"
        state = SessionState(
            last_response="Previous response",
            history=[
                Message(role="system", content="System message"),
                Message(role="user", content="Previous input"),
                Message(role="assistant", content="Previous response")
            ]
        )
        mock_session_repository.get_session.return_value = state
        
        text_processor_service._generate_llm_response("42", session_id)
        
        # Verify session repository was called correctly
        mock_session_repository.get_session.assert_called_with(session_id)
        mock_session_repository.save_session.assert_called_once()
        
    def test_generate_llm_response_exception_handling(self, text_processor_service, mock_ai_client):
        """Test exception handling in _generate_llm_response."""
        mock_ai_client.generate_response.side_effect = Exception("Test error")
        
        response = text_processor_service._generate_llm_response("42")
        
        assert "I encountered an issue: Test error" in response 