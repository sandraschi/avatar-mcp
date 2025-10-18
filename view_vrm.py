import os
import sys
import logging
import numpy as np
import pyvista as pv
from pathlib import Path
from typing import Optional

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

# Try to import VTK for bone visualization
VTK_AVAILABLE = False
VTK_IMPORT_ERROR = None

try:
    logger.debug("Successfully imported vtk package")
    try:
        from vtk import (
            vtkPolyDataMapper, vtkActor,
            vtkLineSource, vtkConeSource, vtkSphereSource
        )
        logger.debug("Successfully imported vtk components from vtk package")
        VTK_AVAILABLE = True
    except ImportError as e:
        VTK_IMPORT_ERROR = f"Failed to import VTK components: {e}"
        logger.warning(VTK_IMPORT_ERROR)
except ImportError:
    try:
        logger.debug("Trying to import from vtkmodules...")
        from vtkmodules.all import (
            vtkPolyDataMapper, vtkActor,
            vtkLineSource, vtkConeSource, vtkSphereSource
        )
        logger.debug("Successfully imported vtk components from vtkmodules")
        VTK_AVAILABLE = True
    except ImportError as e:
        VTK_IMPORT_ERROR = f"Failed to import from vtkmodules: {e}"
        logger.warning(VTK_IMPORT_ERROR)

if not VTK_AVAILABLE:
    logger.warning("VTK is not available. Bone visualization will be disabled.")
    if VTK_IMPORT_ERROR:
        logger.debug(f"VTK import error details: {VTK_IMPORT_ERROR}")

try:
    from src.avatarmcp.models.vrm_loader import VRMLoader, VRMModel
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
    """Create a PyVista PolyData mesh from vertices and faces."""
    if vertices is None or len(vertices) == 0 or faces is None or len(faces) == 0:
        logger.warning("Vertices or faces are empty")
        return None
    
    try:
        # Ensure faces are triangles (3 vertices per face)
        if len(faces[0]) != 3:
            logger.warning(f"Expected triangular faces, got {len(faces[0])} vertices per face")
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

def load_texture(texture_data: bytes, mime_type: str) -> Optional[pv.Texture]:
    """Load a texture from binary data."""
    try:
        # Create a temporary file to load the texture
        import tempfile
        import os
        
        # Determine file extension from mime type
        ext = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
        }.get(mime_type.lower(), '.png')
        
        # Create a temporary file with the texture data
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(texture_data)
            temp_file_path = temp_file.name
        
        # Load the texture using PyVista
        texture = pv.Texture(temp_file_path)
        
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass
            
        return texture
        
    except Exception as e:
        logger.error(f"Error loading texture: {e}", exc_info=True)
        return None

