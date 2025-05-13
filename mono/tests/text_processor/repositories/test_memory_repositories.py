"""
Tests for the in-memory repositories for the Text Processor.
"""
import pytest

from src.modules.text_processor.models.domain import SessionState, Message
from src.modules.text_processor.repositories.memory_repositories import InMemorySessionRepository


@pytest.fixture
def session_repository():
    """Fixture providing an in-memory session repository."""
    return InMemorySessionRepository()


@pytest.fixture
def sample_session_state():
    """Fixture providing a sample session state."""
    return SessionState(
        last_response="Test response",
        history=[
            Message(role="system", content="System message"),
            Message(role="user", content="User message"),
            Message(role="assistant", content="Assistant response")
        ]
    )


class TestInMemorySessionRepository:
    """Tests for the InMemorySessionRepository class."""

    def test_initialization(self, session_repository):
        """Test that the repository initializes correctly."""
        assert hasattr(session_repository, '_storage')
        assert isinstance(session_repository._storage, dict)
        assert len(session_repository._storage) == 0

    def test_get_session_new(self, session_repository):
        """Test getting a new session."""
        session_id = "test-session-id"
        state = session_repository.get_session(session_id)
        
        assert isinstance(state, SessionState)
        assert state.last_response == ""
        assert len(state.history) == 0
        assert session_id in session_repository._storage

    def test_get_session_existing(self, session_repository, sample_session_state):
        """Test getting an existing session."""
        session_id = "test-session-id"
        session_repository._storage[session_id] = sample_session_state
        
        state = session_repository.get_session(session_id)
        
        assert state == sample_session_state
        assert state.last_response == "Test response"
        assert len(state.history) == 3

    def test_save_session_new(self, session_repository, sample_session_state):
        """Test saving a new session."""
        session_id = "test-session-id"
        session_repository.save_session(session_id, sample_session_state)
        
        assert session_id in session_repository._storage
        assert session_repository._storage[session_id] == sample_session_state

    def test_save_session_update(self, session_repository, sample_session_state):
        """Test updating an existing session."""
        session_id = "test-session-id"
        # First save a session
        session_repository.save_session(session_id, sample_session_state)
        
        # Create an updated state
        updated_state = SessionState(
            last_response="Updated response",
            history=[
                Message(role="system", content="System message"),
                Message(role="user", content="User message"),
                Message(role="assistant", content="Assistant response"),
                Message(role="user", content="Follow-up question"),
                Message(role="assistant", content="Follow-up response")
            ]
        )
        
        # Update the session
        session_repository.save_session(session_id, updated_state)
        
        # Verify the session was updated
        state = session_repository.get_session(session_id)
        assert state == updated_state
        assert state.last_response == "Updated response"
        assert len(state.history) == 5

    def test_delete_session_existing(self, session_repository, sample_session_state):
        """Test deleting an existing session."""
        session_id = "test-session-id"
        session_repository._storage[session_id] = sample_session_state
        
        result = session_repository.delete_session(session_id)
        
        assert result is True
        assert session_id not in session_repository._storage

    def test_delete_session_nonexistent(self, session_repository):
        """Test deleting a non-existent session."""
        session_id = "nonexistent-session-id"
        
        result = session_repository.delete_session(session_id)
        
        assert result is False 