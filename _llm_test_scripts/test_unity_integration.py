#!/usr/bin/env python3
"""
Unity Integration Test Suite

Tests the Unity portmanteau tools without requiring Unity to be installed.
This verifies that our MCP server can properly communicate with Unity
when it becomes available.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from avatarmcp.server import AvatarMCPServer


class UnityIntegrationTester:
    """Test suite for Unity integration tools."""

    def __init__(self):
        self.server = None
        self.test_results = []

    async def setup(self):
        """Set up the test environment."""
        print("🔧 Setting up Unity integration test environment...")

        # Initialize server
        self.server = AvatarMCPServer()
        await self.server.start()

        print("✅ Server initialized successfully")

    async def teardown(self):
        """Clean up the test environment."""
        if self.server:
            await self.server.stop()
        print("🧹 Test environment cleaned up")

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")

        self.test_results.append({"test": test_name, "success": success, "message": message})

    async def test_unity_integration_tool(self):
        """Test Unity integration portmanteau tool."""
        print("\n🎮 Testing Unity Integration Tool...")

        try:
            # Test system status by calling the tool function directly
            tool_func = self.server.mcp.tools["unity_integration"]["function"]
            result = await tool_func({"operation": "status"})

            success = result.get("status") == "success"
            self.log_test("Unity Integration - System Status", success, result.get("message", ""))

            # Test avatar load
            result = await tool_func({"operation": "load_avatar", "avatar_path": "models/Nekomimi-chan.vrm"})

            success = result.get("status") == "success"
            self.log_test("Unity Integration - Avatar Load", success, result.get("message", ""))

        except Exception as e:
            self.log_test("Unity Integration Tool", False, str(e))

    async def test_unity_window_manager_tool(self):
        """Test Unity window manager portmanteau tool."""
        print("\n🪟 Testing Unity Window Manager Tool...")

        try:
            # Test window position
            result = await self.server.mcp.call_tool(
                "unity_window_manager",
                {"operation": "position", "x": 100, "y": 100, "width": 800, "height": 600},
            )

            success = result.get("status") == "success"
            self.log_test("Unity Window Manager - Position", success, result.get("message", ""))

            # Test transparency
            result = await self.server.mcp.call_tool(
                "unity_window_manager", {"operation": "transparency", "opacity": 0.8}
            )

            success = result.get("status") == "success"
            self.log_test("Unity Window Manager - Transparency", success, result.get("message", ""))

            # Test visibility
            result = await self.server.mcp.call_tool(
                "unity_window_manager", {"operation": "visibility", "visible": True}
            )

            success = result.get("status") == "success"
            self.log_test("Unity Window Manager - Visibility", success, result.get("message", ""))

            # Test mode
            result = await self.server.mcp.call_tool(
                "unity_window_manager", {"operation": "mode", "mode": "interactive"}
            )

            success = result.get("status") == "success"
            self.log_test("Unity Window Manager - Mode", success, result.get("message", ""))

        except Exception as e:
            self.log_test("Unity Window Manager Tool", False, str(e))

    async def test_unity_config_manager_tool(self):
        """Test Unity config manager portmanteau tool."""
        print("\n⚙️ Testing Unity Config Manager Tool...")

        try:
            # Test get config
            result = await self.server.mcp.call_tool("unity_config_manager", {"operation": "get_config"})

            success = result.get("status") == "success"
            self.log_test("Unity Config Manager - Get Config", success, result.get("message", ""))

            # Test OSC bridge config
            result = await self.server.mcp.call_tool(
                "unity_config_manager",
                {
                    "operation": "osc_bridge",
                    "enabled": True,
                    "server_port": 9000,
                    "client_port": 9001,
                },
            )

            success = result.get("status") == "success"
            self.log_test("Unity Config Manager - OSC Bridge", success, result.get("message", ""))

            # Test plugin list
            result = await self.server.mcp.call_tool("unity_config_manager", {"operation": "plugin_list"})

            success = result.get("status") == "success"
            self.log_test("Unity Config Manager - Plugin List", success, result.get("message", ""))

        except Exception as e:
            self.log_test("Unity Config Manager Tool", False, str(e))

    async def test_osc_communication(self):
        """Test OSC communication with Unity."""
        print("\n📡 Testing OSC Communication...")

        try:
            # Test OSC send
            result = await self.server.mcp.call_tool(
                "osc_communicator",
                {"operation": "send", "address": "/unity/test", "args": ["hello", "unity"]},
            )

            success = result.get("status") == "success"
            self.log_test("OSC Communication - Send", success, result.get("message", ""))

        except Exception as e:
            self.log_test("OSC Communication", False, str(e))

    async def run_all_tests(self):
        """Run all Unity integration tests."""
        print("🧪 Unity Integration Test Suite")
        print("=" * 50)

        await self.setup()

        try:
            await self.test_unity_integration_tool()
            await self.test_unity_window_manager_tool()
            await self.test_unity_config_manager_tool()
            await self.test_osc_communication()

        finally:
            await self.teardown()

        # Print summary
        print("\n📊 Test Summary")
        print("=" * 50)

        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)

        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            print("🎉 All tests passed! Unity integration is ready.")
        else:
            print("⚠️ Some tests failed. Check the output above.")

        return passed == total


async def main():
    """Main test runner."""
    tester = UnityIntegrationTester()
    success = await tester.run_all_tests()

    if success:
        print("\n🚀 Next Steps:")
        print("   1. Install Unity 2022.3.11f1 LTS or later")
        print("   2. Run: .\\build-unity-avatar.ps1")
        print("   3. Start Unity desktop avatar")
        print("   4. Test real Unity integration")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
