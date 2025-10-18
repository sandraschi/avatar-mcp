#!/usr/bin/env python3
"""
Direct VRM avatar loading and display test
Shows actual VRM avatar geometry using matplotlib
"""

def test_vrm_display():
    """Load and display a VRM avatar directly."""
    print("AvatarMCP VRM Display Test")
    print("=" * 40)

    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import os

        # Add src to path
        import sys
        sys.path.insert(0, 'src')

        from avatarmcp.models.vrm_loader import VRMLoader

        print("Loading VRM loader...")

        # Find VRM files
        models_dir = os.path.join(os.getcwd(), 'models')
        if not os.path.exists(models_dir):
            print("ERROR: Models directory not found")
            return

        vrm_files = [f for f in os.listdir(models_dir) if f.endswith('.vrm')]
        if not vrm_files:
            print("ERROR: No VRM files found in models directory")
            return

        # Load the first VRM file
        vrm_path = os.path.join(models_dir, vrm_files[0])
        print(f"Loading VRM file: {vrm_path}")

        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"Loaded VRM with {len(vrm_model.meshes)} meshes")

        # Create 3D plot
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Add coordinate axes
        ax.plot([0, 0.5], [0, 0], [0, 0], color='red', linewidth=3, label='X-axis')
        ax.plot([0, 0], [0, 0.5], [0, 0], color='green', linewidth=3, label='Y-axis')
        ax.plot([0, 0], [0, 0], [0, 0.5], color='blue', linewidth=3, label='Z-axis')

        # Display meshes
        mesh_count = 0
        # Use realistic skin/clothes colors based on typical VRM avatar structure
        # Face/Skin: peach, Clothes: various colors, Hair: dark colors
        avatar_colors = {
            'face': '#FDBCB4',  # Skin tone
            'body': '#FDBCB4',  # Skin tone
            'hair': '#2C1810',  # Dark brown
            'eyes': '#4A90E2',  # Blue eyes
            'shirt': '#FF6B6B', # Red shirt
            'pants': '#4ECDC4', # Teal pants
            'shoes': '#95A5A6', # Gray shoes
            'accessories': '#F39C12' # Orange accessories
        }
        print(f"Using realistic avatar colors: {list(avatar_colors.values())}")

        # Map mesh names to appropriate colors
        def get_mesh_color(mesh_name):
            name_lower = mesh_name.lower()
            if 'face' in name_lower or 'head' in name_lower:
                return avatar_colors['face']
            elif 'hair' in name_lower:
                return avatar_colors['hair']
            elif 'eye' in name_lower:
                return avatar_colors['eyes']
            elif 'body' in name_lower or 'skin' in name_lower:
                return avatar_colors['body']
            elif any(word in name_lower for word in ['shirt', 'top', 'jacket']):
                return avatar_colors['shirt']
            elif any(word in name_lower for word in ['pants', 'skirt', 'bottom']):
                return avatar_colors['pants']
            elif any(word in name_lower for word in ['shoe', 'boot', 'foot']):
                return avatar_colors['shoes']
            else:
                # Cycle through available colors for other parts
                return list(avatar_colors.values())[mesh_count % len(avatar_colors)]

        for i, mesh in enumerate(vrm_model.meshes):
            try:
                if hasattr(mesh, 'vertices') and len(mesh.vertices) > 0:
                    vertices = mesh.vertices
                    faces = mesh.faces if hasattr(mesh, 'faces') and mesh.faces is not None else None

                    # Scale and center the vertices
                    print(f"Original mesh {i} bounds: X({vertices[:,0].min():.3f}, {vertices[:,0].max():.3f}) "
                          f"Y({vertices[:,1].min():.3f}, {vertices[:,1].max():.3f}) "
                          f"Z({vertices[:,2].min():.3f}, {vertices[:,2].max():.3f})")

                    verts = vertices * 10.0  # Scale up VRM units to make visible
                    # Don't center - let the avatar be positioned naturally
                    # verts = verts - np.mean(verts, axis=0)  # Commented out centering

                    print(f"Scaled mesh {i} bounds: X({verts[:,0].min():.3f}, {verts[:,0].max():.3f}) "
                          f"Y({verts[:,1].min():.3f}, {verts[:,1].max():.3f}) "
                          f"Z({verts[:,2].min():.3f}, {verts[:,2].max():.3f})")

                    color = get_mesh_color(mesh.name)
                    print(f"Plotting mesh {i} with color {color}, {len(verts)} points")

                    # Use larger, more visible points with full opacity
                    scatter = ax.scatter(verts[:, 0], verts[:, 1], verts[:, 2],
                                       color=color, alpha=1.0, s=15, label=f'{mesh.name}')
                    print(f"Scatter plot added for mesh {i}: {len(scatter.get_offsets())} points")

                    # If we have faces, draw wireframe triangles to show shape
                    if faces is not None and len(faces) > 0:
                        try:
                            # Draw wireframe for first 100 triangles to show structure
                            wireframe_count = 0
                            for face in faces[:min(100, len(faces))]:
                                if len(face) == 3:  # Triangular face
                                    triangle_verts = verts[face]
                                    # Close the triangle
                                    triangle_verts = np.vstack([triangle_verts, triangle_verts[0]])
                                    ax.plot(triangle_verts[:, 0], triangle_verts[:, 1], triangle_verts[:, 2],
                                          color=color, alpha=0.8, linewidth=2)
                                    wireframe_count += 1
                            print(f"Added {wireframe_count} wireframe triangles for mesh {i}")
                        except Exception as e:
                            print(f"Wireframe drawing failed for mesh {i}: {e}")

                    # Skip bounding box for now to focus on mesh visibility

                    mesh_count += 1
                    print(f"Displayed mesh {i+1} ({mesh.name}): {len(vertices)} vertices, {len(faces) if faces is not None else 0} faces")

                    # Limit to first 3 meshes for performance
                    if mesh_count >= 3:
                        break

            except Exception as e:
                print(f"Warning: Failed to display mesh {i}: {e}")

        if mesh_count > 0:
            # Set labels and title
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'VRM Avatar Display Test\n{os.path.basename(vrm_path)}\n{mesh_count} meshes displayed')

            # Set limits based on actual data bounds
            all_verts = []
            for mesh in vrm_model.meshes[:mesh_count]:
                if hasattr(mesh, 'vertices') and len(mesh.vertices) > 0:
                    scaled_verts = mesh.vertices * 10.0
                    all_verts.extend(scaled_verts)

            if all_verts:
                all_verts = np.array(all_verts)
                margin = 0.1
                x_range = all_verts[:, 0].max() - all_verts[:, 0].min()
                y_range = all_verts[:, 1].max() - all_verts[:, 1].min()
                z_range = all_verts[:, 2].max() - all_verts[:, 2].min()
                max_range = max(x_range, y_range, z_range)

                center_x = (all_verts[:, 0].max() + all_verts[:, 0].min()) / 2
                center_y = (all_verts[:, 1].max() + all_verts[:, 1].min()) / 2
                center_z = (all_verts[:, 2].max() + all_verts[:, 2].min()) / 2

                half_range = max_range / 2 + margin
                ax.set_xlim([center_x - half_range, center_x + half_range])
                ax.set_ylim([center_y - half_range, center_y + half_range])
                ax.set_zlim([center_z - half_range, center_z + half_range])

                ax.grid(True)
                ax.legend()

                print("SUCCESS: VRM avatar displayed!")
                print("You should see the 3D avatar geometry with coordinate axes")
                print("Close the window to exit")
                print("\nBone manipulation available:")
                print("- Press 'b' to toggle bone display")
                print("- Use mouse to rotate view")
                print("- Bones can be controlled via MCP tools")

                # Add interactive bone display toggle
                bone_visible = [False]  # Use list for mutable closure

                def on_key_press(event):
                    if event.key == 'b':
                        bone_visible[0] = not bone_visible[0]
                        print(f"Bone display: {'ON' if bone_visible[0] else 'OFF'}")
                        # In a full implementation, this would show/hide bones
                        # For now, just print the available bones
                        if bone_visible[0]:
                            print(f"Available bones: {list(vrm_model.bones.keys())[:10]}...")

                fig.canvas.mpl_connect('key_press_event', on_key_press)

                plt.show()
            print("ERROR: No meshes could be displayed")
            # Show fallback
            ax.set_title('VRM Loading Test - No Meshes Found\nShowing reference geometry')
            # Add reference sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = 0.3 * np.outer(np.cos(u), np.sin(v))
            y = 0.3 * np.outer(np.sin(u), np.sin(v))
            z = 0.3 * np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_surface(x, y, z, color='gray', alpha=0.5)
            plt.show()

    except ImportError as e:
        print(f"ERROR: Missing dependencies: {e}")
        print("Install required packages:")
        print("pip install matplotlib numpy")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vrm_display()
