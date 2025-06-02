"""
MCP Server Configuration

This module contains configuration constants for the MCP server implementation.
"""

from typing import List

# === MCP Server Configuration ===
MCP_SERVER_COMMAND: str = "python"
MCP_SERVER_ARGS: List[str] = ["-m", "src.mcp_server.server"]

# === Timeout Configuration ===
MCP_TOOLS_TIMEOUT_SECONDS: int = 10
MCP_CALL_TIMEOUT_SECONDS: int = 30

# === UI Configuration ===
DEBOUNCE_DELAY_MS: int = 300
MAX_TEXT_LENGTH: int = 1000

# === Available Tools Configuration ===
AVAILABLE_TOOLS = [
    {
        "name": "calculate",
        "description": "Evaluate mathematical expressions safely",
        "example": "2 + 3 * 4",
    },
    {
        "name": "text_stats",
        "description": "Get statistics about text",
        "example": "Hello world! This is a test.",
    },
    {
        "name": "system_info",
        "description": "Get basic system information",
        "example": "No input required",
    },
    {
        "name": "format_text",
        "description": "Format text in various ways",
        "example": "hello world",
    },
]

# === Socket.IO Event Names ===
SOCKET_EVENTS = {
    "mcp_call_tool": "mcp_call_tool",
    "mcp_get_tools": "mcp_get_tools",
    "mcp_tool_result": "mcp_tool_result",
    "mcp_tools_list": "mcp_tools_list",
    "mcp_error": "mcp_error",
    "mcp_processing_start": "mcp_processing_start",
    "mcp_processing_complete": "mcp_processing_complete",
}
