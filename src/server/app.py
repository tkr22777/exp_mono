"""
Flask Application

This module defines the Flask application for serving HTML and APIs.
"""
from flask import Flask
from flask_cors import CORS

# Import SocketIO instance
from src.server.socketio_instance import init_socketio, socketio

# Import blueprints
from src.server.routes import langchain_bp, main_bp, text_processor_bp
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


if __name__ == "__main__":
    # Run the server directly if this file is executed
    run_server(debug=True)
