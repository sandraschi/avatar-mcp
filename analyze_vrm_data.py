#!/usr/bin/env python3
"""
Analyze VRM Data - Print detailed analysis without trying to render
"""

import os
import sys

import numpy as np

sys.path.insert(0, "src")


def analyze_vrm_data():
    """Analyze VRM data without rendering"""

    try:
        from avatarmcp.models.vrm_loader import VRMLoader

        print("📊 ANALYZING VRM DATA")

        # Load VRM
        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"
        print(f"Loading: {vrm_path}")
        print(f"File exists: {os.path.exists(vrm_path)}")
        print(f"File size: {os.path.getsize(vrm_path):,} bytes")

        vrm_model = VRMLoader.from_file(vrm_path)

        print("\n✅ VRM LOADED")
        print(f"Meshes: {len(vrm_model.meshes)}")
        print(f"Bones: {len(vrm_model.bones)}")
        print(f"Materials: {len(vrm_model.materials)}")
        print(f"Textures: {len(vrm_model.textures)}")

        print("\n📊 DETAILED MESH ANALYSIS:")

        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n=== MESH {i}: {mesh.name} ===")

            vertices = mesh.vertices
            faces = mesh.faces

            print(f"Vertices: {len(vertices)} (shape: {vertices.shape})")
            print(f"Faces: {len(faces)} (shape: {faces.shape})")

            if len(vertices) > 0:
                print("Vertex statistics:")
                print(f"  X range: {vertices[:, 0].min():.6f} to {vertices[:, 0].max():.6f}")
                print(f"  Y range: {vertices[:, 1].min():.6f} to {vertices[:, 1].max():.6f}")
                print(f"  Z range: {vertices[:, 2].min():.6f} to {vertices[:, 2].max():.6f}")

                # Check if vertices are all zeros or similar
                x_zero = np.all(vertices[:, 0] == 0)
                y_zero = np.all(vertices[:, 1] == 0)
                z_zero = np.all(vertices[:, 2] == 0)

                print(f"  All X zero: {x_zero}")
                print(f"  All Y zero: {y_zero}")
                print(f"  All Z zero: {z_zero}")

                # Sample vertices
                print("  First 3 vertices:")
                for j in range(min(3, len(vertices))):
                    v = vertices[j]
                    print(f"    {j}: [{v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}]")

            if len(faces) > 0:
                print("Face statistics:")
                print(f"  Index range: {faces.min()} to {faces.max()}")
                print(f"  Max vertex index: {len(vertices) - 1}")

                # Check for invalid faces
                invalid_faces = np.any(faces >= len(vertices), axis=1)
                invalid_count = np.sum(invalid_faces)
                print(f"  Invalid faces: {invalid_count}/{len(faces)}")

                # Sample faces
                print("  First 3 faces:")
                for j in range(min(3, len(faces))):
                    face = faces[j]
                    print(f"    {j}: [{face[0]}, {face[1]}, {face[2]}]")

            print(f"Has normals: {mesh.normals is not None}")
            print(f"Has texcoords: {mesh.texcoords is not None}")

            # Test PyVista face conversion
            try:
                if hasattr(mesh, "get_pyvista_faces"):
                    pv_faces = mesh.get_pyvista_faces()
                    print(f"PyVista faces: {len(pv_faces)} values")
                    print(f"  Sample: {pv_faces[:12]}")
                else:
                    print("❌ No get_pyvista_faces method!")
            except Exception as e:
                print(f"❌ PyVista face conversion failed: {e}")

        print("\n🔍 CONCLUSION:")
        if len(vrm_model.meshes) == 3:
            face_mesh = vrm_model.meshes[0]
            body_mesh = vrm_model.meshes[1]
            hair_mesh = vrm_model.meshes[2]

            print(f"Face mesh has {len(face_mesh.vertices)} vertices, {len(face_mesh.faces)} faces")
            print(f"Body mesh has {len(body_mesh.vertices)} vertices, {len(body_mesh.faces)} faces")
            print(f"Hair mesh has {len(hair_mesh.vertices)} vertices, {len(hair_mesh.faces)} faces")

            # Check if data looks reasonable
            if len(face_mesh.vertices) > 1000 and len(face_mesh.faces) > 500:
                print("✅ Face mesh data looks reasonable")
            else:
                print("❌ Face mesh data looks insufficient")

            if len(body_mesh.vertices) > 5000 and len(body_mesh.faces) > 3000:
                print("✅ Body mesh data looks reasonable")
            else:
                print("❌ Body mesh data looks insufficient")

        print("\nThe VRM data analysis is complete.")
        print("If the data looks good but rendering fails, it's a PyVista/rendering issue.")

    except Exception as e:
        print(f"❌ Error analyzing VRM: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    analyze_vrm_data()
