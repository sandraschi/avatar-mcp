import sys
import time
import numpy as np

def test_3d_visualization():
    try:
        import pyvista as pv
        print("PyVista imported successfully!")
        
        # Create a plotter with a specific window size
        plotter = pv.Plotter(window_size=[800, 600])
        
        # Create a simple cube
        cube = pv.Cube()
        
        # Add the cube to the plotter with some styling
        plotter.add_mesh(
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
            "3D Visualization Test\nPress 'q' to quit",
            position='upper_left',
            font_size=10,
            color='black'
        )
        
        print("Opening 3D window... (this may take a moment)")
        
        # Show the plotter in a non-blocking way
        plotter.show(auto_close=False, interactive_update=True)
        
        # Simple animation loop
        print("Starting animation...")
        start_time = time.time()
        
        while True:
            # Rotate the cube
            cube.rotate_y(1, inplace=True)
            
            # Update the plotter
            plotter.update()
            plotter.render()
            
            # Process events
            if plotter.iren is not None:
                plotter.iren.process_events()
            
            # Small delay to control animation speed
            time.sleep(0.01)
            
            # Run for about 10 seconds
            if time.time() - start_time > 10:
                break
        
        print("Test complete!")
        plotter.close()
        
    except Exception as e:
        print(f"Error during 3D visualization test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_3d_visualization()
