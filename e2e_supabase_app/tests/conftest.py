"""
Test fixtures for E2E Supabase App.
"""
import pytest
from src.server.app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner() 