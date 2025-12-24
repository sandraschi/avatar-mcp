#!/usr/bin/env python3
"""
Real-time Animated VRM Viewer for Nekomimi-chan
Shows live animations from the AvatarMCP system
"""

import os
import sys
import time

sys.path.insert(0, "src")


def main():
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        from avatarmcp.visualization.manager import VisualizationManager

        # VRM file path
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"

        print(f"🎌 Loading Nekomimi-chan from: {vrm_path}")

        if not os.path.exists(vrm_path):
            print(f"❌ File not found: {vrm_path}")
            return

        # Load VRM using AvatarMCP loader
        print("Loading VRM model...")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ VRM loaded! {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")

        # Create visualization manager (this connects to the animation system)
        print("Starting visualization manager...")
        viz_manager = VisualizationManager()
        viz_manager.start_viewer(window_size=(1024, 768))

        # Load the VRM into the visualization system
        print("Loading VRM into visualization system...")
        success = viz_manager.load_vrm("Nekomimi-chan", vrm_path)

        if success:
            print("✅ VRM loaded into visualization system!")
            print("🎭 Nekomimi-chan should now be visible and animated!")
            print("\n🎮 Controls:")
            print("  - Mouse: Rotate, pan, zoom")
            print("  - Animations are controlled through the MCP system")
            print("  - Use Cursor to play different animations!")

            # Keep the viewer running
            print("\n⏳ Viewer is running... Press Ctrl+C to exit")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping viewer...")
        else:
            print("❌ Failed to load VRM into visualization system")

    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        try:
            if "viz_manager" in locals():
                viz_manager.stop_viewer()
        except Exception:
            pass


if __name__ == "__main__":
    main()
