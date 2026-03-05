import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.avatarmcp.visualization.animation import Animation

from src.avatarmcp.visualization.viewer import VRMViewer


def create_test_animation():
    """Create a simple test animation that moves a model up and down."""
    animation = Animation(name="bounce", duration=2.0, loop=True)

    # Add a simple up-down movement
    animation.add_position_keyframe(0.0, (0, 0, 0))
    animation.add_position_keyframe(0.5, (0, 1, 0))  # Move up
    animation.add_position_keyframe(1.0, (0, 0, 0))  # Back to start

    # Add a simple rotation
    animation.add_rotation_keyframe(0.0, (0, 0, 0))
    animation.add_rotation_keyframe(1.0, (0, 360, 0))  # Rotate 360 degrees

    return animation


async def test_animation():
    print("Starting animation test...")

    # Create a viewer
    viewer = VRMViewer(window_size=(800, 600))

    # Load a test model (replace with your VRM model path)
    test_model_path = "path/to/your/model.vrm"
    if os.path.exists(test_model_path):
        print(f"Loading model: {test_model_path}")
        viewer.load_vrm("test_model", test_model_path)
    else:
        print(f"Test model not found at {test_model_path}")
        print("Using a simple cube for testing...")
        # Create a simple test object if no model is found
        import pyvista as pv

        cube = pv.Cube()
        viewer.plotter.add_mesh(cube, name="test_cube")

    # Create and play test animation
    create_test_animation()
    print("Playing test animation...")
    viewer.play_animation(
        "test_model" if os.path.exists(test_model_path) else "test_cube", "bounce"
    )

    # Keep the viewer open for 10 seconds
    print("Animation will run for 10 seconds...")
    await asyncio.sleep(10)

    # Test speed change
    print("Speeding up animation...")
    viewer.animation_speed = 2.0
    await asyncio.sleep(5)

    # Test pausing
    print("Pausing animation...")
    viewer.is_playing = False
    await asyncio.sleep(2)

    # Test resuming
    print("Resuming animation...")
    viewer.is_playing = True
    await asyncio.sleep(5)

    # Clean up
    print("Test complete!")
    viewer.plotter.close()


if __name__ == "__main__":
    asyncio.run(test_animation())
