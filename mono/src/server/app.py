"""
Flask Application with Socket.IO support for real-time communication.
"""
import argparse
import logging
import logging.config
import os
from typing import Any, Dict, NoReturn

from flask import Flask
from flask_cors import CORS

# Import blueprints
from src.server.routes import langchain_bp, main_bp, mcp_server_bp, text_processor_bp
from src.server.routes.experiments.audio_processor import audio_processor_bp

# Import SocketIO instance
from src.server.socketio_instance import init_socketio, socketio


def setup_logging(debug: bool = False) -> None:
    """Configure hierarchical logging with console output."""
    log_level = logging.DEBUG if debug else logging.INFO

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "src": {"handlers": ["console"], "level": log_level, "propagate": False},
            # Suppress verbose HTTP client logs
            "httpcore": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "httpx": {"handlers": ["console"], "level": "WARNING", "propagate": False},
            "urllib3": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            # Keep OpenAI client logs at INFO level to see request summaries without verbose details
            "openai": {"handlers": ["console"], "level": "INFO", "propagate": False},
        },
    }

    logging.config.dictConfig(logging_config)


# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
init_socketio(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(langchain_bp)
app.register_blueprint(mcp_server_bp)
app.register_blueprint(text_processor_bp)
app.register_blueprint(audio_processor_bp)


def create_app(debug: bool = False) -> Flask:
    """Factory function for creating the Flask application."""
    setup_logging(debug)
    app.debug = debug
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """Run the server with Socket.IO support instead of standard Flask server."""
    setup_logging(debug)
    app.debug = debug

    logger = logging.getLogger(__name__)
    logger.info(f"Starting server on {host}:{port} with debug={debug}")

    # Use socketio.run instead of app.run
    socketio.run(app, host=host, port=port, debug=debug)


def main() -> None:
    """Entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Start the Flask server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument(
        "--debug", action="store_true", help="Whether to run in debug mode"
    )

    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
