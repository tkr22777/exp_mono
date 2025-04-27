"""
Command Line Interface for E2E Supabase App

This module provides a CLI for running the web server.
"""
import click
import os
import sys
from dotenv import load_dotenv

from .app import run_server, app


# Load environment variables if .env file exists
if os.path.exists(".env"):
    load_dotenv()


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=5000, type=int, help="Port to bind the server to")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def main(host: str, port: int, debug: bool) -> None:
    """
    Run the web server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    # Notify the user
    click.echo(f"Starting server on {host}:{port}")
    
    # Run the server
    run_server(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main() 