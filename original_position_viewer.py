#!/usr/bin/env python3
"""
Original Position Viewer - Use VRM vertices exactly as they are
"""
import sys
sys.path.insert(0, 'src')

def create_original_viewer():
    """Render VRM with original vertex positions - no translation"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        print("🎌 Original Position Viewer")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        
        # Create plotter
        plotter = pv.Plotter(title="🎌 Original Positions", window_size=[1200, 800])
        
        # Add small reference at origin
        origin_sphere = pv.Sphere(radius=0.01)
        plotter.add_mesh(origin_sphere, color='red', name='origin')
        
        # Render meshes with ORIGINAL positions
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"Mesh {i} ({mesh.name}):")
            print(f"  Vertices: {len(mesh.vertices)}")
            print("  Original bounds:")
            print(f"    X: {mesh.vertices[:, 0].min():.3f} to {mesh.vertices[:, 0].max():.3f}")
            print(f"    Y: {mesh.vertices[:, 1].min():.3f} to {mesh.vertices[:, 1].max():.3f}")
            print(f"    Z: {mesh.vertices[:, 2].min():.3f} to {mesh.vertices[:, 2].max():.3f}")
            
            # Use ORIGINAL vertices - no translation
            vertices = mesh.vertices  # No .copy(), no translation
            
            # Create mesh
            pv_faces = mesh.get_pyvista_faces()
            vrm_mesh = pv.PolyData(vertices, pv_faces)
            
            plotter.add_mesh(
                vrm_mesh,
                color=colors[i % len(colors)],
                style='surface',
                opacity=0.8,
                name=f'mesh_{i}'
            )
            
            print("  ✅ Added at original position")
        
        # Position camera to see the character at its natural position
        # Face is around Y=1.2-1.4, so look there
        plotter.camera_position = [(2, 1.3, 2), (0, 1.3, 0), (0, 1, 0)]
        plotter.show_axes()
        
        print("\n🎌 Viewing at original VRM coordinates")
        print("Camera aimed at Y=1.3 where the character should be")
        print("Red dot = origin, Character should be above it")
        
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_original_viewer()





