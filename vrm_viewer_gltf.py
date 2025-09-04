import pyvista as pv
import numpy as np
import os
import json
from pygltflib import GLTF2

class VRMViewer:
    def __init__(self, window_size=(1024, 768)):
        self.plotter = pv.Plotter(window_size=window_size)
        
    def load_vrm(self, filepath):
        try:
            print(f"Loading VRM file: {filepath}")
            
            # Load the GLB file directly
            gltf = GLTF2().load(filepath)
            
            # Process each mesh
            for mesh in gltf.meshes:
                for primitive in mesh.primitives:
                    # Get vertex positions
                    pos_accessor = gltf.accessors[primitive.attributes['POSITION']]
                    buffer_view = gltf.bufferViews[pos_accessor.bufferView]
                    buffer = gltf.buffers[buffer_view.buffer]
                    
                    # Get position data
                    data = buffer.data[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]
                    positions = np.frombuffer(data, dtype=np.float32).reshape(-1, 3)
                    
                    # Get indices if they exist
                    if hasattr(primitive, 'indices') and primitive.indices is not None:
                        idx_accessor = gltf.accessors[primitive.indices]
                        idx_buffer_view = gltf.bufferViews[idx_accessor.bufferView]
                        idx_buffer = gltf.buffers[idx_buffer_view.buffer]
                        idx_data = idx_buffer.data[idx_buffer_view.byteOffset:idx_buffer_view.byteOffset + idx_buffer_view.byteLength]
                        
                        # Determine the dtype based on the component type
                        if idx_accessor.componentType == 5123:  # UNSIGNED_SHORT
                            faces = np.frombuffer(idx_data, dtype=np.uint16).reshape(-1, 3)
                        else:  # Default to uint32
                            faces = np.frombuffer(idx_data, dtype=np.uint32).reshape(-1, 3)
                    else:
                        # If no indices, create them from the vertex order
                        faces = np.arange(len(positions), dtype=np.uint32).reshape(-1, 3)
                    
                    # Prepare faces for PyVista
                    faces = np.column_stack(
                        (np.ones(len(faces), dtype=int) * 3, faces)
                    )
                    
                    # Create and add mesh
                    pv_mesh = pv.PolyData(positions, faces.ravel())
                    self.plotter.add_mesh(
                        pv_mesh,
                        color='#FFB6C1',
                        show_edges=False,
                        smooth_shading=True
                    )
            
            # Set up camera and lighting
            self.plotter.camera_position = [(2, 2, 2), (0, 0, 0), (0, 0, 1)]
            self.plotter.enable_lightkit()
            return True
            
        except Exception as e:
            print(f"Error loading VRM: {str(e)}")
            return False
    
    def show(self):
        self.plotter.show()

if __name__ == "__main__":
    # Create the viewer
    viewer = VRMViewer()
    
    # Path to the VRM file
    vrm_path = os.path.join("examples", "Nekomimi-chan.vrm")
    
    # Check if file exists
    if not os.path.exists(vrm_path):
        print(f"Error: VRM file not found at: {vrm_path}")
        print("Please make sure the VRM file exists in the 'examples' directory.")
        exit(1)
    
    # Try to load and show the VRM
    if viewer.load_vrm(vrm_path):
        print("VRM loaded successfully!")
        print("Close the 3D window to exit.")
        viewer.show()
    else:
        print("Failed to load VRM file. Please check the error message above.")
        exit(1)
