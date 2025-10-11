#!/usr/bin/env python3
"""
Matplotlib VRM Viewer - Reliable 3D visualization using matplotlib
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_matplotlib_viewer():
    """Create VRM viewer using matplotlib 3D"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        
        print(f"📊 Matplotlib VRM Viewer: {vrm_path}")
        vrm_model = VRMLoader.from_file(vrm_path)
        print(f"✅ Loaded: {len(vrm_model.meshes)} meshes")
        
        # Create matplotlib figure
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        print(f"\n📊 RENDERING WITH MATPLOTLIB:")
        
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\n--- MESH {i}: {mesh.name} ---")
            
            vertices = mesh.vertices
            faces = mesh.faces
            
            print(f"  Vertices: {len(vertices)}")
            print(f"  Faces: {len(faces)}")
            
            if len(vertices) == 0 or len(faces) == 0:
                print(f"  ⚠️ Empty mesh, skipping")
                continue
            
            try:
                # Create triangular patches for 3D surface
                triangles = []
                for face in faces:
                    if len(face) == 3:
                        triangle = [
                            vertices[face[0]],
                            vertices[face[1]], 
                            vertices[face[2]]
                        ]
                        triangles.append(triangle)
                
                if len(triangles) > 0:
                    # Create 3D polygon collection
                    poly_collection = Poly3DCollection(
                        triangles,
                        alpha=0.7,
                        facecolor=colors[i % len(colors)],
                        edgecolor='none',
                        linewidth=0
                    )
                    
                    ax.add_collection3d(poly_collection)
                    
                    print(f"  ✅ Added {len(triangles)} triangles")
                    
                    # Update plot bounds
                    ax.auto_scale_xyz(
                        vertices[:, 0], 
                        vertices[:, 1], 
                        vertices[:, 2]
                    )
                else:
                    print(f"  ⚠️ No valid triangles")
                    
            except Exception as e:
                print(f"  ❌ Error rendering mesh {i}: {e}")
                # Fallback to point cloud
                ax.scatter(
                    vertices[:, 0],
                    vertices[:, 1], 
                    vertices[:, 2],
                    c=colors[i % len(colors)],
                    s=1,
                    alpha=0.6,
                    label=f"{mesh.name} (points)"
                )
                print(f"  ⚠️ Fallback to point cloud: {len(vertices)} points")
        
        # Set up the plot
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('🎌 Nekomimi-chan VRM Model')
        
        # Equal aspect ratio
        max_range = 0.5  # Adjust based on model size
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([0, max_range*2])
        
        # Better viewing angle
        ax.view_init(elev=20, azim=45)
        
        print(f"\n✅ Matplotlib viewer ready!")
        print(f"🎌 Should show Nekomimi-chan with proper surfaces!")
        print(f"Use mouse to rotate the view")
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_matplotlib_viewer()



