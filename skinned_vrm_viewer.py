#!/usr/bin/env python3
"""
Skinned VRM Viewer - Apply bone transformations to fix missing torso
"""

import os
import sys

import numpy as np

sys.path.insert(0, "src")


def apply_skinning_to_mesh(mesh, bones, bone_indices_map=None):
    """
    Apply bone transformations to mesh vertices using joint weights

    Args:
        mesh: VRMMesh with vertices and skinning attributes
        bones: Dictionary of VRMBone objects
        bone_indices_map: Optional mapping from joint indices to bone names

    Returns:
        Transformed vertices
    """
    vertices = np.array(mesh.vertices, dtype=np.float32)

    # Check if mesh has skinning data
    if not (
        hasattr(mesh, "attributes")
        and "joint_indices" in mesh.attributes
        and "joint_weights" in mesh.attributes
    ):
        print(f"  ⚠️ Mesh {mesh.name} has no skinning data, using original vertices")
        return vertices

    joint_indices = mesh.attributes["joint_indices"]
    joint_weights = mesh.attributes["joint_weights"]

    print(f"  🦴 Applying skinning to {len(vertices)} vertices...")
    print(f"    Joint indices shape: {joint_indices.shape}")
    print(f"    Joint weights shape: {joint_weights.shape}")

    # Create bone index to bone name mapping if not provided
    if bone_indices_map is None:
        bone_names = list(bones.keys())
        bone_indices_map = {
            i: bone_names[i] if i < len(bone_names) else None
            for i in range(max(joint_indices.flatten()) + 1)
        }

    # Initialize transformed vertices
    skinned_vertices = np.zeros_like(vertices)

    # Apply weighted bone transformations
    for vertex_idx in range(len(vertices)):
        vertex = vertices[vertex_idx]
        vertex_homogeneous = np.append(vertex, 1.0)  # [x, y, z, 1]

        # Get bone influences for this vertex
        bone_indices_for_vertex = joint_indices[vertex_idx]
        bone_weights_for_vertex = joint_weights[vertex_idx]

        # Accumulate weighted transformations
        final_vertex = np.zeros(3, dtype=np.float32)
        total_weight = 0.0

        for i in range(len(bone_indices_for_vertex)):
            bone_idx = bone_indices_for_vertex[i]
            weight = bone_weights_for_vertex[i]

            if weight < 0.001:  # Skip negligible weights
                continue

            # Get bone transformation
            bone_name = bone_indices_map.get(bone_idx)
            if bone_name and bone_name in bones:
                bone = bones[bone_name]

                # Create transformation matrix from bone
                # For now, just use position offset (simple transform)
                bone_transform = np.eye(4)
                bone_transform[:3, 3] = bone.position

                # Apply transformation
                transformed_vertex = bone_transform @ vertex_homogeneous
                final_vertex += weight * transformed_vertex[:3]
                total_weight += weight
            else:
                # If bone not found, use original position
                final_vertex += weight * vertex
                total_weight += weight

        # Normalize by total weight (should be ~1.0 for well-formed data)
        if total_weight > 0.001:
            skinned_vertices[vertex_idx] = final_vertex / total_weight
        else:
            skinned_vertices[vertex_idx] = vertex

    print("  ✅ Skinning applied successfully")
    return skinned_vertices


def create_skinned_vrm_viewer():
    """Create VRM viewer with proper skinning applied"""

    try:
        import pyvista as pv

        from avatarmcp.models.vrm_loader import VRMLoader

        vrm_path = r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm"

        if not os.path.exists(vrm_path):
            print(f"❌ VRM file not found: {vrm_path}")
            return

        print(f"🎌 Loading VRM with skinning transformations: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")

        # Setup PyVista viewer
        pv.set_plot_theme("document")
        plotter = pv.Plotter(
            window_size=[1400, 900], title="🎌 Skinned VRM Viewer - With Bone Transformations"
        )

        print("\n🦴 APPLYING SKINNING TRANSFORMATIONS:")

        colors = ["lightsalmon", "lightblue", "darkseagreen"]

        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({mesh.name}) ---")

            # Apply skinning transformations
            skinned_vertices = apply_skinning_to_mesh(mesh, vrm_model.bones)

            # Get faces and validate them (apply same validation as VRM loader)
            faces = np.array(mesh.faces, dtype=np.uint32)

            # Validate faces to prevent PyVista errors
            if faces.size > 0:
                max_index = faces.max()
                if max_index >= len(skinned_vertices):
                    print(
                        f"    ⚠️ Invalid face indices: max {max_index} >= vertex count {len(skinned_vertices)}"
                    )
                    # Remove faces with invalid indices
                    valid_mask = np.all(faces < len(skinned_vertices), axis=1)
                    faces = faces[valid_mask]
                    print(f"    ⚠️ Kept {len(faces)} valid faces")

                # Convert to PyVista format
                if len(faces) > 0:
                    pv_faces = []
                    for face in faces:
                        pv_faces.extend([3, face[0], face[1], face[2]])
                    pv_faces = np.array(pv_faces, dtype=np.uint32)
                else:
                    pv_faces = np.array([], dtype=np.uint32)
            else:
                pv_faces = np.array([], dtype=np.uint32)

            if len(skinned_vertices) > 0 and len(pv_faces) > 0:
                try:
                    # Create PyVista mesh with skinned vertices and validated faces
                    pv_mesh = pv.PolyData(skinned_vertices, pv_faces)

                    plotter.add_mesh(
                        pv_mesh,
                        color=colors[i % len(colors)],
                        smooth_shading=True,
                        show_edges=False,
                        name=f"skinned_mesh_{i}",
                    )

                    print(f"  ✅ Rendered skinned mesh {i}: {len(skinned_vertices)} vertices")

                    # Show vertex displacement
                    original_vertices = np.array(mesh.vertices, dtype=np.float32)
                    displacement = np.linalg.norm(skinned_vertices - original_vertices, axis=1)
                    avg_displacement = displacement.mean()
                    max_displacement = displacement.max()
                    print(
                        f"  📊 Vertex displacement: avg={avg_displacement:.4f}, max={max_displacement:.4f}"
                    )

                except Exception as e:
                    print(f"  ❌ Error rendering skinned mesh {i}: {e}")
            else:
                print(f"  ⚠️ Mesh {i} has no valid geometry")

        # Add coordinate system and lighting
        plotter.add_axes(xlabel="X", ylabel="Y", zlabel="Z")
        plotter.show_grid()

        # Set camera for full body view
        plotter.camera_position = [(3, 2, 3), (0, 1, 0), (0, 0, 1)]
        plotter.enable_trackball_style()

        print("\n✅ Skinned VRM viewer setup complete!")
        print("🎮 Controls:")
        print("  - Mouse: Rotate, pan, zoom")
        print("  - Bone transformations applied to fix missing torso")
        print("  - Press Ctrl+C to exit")

        # Show viewer
        plotter.show()

    except Exception as e:
        print(f"❌ Error in skinned viewer: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_skinned_vrm_viewer()
