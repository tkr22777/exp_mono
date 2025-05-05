"""
Flask Application

This module defines the Flask application for serving HTML and APIs.
"""
from flask import Flask
from flask_cors import CORS

# Import blueprints
from src.server.routes import langchain_bp, main_bp

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(langchain_bp)


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
