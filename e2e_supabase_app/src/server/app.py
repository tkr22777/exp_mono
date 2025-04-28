"""
Flask Application for E2E Supabase App

This module defines a Flask application with routes and Supabase integration.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import datetime

# Import configuration and blueprints
from ..config import settings
from ..auth import auth_bp
from ..messages import messages_bp
from ..web import web_bp

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure the app using settings
    app.config.update(settings.get_flask_config())
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(web_bp)
    
    # Add health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0"
        })
    
    return app

def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Run the server directly if this file is executed
    run_server(debug=True) 