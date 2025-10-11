#!/usr/bin/env python3
"""
Fixed VRM Viewer - Addresses the face array validation issues
"""
import sys
import os
import numpy as np
from pathlib import Path
sys.path.insert(0, 'src')

def validate_and_fix_faces(faces, vertex_count):
    """Validate and fix face indices to prevent PyVista errors"""
    if faces is None or len(faces) == 0:
        return np.array([], dtype=np.uint32).reshape(0, 3)
    
    faces = np.array(faces, dtype=np.uint32)
    
    # Ensure faces is 2D
    if faces.ndim == 1:
        if len(faces) % 3 == 0:
            faces = faces.reshape(-1, 3)
        else:
            print(f"⚠️ Face array length {len(faces)} not divisible by 3, truncating")
            faces = faces[:len(faces) // 3 * 3].reshape(-1, 3)
    
    # Validate face indices are within vertex bounds
    max_index = faces.max() if faces.size > 0 else 0
    if max_index >= vertex_count:
        print(f"⚠️ Invalid face indices detected: max index {max_index} >= vertex count {vertex_count}")
        # Remove faces with invalid indices
        valid_mask = np.all(faces < vertex_count, axis=1)
        faces = faces[valid_mask]
        print(f"⚠️ Removed {np.sum(~valid_mask)} invalid faces, {len(faces)} remain")
    
    # Convert to PyVista format (add face size prefix)
    if len(faces) > 0:
        pv_faces = []
        for face in faces:
            pv_faces.extend([3, face[0], face[1], face[2]])
        return np.array(pv_faces, dtype=np.uint32)
    else:
        return np.array([], dtype=np.uint32)

def create_fixed_vrm_viewer():
    """Create a VRM viewer with proper face validation"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        # Test both models
        test_files = [
            ("Nekomimi-chan", r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'),
            ("AnimeGirl2", r'D:\Dev\repos\avatarmcp\models\AnimeGirl2.vrm')
        ]
        
        pv.set_plot_theme('document')
        plotter = pv.Plotter(
            shape=(1, 2),
            window_size=[1800, 900],
            title="🎌 Fixed VRM Viewer - Validated Face Arrays"
        )
        
        for col, (model_name, vrm_path) in enumerate(test_files):
            if not os.path.exists(vrm_path):
                print(f"❌ {model_name} not found at: {vrm_path}")
                continue
            
            print(f"\n🎌 Loading {model_name} with face validation...")
            
            try:
                vrm_model = VRMLoader.from_file(vrm_path)
                print(f"✅ {model_name}: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
                
                plotter.subplot(0, col)
                plotter.add_text(f"{model_name}", position='upper_left', font_size=14)
                
                colors = ['lightsalmon', 'lightblue', 'darkseagreen']
                
                for i, mesh in enumerate(vrm_model.meshes):
                    vertices = np.array(mesh.vertices, dtype=np.float32)
                    faces = np.array(mesh.faces, dtype=np.uint32)
                    
                    print(f"  --- MESH {i} ---")
                    print(f"    Vertices: {len(vertices)}")
                    print(f"    Original faces: {len(faces)} (shape: {faces.shape})")
                    
                    # Validate and fix faces
                    fixed_faces = validate_and_fix_faces(faces, len(vertices))
                    print(f"    Fixed faces: {len(fixed_faces)} elements")
                    
                    if len(vertices) > 0 and len(fixed_faces) > 0:
                        try:
                            # Create PyVista mesh with validated faces
                            pv_mesh = pv.PolyData(vertices, fixed_faces)
                            
                            plotter.add_mesh(
                                pv_mesh,
                                color=colors[i % len(colors)],
                                smooth_shading=True,
                                show_edges=False,
                                name=f"{model_name}_mesh_{i}"
                            )
                            
                            print(f"    ✅ Successfully rendered mesh {i}")
                            
                        except Exception as mesh_error:
                            print(f"    ❌ PyVista error for mesh {i}: {mesh_error}")
                            # Try as point cloud if faces fail
                            try:
                                point_cloud = pv.PolyData(vertices)
                                plotter.add_mesh(
                                    point_cloud,
                                    color=colors[i % len(colors)],
                                    point_size=5,
                                    render_points_as_spheres=True,
                                    name=f"{model_name}_points_{i}"
                                )
                                print(f"    ⚠️ Rendered mesh {i} as point cloud")
                            except Exception as point_error:
                                print(f"    ❌ Failed to render mesh {i} even as points: {point_error}")
                    else:
                        print(f"    ⚠️ Mesh {i} has no valid geometry to render")
                
                # Set camera for each subplot
                plotter.camera_position = [(2, 1.5, 2), (0, 1, 0), (0, 0, 1)]
                plotter.add_axes()
                
            except Exception as e:
                print(f"❌ Error loading {model_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n✅ Fixed VRM viewer setup complete!")
        print(f"🎮 Controls:")
        print(f"  - Mouse: Rotate, pan, zoom each view independently")
        print(f"  - Face arrays validated and fixed")
        print(f"  - Press Ctrl+C to exit")
        
        # Show comparison
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error in fixed viewer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_fixed_vrm_viewer()

