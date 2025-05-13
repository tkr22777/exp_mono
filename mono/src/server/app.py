"""
Flask Application

This module defines the Flask application for serving HTML and APIs.
"""
import argparse

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


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application
    """
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask server with SocketIO support.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    # Run with SocketIO instead of app.run()
    socketio.run(app, host=host, port=port, debug=debug)


def main():
    """Parse command line arguments and start the server."""
    parser = argparse.ArgumentParser(description="Start the Flask server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument(
        "--debug", action="store_true", help="Whether to run in debug mode"
    )

    args = parser.parse_args()

    print(f"Starting server on {args.host}:{args.port} with debug={args.debug}")
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    # Run the server with command line arguments
    main()
