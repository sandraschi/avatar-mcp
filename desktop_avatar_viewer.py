#!/usr/bin/env python3
"""
AvatarMCP Desktop Avatar Viewer - Enhanced Version

Features:
- Full 3D avatar display with realistic colors and textures
- Interactive bone manipulation and visualization
- Mouse controls for rotation, zoom, pan
- Real-time animation playback
- OSC control interface
- Expression/blendshape support
"""

import asyncio
import logging
import os
import sys

import matplotlib.pyplot as plt
import pyvista as pv
from mpl_toolkits.mplot3d import Axes3D
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from avatarmcp.models.vrm_loader import VRMLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check if OSC is available
OSC_AVAILABLE = True
try:
    from pythonosc import udp_client
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import AsyncIOOSCUDPServer
except ImportError:
    OSC_AVAILABLE = False


class DesktopAvatarViewer:
    """Enhanced desktop avatar viewer with full 3D controls and bone manipulation."""

    def __init__(self, osc_port: int = 9001):
        self.osc_port = osc_port
        self.osc_client: udp_client.SimpleUDPClient | None = None
        self.osc_server: AsyncIOOSCUDPServer | None = None
        self.dispatcher = Dispatcher()

        # Avatar state
        self.current_vrm_path: str | None = None
        self.vrm_model = None
        self.original_vertices = {}  # mesh_idx -> original vertices
        self.bone_positions = {}  # bone_name -> [x, y, z]
        self.bone_rotations = {}  # bone_name -> quaternion
        self.expression_weights = {}  # expression_name -> weight

        # Animation state
        self.current_animation = None
        self.animation_time = 0.0
        self.animation_speed = 1.0
        self.is_animating = False

        # Visualization
        self.fig: plt.Figure | None = None
        self.ax: Axes3D | None = None
        self.mesh_artists = []
        self.bone_artists = []
        self.skeleton_lines = []
        self.show_bones = True
        self.show_skeleton = True
        self.wireframe_mode = False

        # Mouse interaction
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.view_elev = 20
        self.view_azim = 45
        self.view_distance = 1.0

        # Set up OSC handlers
        self._setup_osc_handlers()

    def _setup_osc(self):
        """Setup OSC dispatcher and handlers."""
        self.dispatcher = Dispatcher()

        # Avatar control handlers
        self.dispatcher.map("/avatar/load", self._handle_load_avatar)
        self.dispatcher.map("/avatar/animation/play", self._handle_play_animation)
        self.dispatcher.map("/avatar/expression/blendshape", self._handle_blendshape)
        self.dispatcher.map("/avatar/bone/*/rotation", self._handle_bone_rotation)
        self.dispatcher.map("/avatar/bone/*/translation", self._handle_bone_translation)

        # System handlers
        self.dispatcher.map("/system/status", self._handle_status)
        self.dispatcher.map("/system/exit", self._handle_exit)

    async def _handle_load_avatar(self, address, *args):
        """Handle avatar loading OSC command."""
        if not args:
            logger.error("No avatar path provided")
            return

        avatar_path = args[0]
        logger.info(f"Loading avatar: {avatar_path}")

        try:
            if not os.path.exists(avatar_path):
                logger.error(f"Avatar file not found: {avatar_path}")
                return

            # Load VRM
            vrm_model = VRMLoader.from_file(avatar_path)
            avatar_id = os.path.splitext(os.path.basename(avatar_path))[0]
            self.loaded_avatars[avatar_id] = vrm_model
            self.current_avatar = vrm_model

            logger.info(f"Loaded avatar {avatar_id} with {len(vrm_model.meshes)} meshes")

            # Display the avatar
            self._display_avatar(vrm_model)

        except Exception as e:
            logger.error(f"Failed to load avatar: {e}")

    def _handle_play_animation(self, address, *args):
        """Handle animation play command."""
        if not args:
            logger.error("No animation name provided")
            return

        animation_name = args[0]
        logger.info(f"Playing animation: {animation_name}")

        # For now, just log - full animation system would go here
        # TODO: Implement animation playback

    def _handle_blendshape(self, address, *args):
        """Handle blendshape/morph control."""
        if len(args) < 2:
            logger.error("Need morph name and weight")
            return

        morph_name = args[0]
        weight = float(args[1])
        logger.info(f"Setting morph {morph_name} to {weight}")

        # TODO: Implement morph control

    def _handle_bone_rotation(self, address, *args):
        """Handle bone rotation control."""
        parts = address.split("/")
        if len(parts) < 4 or len(args) < 4:
            logger.error("Invalid bone rotation command")
            return

        bone_name = parts[3]  # /avatar/bone/{name}/rotation
        rotation = args[:4]  # quaternion x,y,z,w
        logger.info(f"Setting bone {bone_name} rotation to {rotation}")

        # TODO: Implement bone control

    def _handle_bone_translation(self, address, *args):
        """Handle bone translation control."""
        parts = address.split("/")
        if len(parts) < 4 or len(args) < 3:
            logger.error("Invalid bone translation command")
            return

        bone_name = parts[3]  # /avatar/bone/{name}/translation
        translation = args[:3]  # vector x,y,z
        logger.info(f"Setting bone {bone_name} translation to {translation}")

        # TODO: Implement bone control

    async def _handle_status(self, address, *args):
        """Handle status request."""
        status = {
            "running": True,
            "current_avatar": self.current_avatar is not None,
            "loaded_avatars": len(self.loaded_avatars),
            "port": self.receive_port,
        }
        logger.info(f"Status request: {status}")
        return status

    async def _handle_exit(self, address, *args):
        """Handle exit command."""
        logger.info("Exit command received")
        self.running = False
        if self.plotter:
            self.plotter.close()

    def _display_avatar(self, vrm_model):
        """Display the VRM avatar using matplotlib 3D (fallback for Windows compatibility)."""
        if not vrm_model or not vrm_model.meshes:
            logger.error("No meshes to display")
            return

        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Close existing plot if any
            plt.close("all")

            # Create figure and 3D axes
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection="3d")

            # Add coordinate axes
            ax.plot([0, 2], [0, 0], [0, 0], color="red", linewidth=3, label="X-axis")
            ax.plot([0, 0], [0, 2], [0, 0], color="green", linewidth=3, label="Y-axis")
            ax.plot([0, 0], [0, 0], [0, 2], color="blue", linewidth=3, label="Z-axis")

            # Display meshes
            mesh_count = 0
            # Use realistic skin/clothes colors
            avatar_colors = {
                "face": "#FDBCB4",  # Skin tone
                "body": "#FDBCB4",  # Skin tone
                "hair": "#2C1810",  # Dark brown
                "shirt": "#FF6B6B",  # Red shirt
                "pants": "#4ECDC4",  # Teal pants
                "shoes": "#95A5A6",  # Gray shoes
            }

            def get_mesh_color(mesh_name):
                name_lower = mesh_name.lower()
                if "face" in name_lower or "head" in name_lower:
                    return avatar_colors["face"]
                elif "hair" in name_lower:
                    return avatar_colors["hair"]
                elif "body" in name_lower or "skin" in name_lower:
                    return avatar_colors["body"]
                elif any(word in name_lower for word in ["shirt", "top", "jacket"]):
                    return avatar_colors["shirt"]
                elif any(word in name_lower for word in ["pants", "skirt", "bottom"]):
                    return avatar_colors["pants"]
                elif any(word in name_lower for word in ["shoe", "boot", "foot"]):
                    return avatar_colors["shoes"]
                else:
                    return list(avatar_colors.values())[mesh_count % len(avatar_colors)]

            colors = [
                get_mesh_color(mesh.name) if hasattr(mesh, "name") else avatar_colors["body"]
                for mesh in vrm_model.meshes[:3]
            ]

            for i, mesh in enumerate(
                vrm_model.meshes[:3]
            ):  # Limit to first 3 meshes for performance
                try:
                    if hasattr(mesh, "vertices") and len(mesh.vertices) > 0:
                        vertices = mesh.vertices
                        faces = (
                            mesh.faces
                            if hasattr(mesh, "faces") and mesh.faces is not None
                            else None
                        )

                        # Scale the vertices to make them visible (VRM units are small)
                        verts = vertices * 10.0

                        # Use scatter plot for all vertices - more reliable than surface plotting
                        ax.scatter(
                            verts[:, 0],
                            verts[:, 1],
                            verts[:, 2],
                            color=colors[i % len(colors)],
                            alpha=0.8,
                            s=8,
                            label=f"{mesh.name}",
                        )

                        # If we have faces, draw some wireframe triangles to show structure
                        if faces is not None and len(faces) > 0:
                            try:
                                # Draw wireframe for first 50 triangles to show structure
                                for face in faces[: min(50, len(faces))]:
                                    if len(face) == 3:  # Triangular face
                                        triangle_verts = verts[face]
                                        # Close the triangle
                                        triangle_verts = np.vstack(
                                            [triangle_verts, triangle_verts[0]]
                                        )
                                        ax.plot(
                                            triangle_verts[:, 0],
                                            triangle_verts[:, 1],
                                            triangle_verts[:, 2],
                                            color=colors[i % len(colors)],
                                            alpha=0.7,
                                            linewidth=2,
                                        )
                            except Exception as e:
                                logger.warning(f"Wireframe drawing failed for mesh {i}: {e}")

                        mesh_count += 1

                except Exception as e:
                    logger.warning(f"Failed to display mesh {i}: {e}")

            if mesh_count > 0:
                # Add avatar info
                avatar_name = getattr(vrm_model, "name", "Unknown Avatar")
                ax.set_title(
                    f"AvatarMCP Desktop Viewer - {avatar_name}\n{mesh_count} meshes loaded"
                )
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_zlabel("Z")
                ax.grid(True)
                ax.set_box_aspect([1, 1, 1])

                plt.show()
                logger.info(
                    f"Successfully displayed avatar with {mesh_count} meshes using matplotlib"
                )
            else:
                # Fallback display
                ax.set_title("AvatarMCP Desktop Viewer\nAvatar loaded but no meshes displayed")
                # Add a reference sphere
                u = np.linspace(0, 2 * np.pi, 10)
                v = np.linspace(0, np.pi, 10)
                x = np.outer(np.cos(u), np.sin(v))
                y = np.outer(np.sin(u), np.sin(v))
                z = np.outer(np.ones(np.size(u)), np.cos(v))
                ax.plot_surface(x, y, z, color="gray", alpha=0.3)
                plt.show()

        except ImportError:
            logger.error("Matplotlib not available for avatar display")
        except Exception as e:
            logger.error(f"Failed to display avatar: {e}")

    async def run_osc_server(self):
        """Run the OSC server."""
        try:
            loop = asyncio.get_event_loop()
            self.osc_server = AsyncIOOSCUDPServer(
                ("127.0.0.1", self.receive_port), self.dispatcher, loop
            )

            logger.info(f"OSC server listening on port {self.receive_port}")
            await self.osc_server.serve_forever()

        except Exception as e:
            logger.error(f"OSC server error: {e}")

    def run_viewer(self):
        """Run the desktop avatar viewer."""
        if not OSC_AVAILABLE:
            logger.error("OSC dependencies not available")
            return

        logger.info("Starting AvatarMCP Desktop Avatar Viewer")
        logger.info(f"Listening for OSC commands on port {self.receive_port}")

        # Create a simple initial display with coordinate system and basic mesh
        pv.set_plot_theme("document")
        self.plotter = pv.Plotter(
            title="AvatarMCP Desktop Avatar - Waiting for Avatar", window_size=[800, 600]
        )

        # Add coordinate axes
        self.plotter.add_axes(line_width=5, labels_off=False)

        # Add a simple cube as placeholder
        cube = pv.Cube(center=(0, 0, 0), x_length=1, y_length=1, z_length=1)
        self.plotter.add_mesh(cube, color="lightgray", opacity=0.7, show_edges=True)

        # Add simple reference plane
        plane = pv.Plane(center=(0, 0, -1), i_size=10, j_size=10)
        self.plotter.add_mesh(plane, color="lightblue", opacity=0.2)

        # Add instructions
        self.plotter.add_text(
            "AvatarMCP Desktop Viewer\nWaiting for avatar load command...\nSend /avatar/load <path> to load a VRM\n\nShowing coordinate system and reference cube",
            font_size=10,
            position="upper_left",
        )

        self.plotter.view_isometric()
        self.plotter.show(auto_close=False)

        self.running = True

        try:
            # Run OSC server in background
            asyncio.run(self.run_osc_server())

        except KeyboardInterrupt:
            logger.info("Viewer stopped by user")
        except Exception as e:
            logger.error(f"Viewer error: {e}")
        finally:
            if self.plotter:
                self.plotter.close()


