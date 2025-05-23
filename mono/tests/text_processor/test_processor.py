"""
Tests for the Text Processor module.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.modules.text_processor.models.domain import ProcessingResult
from src.modules.text_processor.processor import process_text


@pytest.fixture
def mock_text_processor_service():
    """Fixture providing a mock text processor service."""
    service = MagicMock()
    service.process_text.return_value = ProcessingResult(response="Mock response")
    return service


class TestProcessText:
    """Tests for the process_text function."""

    @patch("src.modules.text_processor.processor.get_text_processor_service")
    def test_process_text_without_session(
        self, mock_get_service, mock_text_processor_service
    ):
        """Test process_text without a session ID."""
        # Configure the mock
        mock_get_service.return_value = mock_text_processor_service

        # Call the function
        result = process_text("Test text")

        # Verify the result
        assert result == "Mock response"
        mock_text_processor_service.process_text.assert_called_once_with(
            "Test text", None
        )

    @patch("src.modules.text_processor.processor.get_text_processor_service")
    def test_process_text_with_session(
        self, mock_get_service, mock_text_processor_service
    ):
        """Test process_text with a session ID."""
        # Configure the mock
        mock_get_service.return_value = mock_text_processor_service

        # Call the function
        result = process_text("Test text", "test-session-id")

        # Verify the result
        assert result == "Mock response"
        mock_text_processor_service.process_text.assert_called_once_with(
            "Test text", "test-session-id"
        )
