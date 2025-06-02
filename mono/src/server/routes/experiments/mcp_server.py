"""
MCP Server Routes

This module defines all routes for the MCP Server experiment.
"""

import logging
from typing import Any, Dict, List, Tuple

from flask import Blueprint, Response, jsonify, render_template
from flask_socketio import emit

from src.mcp_server.client import MCPClient
from src.mcp_server.config import AVAILABLE_TOOLS, DEBOUNCE_DELAY_MS, MAX_TEXT_LENGTH, SOCKET_EVENTS
from src.server.socketio_instance import socketio
from src.server.utils.decorators import handle_mcp_errors, emit_on_error, validate_json_data

# Configure logger for this module
logger = logging.getLogger(__name__)

# Create a Blueprint for MCP Server routes with a URL prefix
mcp_server_bp = Blueprint(
    "mcp_server", __name__, url_prefix="/experiments/mcp-server"
)


@mcp_server_bp.route("/", methods=["GET"])
def index() -> str:
    """Serve the MCP Server experiment page."""
    return render_template(
        "experiments/mcp_server/index.html", 
        config={
            "debounce_delay_ms": DEBOUNCE_DELAY_MS,
            "max_text_length": MAX_TEXT_LENGTH,
            "available_tools": AVAILABLE_TOOLS
        }
    )


@mcp_server_bp.route("/api/tools", methods=["GET"])
@handle_mcp_errors
def get_tools() -> Dict[str, Any]:
    """Get list of available MCP tools."""
    tools = MCPClient.get_tools()
    return {"tools": tools}


@mcp_server_bp.route("/api/call-tool", methods=["POST"])
@handle_mcp_errors
@validate_json_data(["tool_name"])
def call_tool() -> Dict[str, Any]:
    """Call an MCP tool."""
    from flask import request
    
    tool_name = request.json["tool_name"]
    arguments = request.json.get("arguments", {})
    
    result = MCPClient.call_tool(tool_name, arguments)
    return {"result": result}


# Socket.IO event handlers for real-time MCP interaction
@socketio.on(SOCKET_EVENTS["mcp_call_tool"])
@emit_on_error(SOCKET_EVENTS["mcp_tool_result"])
def handle_mcp_call_tool_socket(data: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP tool via Socket.IO for real-time updates."""
    if not data or "tool_name" not in data:
        raise ValueError("Tool name is required")
    
    tool_name = data["tool_name"]
    arguments = data.get("arguments", {})
    
    # Emit processing start
    emit(SOCKET_EVENTS["mcp_processing_start"], {
        "tool_name": tool_name, 
        "status": "started"
    })
    
    # Call the MCP tool
    result = MCPClient.call_tool(tool_name, arguments)
    
    # Emit processing complete
    emit(SOCKET_EVENTS["mcp_processing_complete"], {"status": "complete"})
    
    return {
        "tool_name": tool_name,
        "arguments": arguments,
        "result": result
    }


@socketio.on(SOCKET_EVENTS["mcp_get_tools"])
@emit_on_error(SOCKET_EVENTS["mcp_tools_list"])
def handle_mcp_get_tools_socket() -> Dict[str, Any]:
    """Get MCP tools via Socket.IO."""
    tools = MCPClient.get_tools()
    return {"tools": tools} 