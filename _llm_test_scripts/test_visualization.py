"""
Test script for AvatarMCP visualization tools.

This script demonstrates how to use the MCP visualization tools to:
1. Load a VRM model
2. Show it in a 3D viewer
3. Play animations
4. Control the camera and model transforms
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_visualization():
    """Test the visualization tools using MCP protocol."""
    from avatarmcp.core.app import AvatarMCP

    # Initialize AvatarMCP with visualization enabled
    app = AvatarMCP(enable_visualization=True)
    await app.start()

    try:
        # Example: Load a VRM model
        vrm_path = input("Enter path to VRM file: ").strip('"')
        if not Path(vrm_path).exists():
            print(f"Error: File not found: {vrm_path}")
            return

        # Load the model
        print(f"Loading VRM: {vrm_path}")
        load_result = await app.mcp.handle_message(
            {"jsonrpc": "2.0", "method": "load_vrm", "params": {"file_path": vrm_path}, "id": 1}
        )

        if load_result.get("error"):
            print(f"Failed to load VRM: {load_result.get('error')}")
            return

        model_id = load_result["result"].get("model_id")
        print(f"Model loaded with ID: {model_id}")

        # Show the model in 3D viewer
        print("Opening 3D viewer...")
        show_result = await app.mcp.handle_message(
            {
                "jsonrpc": "2.0",
                "method": "visualization.show",
                "params": {"model_id": model_id, "window_size": [1280, 720]},
                "id": 2,
            }
        )

        if show_result.get("error"):
            print(f"Failed to show model: {show_result.get('error')}")
            return

        # List available animations
        animations_result = await app.mcp.handle_message(
            {
                "jsonrpc": "2.0",
                "method": "list_animations",
                "params": {"model_id": model_id},
                "id": 3,
            }
        )

        if animations_result.get("result"):
            animations = animations_result["result"].get("animations", {})
            print("\nAvailable animations:")
            for anim_type, anim_list in animations.items():
                print(f"\n{anim_type.upper()}:")
                for anim in anim_list:
                    print(f"- {anim['name']} (Duration: {anim.get('duration', 'N/A')}s)")

            # Play the first animation if available
            if animations.get("standard_animations"):
                anim_name = animations["standard_animations"][0]["name"]
                print(f"\nPlaying animation: {anim_name}")
                await app.mcp.handle_message(
                    {
                        "jsonrpc": "2.0",
                        "method": "visualization.animate",
                        "params": {
                            "model_id": model_id,
                            "animation_name": anim_name,
                            "loop": True,
                            "speed": 1.0,
                        },
                        "id": 4,
                    }
                )

        # Keep the viewer open
        print("\n3D viewer is running. Press Ctrl+C to exit...")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(test_visualization())