def visualize_bones(plotter: pv.Plotter, model: VRMModel, bone_scale: float = 0.01):
    """Visualize the bone hierarchy of a VRM model with improved visualization.
    
    Args:
        plotter: The PyVista plotter to add the bones to
        model: The VRM model containing the bone data
        bone_scale: Scale factor for bone visualization
    """
    if not VTK_AVAILABLE:
        logger.warning("VTK is not available. Cannot visualize bones.")
        return
    
    if not hasattr(model, 'bones') or not model.bones:
        logger.warning("No bone data found in the model")
        return
    
    try:
        # Create a dictionary to store bone positions
        bone_positions = {}
        
        # First pass: collect all bone positions
        for name, bone in model.bones.items():
            if hasattr(bone, 'position') and bone.position is not None:
                bone_positions[name] = np.array(bone.position)
        
        # If no valid bone positions found, return early
        if not bone_positions:
            logger.warning("No valid bone positions found")
            return
        
        # Calculate the average bone length for scaling
        bone_lengths = []
        for name, bone in model.bones.items():
            if (hasattr(bone, 'parent') and bone.parent in bone_positions and 
                name in bone_positions):
                length = np.linalg.norm(bone_positions[name] - bone_positions[bone.parent])
                bone_lengths.append(length)
        
        avg_bone_length = np.mean(bone_lengths) if bone_lengths else 0.1
        
        # Create a sphere for each bone joint
        sphere = vtkSphereSource()
        sphere.SetRadius(avg_bone_length * 0.1 * bone_scale)
        sphere.SetPhiResolution(16)
        sphere.SetThetaResolution(16)
        
        sphere_mapper = vtkPolyDataMapper()
        if hasattr(sphere_mapper, 'SetInputConnection'):
            sphere_mapper.SetInputConnection(sphere.GetOutputPort())
        else:
            sphere_mapper.SetInput(sphere.GetOutput())
        
        # Create a line source for bone connections
        vtkLineSource()
        
        # Create mappers and actors for bones
        for name, bone in model.bones.items():
            if name not in bone_positions:
                continue
                
            # Create joint sphere
            joint_actor = vtkActor()
            joint_actor.SetMapper(sphere_mapper)
            joint_actor.SetPosition(bone_positions[name])
            
            # Color code the joints based on their position in the hierarchy
            if name.lower() in ['hips', 'spine', 'chest', 'neck', 'head']:
                joint_actor.GetProperty().SetColor(1, 0, 0)  # Red for spine
            elif 'arm' in name.lower() or 'hand' in name.lower():
                joint_actor.GetProperty().SetColor(0, 1, 0)  # Green for arms/hands
            elif 'leg' in name.lower() or 'foot' in name.lower():
                joint_actor.GetProperty().SetColor(0, 0, 1)  # Blue for legs/feet
            else:
                joint_actor.GetProperty().SetColor(1, 1, 0)  # Yellow for others
                
            plotter.add_actor(joint_actor, render=False)
            
            # Create bone connections
            if (hasattr(bone, 'parent') and bone.parent in bone_positions and 
                name in bone_positions):
                
                start_pos = bone_positions[bone.parent]
                end_pos = bone_positions[name]
                
                # Create line between parent and child
                line = vtkLineSource()
                line.SetPoint1(start_pos)
                line.SetPoint2(end_pos)
                
                line_mapper = vtkPolyDataMapper()
                if hasattr(line_mapper, 'SetInputConnection'):
                    line_mapper.SetInputConnection(line.GetOutputPort())
                else:
                    line_mapper.SetInput(line.GetOutput())
                
                line_actor = vtkActor()
                line_actor.SetMapper(line_mapper)
                line_actor.GetProperty().SetLineWidth(2.0)
                line_actor.GetProperty().SetColor(1, 1, 1)  # White lines
                
                plotter.add_actor(line_actor, render=False)
                
                # Add bone direction indicator (cone)
                direction = end_pos - start_pos
                length = np.linalg.norm(direction)
                if length > 1e-6:
                    direction = direction / length
                    cone = vtkConeSource()
                    cone.SetRadius(avg_bone_length * 0.05 * bone_scale)
                    cone.SetHeight(avg_bone_length * 0.2 * bone_scale)
                    cone.SetResolution(12)
                    
                    # Position cone at 3/4 of the bone length
                    cone_pos = start_pos * 0.25 + end_pos * 0.75
                    
                    cone_mapper = vtkPolyDataMapper()
                    if hasattr(cone_mapper, 'SetInputConnection'):
                        cone_mapper.SetInputConnection(cone.GetOutputPort())
                    else:
                        cone_mapper.SetInput(cone.GetOutput())
                    
                    cone_actor = vtkActor()
                    cone_actor.SetMapper(cone_mapper)
                    cone_actor.SetPosition(cone_pos)
                    
                    # Rotate cone to point in bone direction
                    if abs(direction[2]) < 0.99:  # Not pointing along Z
                        axis = np.cross([0, 0, 1], direction)
                        angle = np.arccos(np.clip(direction[2], -1.0, 1.0))
                        cone_actor.RotateWXYZ(
                            np.degrees(angle),
                            axis[0], axis[1], axis[2]
                        )
                    
                    cone_actor.GetProperty().SetColor(1, 0.5, 0)  # Orange cones
                    plotter.add_actor(cone_actor, render=False)
        
        logger.info(f"Visualized {len(bone_positions)} bones")
        
    except Exception as e:
        logger.error(f"Error visualizing bones: {e}", exc_info=True)

