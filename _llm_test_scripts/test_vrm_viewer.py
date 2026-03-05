import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.avatarmcp.visualization.viewer import VRMViewer


def create_test_animation():
    """Create a simple test animation that moves a model up and down."""
    from src.avatarmcp.core.animation import AnimationBlendMode, AnimationClip, AnimationKeyframe

    # Create a simple animation clip
    animation = AnimationClip(
        name="bounce", duration=2.0, loop=True, blend_mode=AnimationBlendMode.OVERRIDE
    )

    # Create keyframes for the animation
    # Start frame - no movement
    keyframe1 = AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 0, 0))

    # Middle frame - move up slightly
    keyframe2 = AnimationKeyframe(
        time=1.0,
        bone_name="Hips",
        position=(0, 0.1, 0),  # Move up slightly
    )

    # End frame - back to start position
    keyframe3 = AnimationKeyframe(time=2.0, bone_name="Hips", position=(0, 0, 0))

    # Add keyframes to the animation
    animation.keyframes = [keyframe1, keyframe2, keyframe3]

    return animation


async def test_vrm_viewer():
    print("Starting VRM viewer test...")

    # Enable debug logging
    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__)

    # Path to the VRM model
    vrm_path = os.path.join("examples", "Nekomimi-chan.vrm")
    if not os.path.exists(vrm_path):
        print(f"Error: VRM model not found at {vrm_path}")
        return

    # Create a viewer
    print("Creating VRMViewer...")
    viewer = VRMViewer(window_size=(1024, 768))

    # Load the VRM model
    print(f"Loading VRM model: {vrm_path}")
    viewer.load_vrm("test_model", vrm_path)

    # Create and add test animation
    print("Creating animation...")
    animation = create_test_animation()

    # Set up the animation in the viewer
    if not hasattr(viewer, "animation_controller"):
        from src.avatarmcp.core.animation import AnimationController

        print("Initializing animation controller...")
        viewer.animation_controller = AnimationController()

    # Add a default layer if none exists
    if not viewer.animation_controller.layers:
        print("Adding default animation layer...")
        viewer.animation_controller.add_layer("Base")

    # Add the animation to the controller
    print("Adding animation to controller...")
    viewer.animation_controller._animation_clips["bounce"] = animation

    # Set up the camera to focus on the model
    viewer.plotter.camera_position = "xy"
    viewer.plotter.camera.azimuth = 30
    viewer.plotter.camera.elevation = 30
    viewer.plotter.camera.zoom(0.8)

    # Play the animation
    print("Playing animation...")

    # Print debug info about the animation
    print(f"Available animations: {list(viewer.animation_controller._animation_clips.keys())}")
    print(f"Available layers: {list(viewer.animation_controller.layers.keys())}")

    # Play the animation
    success = viewer.animation_controller.play_animation("Base", "bounce")
    print(f"Animation play success: {success}")

    # Set up the animation callback
    def update_callback():
        viewer.animation_controller.update()
        return

    # Add the callback to the plotter
    viewer.plotter.add_observer("timer", lambda *args: update_callback())
    viewer.plotter.add_timer_event(33, update_callback)  # ~30 FPS

    # Show the window in non-blocking mode
    print("Showing window...")
    viewer.plotter.show(
        title="VRM Viewer", auto_close=False, interactive=True, interactive_update=True
    )

    # Keep the viewer open for a while
    print("Window should be visible now. Close the window to exit.")

    # Wait for the window to close
    try:
        while viewer.plotter.iren._active:
            await asyncio.sleep(0.1)
    except (AttributeError, KeyboardInterrupt):
        pass

    print("Window closed.")
    viewer._animation_running = False

    # Clean up
    print("Test complete!")
    viewer.plotter.close()


if __name__ == "__main__":
    asyncio.run(test_vrm_viewer())
