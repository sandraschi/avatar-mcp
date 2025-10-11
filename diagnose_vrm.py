#!/usr/bin/env python3
"""
Diagnose VRM - Just analyze the VRM data without rendering
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def diagnose_vrm():
    """Diagnose VRM data to understand why viewers aren't working"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🔍 DIAGNOSING VRM: {vrm_path}")
        print(f"File exists: {os.path.exists(vrm_path)}")
        print(f"File size: {os.path.getsize(vrm_path):,} bytes")
        
        print(f"\n📊 LOADING VRM DATA...")
        vrm_model = VRMLoader.from_file(vrm_path)
        
        print(f"\n✅ VRM LOADED SUCCESSFULLY!")
        print(f"Meshes: {len(vrm_model.meshes)}")
        print(f"Bones: {len(vrm_model.bones)}")
        print(f"Materials: {len(vrm_model.materials)}")
        print(f"Textures: {len(vrm_model.textures)}")
        print(f"Blend shapes: {len(vrm_model.blend_shapes)}")
        
        print(f"\n🔍 MESH ANALYSIS:")
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i}: {mesh.name} ---")
            print(f"  Vertices: {len(mesh.vertices)} (shape: {mesh.vertices.shape})")
            print(f"  Faces: {len(mesh.faces)} (shape: {mesh.faces.shape})")
            
            if len(mesh.vertices) > 0:
                print(f"  Vertex bounds:")
                print(f"    X: {mesh.vertices[:, 0].min():.3f} to {mesh.vertices[:, 0].max():.3f}")
                print(f"    Y: {mesh.vertices[:, 1].min():.3f} to {mesh.vertices[:, 1].max():.3f}")
                print(f"    Z: {mesh.vertices[:, 2].min():.3f} to {mesh.vertices[:, 2].max():.3f}")
            
            if len(mesh.faces) > 0:
                print(f"  Face indices range: {mesh.faces.min()} to {mesh.faces.max()}")
                print(f"  Sample faces: {mesh.faces[:3].tolist()}")
                
                # Check for face validity
                max_vertex_index = len(mesh.vertices) - 1
                invalid_faces = np.any(mesh.faces > max_vertex_index, axis=1)
                invalid_count = np.sum(invalid_faces)
                print(f"  Invalid faces: {invalid_count}/{len(mesh.faces)}")
                
                if invalid_count == 0:
                    print(f"  ✅ All faces are valid!")
                else:
                    print(f"  ❌ {invalid_count} faces have invalid indices!")
            
            print(f"  Normals: {'✅' if mesh.normals is not None else '❌'}")
            print(f"  Texcoords: {'✅' if mesh.texcoords is not None else '❌'}")
        
        print(f"\n🎯 PYVISTA FACE FORMAT TEST:")
        test_mesh = vrm_model.meshes[0]
        
        # Test the new PyVista face format
        if hasattr(test_mesh, 'get_pyvista_faces'):
            pv_faces = test_mesh.get_pyvista_faces()
            print(f"PyVista faces generated: {len(pv_faces)} values")
            print(f"Expected format: [3, v1, v2, v3, 3, v4, v5, v6, ...]")
            print(f"First 12 values: {pv_faces[:12].tolist()}")
            
            # Verify format
            if len(pv_faces) % 4 == 0:
                print(f"✅ Format looks correct (divisible by 4)")
                
                # Check that every 4th value is 3
                cell_sizes = pv_faces[::4]
                if np.all(cell_sizes == 3):
                    print(f"✅ All cell sizes are 3 (triangles)")
                else:
                    print(f"❌ Some cell sizes are not 3: {np.unique(cell_sizes)}")
            else:
                print(f"❌ Format incorrect (not divisible by 4)")
        else:
            print(f"❌ get_pyvista_faces method not found!")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"The VRM data loads correctly. If viewers aren't working, it's likely:")
        print(f"1. PyVista/OpenGL driver issues")
        print(f"2. Threading/GUI problems")  
        print(f"3. Display/window manager issues")
        print(f"4. Python environment conflicts")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"Try a simple test - create a basic PyVista sphere:")
        
        # Test basic PyVista
        try:
            import pyvista as pv
            print(f"PyVista import: ✅")
            
            # Try creating a simple sphere
            sphere = pv.Sphere()
            print(f"Sphere creation: ✅ ({sphere.n_points} points, {sphere.n_cells} cells)")
            
            print(f"Try running: python -c \"import pyvista as pv; pv.Sphere().plot()\"")
            
        except Exception as e:
            print(f"PyVista test failed: ❌ {e}")
        
    except Exception as e:
        print(f"❌ VRM loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_vrm()


