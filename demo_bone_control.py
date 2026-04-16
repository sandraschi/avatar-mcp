#!/usr/bin/env python3
"""
Bone Control Demo - Shows avatar manipulation

This demo demonstrates:
1. Loading avatar
2. Moving bones via OSC commands
3. Animation sequences
4. Interactive control
"""

import asyncio
import logging
import os
import sys

# Add src to path
sys.path.insert(0, "src")

from avatarmcp.mcp_server_clean import MCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def demo_bone_control():
    """Demonstrate bone control functionality."""

    print("🦴 Bone Control Demo")
    print("=" * 30)

    # Find VRM files
    models_dir = "models"
    vrm_files = [f for f in os.listdir(models_dir) if f.endswith(".vrm")] if os.path.exists(models_dir) else []

    if not vrm_files:
        print("❌ No VRM files found in models/ directory")
        return

    vrm_path = os.path.join(models_dir, vrm_files[0])
    print(f"📁 Using VRM: {vrm_path}")

    # Initialize server
    print("\n🔧 Starting MCP Server...")
    server = MCPServer()

    try:
        # Start OSC client
        server._init_osc_client()

        print("✅ OSC client ready")

        # Demo sequence
        print("\n🎬 Starting Demo Sequence...")

        # 1. Load avatar
        print("1. Loading avatar...")
        await server.avatar_load(vrm_path)
        await asyncio.sleep(2)

        # 2. Show bones
        print("2. Enabling bone visualization...")
        # Bones are shown by default in enhanced viewer

        # 3. Head rotation demo
        print("3. Rotating head...")
        await server.bone_control("Head", "rotation", 0.2, 0.1, 0.0, 0.95)
        await asyncio.sleep(1)

        await server.bone_control("Head", "rotation", -0.2, -0.1, 0.0, 0.95)
        await asyncio.sleep(1)

        await server.bone_control("Head", "rotation", 0.0, 0.0, 0.0, 1.0)  # Reset
        await asyncio.sleep(1)

        # 4. Arm movement
        print("4. Moving arms...")
        await server.bone_control("LeftUpperArm", "rotation", 0.5, 0.0, 0.0, 0.866)
        await asyncio.sleep(1)

        await server.bone_control("RightUpperArm", "rotation", -0.5, 0.0, 0.0, 0.866)
        await asyncio.sleep(1)

        # Reset arms
        await server.bone_control("LeftUpperArm", "rotation", 0.0, 0.0, 0.0, 1.0)
        await server.bone_control("RightUpperArm", "rotation", 0.0, 0.0, 0.0, 1.0)
        await asyncio.sleep(1)

        # 5. Leg movement
        print("5. Moving legs...")
        await server.bone_control("LeftUpperLeg", "rotation", 0.3, 0.0, 0.0, 0.954)
        await asyncio.sleep(1)

        await server.bone_control("LeftUpperLeg", "rotation", 0.0, 0.0, 0.0, 1.0)  # Reset
        await asyncio.sleep(1)

        # 6. Expression demo
        print("6. Facial expressions...")
        await server.morph_control("happy", 1.0)
        await asyncio.sleep(2)

        await server.morph_control("happy", 0.0)
        await asyncio.sleep(1)

        # 7. Animation demo
        print("7. Playing animation...")
        await server.animation_play("idle")
        await asyncio.sleep(3)

        await server.animation_stop()
        await asyncio.sleep(1)

        # 8. Export
        print("8. Exporting screenshot...")
        await server.avatar_export("demo_screenshot.png")

        print("\n✅ Demo completed!")
        print("📸 Screenshot saved as: demo_screenshot.png")
        print("🎮 Try the interactive controls in the viewer!")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
    finally:
        print("\n👋 Demo finished!")


if __name__ == "__main__":
    asyncio.run(demo_bone_control())
