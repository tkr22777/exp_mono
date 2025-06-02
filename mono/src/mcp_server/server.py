"""
Simple MCP Server implementation.

This module provides a basic MCP server with common tools like calculator,
text processing, and system information.
"""

import asyncio
import json
import math
import os
import platform
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP


class SimpleMCPServer:
    """A simple MCP server with basic tool implementations."""

    def __init__(self, name: str = "Simple MCP Server") -> None:
        """Initialize the MCP server."""
        self.server = FastMCP(name)
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up all available tools."""

        @self.server.tool(
            name="calculate", description="Evaluate mathematical expressions safely"
        )
        def calculate(expression: str) -> Dict[str, Any]:
            """Calculate mathematical expressions safely."""
            try:
                # Only allow safe mathematical operations
                allowed_names = {
                    k: v for k, v in math.__dict__.items() if not k.startswith("__")
                }
                allowed_names.update(
                    {
                        "abs": abs,
                        "round": round,
                        "min": min,
                        "max": max,
                        "sum": sum,
                        "pow": pow,
                    }
                )

                result = eval(expression, {"__builtins__": {}}, allowed_names)
                return {"expression": expression, "result": result, "success": True}
            except Exception as e:
                return {"expression": expression, "error": str(e), "success": False}

        @self.server.tool(
            name="text_stats",
            description="Get statistics about text (word count, character count, etc.)",
        )
        def text_stats(text: str) -> Dict[str, Any]:
            """Get comprehensive statistics about text."""
            words = text.split()
            lines = text.split("\n")

            return {
                "text_length": len(text),
                "character_count": len(text),
                "word_count": len(words),
                "line_count": len(lines),
                "average_word_length": sum(len(word) for word in words) / len(words)
                if words
                else 0,
                "unique_words": len(
                    set(word.lower().strip('.,!?;:"()[]{}') for word in words)
                ),
                "paragraph_count": len([line for line in lines if line.strip()]),
                "whitespace_count": sum(1 for char in text if char.isspace()),
            }

        @self.server.tool(
            name="system_info", description="Get basic system information"
        )
        def system_info() -> Dict[str, Any]:
            """Get basic system information."""
            return {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "current_directory": os.getcwd(),
                "timestamp": datetime.now().isoformat(),
            }

        @self.server.tool(
            name="format_text",
            description="Format text in various ways (uppercase, lowercase, title case, etc.)",
        )
        def format_text(text: str, format_type: str = "title") -> Dict[str, Any]:
            """Format text in various ways."""
            formatters = {
                "upper": text.upper,
                "lower": text.lower,
                "title": text.title,
                "capitalize": text.capitalize,
                "swapcase": text.swapcase,
                "reverse": lambda: text[::-1],
                "strip": text.strip,
            }

            if format_type not in formatters:
                return {
                    "original": text,
                    "error": f"Unknown format type: {format_type}",
                    "available_formats": list(formatters.keys()),
                    "success": False,
                }

            return {
                "original": text,
                "formatted": formatters[format_type](),
                "format_type": format_type,
                "success": True,
            }

    def run_stdio(self) -> None:
        """Run the server using stdio transport."""
        self.server.run()


def main() -> None:
    """Main entry point for running the MCP server."""
    server = SimpleMCPServer()
    print("Starting MCP Server in stdio mode...", file=sys.stderr)
    server.run_stdio()


if __name__ == "__main__":
    main()
