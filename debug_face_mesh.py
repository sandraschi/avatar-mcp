#!/usr/bin/env python3
"""
Debug Face Mesh - Figure out why the face doesn't look like a face
"""

import sys

sys.path.insert(0, "src")


def debug_face_mesh():
    """Debug why the face mesh doesn't look right"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        print("🔍 DEBUGGING FACE MESH APPEARANCE")

        # Load VRM
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"
        vrm_model = VRMLoader.from_file(vrm_path)

        # Get face mesh
        face_mesh = vrm_model.meshes[0]
        print(f"Face mesh: {face_mesh.name}")
        print(f"Vertices: {len(face_mesh.vertices)}")
        print(f"Faces: {len(face_mesh.faces)}")
        print(f"Has normals: {face_mesh.normals is not None}")

        # Check face data
        print("\nFace data analysis:")
        faces = face_mesh.faces
        print(f"Face shape: {faces.shape}")
        print(f"Face indices range: {faces.min()} to {faces.max()}")
        print(f"Max vertex index: {len(face_mesh.vertices) - 1}")

        # Check for face orientation issues
        print("Sample faces:")
        for i in range(min(5, len(faces))):
            face = faces[i]
            print(
                f"  Face {i}: {face} -> vertices {face_mesh.vertices[face[0]]}, {face_mesh.vertices[face[1]]}, {face_mesh.vertices[face[2]]}"
            )

        # Create plotter
        plotter = pv.Plotter(title="🔍 Face Mesh Debug", window_size=[1400, 800])

        # Center the vertices
        vertices = face_mesh.vertices.copy()
        vertices[:, 1] -= 1.3  # Center vertically

        # Create PyVista mesh
        pv_faces = face_mesh.get_pyvista_faces()
        vrm_mesh = pv.PolyData(vertices, pv_faces)

        # Add reference sphere
        sphere = pv.Sphere(radius=0.05)
        plotter.add_mesh(sphere, color="red", opacity=0.8, name="origin")

        print("\n🔍 TRYING DIFFERENT RENDERING MODES:")

        # Try 1: Basic surface
        try:
            plotter.add_mesh(
                vrm_mesh,
                color="lightblue",
                style="surface",
                name="surface_mode",
                opacity=0.7,
                show_edges=False,
            )
            print("✅ Surface mode added")
        except Exception as e:
            print(f"❌ Surface mode failed: {e}")

        # Try 2: Wireframe to see structure
        try:
            wireframe_mesh = vrm_mesh.copy()
            plotter.add_mesh(
                wireframe_mesh,
                color="black",
                style="wireframe",
                line_width=2,
                name="wireframe_mode",
            )
            print("✅ Wireframe mode added")
        except Exception as e:
            print(f"❌ Wireframe mode failed: {e}")

        # Try 3: Points to see vertex distribution
        try:
            points_mesh = pv.PolyData(vertices)
            plotter.add_mesh(
                points_mesh,
                color="yellow",
                style="points",
                point_size=3,
                name="points_mode",
                render_points_as_spheres=True,
            )
            print("✅ Points mode added")
        except Exception as e:
            print(f"❌ Points mode failed: {e}")

        # Setup scene
        plotter.show_axes()
        plotter.add_text(
            "Red = origin\nBlue = surface\nBlack = wireframe\nYellow = vertices",
            position="upper_left",
        )

        # Multiple camera angles
        plotter.camera_position = [(0.3, 0.2, 0.3), (0, 0, 0), (0, 1, 0)]

        print("\n🔍 Debug viewer ready!")
        print("You should see:")
        print("  - Red sphere at origin")
        print("  - Blue surface (the 'something')")
        print("  - Black wireframe overlay")
        print("  - Yellow points showing vertex positions")
        print("This will help us understand what's wrong with the face")

        # Show
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_face_mesh()
