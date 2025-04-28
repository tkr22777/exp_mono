"""
Flask Application for E2E Supabase App

This module defines a Flask application with routes and Supabase integration.
"""
from flask import Flask, jsonify, session, send_from_directory
from flask_cors import CORS
import datetime
import os
import logging
from pathlib import Path

# Import configuration and blueprints
from ..config import settings
from ..auth import auth_bp
from ..messages import messages_bp
from ..web import web_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    # Get the path to the web directory for templates and static files
    web_dir = Path(__file__).parent.parent / 'web'
    static_folder = web_dir / 'static'
    template_folder = web_dir / 'templates'
    
    # Initialize Flask app with static and template folders explicitly set
    app = Flask(__name__, 
                static_folder=str(static_folder),
                static_url_path='/static',
                template_folder=str(template_folder))
    
    # Configure the app using settings
    app.config.update(settings.get_flask_config())
    
    # Ensure secret key is set
    if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'dev-secret-key':
        logging.warning("Using default development secret key. Set SECRET_KEY in .env for production.")
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True)
    
    # Register error handler for all routes
    @app.errorhandler(Exception)
    def handle_error(e):
        logging.error(f"Unhandled exception: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred. Please try again later.",
            "details": str(e) if app.debug else None
        }), 500
    
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
    
    # Add favicon route to prevent 404s
    @app.route('/favicon.ico')
    def favicon():
        """Serve the favicon."""
        return send_from_directory(str(static_folder), 'favicon.ico')
    
    # Add session debugging endpoint if in debug mode
    if app.debug:
        @app.route("/debug/session", methods=["GET"])
        def debug_session():
            """Debug endpoint to view session details."""
            return jsonify({
                "session": {k: str(v) for k, v in session.items()},
                "has_token": "access_token" in session
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
    logging.info(f"Starting server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Run the server directly if this file is executed
    run_server(debug=True) 