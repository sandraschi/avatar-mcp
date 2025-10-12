#!/usr/bin/env python3
"""
Desktop Avatar Viewer - OSC-controlled VRM avatar display
Immediate replacement for Unity desktop avatar until Unity is available
"""
import sys
import os
import threading
import time
import logging
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, 'src')

# Import required libraries
try:
    from pythonosc import dispatcher, osc_server, udp_client
    from pythonosc.osc_server import AsyncIOOSCUDPServer
    import asyncio
    import pyvista as pv
    from avatarmcp.models.vrm_loader import VRMLoader
    OSC_AVAILABLE = True
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install python-osc pyvista trimesh pygltflib")
    OSC_AVAILABLE = False

logger = logging.getLogger(__name__)

class DesktopAvatarViewer:
    """Desktop avatar viewer that receives OSC commands and displays VRM avatars."""

    def __init__(self):
        self.osc_server: Optional[AsyncIOOSCUDPServer] = None
        self.plotter: Optional[pv.Plotter] = None
        self.current_avatar: Optional[Any] = None
        self.loaded_avatars: Dict[str, Any] = {}
        self.running = False

        # OSC settings
        self.receive_port = 9000  # Listen for commands from MCP
        self.send_port = 9001     # Send responses back

        # Setup OSC
        if OSC_AVAILABLE:
            self._setup_osc()

    def _setup_osc(self):
        """Setup OSC dispatcher and handlers."""
        self.dispatcher = dispatcher.Dispatcher()

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
        parts = address.split('/')
        if len(parts) < 4 or len(args) < 4:
            logger.error("Invalid bone rotation command")
            return

        bone_name = parts[3]  # /avatar/bone/{name}/rotation
        rotation = args[:4]  # quaternion x,y,z,w
        logger.info(f"Setting bone {bone_name} rotation to {rotation}")

        # TODO: Implement bone control

    def _handle_bone_translation(self, address, *args):
        """Handle bone translation control."""
        parts = address.split('/')
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
            "port": self.receive_port
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
        """Display the VRM avatar in a PyVista window."""
        if not vrm_model or not vrm_model.meshes:
            logger.error("No meshes to display")
            return

        # Close existing plotter
        if self.plotter:
            self.plotter.close()

        # Create new plotter
        pv.set_plot_theme('document')
        self.plotter = pv.Plotter(title="AvatarMCP Desktop Avatar", window_size=[800, 1000])

        # Display first mesh (face)
        mesh = vrm_model.meshes[0]  # Face mesh
        logger.info(f"Displaying mesh: {mesh.name}")

        try:
            pv_faces = mesh.get_pyvista_faces()
            vrm_mesh = pv.PolyData(mesh.vertices, pv_faces)

            # Center the mesh
            vrm_mesh.translate([-vrm_mesh.center[0], -vrm_mesh.center[1] - 1.3, -vrm_mesh.center[2]])

            self.plotter.add_mesh(vrm_mesh, color='lightblue', show_edges=False)
            self.plotter.view_isometric()
            self.plotter.show(auto_close=False)

        except Exception as e:
            logger.error(f"Failed to display mesh: {e}")

    async def run_osc_server(self):
        """Run the OSC server."""
        try:
            loop = asyncio.get_event_loop()
            self.osc_server = AsyncIOOSCUDPServer(
                ("127.0.0.1", self.receive_port),
                self.dispatcher,
                loop
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

        # Create a simple initial display
        pv.set_plot_theme('document')
        self.plotter = pv.Plotter(title="AvatarMCP Desktop Avatar - Waiting for Avatar", window_size=[800, 600])
        self.plotter.add_text("Waiting for avatar load command...\nSend /avatar/load <path> to load a VRM", font_size=12)
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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    viewer = DesktopAvatarViewer()
    viewer.run_viewer()


if __name__ == "__main__":
    main()
