#!/usr/bin/env python3
"""
Server Entry Script

This script starts the web server for the LangChain Agent interface.
"""
import sys
from src.server.cli import main

if __name__ == "__main__":
    # Add default timeout if not specified
    if "--timeout" not in sys.argv:
        sys.argv.extend(["--timeout", "300"])
    main() 