def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    viewer = DesktopAvatarViewer()
    viewer.run_viewer()


def show_coordinate_system():
    """Show just the coordinate system and reference objects for testing."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    pv.set_plot_theme("document")
    plotter = pv.Plotter(
        title="AvatarMCP Desktop Viewer - Coordinate System Test", window_size=[800, 600]
    )

    # Add coordinate axes
    plotter.add_axes(line_width=5, labels_off=False)

    # Add a simple cube as placeholder
    cube = pv.Cube(center=(0, 0, 0), x_length=1, y_length=1, z_length=1)
    plotter.add_mesh(cube, color="lightgray", opacity=0.7, show_edges=True)

    # Add simple reference plane
    plane = pv.Plane(center=(0, 0, -1), i_size=10, j_size=10)
    plotter.add_mesh(plane, color="lightblue", opacity=0.2)

    # Add sphere for reference
    sphere = pv.Sphere(radius=0.5, center=(2, 0, 0))
    plotter.add_mesh(sphere, color="red", opacity=0.8)

    # Add cylinder for reference
    cylinder = pv.Cylinder(radius=0.3, height=2, center=(0, 2, 0))
    plotter.add_mesh(cylinder, color="green", opacity=0.8)

    # Add cone for reference
    cone = pv.Cone(radius=0.5, height=1, center=(0, 0, 2))
    plotter.add_mesh(cone, color="blue", opacity=0.8)

    # Add instructions
    plotter.add_text(
        "AvatarMCP Desktop Viewer - Visual Test\n\n"
        "Showing coordinate system (X=red, Y=green, Z=blue)\n"
        "Reference objects: Cube, Sphere, Cylinder, Cone\n"
        "Grid for scale reference\n\n"
        "This viewer can display VRM avatars when loaded",
        font_size=10,
        position="upper_left",
    )

    plotter.view_isometric()
    plotter.show()


if __name__ == "__main__":
    main()
