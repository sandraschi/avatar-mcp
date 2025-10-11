#!/usr/bin/env python3
"""
Matplotlib VRM Simple - Use matplotlib instead of PyVista
"""
import sys
import os
import numpy as np
sys.path.insert(0, 'src')

def create_matplotlib_viewer():
    """Create VRM viewer using matplotlib (more reliable than PyVista)"""
    
    try:
        from avatarmcp.models.vrm_loader import VRMLoader
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        print(f"📊 Matplotlib VRM Viewer (more reliable)")
        
        # Load VRM
        vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
        vrm_model = VRMLoader.from_file(vrm_path)
        
        # Create figure
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        colors = ['red', 'blue', 'green']
        
        print(f"Rendering {len(vrm_model.meshes)} meshes...")
        
        for i, mesh in enumerate(vrm_model.meshes):
            print(f"\nMesh {i} ({mesh.name}):")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            
            vertices = mesh.vertices
            faces = mesh.faces
            
            # Show vertex scatter plot first
            ax.scatter(
                vertices[:, 0], 
                vertices[:, 1], 
                vertices[:, 2],
                c=colors[i % len(colors)],
                s=0.1,
                alpha=0.6,
                label=f"{mesh.name} vertices"
            )
            print(f"  ✅ Added vertex scatter")
            
            # Try to add some triangular surfaces (just first 100 for performance)
            if len(faces) > 0:
                triangles = []
                for j in range(min(100, len(faces))):
                    face = faces[j]
                    if all(idx < len(vertices) for idx in face):
                        triangle = [
                            vertices[face[0]],
                            vertices[face[1]], 
                            vertices[face[2]]
                        ]
                        triangles.append(triangle)
                
                if triangles:
                    poly_collection = Poly3DCollection(
                        triangles,
                        alpha=0.3,
                        facecolor=colors[i % len(colors)],
                        edgecolor='black',
                        linewidth=0.1
                    )
                    ax.add_collection3d(poly_collection)
                    print(f"  ✅ Added {len(triangles)} triangular surfaces")
        
        # Set up the plot
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        ax.set_title('VRM Model - Matplotlib Viewer')
        
        # Auto-scale to fit the data
        all_vertices = np.vstack([mesh.vertices for mesh in vrm_model.meshes])
        ax.auto_scale_xyz(
            all_vertices[:, 0], 
            all_vertices[:, 1], 
            all_vertices[:, 2]
        )
        
        print(f"\n📊 Matplotlib viewer ready!")
        print(f"This should DEFINITELY show something!")
        print(f"Look for colored point clouds representing the character parts")
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_matplotlib_viewer()


