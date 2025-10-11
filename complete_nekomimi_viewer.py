#!/usr/bin/env python3
"""
Complete Nekomimi Viewer - Render all three meshes (Face, Body, Hair)
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_complete_viewer():
    """Create complete Nekomimi-chan viewer with all meshes"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        print(f"🎌 Creating complete Nekomimi-chan viewer")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        
        # Create plotter
        plotter = pv.Plotter(title="🎌 Complete Nekomimi-chan", window_size=[1400, 1000])
        
        # Colors for each mesh part
        colors = ['lightcoral', 'lightblue', 'lightgreen']  # Face, Body, Hair
        names = ['Face', 'Body', 'Hair']
        
        print(f"\n🎌 RENDERING ALL MESHES:")
        
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i}: {mesh.name} ---")
            print(f"Vertices: {len(mesh.vertices)}")
            print(f"Faces: {len(mesh.faces)}")
            
            # Center the vertices (subtract the face center offset)
            vertices = mesh.vertices.copy()
            vertices[:, 1] -= 1.3  # Center vertically based on face position
            
            print(f"Bounds after centering:")
            print(f"  X: {vertices[:, 0].min():.3f} to {vertices[:, 0].max():.3f}")
            print(f"  Y: {vertices[:, 1].min():.3f} to {vertices[:, 1].max():.3f}")
            print(f"  Z: {vertices[:, 2].min():.3f} to {vertices[:, 2].max():.3f}")
            
            try:
                # Create PyVista mesh
                pv_faces = mesh.get_pyvista_faces()
                vrm_mesh = pv.PolyData(vertices, pv_faces)
                
                # Add to scene
                plotter.add_mesh(
                    vrm_mesh,
                    color=colors[i % len(colors)],
                    style='surface',
                    name=f'mesh_{i}_{names[i] if i < len(names) else "unknown"}',
                    opacity=0.9,
                    show_edges=False,
                    smooth_shading=True
                )
                
                print(f"✅ {names[i] if i < len(names) else 'Mesh'} rendered successfully")
                
            except Exception as e:
                print(f"❌ Error rendering mesh {i}: {e}")
        
        # Add small reference sphere
        sphere = pv.Sphere(radius=0.02)
        plotter.add_mesh(sphere, color='red', opacity=0.8, name='origin')
        
        # Setup scene
        plotter.show_axes()
        plotter.add_text(
            "🎌 Complete Nekomimi-chan\nRed=Face, Blue=Body, Green=Hair", 
            position='upper_left',
            font_size=12
        )
        
        # Good camera angle for character viewing
        plotter.camera_position = [(0.5, 0.2, 0.8), (0, 0, 0), (0, 1, 0)]
        
        # Enable mouse interaction
        plotter.enable_trackball_style()
        
        print(f"\n🎌 Complete Nekomimi-chan viewer ready!")
        print(f"You should see the full character:")
        print(f"  🔴 Light coral face")
        print(f"  🔵 Light blue body/clothing")  
        print(f"  🟢 Light green hair")
        print(f"  🔴 Red dot at origin")
        print(f"Use mouse to rotate, zoom, and pan!")
        
        # Show
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_complete_viewer()



