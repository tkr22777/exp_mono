"""
Flask Application for E2E Supabase App

This module defines a Flask application with basic routes and functionality.
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import datetime

# Initialize Flask app
app = Flask(
    __name__, 
    static_folder="static",
    template_folder="templates"
)

# Enable CORS for all routes
CORS(app)

# Sample data for demonstration
messages = []

@app.route("/", methods=["GET"])
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@app.route("/api/message", methods=["POST"])
def add_message():
    """Add a new message to the list."""
    data = request.json
    
    if not data or "text" not in data:
        return jsonify({"error": "Message text is required"}), 400
    
    # Extract message text
    text = data["text"]
    author = data.get("author", "Anonymous")
    
    # Create message object
    message = {
        "id": len(messages) + 1,
        "text": text,
        "author": author,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Add to messages list
    messages.append(message)
    
    return jsonify({"success": True, "message": message})

@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Get all messages."""
    return jsonify({"success": True, "messages": messages})

@app.route("/api/messages/<int:message_id>", methods=["GET"])
def get_message(message_id):
    """Get a specific message by ID."""
    for message in messages:
        if message["id"] == message_id:
            return jsonify({"success": True, "message": message})
    
    return jsonify({"success": False, "error": "Message not found"}), 404

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    })

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    return app

def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Run the server directly if this file is executed
    run_server(debug=True) 