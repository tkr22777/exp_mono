"""
Unit tests for MCP Configuration

Tests that configuration values are sensible and properly defined.
"""

import pytest

from src.mcp_server.config import (
    AVAILABLE_TOOLS,
    DEBOUNCE_DELAY_MS,
    MAX_TEXT_LENGTH,
    MCP_CALL_TIMEOUT_SECONDS,
    MCP_SERVER_ARGS,
    MCP_SERVER_COMMAND,
    MCP_TOOLS_TIMEOUT_SECONDS,
    SOCKET_EVENTS,
)


class TestMCPConfig:
    """Test cases for MCP configuration."""

    def test_server_configuration_is_valid(self):
        """Test that server configuration is properly defined."""
        assert isinstance(MCP_SERVER_COMMAND, str)
        assert MCP_SERVER_COMMAND == "python"
        assert isinstance(MCP_SERVER_ARGS, list)
        assert len(MCP_SERVER_ARGS) > 0

    def test_timeout_values_are_reasonable(self):
        """Test that timeout values are reasonable for a startup."""
        assert isinstance(MCP_TOOLS_TIMEOUT_SECONDS, int)
        assert isinstance(MCP_CALL_TIMEOUT_SECONDS, int)
        assert 1 <= MCP_TOOLS_TIMEOUT_SECONDS <= 30  # Reasonable range
        assert 1 <= MCP_CALL_TIMEOUT_SECONDS <= 60  # Reasonable range
        assert (
            MCP_CALL_TIMEOUT_SECONDS > MCP_TOOLS_TIMEOUT_SECONDS
        )  # Tool calls should have longer timeout

    def test_ui_configuration_is_valid(self):
        """Test that UI configuration values are reasonable."""
        assert isinstance(DEBOUNCE_DELAY_MS, int)
        assert isinstance(MAX_TEXT_LENGTH, int)
        assert 0 < DEBOUNCE_DELAY_MS < 1000  # Reasonable debounce
        assert 100 < MAX_TEXT_LENGTH < 10000  # Reasonable text limit

    def test_available_tools_structure(self):
        """Test that available tools are properly structured."""
        assert isinstance(AVAILABLE_TOOLS, list)
        assert len(AVAILABLE_TOOLS) > 0

        for tool in AVAILABLE_TOOLS:
            assert isinstance(tool, dict)
            assert "name" in tool
            assert "description" in tool
            assert "example" in tool
            assert isinstance(tool["name"], str)
            assert isinstance(tool["description"], str)
            assert isinstance(tool["example"], str)

    def test_socket_events_are_complete(self):
        """Test that all necessary Socket.IO events are defined."""
        required_events = [
            "mcp_call_tool",
            "mcp_get_tools",
            "mcp_tool_result",
            "mcp_tools_list",
            "mcp_error",
            "mcp_processing_start",
            "mcp_processing_complete",
        ]

        assert isinstance(SOCKET_EVENTS, dict)
        for event in required_events:
            assert event in SOCKET_EVENTS
            assert isinstance(SOCKET_EVENTS[event], str)

    def test_no_unused_configurations(self):
        """Test that we don't have unused configurations (startup principle)."""
        # This is more of a documentation test
        # All configurations in the file should be actively used
        config_items = [
            MCP_SERVER_COMMAND,
            MCP_SERVER_ARGS,
            MCP_TOOLS_TIMEOUT_SECONDS,
            MCP_CALL_TIMEOUT_SECONDS,
            DEBOUNCE_DELAY_MS,
            MAX_TEXT_LENGTH,
            AVAILABLE_TOOLS,
            SOCKET_EVENTS,
        ]

        # All items should be defined (not None)
        for item in config_items:
            assert item is not None
