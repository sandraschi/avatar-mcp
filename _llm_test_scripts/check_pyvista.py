import sys

import pyvista as pv


def check_pyvista():
    print("PyVista version:", pv.__version__)
    print("Python version:", sys.version)
    print("OpenGL version:", pv.Report().opengl_info)

    # Try to create a simple plot
    try:
        plotter = pv.Plotter(off_screen=True)
        cube = pv.Cube()
        plotter.add_mesh(cube)
        plotter.screenshot("test_cube.png")
        print("✓ Successfully created a cube and saved to test_cube.png")
        return True
    except Exception as e:
        print("✗ Error creating plot:", str(e))
        return False


if __name__ == "__main__":
    check_pyvista()
