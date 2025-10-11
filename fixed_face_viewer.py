#!/usr/bin/env python3
"""
Fixed Face Viewer - Properly render faces as triangular surfaces, not point clouds
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_fixed_face_viewer():
    """Create VRM viewer with properly rendered triangular faces"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading VRM with fixed face rendering: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
        
        # Setup PyVista viewer
        pv.set_plot_theme('document')
        plotter = pv.Plotter(
            window_size=[1400, 900],
            title="🎌 Fixed Face VRM Viewer - Proper Triangular Surfaces"
        )
        
        print(f"\n🔧 FIXING FACE RENDERING:")
        
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({mesh.name}) ---")
            
            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.uint32)
            
            print(f"  Vertices: {len(vertices)}")
            print(f"  Original faces shape: {faces.shape}")
            
            if len(vertices) == 0:
                print(f"  ⚠️ No vertices, skipping")
                continue
            
            # Analyze and fix faces for proper PyVista rendering
            if len(faces) > 0 and faces.ndim == 2:
                print(f"  Face data type: {faces.dtype}")
                print(f"  Face min/max indices: {faces.min()} - {faces.max()}")
                
                # Ensure faces are valid triangles
                if faces.shape[1] == 3:
                    # Remove faces with invalid indices
                    valid_faces = faces[np.all(faces < len(vertices), axis=1)]
                    print(f"  Valid faces: {len(valid_faces)}/{len(faces)}")
                    
                    if len(valid_faces) > 0:
                        try:
                            # Create PyVista mesh - the key is NOT converting to the [3,v1,v2,v3] format
                            # PyVista can handle triangular faces directly
                            pv_mesh = pv.PolyData(vertices, valid_faces)
                            
                            # Verify the mesh was created correctly
                            print(f"  PyVista mesh: {pv_mesh.n_points} points, {pv_mesh.n_cells} cells")
                            
                            plotter.add_mesh(
                                pv_mesh,
                                color=colors[i % len(colors)],
                                smooth_shading=True,
                                show_edges=False,  # Don't show wireframe
                                opacity=1.0,       # Solid surfaces
                                lighting=True,     # Enable lighting
                                name=f"mesh_{i}"
                            )
                            
                            print(f"  ✅ Rendered as solid triangular surface")
                            
                        except Exception as e:
                            print(f"  ❌ PyVista surface error: {e}")
                            # Fallback to point cloud if surface fails
                            point_cloud = pv.PolyData(vertices)
                            plotter.add_mesh(
                                point_cloud,
                                color=colors[i % len(colors)],
                                point_size=2,
                                render_points_as_spheres=False,  # Use simple points, not spheres
                                name=f"points_{i}"
                            )
                            print(f"  ⚠️ Fallback to point cloud")
                    else:
                        print(f"  ❌ No valid faces found")
                else:
                    print(f"  ❌ Invalid face shape: expected Nx3, got {faces.shape}")
            else:
                print(f"  ❌ No face data or invalid format")
                
        # Add lighting and environment
        plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z')
        plotter.show_grid()
        
        # Better lighting for 3D surfaces
        plotter.enable_shadows()
        
        # Position camera to view full character
        plotter.camera_position = [(2, 1.5, 2), (0, 1, 0), (0, 1, 0)]
        plotter.enable_trackball_style()
        
        print(f"\n✅ Fixed face viewer ready!")
        print(f"🎮 Features:")
        print(f"  - Proper triangular surface rendering (no more balls!)")
        print(f"  - Solid surfaces with lighting")
        print(f"  - All clothing parts should appear as continuous surfaces")
        print(f"  - Mouse: Rotate, pan, zoom")
        print(f"  - Press Ctrl+C to exit")
        
        # Show viewer
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_fixed_face_viewer()


