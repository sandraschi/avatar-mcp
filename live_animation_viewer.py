#!/usr/bin/env python3
"""
Live Animation Viewer for Nekomimi-chan
Direct integration with PyVista for real-time animation display
"""
import sys
import os
import time
import threading
import numpy as np
sys.path.insert(0, 'src')

class LiveAnimationViewer:
    def __init__(self):
        self.vrm_model = None
        self.plotter = None
        self.meshes = []
        self.current_animation = "idle"
        self.animation_time = 0.0
        self.running = False
        
    def load_vrm(self, file_path):
        """Load the VRM model"""
        try:
            from avatarmcp.models.vrm_loader import VRMLoader
            print(f"🎌 Loading VRM: {file_path}")
            self.vrm_model = VRMLoader.from_file(file_path)
            print(f"✅ Loaded: {len(self.vrm_model.meshes)} meshes, {len(self.vrm_model.bones)} bones")
            return True
        except Exception as e:
            print(f"❌ Error loading VRM: {e}")
            return False
    
    def setup_viewer(self):
        """Setup PyVista viewer"""
        try:
            import pyvista as pv
            pv.set_plot_theme('document')
            
            self.plotter = pv.Plotter(
                window_size=[1024, 768],
                title="🎌 Nekomimi-chan Live Animation Viewer"
            )
            
            # Add meshes to viewer
            if self.vrm_model and self.vrm_model.meshes:
                for i, mesh in enumerate(self.vrm_model.meshes):
                    if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                        if len(mesh.vertices) > 0 and len(mesh.faces) > 0:
                            # Convert to PyVista format
                            vertices = np.array(mesh.vertices)
                            faces = np.array(mesh.faces)
                            
                            # Create PyVista mesh
                            if len(faces.shape) == 2 and faces.shape[1] == 3:
                                pv_faces = []
                                for face in faces:
                                    pv_faces.extend([3] + list(face))
                                pv_mesh = pv.PolyData(vertices, pv_faces)
                            else:
                                pv_mesh = pv.PolyData(vertices)
                            
                            # Add to plotter with different colors
                            colors = ['lightpink', 'lightblue', 'lightgreen']
                            color = colors[i % len(colors)]
                            self.plotter.add_mesh(pv_mesh, color=color, opacity=0.9, name=f"mesh_{i}")
                            self.meshes.append(pv_mesh)
                            print(f"  ✅ Added mesh {i}: {len(vertices)} vertices")
            
            # Add coordinate system and grid
            self.plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z')
            self.plotter.show_grid()
            self.plotter.camera_position = 'iso'
            
            return True
        except Exception as e:
            print(f"❌ Error setting up viewer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def animate_mesh(self, mesh_index, animation_name, time_factor):
        """Apply simple animation to a mesh"""
        if mesh_index < len(self.meshes):
            mesh = self.meshes[mesh_index]
            
            # Simple animations based on time
            if animation_name == "wave":
                # Wave-like motion
                wave_amplitude = 0.1
                wave_freq = 2.0
                offset = np.sin(time_factor * wave_freq) * wave_amplitude
                mesh.points[:, 1] += offset
                
            elif animation_name == "dance":
                # Rhythmic dance motion
                dance_amplitude = 0.05
                dance_freq = 1.5
                offset_x = np.sin(time_factor * dance_freq) * dance_amplitude
                offset_z = np.cos(time_factor * dance_freq * 0.7) * dance_amplitude
                mesh.points[:, 0] += offset_x
                mesh.points[:, 2] += offset_z
                
            elif animation_name == "jump":
                # Jumping motion
                jump_amplitude = 0.3
                jump_freq = 3.0
                offset_y = abs(np.sin(time_factor * jump_freq)) * jump_amplitude
                mesh.points[:, 1] += offset_y
                
            elif animation_name == "bow":
                # Bowing motion
                bow_amplitude = 0.2
                bow_freq = 0.8
                angle = np.sin(time_factor * bow_freq) * bow_amplitude
                # Simple rotation around X axis
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                for point in mesh.points:
                    y, z = point[1], point[2]
                    point[1] = y * cos_a - z * sin_a
                    point[2] = y * sin_a + z * cos_a
    
    def animation_loop(self):
        """Animation update loop"""
        while self.running:
            try:
                # Update animation time
                self.animation_time += 0.016  # ~60 FPS
                
                # Apply animations to meshes
                for i in range(len(self.meshes)):
                    self.animate_mesh(i, self.current_animation, self.animation_time)
                
                # Update the plotter
                if self.plotter:
                    self.plotter.render()
                
                time.sleep(0.016)  # ~60 FPS
                
            except Exception as e:
                print(f"❌ Animation error: {e}")
                break
    
    def start(self, file_path):
        """Start the live animation viewer"""
        try:
            # Load VRM
            if not self.load_vrm(file_path):
                return False
            
            # Setup viewer
            if not self.setup_viewer():
                return False
            
            print("🚀 Starting live animation viewer...")
            print("🎮 Controls:")
            print("  - Mouse: Rotate, pan, zoom")
            print("  - Use MCP commands to change animations")
            print("  - Press Ctrl+C to exit")
            
            # Start animation loop in background
            self.running = True
            animation_thread = threading.Thread(target=self.animation_loop, daemon=True)
            animation_thread.start()
            
            # Show the viewer (this blocks until window is closed)
            self.plotter.show()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping viewer...")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.running = False

def main():
    viewer = LiveAnimationViewer()
    vrm_path = r'C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm'
    
    if not os.path.exists(vrm_path):
        print(f"❌ File not found: {vrm_path}")
        return
    
    viewer.start(vrm_path)

if __name__ == "__main__":
    main()
