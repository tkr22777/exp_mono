"""
Tests for the API endpoints.
"""
import json
import time


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_login_required(client):
    """Test that endpoints requiring authentication return 401 if not logged in."""
    response = client.get("/auth/profile")
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_register_and_login(client):
    """Test user registration and login."""
    # Generate unique email with timestamp to avoid conflicts
    unique_email = f"test_{int(time.time())}@example.com"

    # Register a new user
    register_data = {"email": unique_email, "password": "securepassword"}
    response = client.post(
        "/auth/register",
        data=json.dumps(register_data),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "user" in data
    assert data["user"]["email"] == unique_email

    # Login with the user
    login_data = {"email": unique_email, "password": "securepassword"}
    response = client.post(
        "/auth/login", data=json.dumps(login_data), content_type="application/json"
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "user" in data
    assert data["user"]["email"] == unique_email


def test_logout(client):
    """Test user logout."""
    # Register and login first
    register_data = {
        "email": f"logout_{int(time.time())}@example.com",
        "password": "securepassword",
    }
    client.post(
        "/auth/register",
        data=json.dumps(register_data),
        content_type="application/json",
    )

    # Test logout
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    # Verify logged out by trying to access profile
    response = client.get("/auth/profile")
    assert response.status_code == 401
