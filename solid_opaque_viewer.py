#!/usr/bin/env python3
"""
Solid Opaque Viewer - No transparency, solid colors
"""

import sys

sys.path.insert(0, "src")


def create_solid_viewer():
    """Create viewer with completely solid, opaque meshes"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        print("🎌 SOLID OPAQUE Viewer - No transparency!")

        # Load VRM
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"
        vrm_model = VRMLoader.from_file(vrm_path)

        # Create plotter
        plotter = pv.Plotter(title="🎌 SOLID Nekomimi-chan", window_size=[1200, 800])

        # Bright, distinct colors
        colors = ["red", "blue", "green"]  # Bright, solid colors

        for i, mesh in enumerate(vrm_model.meshes):
            print(f"Adding mesh {i}: {mesh.name}")

            # Center the mesh
            vertices = mesh.vertices.copy()
            vertices[:, 1] -= 1.3

            # Create mesh
            pv_faces = mesh.get_pyvista_faces()
            vrm_mesh = pv.PolyData(vertices, pv_faces)

            # Add with SOLID, OPAQUE settings
            plotter.add_mesh(
                vrm_mesh,
                color=colors[i % len(colors)],
                style="surface",
                opacity=1.0,  # COMPLETELY OPAQUE
                show_edges=False,
                smooth_shading=True,
                ambient=0.3,  # Add some ambient lighting
                diffuse=0.8,  # Strong diffuse lighting
                specular=0.1,  # Minimal specular
            )

            print(f"✅ {mesh.name} - SOLID {colors[i % len(colors)]}")

        # Add bright reference
        sphere = pv.Sphere(radius=0.05)
        plotter.add_mesh(sphere, color="yellow", opacity=1.0)

        # Setup scene with good lighting
        plotter.show_axes()
        plotter.add_text(
            "SOLID COLORS - NO TRANSPARENCY\nRed=Face, Blue=Body, Green=Hair, Yellow=Origin",
            position="upper_left",
            font_size=10,
        )

        # Position camera
        plotter.camera_position = [(0.5, 0.2, 0.8), (0, 0, 0), (0, 1, 0)]
        plotter.enable_trackball_style()

        # Better lighting
        plotter.enable_shadows()

        print("\n🎌 SOLID viewer ready!")
        print("Should see BRIGHT, SOLID colors:")
        print("  🔴 RED face (completely opaque)")
        print("  🔵 BLUE body (completely opaque)")
        print("  🟢 GREEN hair (completely opaque)")
        print("  🟡 YELLOW reference sphere")
        print("NO transparency - everything should be clearly visible!")

        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_solid_viewer()
