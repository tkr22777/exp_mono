"""
Tests for the TextProcessorService.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.modules.llms import AIClientError
from src.modules.text_processor.models.domain import (
    Message,
    ProcessingResult,
    SessionState,
)
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
        session_repository=mock_session_repository, ai_client=mock_ai_client
    )


class TestTextProcessorService:
    """Tests for the TextProcessorService class."""

    def test_initialization(
        self, text_processor_service, mock_session_repository, mock_ai_client
    ):
        """Test that the service initializes correctly with dependencies."""
        assert text_processor_service.session_repository == mock_session_repository
        assert text_processor_service.ai_client == mock_ai_client

    def test_process_text_empty_input(self, text_processor_service):
        """Test process_text with empty input."""
        result = text_processor_service.process_text("")
        assert isinstance(result, ProcessingResult)
        assert result.response == "Please provide some text to work with."
        assert result.session_id is None

    def test_process_text_whitespace_input(self, text_processor_service):
        """Test process_text with whitespace only input."""
        result = text_processor_service.process_text("   ")
        assert isinstance(result, ProcessingResult)
        assert result.response == "Please provide some text to work with."
        assert result.session_id is None

    def test_process_text_with_session(self, text_processor_service, mock_ai_client):
        """Test process_text with a session ID."""
        session_id = "test-session-id"
        result = text_processor_service.process_text("a bright blue cow", session_id)

        assert isinstance(result, ProcessingResult)
        assert result.response == "Mock AI response"
        assert result.session_id == session_id
        mock_ai_client.generate_response.assert_called_once()

    def test_process_text_first_input(self, text_processor_service, mock_ai_client):
        """Test process_text with first text input."""
        result = text_processor_service.process_text("a bright blue cow")

        assert isinstance(result, ProcessingResult)
        assert result.response == "Mock AI response"
        mock_ai_client.generate_response.assert_called_once()

    def test_generate_llm_response_valid_text(
        self, text_processor_service, mock_ai_client
    ):
        """Test _generate_llm_response with valid text."""
        response = text_processor_service._generate_llm_response("a bright blue cow")
        assert response == "Mock AI response"
        mock_ai_client.generate_response.assert_called_once()

    def test_generate_llm_response_transformation_instruction(
        self, text_processor_service, mock_ai_client
    ):
        """Test _generate_llm_response with transformation instruction."""
        response = text_processor_service._generate_llm_response("make it red")
        assert response == "Mock AI response"
        mock_ai_client.generate_response.assert_called_once()

    def test_generate_llm_response_with_session(
        self, text_processor_service, mock_session_repository
    ):
        """Test _generate_llm_response with a session ID."""
        session_id = "test-session-id"
        state = SessionState(
            last_response="a bright blue cow",
            history=[
                Message(role="system", content="System message"),
                Message(role="user", content="a bright blue cow"),
                Message(role="assistant", content="a bright blue cow"),
            ],
        )
        mock_session_repository.get_session.return_value = state

        text_processor_service._generate_llm_response("make it red", session_id)

        # Verify session repository was called correctly
        mock_session_repository.get_session.assert_called_with(session_id)
        mock_session_repository.save_session.assert_called_once()

    def test_generate_llm_response_exception_handling(
        self, text_processor_service, mock_ai_client
    ):
        """Test exception handling in _generate_llm_response."""
        mock_ai_client.generate_response.side_effect = AIClientError("Test AI error")

        response = text_processor_service._generate_llm_response("some text")

        assert "I encountered an AI processing issue: Test AI error" in response
