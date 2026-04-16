"""
Test script for VRM animation functionality.

This script tests loading a VRM model and playing its animations.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from avatarmcp.server import (
    list_animations,
    list_blend_shapes,
    load_vrm,
    play_animation,
    set_blend_shape,
    stop_animation,
    unload_vrm,
)


def test_animation(vrm_path: str):
    """Test animation functionality with a VRM model."""
    print(f"\n{'=' * 80}")
    print(f"Testing VRM Animation: {vrm_path}")
    print(f"{'=' * 80}")

    # 1. Load the VRM file
    print("\n1. Loading VRM file...")
    result = load_vrm(vrm_path)

    if result.get("status") != "success":
        print(f"❌ Failed to load VRM: {result.get('error', 'Unknown error')}")
        return

    model_id = result["model_id"]
    print(f"✅ Successfully loaded VRM. Model ID: {model_id}")

    # 2. List available animations
    print("\n2. Listing available animations...")
    anims = list_animations(model_id)

    if anims.get("status") != "success":
        print(f"❌ Failed to list animations: {anims.get('error', 'Unknown error')}")
        return

    print(f"Found {anims.get('counts', {}).get('total', 0)} animations:")
    print(f"- Standard: {anims.get('counts', {}).get('standard', 0)}")
    print(f"- VRM: {anims.get('counts', {}).get('vrm', 0)}")
    print(f"- Custom: {anims.get('counts', {}).get('custom', 0)}")

    # 3. Test playing an animation if available
    if anims.get("animations"):
        # Find a VRM animation if available, otherwise use the first one
        anim_to_play = next((a for a in anims["animations"] if a.get("type") == "vrm"), None)
        if not anim_to_play:
            anim_to_play = anims["animations"][0]

        anim_name = anim_to_play["name"]
        print(f"\n3. Playing animation: {anim_name}")

        play_result = play_animation(model_id=model_id, animation_name=anim_name, loop=True, weight=1.0, speed=1.0)

        if play_result.get("status") == "success":
            print("✅ Playing animation for 3 seconds...")
            time.sleep(3)

            # 4. Stop the animation
            print("\n4. Stopping animation...")
            stop_result = stop_animation(model_id=model_id, animation_name=anim_name, fade_out=0.5)

            if stop_result.get("status") == "success":
                print("✅ Animation stopped with fade out")
            else:
                print(f"❌ Failed to stop animation: {stop_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to play animation: {play_result.get('error', 'Unknown error')}")

    # 5. Test blend shapes if available
    print("\n5. Testing blend shapes...")
    blend_shapes = list_blend_shapes(model_id)

    if blend_shapes.get("status") == "success" and blend_shapes.get("blend_shapes"):
        test_blend_shape = next(iter(blend_shapes["blend_shapes"].keys()), None)
        if test_blend_shape:
            print(f"Testing blend shape: {test_blend_shape}")

            # Animate the blend shape
            for weight in [0.0, 0.5, 1.0, 0.5, 0.0]:
                set_blend_shape(model_id, test_blend_shape, weight)
                print(f"  - Set {test_blend_shape} to {weight:.1f}")
                time.sleep(0.5)
            print("✅ Blend shape test complete")
        else:
            print("No blend shapes found to test")
    else:
        print("No blend shapes available")

    # 6. Clean up
    print("\n6. Cleaning up...")
    unload_result = unload_vrm(model_id)

    if unload_result.get("status") == "success":
        print("✅ Successfully unloaded model")
    else:
        print(f"❌ Failed to unload model: {unload_result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        vrm_path = sys.argv[1]
    else:
        # Default to the example VRM if no path is provided
        vrm_path = str(Path(__file__).parent / "Nekomimi-chan.vrm")

    test_animation(vrm_path)
