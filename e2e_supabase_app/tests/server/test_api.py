"""
Tests for the API endpoints.
"""
import json

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_add_message(client, sample_message):
    """Test adding a new message."""
    response = client.post(
        "/api/message", 
        json=sample_message
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"]["text"] == sample_message["text"]
    assert data["message"]["author"] == sample_message["author"]
    assert "timestamp" in data["message"]
    assert data["message"]["id"] == 1

def test_get_messages_empty(client):
    """Test getting all messages when there are none."""
    response = client.get("/api/messages")
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data["success"] is True
    assert data["messages"] == []

def test_get_messages(client, add_sample_messages):
    """Test getting all messages."""
    response = client.get("/api/messages")
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["messages"]) == 3

def test_get_message_by_id(client, add_sample_messages):
    """Test getting a specific message by ID."""
    response = client.get("/api/messages/1")
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"]["id"] == 1
    assert data["message"]["text"] == "First test message"
    assert data["message"]["author"] == "User 1"

def test_get_message_not_found(client):
    """Test getting a message that doesn't exist."""
    response = client.get("/api/messages/999")
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert data["success"] is False
    assert "error" in data

def test_add_message_missing_text(client):
    """Test adding a message without text."""
    response = client.post(
        "/api/message", 
        json={"author": "Test Author"}
    )
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert "error" in data 