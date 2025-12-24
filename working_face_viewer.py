#!/usr/bin/env python3
"""
Working Face Viewer - Back to what was actually working before
"""

import sys

sys.path.insert(0, "src")


def create_working_viewer():
    """Go back to what was working - face + clothing, just fix surface rendering"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        print("🎌 Back to working viewer - Face + Clothing")

        # Load VRM
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"
        vrm_model = VRMLoader.from_file(vrm_path)

        # Create plotter
        plotter = pv.Plotter(title="🎌 Working Nekomimi-chan", window_size=[1200, 800])

        # Render all 3 meshes like we did when it was working
        colors = ["lightcoral", "lightblue", "lightgreen"]  # Face, Body, Hair

        for i, mesh in enumerate(vrm_model.meshes):
            print(f"Adding mesh {i}: {mesh.name}")

            # Use original vertices with minimal adjustment
            vertices = mesh.vertices.copy()
            vertices[:, 1] -= 1.3  # Same adjustment that worked before

            # Use the PyVista face format that worked
            pv_faces = mesh.get_pyvista_faces()
            vrm_mesh = pv.PolyData(vertices, pv_faces)

            # Add mesh with the settings that showed faces before
            plotter.add_mesh(
                vrm_mesh,
                color=colors[i % len(colors)],
                style="surface",  # This should show solid surfaces, not balls
                opacity=0.9,
                smooth_shading=True,
                show_edges=False,
            )

            print(f"✅ Added {mesh.name}")

        # Camera and scene setup
        plotter.show_axes()
        plotter.camera_position = [(0.5, 0.2, 0.8), (0, 0, 0), (0, 1, 0)]
        plotter.enable_trackball_style()

        print("🎌 Ready! You should see:")
        print("  - Face (light coral)")
        print("  - Body/Clothing (light blue)")
        print("  - Hair (light green)")
        print("  - NO little balls - solid surfaces!")

        # Show
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_working_viewer()
