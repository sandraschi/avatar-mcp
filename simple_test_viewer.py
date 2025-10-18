#!/usr/bin/env python3
"""
Simple Test Viewer - Minimal test to see what's actually showing
"""
import sys
sys.path.insert(0, 'src')

def simple_test():
    """Simple test to see what's happening"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        print("🔍 SIMPLE TEST - What do you actually see?")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        
        # Just test with the face mesh
        face_mesh = vrm_model.meshes[0]
        print(f"Face mesh: {len(face_mesh.vertices)} vertices, {len(face_mesh.faces)} faces")
        
        # Create plotter
        plotter = pv.Plotter(title="Simple Test - What do you see?", window_size=[800, 600])
        
        # Add obvious reference objects
        print("Adding reference objects...")
        
        # Big red sphere at origin
        big_sphere = pv.Sphere(radius=0.2)
        plotter.add_mesh(big_sphere, color='red', name='big_red_sphere')
        print("✅ Big red sphere added")
        
        # Small blue sphere offset
        small_sphere = pv.Sphere(radius=0.1, center=[0.5, 0, 0])
        plotter.add_mesh(small_sphere, color='blue', name='small_blue_sphere')
        print("✅ Small blue sphere added")
        
        # Simple cube
        cube = pv.Cube()
        cube.translate([0, 0.5, 0])
        plotter.add_mesh(cube, color='green', name='green_cube')
        print("✅ Green cube added")
        
        # Now try the face mesh
        print("Adding face mesh...")
        vertices = face_mesh.vertices.copy()
        # Don't move it too much
        vertices[:, 1] -= 1.0  # Just move down a bit
        
        try:
            pv_faces = face_mesh.get_pyvista_faces()
            face_pv_mesh = pv.PolyData(vertices, pv_faces)
            plotter.add_mesh(face_pv_mesh, color='yellow', name='face_mesh', opacity=0.8)
            print("✅ Face mesh added")
        except Exception as e:
            print(f"❌ Face mesh failed: {e}")
        
        # Setup scene
        plotter.show_axes()
        plotter.add_text("RED=big sphere, BLUE=small sphere, GREEN=cube, YELLOW=face", position='upper_left')
        
        # Reset camera to see everything
        plotter.reset_camera()
        
        print("\n🔍 TEST QUESTION:")
        print("What do you see? Please describe:")
        print("1. Big red sphere? (should be obvious)")
        print("2. Small blue sphere to the right?")
        print("3. Green cube above?")
        print("4. Yellow face mesh? (this is what we're testing)")
        print("5. Coordinate axes?")
        
        # Show
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()





