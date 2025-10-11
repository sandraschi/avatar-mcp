#!/usr/bin/env python3
"""
Basic VRM Viewer - Use original vertices, no skinning transformations
Just focus on getting the meshes to display correctly as-is
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_basic_vrm_viewer():
    """Create the simplest possible VRM viewer that just works"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading VRM (basic viewer): {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
        
        # Setup PyVista viewer
        pv.set_plot_theme('document')
        plotter = pv.Plotter(
            window_size=[1200, 800],
            title="🎌 Basic VRM Viewer - Original T-Pose"
        )
        
        print(f"\n🎭 RENDERING MESHES IN ORIGINAL T-POSE:")
        
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        
        mesh_count = 0
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({mesh.name}) ---")
            
            # Use original vertices (no skinning transformation)
            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.uint32)
            
            print(f"  Vertices: {len(vertices)}")
            print(f"  Faces: {len(faces)}")
            
            if len(vertices) == 0:
                print(f"  ⚠️ No vertices, skipping")
                continue
                
            # Analyze mesh bounds
            min_pos = vertices.min(axis=0)
            max_pos = vertices.max(axis=0)
            center = vertices.mean(axis=0)
            
            print(f"  Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            print(f"  Bounds: ({min_pos[0]:.3f}, {min_pos[1]:.3f}, {min_pos[2]:.3f}) to ({max_pos[0]:.3f}, {max_pos[1]:.3f}, {max_pos[2]:.3f})")
            
            try:
                # Create PyVista mesh (faces are already validated by VRM loader)
                if len(faces) > 0:
                    pv_mesh = pv.PolyData(vertices, faces)
                    
                    plotter.add_mesh(
                        pv_mesh,
                        color=colors[i % len(colors)],
                        smooth_shading=True,
                        show_edges=False,
                        opacity=0.9,
                        name=f"mesh_{i}_{mesh.name.replace(' ', '_')}"
                    )
                    
                    print(f"  ✅ Rendered mesh with faces")
                    mesh_count += 1
                else:
                    # Render as point cloud if no faces
                    point_cloud = pv.PolyData(vertices)
                    plotter.add_mesh(
                        point_cloud,
                        color=colors[i % len(colors)],
                        point_size=3,
                        render_points_as_spheres=True,
                        name=f"points_{i}"
                    )
                    print(f"  ✅ Rendered as point cloud")
                    mesh_count += 1
                    
            except Exception as e:
                print(f"  ❌ Failed to render mesh {i}: {e}")
        
        if mesh_count == 0:
            print(f"\n❌ No meshes were rendered successfully!")
            # Add test object to verify viewer works
            test_sphere = pv.Sphere(radius=0.1, center=(0, 1, 0))
            plotter.add_mesh(test_sphere, color='yellow')
            print(f"Added test sphere")
        else:
            print(f"\n✅ Successfully rendered {mesh_count} meshes")
        
        # Add reference objects
        plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z')
        plotter.show_grid()
        
        # Set camera to view the character
        plotter.camera_position = [(2, 1.5, 2), (0, 1, 0), (0, 1, 0)]
        plotter.enable_trackball_style()
        
        print(f"\n🎌 Basic VRM viewer ready!")
        print(f"🎮 Features:")
        print(f"  - Original T-pose vertices (no deformation)")
        print(f"  - All mesh components should be visible") 
        print(f"  - Mouse: Rotate, pan, zoom")
        print(f"  - The torso should be visible if it exists")
        print(f"  - Press Ctrl+C to exit")
        
        # Show viewer
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_basic_vrm_viewer()


