#!/usr/bin/env python3
"""
Ultra Simple VRM Viewer - Minimal PyVista approach to avoid shader issues
"""

import sys

import numpy as np

sys.path.insert(0, "src")


def create_ultra_simple_viewer():
    """Create the most basic possible VRM viewer"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"

        print(f"🎌 Loading VRM (ultra simple): {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes")

        # Use the simplest possible PyVista setup
        plotter = pv.Plotter(title="🎌 Ultra Simple VRM Viewer")

        print("\n🔧 ULTRA SIMPLE RENDERING:")

        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({mesh.name}) ---")

            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.uint32)

            print(f"  Vertices: {len(vertices)}")
            print(f"  Faces: {len(faces)} shape: {faces.shape}")

            if len(vertices) == 0:
                continue

            # Use the most basic approach - let PyVista handle everything automatically
            try:
                # Just pass vertices and faces directly to PyVista
                mesh_poly = pv.PolyData(vertices, faces)

                # Add with minimal settings - no fancy lighting or shading
                plotter.add_mesh(
                    mesh_poly,
                    color=["red", "green", "blue"][i % 3],
                    style="surface",  # Explicit surface style
                    opacity=1.0,
                )

                print(f"  ✅ Added mesh {i} as surface")

            except Exception as e:
                print(f"  ❌ Error with mesh {i}: {e}")
                # If surface fails, try wireframe
                try:
                    mesh_poly = pv.PolyData(vertices, faces)
                    plotter.add_mesh(
                        mesh_poly,
                        color=["red", "green", "blue"][i % 3],
                        style="wireframe",
                        line_width=2,
                    )
                    print(f"  ⚠️ Added mesh {i} as wireframe")
                except Exception as e2:
                    print(f"  ❌ Wireframe also failed: {e2}")

        # Minimal scene setup
        plotter.show_axes()

        print("\n✅ Ultra simple viewer ready!")
        print("If you see wireframes instead of surfaces, that's expected due to OpenGL issues")
        print("The important thing is that the mesh structure is correct")

        # Show viewer
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_ultra_simple_viewer()
