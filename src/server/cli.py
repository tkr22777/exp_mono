"""
Command Line Interface for Web Server

This module provides a CLI for running the web server.
"""
import os

import click
from dotenv import load_dotenv

from src.server.app import app, run_server

# Load environment variables
load_dotenv()


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=5000, type=int, help="Port to bind the server to")
@click.option("--debug", is_flag=True, help="Run in debug mode")
@click.option("--timeout", default=300, type=int, help="Request timeout in seconds")
def main(host: str, port: int, debug: bool, timeout: int) -> None:
    """
    Run the web server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
        timeout: Request timeout in seconds
    """
    # Notify the user
    click.echo(f"Starting server on {host}:{port}")

    # Configure request timeout
    app.config["REQUEST_TIMEOUT"] = timeout

    # Run the server
    run_server(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
