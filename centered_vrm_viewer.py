#!/usr/bin/env python3
"""
Centered VRM Viewer - Center both sphere and VRM mesh for better viewing
"""
import sys
sys.path.insert(0, 'src')

def create_centered_viewer():
    """Create VRM viewer with proper centering"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        print("🎌 Creating centered VRM viewer")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        
        # Create plotter
        plotter = pv.Plotter(title="🎌 Centered Nekomimi-chan Viewer", window_size=[1200, 800])
        
        # Process just the face mesh for speed
        face_mesh = vrm_model.meshes[0]
        print(f"Rendering: {face_mesh.name}")
        print(f"Original bounds: Y {face_mesh.vertices[:, 1].min():.3f} to {face_mesh.vertices[:, 1].max():.3f}")
        
        # CENTER the mesh by translating it to origin
        vertices = face_mesh.vertices.copy()
        # Move the face down so it's centered around Y=0
        vertices[:, 1] -= 1.3  # Subtract the midpoint Y coordinate
        
        print(f"Centered bounds: Y {vertices[:, 1].min():.3f} to {vertices[:, 1].max():.3f}")
        
        # Create PyVista mesh
        pv_faces = face_mesh.get_pyvista_faces()
        vrm_mesh = pv.PolyData(vertices, pv_faces)
        
        # Add reference sphere at origin
        sphere = pv.Sphere(radius=0.1)  # Small sphere
        plotter.add_mesh(sphere, color='red', opacity=0.5, name='origin_ref')
        
        # Add VRM mesh
        plotter.add_mesh(
            vrm_mesh,
            color='lightblue',
            style='surface',
            show_edges=False,
            name='vrm_face'
        )
        
        print("✅ Both meshes added and centered")
        
        # Setup scene
        plotter.show_axes()
        plotter.add_text("Red sphere = origin\nBlue = Nekomimi face", position='upper_left')
        
        # Camera positioned to see both
        plotter.camera_position = [(0.5, 0.3, 0.5), (0, 0, 0), (0, 1, 0)]
        plotter.reset_camera()
        
        print("🎌 Viewer ready - face should be clearly visible now!")
        
        # Show
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_centered_viewer()





