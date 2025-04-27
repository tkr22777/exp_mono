"""
Test fixtures for E2E Supabase App.
"""
import pytest
from src.server.app import create_app, messages

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    # Clear messages before each test
    messages.clear()
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def sample_message():
    """A sample message for testing."""
    return {
        "text": "Test message",
        "author": "Test Author"
    }

@pytest.fixture
def add_sample_messages(client):
    """Add some sample messages for testing."""
    messages = [
        {"text": "First test message", "author": "User 1"},
        {"text": "Second test message", "author": "User 2"},
        {"text": "Third test message", "author": "User 3"}
    ]
    
    for message in messages:
        client.post("/api/message", json=message)
    
    return messages 