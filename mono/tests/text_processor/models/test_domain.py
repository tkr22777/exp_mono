"""
Tests for the Text Processor domain models.
"""
import pytest
from pydantic import ValidationError

from src.modules.text_processor.models.domain import Message, SessionState, ProcessingResult


class TestMessage:
    """Tests for the Message class."""

    def test_valid_message_creation(self):
        """Test creating a valid message."""
        message = Message(role="user", content="Test message")
        
        assert message.role == "user"
        assert message.content == "Test message"

    def test_missing_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            Message(role="user")  # Missing content
            
        with pytest.raises(ValidationError):
            Message(content="Test message")  # Missing role


class TestSessionState:
    """Tests for the SessionState class."""

    def test_default_initialization(self):
        """Test initializing with default values."""
        state = SessionState()
        
        assert state.last_response == ""
        assert isinstance(state.history, list)
        assert len(state.history) == 0

    def test_custom_initialization(self):
        """Test initializing with custom values."""
        history = [
            Message(role="system", content="System message"),
            Message(role="user", content="User message"),
            Message(role="assistant", content="Assistant response")
        ]
        
        state = SessionState(last_response="Test response", history=history)
        
        assert state.last_response == "Test response"
        assert len(state.history) == 3
        assert state.history[0].role == "system"
        assert state.history[1].role == "user"
        assert state.history[2].role == "assistant"


class TestProcessingResult:
    """Tests for the ProcessingResult class."""

    def test_initialization_with_required_fields(self):
        """Test initializing with only required fields."""
        result = ProcessingResult(response="Test response")
        
        assert result.response == "Test response"
        assert result.session_id is None

    def test_initialization_with_all_fields(self):
        """Test initializing with all fields."""
        result = ProcessingResult(response="Test response", session_id="test-session-id")
        
        assert result.response == "Test response"
        assert result.session_id == "test-session-id"

    def test_missing_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            ProcessingResult()  # Missing response 