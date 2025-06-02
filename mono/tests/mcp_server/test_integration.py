#!/usr/bin/env python3
"""
Quick test script for MCP server functionality.
"""

import asyncio
import subprocess
import sys
import time
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_communication() -> bool:
    """Test basic MCP server-client communication."""
    print("🚀 Testing MCP Server-Client Communication...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server.server"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")
                
                # Initialize the connection
                await session.initialize()
                print("✅ Session initialized")
                
                # List available tools
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test calculator tool
                print("\n🧮 Testing calculator tool...")
                calc_result = await session.call_tool(
                    "calculate", 
                    arguments={"expression": "2 + 3 * 4"}
                )
                
                if calc_result.content:
                    import json
                    calc_data = json.loads(calc_result.content[0].text)
                    if calc_data.get("success") and calc_data.get("result") == 14:
                        print("✅ Calculator test passed")
                    else:
                        print(f"❌ Calculator test failed: {calc_data}")
                        return False
                
                # Test text stats tool
                print("\n📊 Testing text stats tool...")
                text_result = await session.call_tool(
                    "text_stats", 
                    arguments={"text": "Hello world! This is a test."}
                )
                
                if text_result.content:
                    text_data = json.loads(text_result.content[0].text)
                    if text_data.get("word_count") == 6:
                        print("✅ Text stats test passed")
                    else:
                        print(f"❌ Text stats test failed: {text_data}")
                        return False
                
                # Test system info tool
                print("\n💻 Testing system info tool...")
                sys_result = await session.call_tool("system_info", arguments={})
                
                if sys_result.content:
                    sys_data = json.loads(sys_result.content[0].text)
                    if "platform" in sys_data and "python_version" in sys_data:
                        print("✅ System info test passed")
                    else:
                        print(f"❌ System info test failed: {sys_data}")
                        return False
                
                # Test text formatting tool
                print("\n🎨 Testing text formatting tool...")
                format_result = await session.call_tool(
                    "format_text", 
                    arguments={"text": "hello world", "format_type": "upper"}
                )
                
                if format_result.content:
                    format_data = json.loads(format_result.content[0].text)
                    if format_data.get("success") and format_data.get("formatted") == "HELLO WORLD":
                        print("✅ Text formatting test passed")
                    else:
                        print(f"❌ Text formatting test failed: {format_data}")
                        return False
                
                return True
                
    except Exception as e:
        print(f"❌ Error during MCP communication test: {e}")
        return False


async def main() -> None:
    """Run all MCP tests."""
    print("🔧 MCP Server Test Suite")
    print("=" * 50)
    
    # Test stdio mode (main MCP protocol)
    stdio_success = await test_mcp_communication()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Stdio Mode: {'✅ PASS' if stdio_success else '❌ FAIL'}")
    
    if stdio_success:
        print("\n🎉 All tests passed! Your MCP server is ready to use.")
        print("\n📖 Usage:")
        print("   make mcp-server  # Start the server")
        print("   make mcp-client  # Start the interactive client")
    else:
        print("\n⚠️  Tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 