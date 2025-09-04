"""
A simple test script to verify 3D visualization with PyVista.
This creates a rotating cube to test if 3D rendering works.
"""
import sys
import time
import numpy as np
import pyvista as pv

def main():
    print("Starting 3D visualization test...")
    
    # Create a plotter
    plotter = pv.Plotter(window_size=(800, 600))
    plotter.background_color = 'white'
    
    # Create a simple cube
    cube = pv.Cube()
    
    # Add the cube to the plotter
    actor = plotter.add_mesh(
        cube,
        color='lightblue',
        show_edges=True,
        edge_color='black',
        lighting=True,
        smooth_shading=True
    )
    
    # Set a nice camera position
    plotter.camera_position = 'xy'
    plotter.show_axes()
    
    # Add some text
    plotter.add_text(
        "3D Visualization Test\nYou should see a rotating cube",
        position='upper_left',
        font_size=10,
        color='black'
    )
    
    print("Opening 3D window...")
    
    # Open the plotter in interactive mode
    plotter.show(
        title="3D Visualization Test",
        interactive=True,
        interactive_update=True,
        auto_close=False
    )
    
    # Animation loop
    print("Starting animation (press 'q' to quit)...")
    
    angle = 0
    while plotter.ren_win and plotter.iren._active:
        # Rotate the cube
        cube.rotate_y(1, inplace=True)
        actor.user_matrix = cube.user_matrix
        
        # Update the plotter
        plotter.update()
        plotter.render()
        
        # Small delay to control animation speed
        time.sleep(0.01)
        
        # Process events
        if plotter.iren is not None:
            plotter.iren.process_events()
    
    print("Test complete!")
    plotter.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise
