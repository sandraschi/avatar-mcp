#!/usr/bin/env python3
"""Quick test to verify Unity tools are available."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from avatarmcp.server import AvatarMCPServer


async def test_unity_tools():
    """Test that Unity tools are available."""
    print("🔧 Testing Unity tools availability...")

    server = AvatarMCPServer()
    await server.start()

    # Check available tools by inspecting the mcp object
    print(f"🔍 MCP object type: {type(server.mcp)}")
    print(f"🔍 MCP attributes: {dir(server.mcp)}")

    # Try to find tools in different ways
    if hasattr(server.mcp, "tool"):
        print(f"🔍 MCP.tool type: {type(server.mcp.tool)}")
        if hasattr(server.mcp.tool, "__dict__"):
            print(f"🔍 MCP.tool attributes: {list(server.mcp.tool.__dict__.keys())}")

    # Check if tools are registered in the portmanteau tool classes
    print(f"🔍 Unity integration tool: {hasattr(server, 'unity_integration_tool')}")
    print(f"🔍 Unity window manager tool: {hasattr(server, 'unity_window_manager_tool')}")
    print(f"🔍 Unity config manager tool: {hasattr(server, 'unity_config_manager_tool')}")

    await server.stop()
    print("✅ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_unity_tools())