def visualize_vrm_model(model: VRMModel, show_bones: bool = True) -> None:
    """Visualize a VRM model using PyVista with enhanced error handling and visualization.
    
    Args:
        model: The VRM model to visualize
        show_bones: Whether to show the bone hierarchy
    """
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
    
    # Preload all textures
    textures = {}
    for tex_idx, texture in enumerate(model.textures):
        if hasattr(texture, 'data') and texture.data:
            tex = load_texture(texture.data, texture.mime_type)
            if tex is not None:
                textures[tex_idx] = tex
                logger.info(f"Loaded texture {tex_idx}: {texture.name} ({texture.width}x{texture.height})")
    
    # Add each mesh to the plotter
    for i, mesh in enumerate(model.meshes):
        if mesh.vertices is None or len(mesh.vertices) == 0 or mesh.faces is None or len(mesh.faces) == 0:
            logger.warning(f"Skipping mesh {i}: No vertices or faces")
            continue
            
        try:
            logger.debug(f"Processing mesh {i} with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
            
            # Default material properties
            color = [0.8, 0.8, 0.8]  # Default gray
            opacity = 1.0
            metallic = 0.1
            roughness = 0.9
            texture = None
            
            # Get material properties if available
            if hasattr(mesh, 'material_index') and mesh.material_index is not None:
                if 0 <= mesh.material_index < len(model.materials):
                    material = model.materials[mesh.material_index]
                    
                    # Base color
                    if hasattr(material, 'base_color') and material.base_color:
                        color = material.base_color[:3]  # RGB only
                        if len(material.base_color) > 3:
                            opacity = float(material.base_color[3])
                    
                    # Material properties
                    if hasattr(material, 'metallic_factor'):
                        metallic = float(material.metallic_factor)
                    if hasattr(material, 'roughness_factor'):
                        roughness = float(material.roughness_factor)
                    
                    # Try to get base color texture
                    if hasattr(material, 'texture_indices'):
                        base_color_tex_idx = material.texture_indices.get('baseColorTexture')
                        if base_color_tex_idx is not None and base_color_tex_idx in textures:
                            texture = textures[base_color_tex_idx]
                            logger.debug(f"Using texture {base_color_tex_idx} for mesh {i}")
                    
                    logger.info(f"Mesh {i} material: {getattr(material, 'name', 'unnamed')} "
                              f"(color={color}, opacity={opacity}, metallic={metallic}, roughness={roughness})")
            
            # Create the mesh
            poly = create_mesh_from_data(mesh.vertices, mesh.faces)
            if poly is None:
                logger.warning(f"Failed to create mesh {i}")
                continue
                
            # Add UV coordinates if available
            if hasattr(mesh, 'texcoords') and mesh.texcoords is not None:
                # Use PyVista's texture mapping
                poly.texture_map_to_plane(inplace=True)
            
            # Add the mesh to the plotter
            plotter.add_mesh(
                poly,
                color=color,
                opacity=opacity,
                metallic=metallic,
                roughness=roughness,
                texture=texture,
                show_edges=False,  # Disable edges for better visual with textures
                smooth_shading=True,
                name=f"mesh_{i}",
                reset_camera=(i == 0)  # Reset camera only for the first mesh
            )
            
            logger.info(f"Added mesh {i} with {poly.n_points} points and {poly.n_cells} faces")
            
        except Exception as e:
            logger.error(f"Error processing mesh {i}: {e}", exc_info=True)
    
    # Add bone visualization if enabled and VTK is available
    if show_bones and hasattr(model, 'bones') and model.bones:
        if VTK_AVAILABLE:
            logger.info("Visualizing bone hierarchy...")
            visualize_bones(plotter, model)
        else:
            logger.warning("VTK is not available. Bone visualization is disabled.")
            # Fallback: Just show bone positions as points
            bone_positions = [bone.position for bone in model.bones.values() 
                            if hasattr(bone, 'position') and bone.position is not None]
            if bone_positions:
                points = pv.PolyData(bone_positions)
                plotter.add_mesh(
                    points,
                    color='red',
                    point_size=10,
                    render_points_as_spheres=True,
                    name="bone_positions"
                )
    
    # Add coordinate axes and other helpful visualization aids
    plotter.add_axes(interactive=True)
    plotter.add_bounding_box(color='black', corner_factor=0.5, line_width=1)
    
    # Set a better camera position
    plotter.view_isometric()
    
    # Add a help message
    help_text = """VRM Model Viewer Controls:
    - Left-click and drag to rotate
    - Right-click and drag to pan
    - Scroll to zoom
    - 'r' to reset view
    - 'q' to quit
    """
    plotter.add_text(help_text, position='lower_left', font_size=8, color='black')
    
    # Show the plotter with better camera settings
    try:
        plotter.camera_position = 'xy'
        plotter.enable_parallel_projection()
        plotter.show(title="VRM Model Viewer")
    except Exception as e:
        logger.error(f"Error showing plot: {e}", exc_info=True)

def main():
    """Main function to load and visualize a VRM file with better argument handling."""
    import argparse
    
    parser = argparse.ArgumentParser(description='View a VRM 3D model')
    parser.add_argument('vrm_file', type=str, help='Path to the VRM file to view')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-bones', action='store_true', help='Disable bone visualization')
    parser.add_argument('--bone-scale', type=float, default=0.01, 
                       help='Scale factor for bone visualization (default: 0.01)')
    
    args = parser.parse_args()
    
    # Set log level
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    # Load and visualize the model
    model = load_vrm_model(args.vrm_file)
    
    if model:
        # Log model statistics
        logger.info(f"Loaded VRM model with {len(model.meshes)} meshes, "
                   f"{len(model.materials)} materials, and {len(model.bones)} bones")
        
        # Visualize the model with or without bones
        visualize_vrm_model(model, show_bones=not args.no_bones)
    else:
        logger.error("Failed to load VRM model")
        sys.exit(1)

if __name__ == "__main__":
    main()
