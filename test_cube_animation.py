import sys
import os
import time
import asyncio
import numpy as np
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import pyvista as pv
from src.avatarmcp.visualization.viewer import VRMViewer

class SimpleAnimation:
    def __init__(self, duration=2.0, loop=True):
        self.duration = duration
        self.loop = loop
        self.time = 0.0
        
    def update(self, delta_time):
        self.time += delta_time
        if self.loop:
            self.time %= self.duration
        
    def get_transform(self):
        # Simple up-down movement
        y_pos = np.sin((self.time / self.duration) * 2 * np.pi) * 0.5
        # Rotation around Y axis
        angle = (self.time / self.duration) * 360
        return [0, y_pos, 0], [0, angle, 0]

async def test_cube_animation():
    print("Starting cube animation test...")
    
    # Create a viewer
    viewer = VRMViewer(window_size=(800, 600))
    
    # Create a simple cube
    cube = pv.Cube()
    viewer.plotter.add_mesh(cube, name="test_cube")
    viewer.plotter.camera_position = 'xy'
    viewer.plotter.show_axes()
    
    # Create and play test animation
    animation = SimpleAnimation(duration=3.0, loop=True)
    viewer.active_animations["test_cube"] = animation
    viewer.is_playing = True
    
    print("Playing animation for 10 seconds...")
    print("You should see a cube bouncing up and down while rotating.")
    
    start_time = time.time()
    while time.time() - start_time < 10:  # Run for 10 seconds
        if viewer.is_playing and viewer.active_animations:
            # Update animations
            for anim in viewer.active_animations.values():
                anim.update(0.016)  # ~60 FPS
                pos, rot = anim.get_transform()
                # Apply transform to the cube
                viewer.plotter.add_mesh(
                    cube, name="test_cube",
                    reset_camera=False,
                    show_edges=True,
                    color="lightblue",
                    position=pos,
                    rotation=rot
                )
            
            # Update the viewer
            viewer.update()
        
        await asyncio.sleep(1/60)  # ~60 FPS
    
    print("Test complete!")
    viewer.plotter.close()

if __name__ == "__main__":
    asyncio.run(test_cube_animation())
