#!/usr/bin/env python3
"""
Development Server Script

This script starts the Flask development server with SocketIO support.
"""

import argparse

from src.server.app import run_server


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
    main()
