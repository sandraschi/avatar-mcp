#!/usr/bin/env python3
"""
Simple VRM Viewer for Nekomimi-chan
Uses PyVista for 3D visualization
"""

import os
import sys

sys.path.insert(0, "src")


def main():
    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        # VRM file path
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"

        print(f"🎌 Loading Nekomimi-chan from: {vrm_path}")

        if not os.path.exists(vrm_path):
            print(f"❌ File not found: {vrm_path}")
            return

        # Load VRM using AvatarMCP loader
        print("Loading VRM model...")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ VRM loaded! Model type: {type(vrm_model)}")

        # Create PyVista plotter
        print("Creating 3D viewer...")
        pv.set_plot_theme("document")
        plotter = pv.Plotter(window_size=[1024, 768], title="Nekomimi-chan VRM Viewer")

        # Add coordinate system
        plotter.add_axes(xlabel="X", ylabel="Y", zlabel="Z")
        plotter.show_grid()

        # Try to extract and display meshes
        mesh_added = False
        if hasattr(vrm_model, "meshes") and vrm_model.meshes:
            print(f"Found {len(vrm_model.meshes)} meshes")
            for i, mesh in enumerate(vrm_model.meshes):
                try:
                    if hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
                        if len(mesh.vertices) > 0 and len(mesh.faces) > 0:
                            # Convert to PyVista format
                            vertices = mesh.vertices
                            faces = mesh.faces

                            # Create PyVista mesh
                            if len(faces.shape) == 2 and faces.shape[1] == 3:
                                # Triangular faces
                                pv_faces = []
                                for face in faces:
                                    pv_faces.extend([3] + list(face))
                                pv_mesh = pv.PolyData(vertices, pv_faces)
                            else:
                                # Try as points if faces don't work
                                pv_mesh = pv.PolyData(vertices)

                            # Add to plotter
                            color = ["lightpink", "lightblue", "lightgreen", "lightyellow"][i % 4]
                            plotter.add_mesh(pv_mesh, color=color, opacity=0.8)
                            mesh_added = True
                            print(f"  ✅ Added mesh {i}: {len(vertices)} vertices")

                except Exception as e:
                    print(f"  ❌ Error with mesh {i}: {e}")

        # If no meshes added, show a placeholder
        if not mesh_added:
            print("No valid meshes found, showing placeholder...")
            sphere = pv.Sphere(radius=1.0)
            plotter.add_mesh(sphere, color="lightcoral", label="Placeholder - VRM loading issue")

        # Set camera
        plotter.camera_position = "iso"
        plotter.camera.zoom(1.2)

        print("🚀 Opening 3D viewer window...")
        print("Use mouse to rotate, zoom, and pan the view!")

        # Show the viewer (this should open the GUI window)
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
