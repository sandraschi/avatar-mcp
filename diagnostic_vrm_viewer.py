#!/usr/bin/env python3
"""
Diagnostic VRM Viewer - Analyze mesh structure and rendering issues
"""

import os
import sys

sys.path.insert(0, "src")


def main():
    try:
        import numpy as np
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
        print(f"✅ VRM loaded! {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")

        # Analyze each mesh in detail
        print("\n🔍 MESH ANALYSIS:")
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ---")
            if hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
                vertices = np.array(mesh.vertices, dtype=np.float32)
                faces = np.array(mesh.faces, dtype=np.int32)

                print(f"  Vertices: {len(vertices)}")
                print(f"  Faces: {len(faces)}")
                print(f"  Vertex range X: {vertices[:, 0].min():.3f} to {vertices[:, 0].max():.3f}")
                print(f"  Vertex range Y: {vertices[:, 1].min():.3f} to {vertices[:, 1].max():.3f}")
                print(f"  Vertex range Z: {vertices[:, 2].min():.3f} to {vertices[:, 2].max():.3f}")

                # Calculate center and size
                center = vertices.mean(axis=0)
                size = vertices.max(axis=0) - vertices.min(axis=0)
                print(f"  Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
                print(f"  Size: ({size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f})")

                # Check face structure
                if len(faces) > 0:
                    print(f"  Face shape: {faces.shape}")
                    if faces.shape[1] == 3:
                        print("  ✅ Triangular faces (good)")
                    else:
                        print(f"  ⚠️ Non-triangular faces: {faces.shape[1]} vertices per face")

                # Check for degenerate faces
                if len(faces) > 0 and faces.shape[1] == 3:
                    valid_faces = 0
                    for face in faces[:100]:  # Check first 100 faces
                        if face[0] != face[1] and face[1] != face[2] and face[0] != face[2]:
                            valid_faces += 1
                    print(f"  Valid faces (sample): {valid_faces}/100")
            else:
                print("  ❌ Missing vertices or faces")

        # Create PyVista plotter with better settings
        print("\n🖥️ Creating diagnostic viewer...")
        pv.set_plot_theme("document")

        plotter = pv.Plotter(window_size=[1400, 1000], title="🔍 Nekomimi-chan Diagnostic Viewer")

        # Colors for each mesh - make them very distinct
        mesh_colors = ["red", "blue", "green"]
        mesh_names = ["Body/Torso", "Clothing/Accessories", "Hair"]

        # Process each mesh with detailed diagnostics
        mesh_count = 0
        for i, mesh in enumerate(vrm_model.meshes):
            try:
                if hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
                    vertices = np.array(mesh.vertices, dtype=np.float32)
                    faces = np.array(mesh.faces, dtype=np.int32)

                    if len(vertices) > 0 and len(faces) > 0 and faces.shape[1] == 3:
                        # Convert to PyVista format
                        pv_faces = []
                        valid_face_count = 0
                        for face in faces:
                            # Check for valid face indices
                            if (
                                face[0] < len(vertices)
                                and face[1] < len(vertices)
                                and face[2] < len(vertices)
                                and face[0] != face[1]
                                and face[1] != face[2]
                                and face[0] != face[2]
                            ):
                                pv_faces.extend([3, face[0], face[1], face[2]])
                                valid_face_count += 1

                        if len(pv_faces) > 0:
                            # Create mesh
                            pv_mesh = pv.PolyData(vertices, pv_faces)

                            # Add with distinct color and transparency
                            color = mesh_colors[i % len(mesh_colors)]
                            opacity = 0.8 if i == 0 else 0.9  # Make body slightly transparent

                            plotter.add_mesh(
                                pv_mesh,
                                color=color,
                                opacity=opacity,
                                show_edges=False,
                                smooth_shading=True,
                                name=f"mesh_{i}_{mesh_names[i % len(mesh_names)]}",
                            )
                            mesh_count += 1
                            print(
                                f"  ✅ Rendered mesh {i} ({mesh_names[i % len(mesh_names)]}): {valid_face_count}/{len(faces)} faces"
                            )
                        else:
                            print(f"  ❌ Mesh {i}: No valid faces after filtering")
                    else:
                        print(f"  ⚠️ Mesh {i}: Skipped (empty or invalid)")

            except Exception as e:
                print(f"  ❌ Error processing mesh {i}: {e}")

        if mesh_count == 0:
            print("❌ No meshes could be rendered!")
            sphere = pv.Sphere(radius=1.0)
            plotter.add_mesh(sphere, color="red", label="ERROR: No meshes")
        else:
            print(f"\n✅ Successfully rendered {mesh_count}/3 meshes")

        # Add coordinate system and grid
        plotter.add_axes(xlabel="X", ylabel="Y", zlabel="Z", line_width=3)
        plotter.show_grid(color="lightgray")

        # Set camera to get good view of full body
        plotter.camera_position = [
            (2, 2, 2),  # Camera position
            (0, 1, 0),  # Look at average body height
            (0, 0, 1),  # Up vector
        ]

        # Enable better interaction
        plotter.enable_trackball_style()

        print("\n🚀 Opening diagnostic viewer...")
        print("🎮 Controls:")
        print("  - Left drag: Rotate")
        print("  - Right drag: Pan")
        print("  - Scroll: Zoom")
        print("  - 'r': Reset view")
        print("  - 'q': Quit")
        print("\n🔍 LOOK FOR:")
        print("  - RED: Body/Torso (should be main body)")
        print("  - BLUE: Clothing/Accessories")
        print("  - GREEN: Hair")
        print("  - Check if parts are positioned correctly")

        # Show the viewer
        plotter.show()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
