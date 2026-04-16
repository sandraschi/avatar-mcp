#!/usr/bin/env python3
"""
Debug PyVista VRM - Test PyVista with VRM data step by step
"""

import sys

sys.path.insert(0, "src")


def debug_pyvista_vrm():
    """Debug PyVista VRM rendering step by step"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        print("🔍 STEP 1: Test basic PyVista")

        # First, confirm PyVista works with a sphere
        sphere = pv.Sphere()
        print(f"✅ Sphere created: {sphere.n_points} points, {sphere.n_cells} cells")

        # Create plotter
        plotter = pv.Plotter(title="🔍 PyVista VRM Debug")

        # Add sphere as reference
        plotter.add_mesh(sphere, color="green", opacity=0.3, name="reference_sphere")
        print("✅ Reference sphere added")

        print("\n🔍 STEP 2: Load VRM data")
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ VRM loaded: {len(vrm_model.meshes)} meshes")

        print("\n🔍 STEP 3: Test one VRM mesh")

        # Get just the face mesh (smallest one)
        face_mesh = vrm_model.meshes[0]
        print(f"Testing mesh: {face_mesh.name}")
        print(f"Vertices: {len(face_mesh.vertices)}")
        print(f"Faces: {len(face_mesh.faces)}")

        # Check vertex bounds
        vertices = face_mesh.vertices
        print("Vertex bounds:")
        print(f"  X: {vertices[:, 0].min():.3f} to {vertices[:, 0].max():.3f}")
        print(f"  Y: {vertices[:, 1].min():.3f} to {vertices[:, 1].max():.3f}")
        print(f"  Z: {vertices[:, 2].min():.3f} to {vertices[:, 2].max():.3f}")

        print("\n🔍 STEP 4: Create PyVista mesh from VRM data")

        # Use our new PyVista face format
        pv_faces = face_mesh.get_pyvista_faces()
        print(f"PyVista faces: {len(pv_faces)} values")
        print(f"First 12 values: {pv_faces[:12]}")

        # Create the mesh
        try:
            vrm_pv_mesh = pv.PolyData(vertices, pv_faces)
            print(f"✅ PyVista mesh created: {vrm_pv_mesh.n_points} points, {vrm_pv_mesh.n_cells} cells")

            # Check if mesh is valid
            print(f"Mesh bounds: {vrm_pv_mesh.bounds}")
            print(f"Mesh center: {vrm_pv_mesh.center}")

            # Add to plotter
            plotter.add_mesh(
                vrm_pv_mesh,
                color="lightblue",
                style="surface",
                name="vrm_face",
                show_edges=True,
                edge_color="black",
                line_width=1,
            )
            print("✅ VRM mesh added to plotter")

        except Exception as e:
            print(f"❌ Error creating PyVista mesh: {e}")
            import traceback

            traceback.print_exc()
            return

        print("\n🔍 STEP 5: Setup scene and show")

        # Setup scene
        plotter.show_axes()
        plotter.add_text("Green sphere = PyVista test\nBlue mesh = VRM face", position="upper_left")

        # Position camera to see both
        plotter.camera_position = [(3, 2, 3), (0, 0, 0), (0, 1, 0)]

        print("✅ Debug viewer ready!")
        print("You should see:")
        print("  - Green transparent sphere (PyVista test)")
        print("  - Blue face mesh with wireframe (VRM data)")
        print("If you only see the sphere, there's an issue with VRM->PyVista conversion")

        # Show
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_pyvista_vrm()
