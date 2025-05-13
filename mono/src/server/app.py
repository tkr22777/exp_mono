"""
Flask Application

This module defines the Flask application for serving HTML and APIs.
"""
import argparse
import logging
import logging.config
import os
from typing import NoReturn, Dict, Any

from flask import Flask
from flask_cors import CORS

# Import blueprints
from src.server.routes import langchain_bp, main_bp, text_processor_bp

# Import SocketIO instance
from src.server.socketio_instance import init_socketio, socketio

# Import audio processor blueprint if available
try:
    from src.server.routes.experiments.audio_processor import audio_processor_bp

    has_audio_processor = True
except ImportError:
    has_audio_processor = False

# Configure logging
def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        debug: Whether to enable debug logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Basic configuration
    logging_config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': log_level,
                'propagate': True
            },
            'src': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Enable CORS for all routes
CORS(app)

# Initialize SocketIO with the app
init_socketio(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(langchain_bp)
app.register_blueprint(text_processor_bp)

# Register audio processor blueprint if available
if has_audio_processor:
    app.register_blueprint(audio_processor_bp)


def create_app(debug: bool = False) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        debug: Whether to enable debug mode
        
    Returns:
        Configured Flask application
    """
    # Set up logging
    setup_logging(debug)
    
    # Configure Flask app
    app.debug = debug
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask server with SocketIO support.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    # Set up logging
    setup_logging(debug)
    
    # Configure Flask app
    app.debug = debug
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Starting server on {host}:{port} with debug={debug}")
    
    # Run with SocketIO instead of app.run()
    socketio.run(app, host=host, port=port, debug=debug)


def main() -> None:
    """Parse command line arguments and start the server."""
    parser = argparse.ArgumentParser(description="Start the Flask server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument(
        "--debug", action="store_true", help="Whether to run in debug mode"
    )

    args = parser.parse_args()

    # Run the server with command line arguments
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    # Run the server with command line arguments
    main()
