#!/usr/bin/env python3
"""
Trimesh VRM Viewer - Use trimesh for better 3D model support
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_trimesh_viewer():
    """Create VRM viewer using trimesh instead of PyVista"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import trimesh
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"🎌 Loading VRM with trimesh: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes")
        
        print(f"\n🔧 CREATING TRIMESH SCENE:")
        
        # Create a trimesh scene
        scene = trimesh.Scene()
        
        colors = [
            [255, 100, 100, 255],  # Red for face
            [100, 100, 255, 255],  # Blue for body  
            [100, 255, 100, 255]   # Green for hair
        ]
        
        mesh_count = 0
        for i, vrm_mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i} ({vrm_mesh.name}) ---")
            
            vertices = np.array(vrm_mesh.vertices, dtype=np.float32)
            faces = np.array(vrm_mesh.faces, dtype=np.uint32)
            
            print(f"  Vertices: {len(vertices)}")
            print(f"  Faces: {len(faces)} shape: {faces.shape}")
            
            if len(vertices) == 0 or len(faces) == 0:
                print(f"  ⚠️ Empty mesh, skipping")
                continue
                
            try:
                # Create trimesh object
                if faces.ndim == 2 and faces.shape[1] == 3:
                    # Valid triangular faces
                    mesh = trimesh.Trimesh(
                        vertices=vertices,
                        faces=faces,
                        vertex_colors=None
                    )
                    
                    # Set mesh color
                    mesh.visual.face_colors = colors[i % len(colors)]
                    
                    # Add to scene
                    scene.add_geometry(mesh, node_name=f"mesh_{i}")
                    
                    print(f"  ✅ Added to trimesh scene")
                    print(f"  Mesh bounds: {mesh.bounds}")
                    print(f"  Mesh volume: {mesh.volume:.4f}")
                    print(f"  Is watertight: {mesh.is_watertight}")
                    
                    mesh_count += 1
                    
                else:
                    print(f"  ❌ Invalid face shape: {faces.shape}")
                    
            except Exception as e:
                print(f"  ❌ Error creating trimesh: {e}")
        
        if mesh_count == 0:
            print(f"\n❌ No meshes were added to scene!")
            return
            
        print(f"\n✅ Scene created with {mesh_count} meshes")
        print(f"Scene bounds: {scene.bounds}")
        
        # Show the scene
        print(f"\n🎌 Opening trimesh viewer...")
        print(f"This should open a new window with the 3D model")
        print(f"Use mouse to rotate, zoom, and pan")
        
        # Trimesh has a built-in viewer
        scene.show()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Trimesh might not be installed or might have issues")
        print(f"Let's try a basic matplotlib 3D plot instead...")
        
        # Fallback to matplotlib
        try_matplotlib_viewer()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def try_matplotlib_viewer():
    """Fallback to matplotlib 3D viewer"""
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"📊 Fallback: matplotlib 3D plot")
        vrm_model = VRMLoader.from_file(vrm_path)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        colors = ['red', 'blue', 'green']
        
        for i, mesh in enumerate(vrm_model.meshes):
            vertices = np.array(mesh.vertices, dtype=np.float32)
            
            if len(vertices) > 0:
                # Plot as scatter points
                ax.scatter(
                    vertices[:, 0], 
                    vertices[:, 1], 
                    vertices[:, 2],
                    c=colors[i % len(colors)],
                    s=1,
                    alpha=0.6,
                    label=f"Mesh {i} ({mesh.name})"
                )
                
                print(f"  ✅ Plotted mesh {i}: {len(vertices)} points")
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y') 
        ax.set_zlabel('Z')
        ax.legend()
        ax.set_title('VRM Model - Point Cloud View')
        
        print(f"✅ Matplotlib viewer ready!")
        plt.show()
        
    except Exception as e:
        print(f"❌ Matplotlib fallback failed: {e}")

if __name__ == "__main__":
    create_trimesh_viewer()



