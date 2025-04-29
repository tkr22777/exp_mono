"""
Tests for the Flask application.
"""


def test_index_page(client):
    """Test the index page loads correctly."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"E2E Supabase App" in response.data
    assert (
        b"A secure, end-to-end application with Flask and Supabase integration"
        in response.data
    )
    assert b"Get Started" in response.data


def test_app_configuration(app):
    """Test the app is configured correctly."""
    assert app.testing is True
