#!/usr/bin/env python3
"""
Simple Working VRM Viewer - No animation, just proper display
Focus on getting a clean, interactive 3D view first
"""
import sys
import os
sys.path.insert(0, 'src')

def main():
    try:
        import pyvista as pv
        from avatarmcp.models.vrm_loader import VRMLoader
        import numpy as np
        
        # VRM file path
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading Nekomimi-chan from: {vrm_path}")
        
        if not os.path.exists(vrm_path):
            print(f"❌ File not found: {vrm_path}")
            return
        
        # Load VRM using AvatarMCP loader
        print("Loading VRM model...")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ VRM loaded! {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
        
        # Create PyVista plotter with better settings
        print("Creating 3D viewer...")
        pv.set_plot_theme('document')
        
        plotter = pv.Plotter(
            window_size=[1200, 900],
            title="🎌 Nekomimi-chan VRM Viewer (Static)"
        )
        
        # Process each mesh more carefully
        mesh_count = 0
        for i, mesh in enumerate(vrm_model.meshes):
            try:
                if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                    vertices = np.array(mesh.vertices, dtype=np.float32)
                    faces = np.array(mesh.faces, dtype=np.int32)
                    
                    print(f"Mesh {i}: {len(vertices)} vertices, {len(faces)} faces")
                    
                    if len(vertices) > 0 and len(faces) > 0:
                        # Ensure faces are triangular
                        if faces.shape[1] == 3:
                            # Convert to PyVista format: [3, v1, v2, v3, 3, v4, v5, v6, ...]
                            pv_faces = []
                            for face in faces:
                                pv_faces.extend([3, face[0], face[1], face[2]])
                            
                            # Create mesh
                            pv_mesh = pv.PolyData(vertices, pv_faces)
                            
                            # Add material-based coloring
                            if i == 0:
                                color = 'lightpink'  # Body/skin
                                opacity = 1.0
                            elif i == 1:
                                color = 'lightblue'  # Clothes
                                opacity = 0.9
                            else:
                                color = 'lightgreen'  # Hair/accessories
                                opacity = 0.95
                            
                            plotter.add_mesh(
                                pv_mesh, 
                                color=color, 
                                opacity=opacity,
                                show_edges=False,
                                smooth_shading=True,
                                name=f"mesh_{i}"
                            )
                            mesh_count += 1
                            print(f"  ✅ Added mesh {i} successfully")
                        else:
                            print(f"  ⚠️ Mesh {i}: Non-triangular faces, skipping")
                    else:
                        print(f"  ⚠️ Mesh {i}: Empty vertices or faces")
                else:
                    print(f"  ⚠️ Mesh {i}: Missing vertices or faces attributes")
                    
            except Exception as e:
                print(f"  ❌ Error processing mesh {i}: {e}")
        
        if mesh_count == 0:
            print("❌ No meshes could be loaded! Adding placeholder...")
            sphere = pv.Sphere(radius=1.0)
            plotter.add_mesh(sphere, color='red', label='Error - No meshes loaded')
        else:
            print(f"✅ Successfully loaded {mesh_count} meshes")
        
        # Add coordinate system and grid
        plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z', line_width=2)
        plotter.show_grid(color='lightgray')
        
        # Set better camera position
        plotter.camera_position = [
            (3, 3, 3),  # Camera position
            (0, 0, 0),  # Look at origin
            (0, 0, 1)   # Up vector
        ]
        
        # Enable better interaction
        plotter.enable_trackball_style()
        
        print("🚀 Opening 3D viewer window...")
        print("🎮 Mouse Controls:")
        print("  - Left click + drag: Rotate")
        print("  - Right click + drag: Pan")
        print("  - Scroll wheel: Zoom")
        print("  - Press 'r' to reset view")
        print("  - Press 'q' to quit")
        
        # Show the viewer
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
