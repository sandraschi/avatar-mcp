import sys

def test_pyvista():
    print("Testing PyVista installation...")
    
    try:
        import pyvista as pv
        print(f"PyVista version: {pv.__version__}")
        
        # Try to create a simple plot
        plotter = pv.Plotter(off_screen=True)
        cube = pv.Cube()
        plotter.add_mesh(cube, color='lightblue')
        
        # Save to a file instead of showing
        output_file = "test_output.png"
        plotter.screenshot(output_file)
        print(f"Success! Check {output_file} for the test image.")
        return True
        
    except Exception as e:
        print(f"Error testing PyVista: {e}")
        return False

if __name__ == "__main__":
    success = test_pyvista()
    if not success:
        sys.exit(1)
