#!/usr/bin/env python3
"""
Test PyVista Basic - Test the exact format PyVista expects
"""
import sys
import numpy as np
sys.path.insert(0, 'src')

def test_pyvista_basic():
    """Test PyVista with the exact documented format"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import pyvista as pv
        
        print("🔧 TESTING PYVISTA BASIC FORMAT")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        face_mesh = vrm_model.meshes[0]
        
        print(f"Face mesh: {len(face_mesh.vertices)} vertices, {len(face_mesh.faces)} faces")
        
        # Get vertices and center them
        vertices = face_mesh.vertices.copy()
        vertices[:, 1] -= 1.3
        
        # Get faces - try different PyVista formats
        faces = face_mesh.faces
        
        print(f"Original faces shape: {faces.shape}")
        print(f"Sample faces: {faces[:3]}")
        
        # Create plotter
        plotter = pv.Plotter(title="PyVista Format Test", window_size=[800, 600])
        
        # Add reference sphere
        sphere = pv.Sphere(radius=0.1)
        plotter.add_mesh(sphere, color='red', opacity=0.5)
        
        print("\nTesting different PyVista formats:")
        
        # Method 1: Direct triangular faces (most common)
        try:
            print("Method 1: Direct triangular faces")
            mesh1 = pv.PolyData(vertices, faces)
            plotter.add_mesh(mesh1, color='blue', opacity=0.7, name='method1')
            print("✅ Method 1 successful")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: Our custom format
        try:
            print("Method 2: Custom PyVista format")
            pv_faces = face_mesh.get_pyvista_faces()
            mesh2 = pv.PolyData(vertices, pv_faces)
            mesh2.translate([0.3, 0, 0])  # Offset to see difference
            plotter.add_mesh(mesh2, color='green', opacity=0.7, name='method2')
            print("✅ Method 2 successful")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Manual triangles with correct format
        try:
            print("Method 3: Manual triangle format")
            # Create faces manually in the exact PyVista format
            pv_faces_manual = []
            for i in range(min(100, len(faces))):  # Just first 100 faces for test
                face = faces[i]
                pv_faces_manual.extend([3, int(face[0]), int(face[1]), int(face[2])])
            
            pv_faces_manual = np.array(pv_faces_manual, dtype=np.int32)
            mesh3 = pv.PolyData(vertices, pv_faces_manual)
            mesh3.translate([-0.3, 0, 0])  # Offset to see difference
            plotter.add_mesh(mesh3, color='yellow', opacity=0.7, name='method3')
            print("✅ Method 3 successful")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        
        # Setup scene
        plotter.show_axes()
        plotter.add_text("Red=ref, Blue=direct, Green=custom, Yellow=manual", position='upper_left')
        plotter.reset_camera()
        
        print("\n🔧 Test ready! You should see:")
        print("  - Red sphere (reference)")
        print("  - Blue, green, yellow face attempts")
        print("  - At least ONE should show the face properly")
        
        plotter.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pyvista_basic()