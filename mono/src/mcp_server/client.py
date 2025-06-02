"""
MCP Client Manager

This module provides a clean interface for interacting with MCP servers,
abstracting away the complexity of async event loops and thread management.
"""

import asyncio
import concurrent.futures
import json
import logging
from typing import Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import (
    MCP_CALL_TIMEOUT_SECONDS,
    MCP_SERVER_ARGS,
    MCP_SERVER_COMMAND,
    MCP_TOOLS_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class MCPClient:
    """
    A simple, synchronous interface for MCP operations.

    Handles all the async/thread complexity internally, providing
    clean synchronous methods for use in Flask routes.
    """

    @classmethod
    def get_tools(cls) -> List[Dict[str, Any]]:
        """
        Get list of available MCP tools.

        Returns:
            List of tool definitions with name, description, and inputSchema

        Raises:
            Exception: If MCP server communication fails
        """

        def run_in_new_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:

                async def get_tools():
                    server_params = StdioServerParameters(
                        command=MCP_SERVER_COMMAND, args=MCP_SERVER_ARGS, env=None
                    )

                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            tools_response = await session.list_tools()

                            tools = []
                            for tool in tools_response.tools:
                                # Handle inputSchema - it might already be a dict
                                input_schema = tool.inputSchema
                                if hasattr(input_schema, "dict"):
                                    input_schema = input_schema.dict()
                                elif input_schema is None:
                                    input_schema = {}

                                tools.append(
                                    {
                                        "name": tool.name,
                                        "description": tool.description,
                                        "inputSchema": input_schema,
                                    }
                                )
                            return tools

                return loop.run_until_complete(get_tools())
            finally:
                loop.close()

        # Run in thread pool with fresh event loop
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result(timeout=MCP_TOOLS_TIMEOUT_SECONDS)

    @classmethod
    def call_tool(cls, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool with the given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Dictionary containing the tool result

        Raises:
            Exception: If MCP server communication fails
        """

        def run_in_new_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:

                async def call_tool():
                    server_params = StdioServerParameters(
                        command=MCP_SERVER_COMMAND, args=MCP_SERVER_ARGS, env=None
                    )

                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            result = await session.call_tool(
                                tool_name, arguments=arguments
                            )

                            if result.content:
                                try:
                                    # Try to parse JSON result
                                    return json.loads(result.content[0].text)
                                except json.JSONDecodeError:
                                    return {"text": result.content[0].text}
                            else:
                                return {"result": "No content returned"}

                return loop.run_until_complete(call_tool())
            finally:
                loop.close()

        # Run in thread pool with fresh event loop
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result(timeout=MCP_CALL_TIMEOUT_SECONDS)
