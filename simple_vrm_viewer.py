"""
Simple VRM viewer to test model loading and display.
"""
import asyncio
import os
import numpy as np
from pathlib import Path
import pyvista as pv
from pygltflib import GLTF2
from src.avatarmcp.visualization.viewer import VRMViewer

async def main():
    print("Starting simple VRM viewer...")
    
    # Path to the VRM model
    vrm_path = os.path.join("examples", "Nekomimi-chan.vrm")
    if not os.path.exists(vrm_path):
        print(f"Error: VRM model not found at {vrm_path}")
        return
    
    # Create and configure the viewer
    print("Creating VRMViewer...")
    viewer = VRMViewer(window_size=(1024, 768))
    
    # Load the VRM model
    print(f"Loading VRM model: {vrm_path}")
    
    try:
        print(f"Loading VRM model from: {vrm_path}")
        
        # Load the VRM model (VRM is based on glTF 2.0)
        gltf = GLTF2().load(vrm_path)
        
        # Get the first mesh (simplified - VRM can have multiple meshes)
        if not gltf.meshes:
            raise ValueError("No meshes found in VRM file")
            
        # Get the first primitive of the first mesh
        primitive = gltf.meshes[0].primitives[0]
        
        # Get accessors for position and indices
        positions = gltf.accessor(primitive.attributes.POSITION)
        indices = gltf.accessor(primitive.indices) if hasattr(primitive, 'indices') else None
        
        # Get the buffer views
        positions_data = gltf.get_data_from_buffer_uri(positions.bufferView)
        
        # Convert to numpy array
        vertices = np.frombuffer(positions_data, dtype=np.float32).reshape(-1, 3)
        
        # Get faces (indices)
        if indices is not None:
            indices_data = gltf.get_data_from_buffer_uri(indices.bufferView)
            faces = np.frombuffer(indices_data, dtype=np.uint16).reshape(-1, 3)
        else:
            # If no indices, assume triangles are defined by the vertex order
            faces = np.arange(len(vertices), dtype=np.uint16).reshape(-1, 3)
        
        # Reshape faces for PyVista
        faces = np.column_stack(
            (np.ones(len(faces), dtype=int) * 3, faces)
        )
        
        # Create PyVista mesh
        mesh = pv.PolyData(vertices, faces.ravel())
        
        # Add the mesh to the plotter
        viewer.plotter.add_mesh(
            mesh,
            color='#FFB6C1',
            show_edges=False,
            smooth_shading=True,
            specular=0.5,
            specular_power=30,
            ambient=0.3,
            diffuse=0.7
        )
        
        # Set up the camera
        viewer.plotter.camera_position = [(2, 2, 2), (0, 1, 0), (0, 0, 1)]
        viewer.plotter.camera.zoom(1.2)
        
        # Add some lighting
        viewer.plotter.enable_lightkit()
        viewer.plotter.add_light(position=(1, 1, 1), color='white')
        
        print("Nekomimi-chan is ready! 🐱")
        
    except Exception as e:
        print(f"Error loading VRM model: {e}")
        print("Falling back to a simple representation...")
        
        # Fall back to a simple sphere if VRM loading fails
        print("Falling back to simple representation...")
        print("Error details:", str(e))
        
        # Create a simple sphere as fallback
        sphere = pv.Sphere(radius=0.5, center=(0, 0, 1))
        viewer.plotter.add_mesh(sphere, color='lightblue')
        viewer.plotter.camera_position = 'xy'
    
    # Show the window in blocking mode first
    print("Showing window (blocking mode)...")
    viewer.plotter.show(title="VRM Viewer", full_screen=True)
    
    print("Window closed.")

if __name__ == "__main__":
    asyncio.run(main())
