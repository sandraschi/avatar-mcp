import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vrm_viewer.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

try:
    import pyvista as pv
    from pyvista import PolyData
    import trimesh
    from trimesh import Trimesh
    from trimesh.voxel import creation
    from pygltflib import GLTF2
    
    # Import local modules
    from src.avatarmcp.models.vrm_loader import VRMLoader, VRMModel, VRMMesh, VRMMaterial
    from src.avatarmcp.utils.logging_utils import setup_logging
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.info("Please install the required packages with: pip install -r requirements.txt")
    sys.exit(1)

def load_vrm_model(file_path: str) -> Optional[VRMModel]:
    """Load a VRM model from file with enhanced error handling.
    
    Args:
        file_path: Path to the VRM file
        
    Returns:
        VRMModel instance or None if loading fails
    """
    if not os.path.exists(file_path):
        logger.error(f"VRM file not found: {file_path}")
        return None
        
    try:
        logger.info(f"Loading VRM model from: {file_path}")
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logger.info(f"File size: {file_size:.2f} MB")
        
        model = VRMLoader.from_file(file_path)
        
        if model is None:
            logger.error("Failed to load VRM model")
            return None
            
        logger.info(f"Successfully loaded VRM model with {len(model.meshes)} meshes and {len(model.materials)} materials")
        
        # Log mesh statistics
        for i, mesh in enumerate(model.meshes):
            vert_count = len(mesh.vertices) if mesh.vertices is not None else 0
            face_count = len(mesh.faces) if mesh.faces is not None else 0
            mat_idx = mesh.material_index if hasattr(mesh, 'material_index') else 'N/A'
            logger.debug(f"Mesh {i}: {vert_count} vertices, {face_count} faces, material: {mat_idx}")
            
        return model
        
    except Exception as e:
        logger.error(f"Error loading VRM model: {e}", exc_info=True)
        return None

def create_mesh_from_data(vertices: np.ndarray, faces: np.ndarray) -> Optional[pv.PolyData]:
    """Create a PyVista mesh from vertices and faces with robust error handling."""
    if vertices is None or faces is None:
        logger.error("Vertices and faces must not be None")
        return None
        
    if len(vertices) == 0 or len(faces) == 0:
        logger.error("Vertices and faces must not be empty")
        return None
        
    try:
        # Ensure vertices are in the correct format (Nx3)
        vertices = np.asarray(vertices, dtype=np.float32)
        if vertices.shape[1] != 3:
            logger.warning(f"Expected vertices to be Nx3, got {vertices.shape}")
            if vertices.shape[0] == 3 and len(vertices.shape) > 1:
                vertices = vertices.T  # Transpose if 3xN
            else:
                return None
                
        # Process faces
        if len(faces.shape) == 1:
            # Assume it's already in PyVista format with leading vertex counts
            faces_pv = faces.astype(np.int32)
        else:
            # Convert to PyVista format: [n, v0, v1, v2, ...] for each face
            if faces.shape[1] < 3:
                logger.error(f"Invalid face format: expected at least 3 vertices per face, got {faces.shape}")
                return None
                
            # Convert to triangles if needed
            if faces.shape[1] > 3:
                logger.debug(f"Converting {faces.shape[1]}-gon faces to triangles")
                try:
                    tri_faces = []
                    for face in faces:
                        if len(face) < 3:
                            continue
                        # Simple fan triangulation
                        for i in range(2, len(face)):
                            tri_faces.append([face[0], face[i-1], face[i]])
                    faces = np.array(tri_faces, dtype=np.int32)
                except Exception as e:
                    logger.error(f"Failed to triangulate faces: {e}")
                    return None
            
            # Convert to PyVista format
            faces_pv = np.hstack([
                np.full((faces.shape[0], 1), 3),  # Number of vertices per face (3 for triangles)
                faces.astype(np.int32)
            ]).flatten()
        
        # Create the PyVista mesh
        return pv.PolyData(vertices, faces=faces_pv)
        
    except Exception as e:
        logger.error(f"Error creating mesh: {e}", exc_info=True)
        return None

def visualize_vrm_model(model: VRMModel) -> None:
    """Visualize a VRM model using PyVista with enhanced error handling and visualization."""
    if not model or not model.meshes:
        logger.error("No valid model or meshes to visualize")
        return
        
    # Create a plotter with better defaults
    plotter = pv.Plotter(
        window_size=(1600, 900),
        lighting='three lights',
        polygon_smoothing=True
    )
    
    plotter.set_background('white')
    
    # Add each mesh to the plotter
    for i, mesh in enumerate(model.meshes):
        if mesh.vertices is None or len(mesh.vertices) == 0 or mesh.faces is None or len(mesh.faces) == 0:
            logger.warning(f"Skipping mesh {i}: No vertices or faces")
            continue
            
        try:
            logger.debug(f"Processing mesh {i} with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
            
            # Get material properties
            color = [0.8, 0.8, 0.8]  # Default gray
            opacity = 1.0
            
            if hasattr(mesh, 'material_index') and mesh.material_index is not None:
                if 0 <= mesh.material_index < len(model.materials):
                    material = model.materials[mesh.material_index]
                    if hasattr(material, 'base_color') and material.base_color:
                        color = material.base_color[:3]  # RGB only
                        if len(material.base_color) > 3:
                            opacity = float(material.base_color[3])
                    
                    logger.debug(f"Mesh {i} using material {mesh.material_index}: color={color}, opacity={opacity}")
            
            # Create the mesh
            poly = create_mesh_from_data(mesh.vertices, mesh.faces)
            if poly is None:
                logger.warning(f"Failed to create mesh {i}")
                continue
                
            # Add the mesh to the plotter
            plotter.add_mesh(
                poly,
                color=color,
                opacity=opacity,
                show_edges=True,
                edge_color='black',
                line_width=0.5,
                smooth_shading=True,
                name=f"mesh_{i}",
                reset_camera=(i == 0)  # Reset camera only for the first mesh
            )
            
            logger.info(f"Added mesh {i} with {poly.n_points} points and {poly.n_cells} faces")
            
        except Exception as e:
            logger.error(f"Error processing mesh {i}: {e}", exc_info=True)
    
    # Add coordinate axes and other helpful visualization aids
    plotter.add_axes(interactive=True)
    plotter.add_bounding_box(color='black', corner_factor=0.5, line_width=1)
    
    # Set a better camera position
    plotter.view_isometric()
    
    # Show the plot
    logger.info("Rendering VRM model...")
    plotter.show(title="VRM Model Viewer")

def main():
    """Main function to load and visualize a VRM file with better argument handling."""
    import argparse
    
    parser = argparse.ArgumentParser(description='View a VRM 3D model')
    parser.add_argument('vrm_file', type=str, help='Path to the VRM file to view')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set log level
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    # Load and visualize the model
    model = load_vrm_model(args.vrm_file)
    
    if model:
        visualize_vrm_model(model)
    else:
        logger.error("Failed to load VRM model")
        sys.exit(1)

if __name__ == "__main__":
    main()
