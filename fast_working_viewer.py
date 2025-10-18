#!/usr/bin/env python3
"""
Fast Working Viewer - Uses the new PyVista face format method
"""
import sys
sys.path.insert(0, 'src')

def create_fast_viewer():
    """Create a fast VRM viewer using the fixed PyVista face format"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Fast VRM Viewer: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes")
        
        # Fast PyVista setup
        pv.set_plot_theme('document')
        plotter = pv.Plotter(title="🎌 Fast Working VRM Viewer")
        
        print("\n🚀 FAST RENDERING WITH FIXED FACES:")
        
        # Just render one mesh for speed
        mesh = vrm_model.meshes[0]  # Face mesh
        print(f"Rendering: {mesh.name}")
        print(f"Vertices: {len(mesh.vertices)}")
        print(f"Faces: {len(mesh.faces)}")
        
        # Use the new PyVista face format method
        pv_faces = mesh.get_pyvista_faces()
        print(f"PyVista faces: {len(pv_faces)} values")
        print(f"First few: {pv_faces[:12]}")
        
        # Create PyVista mesh
        mesh_poly = pv.PolyData(mesh.vertices, pv_faces)
        
        # Add to scene
        plotter.add_mesh(
            mesh_poly,
            color='lightblue',
            style='surface',
            show_edges=False
        )
        
        print("✅ Successfully rendered face mesh!")
        
        # Quick scene setup
        plotter.show_axes()
        plotter.camera_position = [(2, 1, 2), (0, 0, 0), (0, 1, 0)]
        
        print("🎌 Opening viewer - should show Nekomimi-chan's face as a proper surface!")
        
        # Show viewer
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_fast_viewer()





