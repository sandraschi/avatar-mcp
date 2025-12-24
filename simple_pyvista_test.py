import pyvista as pv


def main():
    # Create a plotter
    plotter = pv.Plotter()

    # Create a simple cube
    cube = pv.Cube()

    # Add the cube to the plotter
    plotter.add_mesh(cube, color="lightblue", show_edges=True)

    # Set a nice camera position
    plotter.camera_position = "xy"
    plotter.show_axes()

    # Define a simple animation callback
    def update_cube():
        nonlocal cube
        # Rotate the cube
        cube.rotate_y(2, inplace=True)
        # Update the actor
        plotter.add_mesh(cube, name="cube", color="lightblue", show_edges=True)

    # Add the callback to the plotter
    plotter.add_callback(update_cube, interval=50)  # Update every 50ms

    # Show the plotter
    plotter.show(title="Simple PyVista Test")


if __name__ == "__main__":
    main()
