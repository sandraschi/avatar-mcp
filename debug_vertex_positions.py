#!/usr/bin/env python3
"""
Debug Vertex Positions - Check if vertices are in valid ranges
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def debug_vertex_positions():
    """Debug vertex positions to understand the empty viewer issue"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading VRM to debug vertex positions: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes, {len(vrm_model.bones)} bones")
        
        # Setup simple viewer without skinning
        pv.set_plot_theme('document')
        plotter = pv.Plotter(
            window_size=[1200, 800],
            title="🎌 Debug VRM Vertex Positions - No Skinning"
        )
        
        print(f"\n📊 VERTEX POSITION ANALYSIS:")
        
        colors = ['red', 'green', 'blue']
        all_vertices = []
        
        for i, mesh in enumerate(vrm_model.meshes):
            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.uint32)
            
            print(f"\n--- MESH {i} ({mesh.name}) ---")
            print(f"  Vertices: {len(vertices)}")
            print(f"  Faces: {len(faces)}")
            
            if len(vertices) > 0:
                # Analyze vertex bounds
                min_pos = vertices.min(axis=0)
                max_pos = vertices.max(axis=0)
                center = vertices.mean(axis=0)
                size = max_pos - min_pos
                
                print(f"  Min position: ({min_pos[0]:.3f}, {min_pos[1]:.3f}, {min_pos[2]:.3f})")
                print(f"  Max position: ({max_pos[0]:.3f}, {max_pos[1]:.3f}, {max_pos[2]:.3f})")
                print(f"  Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
                print(f"  Size: ({size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f})")
                
                # Check for problematic values
                has_nan = np.any(np.isnan(vertices))
                has_inf = np.any(np.isinf(vertices))
                too_large = np.any(np.abs(vertices) > 1000)
                
                print(f"  Has NaN: {has_nan}")
                print(f"  Has Inf: {has_inf}")
                print(f"  Too large (>1000): {too_large}")
                
                if has_nan or has_inf or too_large:
                    print(f"  🚨 PROBLEMATIC VERTICES DETECTED!")
                    continue
                
                all_vertices.append(vertices)
                
                # Try to render just the vertices as points first
                try:
                    point_cloud = pv.PolyData(vertices)
                    plotter.add_mesh(
                        point_cloud,
                        color=colors[i % len(colors)],
                        point_size=8,
                        render_points_as_spheres=True,
                        name=f"points_mesh_{i}"
                    )
                    print(f"  ✅ Rendered as point cloud")
                    
                    # Also try with faces if they exist
                    if len(faces) > 0 and faces.ndim == 2 and faces.shape[1] == 3:
                        # Simple face validation
                        max_face_index = faces.max()
                        if max_face_index < len(vertices):
                            try:
                                pv_mesh = pv.PolyData(vertices, faces)
                                plotter.add_mesh(
                                    pv_mesh,
                                    color=colors[i % len(colors)],
                                    opacity=0.7,
                                    show_edges=True,
                                    name=f"faces_mesh_{i}"
                                )
                                print(f"  ✅ Rendered with faces")
                            except Exception as face_error:
                                print(f"  ⚠️ Face rendering failed: {face_error}")
                        else:
                            print(f"  ⚠️ Invalid face indices: max {max_face_index} >= {len(vertices)}")
                    
                except Exception as e:
                    print(f"  ❌ Failed to render mesh {i}: {e}")
            else:
                print(f"  ⚠️ No vertices in mesh {i}")
        
        # Overall scene analysis
        if all_vertices:
            combined_vertices = np.vstack(all_vertices)
            scene_min = combined_vertices.min(axis=0)
            scene_max = combined_vertices.max(axis=0)
            scene_center = combined_vertices.mean(axis=0)
            scene_size = scene_max - scene_min
            
            print(f"\n🌍 OVERALL SCENE:")
            print(f"  Total vertices: {len(combined_vertices)}")
            print(f"  Scene bounds: ({scene_min[0]:.3f}, {scene_min[1]:.3f}, {scene_min[2]:.3f}) to ({scene_max[0]:.3f}, {scene_max[1]:.3f}, {scene_max[2]:.3f})")
            print(f"  Scene center: ({scene_center[0]:.3f}, {scene_center[1]:.3f}, {scene_center[2]:.3f})")
            print(f"  Scene size: ({scene_size[0]:.3f}, {scene_size[1]:.3f}, {scene_size[2]:.3f})")
            
            # Set appropriate camera position based on scene
            camera_distance = max(scene_size) * 2
            plotter.camera_position = [
                (scene_center[0] + camera_distance, scene_center[1] + camera_distance, scene_center[2] + camera_distance),
                (scene_center[0], scene_center[1], scene_center[2]),
                (0, 1, 0)
            ]
        else:
            print(f"\n❌ NO VALID VERTICES FOUND!")
            # Add a test sphere to verify the viewer works
            test_sphere = pv.Sphere(radius=0.1, center=(0, 0, 0))
            plotter.add_mesh(test_sphere, color='yellow', name='test_sphere')
            print(f"  Added test sphere to verify viewer functionality")
        
        # Add reference objects
        plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z')
        plotter.show_grid()
        
        print(f"\n✅ Debug viewer setup complete!")
        print(f"🎮 Controls:")
        print(f"  - Mouse: Rotate, pan, zoom")
        print(f"  - If empty, vertices might be at unexpected positions")
        print(f"  - Press Ctrl+C to exit")
        
        # Show viewer
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error in debug viewer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vertex_positions()


