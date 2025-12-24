#!/usr/bin/env python3
"""
Enhanced VRM Viewer - Properly identifies and positions mesh components
"""

import os
import sys

import numpy as np

sys.path.insert(0, "src")


class EnhancedVRMViewer:
    def __init__(self):
        self.vrm_model = None
        self.plotter = None
        self.mesh_components = []
        self.running = False
        self.animation_time = 0.0
        self.current_animation = "idle"

    def load_vrm(self, file_path):
        """Load VRM with mesh classification"""
        try:
            from avatarmcp.models.vrm_loader import VRMLoader

            print(f"🎌 Loading VRM with enhanced parsing: {file_path}")
            self.vrm_model = VRMLoader.from_file(file_path)
            print(
                f"✅ Loaded: {len(self.vrm_model.meshes)} meshes, {len(self.vrm_model.bones)} bones"
            )

            # Analyze and classify meshes
            self._classify_meshes()
            return True

        except Exception as e:
            print(f"❌ Error loading VRM: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _classify_meshes(self):
        """Classify meshes by type and content"""
        print("\n🔍 MESH CLASSIFICATION:")

        for i, mesh in enumerate(self.vrm_model.meshes):
            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.int32)

            # Calculate mesh properties
            vertex_count = len(vertices)
            face_count = len(faces)

            # Calculate bounding box
            min_bounds = vertices.min(axis=0)
            max_bounds = vertices.max(axis=0)
            center = (min_bounds + max_bounds) / 2
            size = max_bounds - min_bounds

            # Calculate vertex density (vertices per unit volume)
            volume = np.prod(size) if np.all(size > 0) else 1
            density = vertex_count / volume

            # Classify based on properties
            mesh_type = self._determine_mesh_type(i, vertex_count, center, size, density)

            print(f"--- MESH {i} ({mesh_type}) ---")
            print(f"  Vertices: {vertex_count}")
            print(f"  Faces: {face_count}")
            print(f"  Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            print(f"  Size: ({size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f})")
            print(f"  Density: {density:.1f} verts/unit³")
            print(f"  Type: {mesh_type}")

            # Store classification
            mesh_info = {
                "index": i,
                "type": mesh_type,
                "vertices": vertices,
                "faces": faces,
                "vertex_count": vertex_count,
                "center": center,
                "size": size,
                "density": density,
            }
            self.mesh_components.append(mesh_info)

    def _determine_mesh_type(
        self, index: int, vertex_count: int, center: np.ndarray, size: np.ndarray, density: float
    ) -> str:
        """Determine mesh type based on properties"""

        # Analysis based on typical VRM structure
        if index == 0:
            # First mesh is usually the body/face
            if vertex_count < 6000:
                return "Face/Head"
            else:
                return "Body/Torso"
        elif index == 1:
            # Second mesh is often clothing or body parts
            if vertex_count > 8000:
                return "Clothing/Outfit"
            else:
                return "Arms/Limbs"
        elif index == 2:
            # Third mesh is typically hair
            if center[1] > 1.0:  # High Y position
                return "Hair"
            else:
                return "Accessories"
        else:
            return "Other"

    def setup_viewer(self):
        """Setup PyVista viewer with proper mesh classification"""
        try:
            import pyvista as pv

            pv.set_plot_theme("document")

            self.plotter = pv.Plotter(
                window_size=[1400, 1000], title="🎌 Enhanced AnimeGirl2 Viewer"
            )

            if not self.mesh_components:
                print("❌ No mesh components classified")
                return False

            # Render each mesh component with appropriate settings
            for mesh_info in self.mesh_components:
                try:
                    vertices = mesh_info["vertices"]
                    faces = mesh_info["faces"]
                    mesh_type = mesh_info["type"]
                    index = mesh_info["index"]

                    # Apply type-specific positioning and styling
                    positioned_vertices = self._position_mesh_by_type(vertices, mesh_type, index)

                    # Convert to PyVista format
                    if len(faces) > 0 and faces.shape[1] == 3:
                        pv_faces = []
                        for face in faces:
                            if all(face < len(positioned_vertices)):
                                pv_faces.extend([3, face[0], face[1], face[2]])

                        if len(pv_faces) > 0:
                            pv_mesh = pv.PolyData(positioned_vertices, pv_faces)

                            # Type-specific styling
                            color, opacity = self._get_mesh_style(mesh_type)

                            self.plotter.add_mesh(
                                pv_mesh,
                                color=color,
                                opacity=opacity,
                                smooth_shading=True,
                                show_edges=False,
                                name=f"{mesh_type}_{index}",
                            )

                            print(f"  ✅ Rendered {mesh_type}: {len(positioned_vertices)} vertices")
                        else:
                            print(f"  ⚠️ {mesh_type}: No valid faces")
                    else:
                        print(f"  ⚠️ {mesh_type}: Invalid face data")

                except Exception as e:
                    print(f"  ❌ Error rendering {mesh_info['type']}: {e}")

            # Add coordinate system and lighting
            self.plotter.add_axes(xlabel="X", ylabel="Y", zlabel="Z")
            self.plotter.show_grid()

            # Set camera for full body view
            self.plotter.camera_position = [(3, 2, 3), (0, 1, 0), (0, 0, 1)]
            self.plotter.enable_trackball_style()

            print("\n✅ Enhanced viewer setup complete!")
            return True

        except Exception as e:
            print(f"❌ Error setting up enhanced viewer: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _position_mesh_by_type(
        self, vertices: np.ndarray, mesh_type: str, index: int
    ) -> np.ndarray:
        """Position mesh vertices based on their type"""
        positioned = vertices.copy()

        if "Body" in mesh_type or "Torso" in mesh_type:
            # Body should be centered
            positioned[:, 1] += 0.0  # No Y offset
            positioned[:, 2] += 0.0  # No Z offset

        elif "Face" in mesh_type or "Head" in mesh_type:
            # Face/head should be slightly forward
            positioned[:, 2] += 0.02

        elif "Clothing" in mesh_type or "Outfit" in mesh_type:
            # Clothing should be slightly outside body
            positioned[:, 2] += 0.005

        elif "Arms" in mesh_type or "Limbs" in mesh_type:
            # Arms should connect to shoulders
            # Find likely shoulder connection points
            shoulder_mask = (positioned[:, 1] > np.percentile(positioned[:, 1], 80)) & (
                np.abs(positioned[:, 0]) > np.percentile(np.abs(positioned[:, 0]), 60)
            )
            # Slight inward adjustment for better connection
            positioned[shoulder_mask, 2] -= 0.01

        elif "Hair" in mesh_type:
            # Hair should be positioned on head
            positioned[:, 2] -= 0.01  # Slightly back
            positioned[:, 1] += 0.02  # Slightly up

        elif "Accessories" in mesh_type:
            # Accessories get slight forward positioning
            positioned[:, 2] += 0.01

        return positioned

    def _get_mesh_style(self, mesh_type: str) -> tuple[str, float]:
        """Get color and opacity for mesh type"""
        styles = {
            "Face/Head": ("lightsalmon", 1.0),
            "Body/Torso": ("lightpink", 0.95),
            "Clothing/Outfit": ("lightblue", 0.9),
            "Arms/Limbs": ("lightcoral", 0.95),
            "Hair": ("darkseagreen", 0.9),
            "Accessories": ("lightgoldenrodyellow", 0.8),
            "Other": ("lightgray", 0.7),
        }
        return styles.get(mesh_type, ("lightgray", 0.8))

    def start(self, file_path):
        """Start the enhanced VRM viewer"""
        try:
            if not self.load_vrm(file_path):
                return False

            if not self.setup_viewer():
                return False

            print("\n🎌 Starting Enhanced VRM Viewer...")
            print("🎮 Features:")
            print("  - Intelligent mesh classification")
            print("  - Proper component positioning")
            print("  - Type-aware rendering")
            print("  - Mouse: Rotate, pan, zoom")
            print("  - Press Ctrl+C to exit")

            # Show viewer (blocking)
            self.plotter.show()

            return True

        except KeyboardInterrupt:
            print("\n🛑 Stopping enhanced viewer...")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    viewer = EnhancedVRMViewer()
    vrm_path = r"D:\Dev\repos\avatarmcp\models\AnimeGirl2.vrm"

    if not os.path.exists(vrm_path):
        print(f"❌ File not found: {vrm_path}")
        return

    viewer.start(vrm_path)


if __name__ == "__main__":
    main()
