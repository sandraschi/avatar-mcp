#!/usr/bin/env python3
"""
Quick Face Fix Viewer - Fix the PyVista face format issue
"""

import sys

import numpy as np

sys.path.insert(0, "src")


def create_quick_fix_viewer():
    """Create VRM viewer with properly formatted faces for PyVista"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"

        print(f"🎌 Loading VRM with face fix: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes")

        # Simple PyVista setup
        plotter = pv.Plotter(title="🎌 Fixed Face VRM Viewer")

        print("\n🔧 FIXING FACE FORMAT:")

        for i, mesh in enumerate(vrm_model.meshes[:1]):  # Just load first mesh for speed
            print(f"\n--- MESH {i} ({mesh.name}) ---")

            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.uint32)

            print(f"  Vertices: {len(vertices)}")
            print(f"  Original faces shape: {faces.shape}")

            if len(vertices) == 0 or len(faces) == 0:
                continue

            try:
                # THE KEY FIX: Convert faces to PyVista format
                # PyVista expects [n_points_in_cell, point1, point2, point3] for each face
                if faces.ndim == 2 and faces.shape[1] == 3:
                    # Convert triangular faces to PyVista format
                    pv_faces = []
                    for face in faces:
                        pv_faces.extend([3, face[0], face[1], face[2]])
                    pv_faces = np.array(pv_faces, dtype=np.uint32)

                    print(f"  Fixed faces shape: {pv_faces.shape}")
                    print(f"  First few face values: {pv_faces[:12]}")

                    # Create PyVista mesh with fixed faces
                    mesh_poly = pv.PolyData(vertices, pv_faces)

                    # Add with simple coloring
                    plotter.add_mesh(
                        mesh_poly,
                        color="lightblue",
                        style="surface",
                        show_edges=True,
                        edge_color="black",
                        line_width=1,
                    )

                    print("  ✅ Successfully added mesh with fixed faces!")
                    break  # Just show one mesh for now

                else:
                    print(f"  ❌ Invalid face format: {faces.shape}")

            except Exception as e:
                print(f"  ❌ Error: {e}")

        # Simple scene setup
        plotter.show_axes()
        plotter.camera_position = [(2, 1, 2), (0, 0, 0), (0, 1, 0)]

        print("\n✅ Fixed face viewer ready!")
        print("Should show the face/head mesh as a proper surface now!")

        # Show viewer
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_quick_fix_viewer()
