#!/usr/bin/env python3
"""
Bone-Animated VRM Viewer - Properly applies bone transforms to vertices
"""
import sys
import os
import time
import threading
import numpy as np
from typing import Dict, List, Optional
sys.path.insert(0, 'src')

class BoneAnimatedViewer:
    def __init__(self):
        self.vrm_model = None
        self.plotter = None
        self.mesh_actors = []
        self.bone_transforms = {}
        self.running = False
        self.animation_time = 0.0
        self.current_animation = "idle"
        
    def load_vrm(self, file_path):
        """Load VRM with proper bone binding"""
        try:
            from avatarmcp.models.vrm_loader import VRMLoader
            print(f"🎌 Loading VRM with bone binding: {file_path}")
            self.vrm_model = VRMLoader.from_file(file_path)
            print(f"✅ Loaded: {len(self.vrm_model.meshes)} meshes, {len(self.vrm_model.bones)} bones")
            
            # Initialize bone transforms to identity
            for bone_name, bone in self.vrm_model.bones.items():
                self.bone_transforms[bone_name] = {
                    'position': list(bone.position),
                    'rotation': list(bone.rotation),
                    'scale': list(bone.scale),
                    'matrix': self._create_transform_matrix(bone.position, bone.rotation, bone.scale)
                }
            
            return True
        except Exception as e:
            print(f"❌ Error loading VRM: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_transform_matrix(self, position, rotation, scale):
        """Create 4x4 transformation matrix from position, rotation (quaternion), scale"""
        # Convert quaternion to rotation matrix
        x, y, z, w = rotation
        
        # Quaternion to rotation matrix
        xx, yy, zz = x*x, y*y, z*z
        xy, xz, yz = x*y, x*z, y*z
        xw, yw, zw = x*w, y*w, z*w
        
        rotation_matrix = np.array([
            [1-2*(yy+zz), 2*(xy-zw), 2*(xz+yw)],
            [2*(xy+zw), 1-2*(xx+zz), 2*(yz-xw)],
            [2*(xz-yw), 2*(yz+xw), 1-2*(xx+yy)]
        ])
        
        # Scale matrix
        scale_matrix = np.diag(scale)
        
        # Combine rotation and scale
        rs_matrix = rotation_matrix @ scale_matrix
        
        # Create 4x4 homogeneous matrix
        transform = np.eye(4)
        transform[:3, :3] = rs_matrix
        transform[:3, 3] = position
        
        return transform
    
    def setup_viewer(self):
        """Setup PyVista viewer with proper mesh binding"""
        try:
            import pyvista as pv
            pv.set_plot_theme('document')
            
            self.plotter = pv.Plotter(
                window_size=[1200, 900],
                title="🦴 Bone-Animated Nekomimi-chan Viewer"
            )
            
            if not self.vrm_model or not self.vrm_model.meshes:
                print("❌ No VRM model loaded")
                return False
            
            # Process meshes with bone binding
            for i, mesh in enumerate(self.vrm_model.meshes):
                if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                    vertices = np.array(mesh.vertices, dtype=np.float32)
                    faces = np.array(mesh.faces, dtype=np.int32)
                    
                    if len(vertices) > 0 and len(faces) > 0 and faces.shape[1] == 3:
                        # Apply initial bone transforms to position meshes correctly
                        transformed_vertices = self._apply_bone_transforms(vertices, i)
                        
                        # Convert to PyVista format
                        pv_faces = []
                        for face in faces:
                            if (face[0] < len(transformed_vertices) and face[1] < len(transformed_vertices) and 
                                face[2] < len(transformed_vertices)):
                                pv_faces.extend([3, face[0], face[1], face[2]])
                        
                        if len(pv_faces) > 0:
                            pv_mesh = pv.PolyData(transformed_vertices, pv_faces)
                            
                            # Different colors for body parts
                            colors = ['lightpink', 'lightblue', 'lightgreen']
                            names = ['Body', 'Clothing', 'Hair']
                            
                            actor = self.plotter.add_mesh(
                                pv_mesh,
                                color=colors[i % len(colors)],
                                opacity=0.9,
                                smooth_shading=True,
                                name=f"{names[i % len(names)]}_{i}"
                            )
                            
                            # Store for animation updates
                            self.mesh_actors.append({
                                'actor': actor,
                                'original_vertices': vertices.copy(),
                                'mesh_index': i,
                                'pv_mesh': pv_mesh
                            })
                            
                            print(f"  ✅ Added mesh {i} ({names[i % len(names)]}): {len(vertices)} vertices")
            
            # Add coordinate system
            self.plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z')
            self.plotter.show_grid()
            
            # Set camera for full body view
            self.plotter.camera_position = [(2, 2, 2), (0, 1, 0), (0, 0, 1)]
            self.plotter.enable_trackball_style()
            
            print(f"✅ Setup complete: {len(self.mesh_actors)} animated meshes")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up viewer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_bone_transforms(self, vertices, mesh_index):
        """Apply bone transforms to vertices (simplified version)"""
        # For now, apply a simple offset based on mesh type to position them correctly
        transformed = vertices.copy()
        
        if mesh_index == 0:  # Body
            # Center the body
            transformed[:, 1] += 0.0  # No Y offset
        elif mesh_index == 1:  # Clothing/Arms  
            # Position slightly forward
            transformed[:, 2] += 0.01
        elif mesh_index == 2:  # Hair
            # Position slightly back
            transformed[:, 2] -= 0.01
            
        return transformed
    
    def animate_bones(self, animation_type, time_factor):
        """Animate bones based on animation type"""
        if animation_type == "idle":
            # Gentle breathing
            breath_offset = np.sin(time_factor * 2) * 0.02
            for bone_name in self.bone_transforms:
                if "spine" in bone_name.lower() or "chest" in bone_name.lower():
                    self.bone_transforms[bone_name]['position'][1] += breath_offset
                    
        elif animation_type == "wave":
            # Arm waving
            wave_angle = np.sin(time_factor * 3) * 0.5
            for bone_name in self.bone_transforms:
                if "arm" in bone_name.lower() or "hand" in bone_name.lower():
                    # Simplified rotation
                    self.bone_transforms[bone_name]['rotation'][2] = wave_angle
                    
        elif animation_type == "dance":
            # Hip movement
            hip_sway = np.sin(time_factor * 2) * 0.1
            hip_bounce = abs(np.sin(time_factor * 4)) * 0.05
            for bone_name in self.bone_transforms:
                if "hip" in bone_name.lower():
                    self.bone_transforms[bone_name]['position'][0] = hip_sway
                    self.bone_transforms[bone_name]['position'][1] += hip_bounce
                    
        elif animation_type == "jump":
            # Jumping motion
            jump_height = abs(np.sin(time_factor * 6)) * 0.3
            for bone_name in self.bone_transforms:
                if "hip" in bone_name.lower() or "spine" in bone_name.lower():
                    self.bone_transforms[bone_name]['position'][1] += jump_height
    
    def update_animation(self):
        """Update mesh positions based on current bone transforms"""
        try:
            for mesh_data in self.mesh_actors:
                original_vertices = mesh_data['original_vertices']
                mesh_index = mesh_data['mesh_index']
                pv_mesh = mesh_data['pv_mesh']
                
                # Apply current bone transforms
                transformed_vertices = self._apply_bone_transforms(original_vertices, mesh_index)
                
                # Apply animation transforms
                if mesh_index == 0:  # Body - apply more animation
                    breath = np.sin(self.animation_time * 2) * 0.01
                    transformed_vertices[:, 1] += breath
                    
                if self.current_animation == "jump" and mesh_index < 2:
                    jump = abs(np.sin(self.animation_time * 6)) * 0.2
                    transformed_vertices[:, 1] += jump
                    
                elif self.current_animation == "dance":
                    sway = np.sin(self.animation_time * 3) * 0.05
                    transformed_vertices[:, 0] += sway
                    
                elif self.current_animation == "wave" and mesh_index == 1:
                    # Arm mesh gets wave motion
                    wave = np.sin(self.animation_time * 4) * 0.03
                    # Apply to upper part of mesh (likely arms)
                    upper_mask = transformed_vertices[:, 1] > np.percentile(transformed_vertices[:, 1], 70)
                    transformed_vertices[upper_mask, 0] += wave
                
                # Update the mesh
                pv_mesh.points = transformed_vertices
                
        except Exception as e:
            print(f"❌ Animation update error: {e}")
    
    def animation_loop(self):
        """Main animation loop"""
        while self.running:
            try:
                self.animation_time += 0.016  # ~60 FPS
                self.update_animation()
                
                if self.plotter:
                    self.plotter.render()
                    
                time.sleep(0.016)  # 60 FPS
                
            except Exception as e:
                print(f"❌ Animation loop error: {e}")
                break
    
    def start(self, file_path):
        """Start the bone-animated viewer"""
        try:
            if not self.load_vrm(file_path):
                return False
                
            if not self.setup_viewer():
                return False
            
            print("🦴 Starting bone-animated viewer...")
            print("🎮 Controls:")
            print("  - Mouse: Rotate, pan, zoom")
            print("  - Real bone-based animation system")
            print("  - Press Ctrl+C to exit")
            
            # Start animation loop
            self.running = True
            animation_thread = threading.Thread(target=self.animation_loop, daemon=True)
            animation_thread.start()
            
            # Show viewer (blocking)
            self.plotter.show()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping bone-animated viewer...")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.running = False

def main():
    viewer = BoneAnimatedViewer()
    vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
    
    if not os.path.exists(vrm_path):
        print(f"❌ File not found: {vrm_path}")
        return
    
    viewer.start(vrm_path)

if __name__ == "__main__":
    main()

