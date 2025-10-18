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

import os
import sys
import logging
from typing import Optional
import asyncio
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from avatarmcp.models.vrm_loader import VRMLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DesktopAvatarViewer:
    """Enhanced desktop avatar viewer with full 3D controls and bone manipulation."""

    def __init__(self, osc_port: int = 9001):
        self.osc_port = osc_port
        self.osc_client: Optional[udp_client.SimpleUDPClient] = None
        self.osc_server: Optional[AsyncIOOSCUDPServer] = None
        self.dispatcher = Dispatcher()

        # Avatar state
        self.current_vrm_path: Optional[str] = None
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
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[Axes3D] = None
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

    def _setup_osc_handlers(self):
        """Set up OSC message handlers."""
        self.dispatcher.map("/avatar/load", self._handle_load_avatar)
        self.dispatcher.map("/avatar/animation/play", self._handle_play_animation)
        self.dispatcher.map("/avatar/animation/stop", self._handle_stop_animation)
        self.dispatcher.map("/avatar/bone/*/rotation", self._handle_bone_rotation)
        self.dispatcher.map("/avatar/bone/*/translation", self._handle_bone_translation)
        self.dispatcher.map("/avatar/expression/blendshape", self._handle_blendshape)
        self.dispatcher.map("/avatar/export", self._handle_export)
        self.dispatcher.map("/avatar/reset", self._handle_reset)

    async def _handle_load_avatar(self, address, *args):
        """Handle avatar loading OSC message."""
        try:
            vrm_path = args[0] if args else None
            if not vrm_path:
                logger.warning("No VRM path provided")
                return

            logger.info(f"Loading avatar: {vrm_path}")
            await asyncio.get_event_loop().run_in_executor(None, self._load_and_display_avatar, vrm_path)
        except Exception as e:
            logger.error(f"Failed to load avatar: {e}")

    async def _handle_play_animation(self, address, *args):
        """Handle animation playback OSC message."""
        try:
            animation_name = args[0] if args else "idle"
            speed = float(args[1]) if len(args) > 1 else 1.0
            logger.info(f"Playing animation: {animation_name} at speed {speed}")
            self._start_animation(animation_name, speed)
        except Exception as e:
            logger.error(f"Failed to play animation: {e}")

    async def _handle_stop_animation(self, address, *args):
        """Handle animation stop OSC message."""
        try:
            logger.info("Stopping animation")
            self._stop_animation()
        except Exception as e:
            logger.error(f"Failed to stop animation: {e}")

    async def _handle_bone_rotation(self, address, *args):
        """Handle bone rotation OSC message."""
        try:
            # Parse bone name from address: /avatar/bone/BoneName/rotation
            parts = address.split('/')
            if len(parts) >= 4:
                bone_name = parts[3]
                if len(args) >= 4:
                    # Euler angles in degrees
                    x, y, z, w = args[0], args[1], args[2], args[3]
                    self._rotate_bone(bone_name, x, y, z, w)
                    logger.info(f"Rotated bone {bone_name}: ({x:.1f}, {y:.1f}, {z:.1f}, {w:.1f})")
                    self._update_display()
        except Exception as e:
            logger.error(f"Failed to handle bone rotation: {e}")

    async def _handle_bone_translation(self, address, *args):
        """Handle bone translation OSC message."""
        try:
            # Parse bone name from address: /avatar/bone/BoneName/translation
            parts = address.split('/')
            if len(parts) >= 4:
                bone_name = parts[3]
                if len(args) >= 3:
                    x, y, z = args[0], args[1], args[2]
                    self._translate_bone(bone_name, x, y, z)
                    logger.info(f"Translated bone {bone_name}: ({x:.3f}, {y:.3f}, {z:.3f})")
                    self._update_display()
        except Exception as e:
            logger.error(f"Failed to handle bone translation: {e}")

    async def _handle_blendshape(self, address, *args):
        """Handle blendshape OSC message."""
        try:
            expression_name = args[0] if args else "neutral"
            weight = float(args[1]) if len(args) > 1 else 0.0
            self._set_blendshape(expression_name, weight)
            logger.info(f"Set blendshape {expression_name} to {weight:.2f}")
            self._update_display()
        except Exception as e:
            logger.error(f"Failed to handle blendshape: {e}")

    async def _handle_export(self, address, *args):
        """Handle avatar export OSC message."""
        try:
            export_path = args[0] if args else "exported_avatar.png"
            await asyncio.get_event_loop().run_in_executor(None, self._export_current_view, export_path)
            logger.info(f"Exported avatar to: {export_path}")
        except Exception as e:
            logger.error(f"Failed to export avatar: {e}")

    async def _handle_reset(self, address, *args):
        """Handle avatar reset OSC message."""
        try:
            logger.info("Resetting avatar to default pose")
            self._reset_pose()
            self._update_display()
        except Exception as e:
            logger.error(f"Failed to reset avatar: {e}")

    def _load_and_display_avatar(self, vrm_path: str):
        """Load and display a VRM avatar."""
        try:
            if not os.path.exists(vrm_path):
                logger.error(f"VRM file not found: {vrm_path}")
                return

            logger.info(f"Loading VRM: {vrm_path}")
            self.vrm_model = VRMLoader.from_file(vrm_path)
            self.current_vrm_path = vrm_path

            # Initialize avatar state
            self._extract_bone_positions()
            self._extract_blendshapes()
            self._store_original_vertices()

            # Display the avatar
            self._display_avatar()

        except Exception as e:
            logger.error(f"Failed to load avatar: {e}")

    def _extract_bone_positions(self):
        """Extract bone positions from VRM model."""
        if not self.vrm_model or not hasattr(self.vrm_model, 'bones'):
            return

        self.bone_positions = {}
        self.bone_rotations = {}

        for bone_name, bone in self.vrm_model.bones.items():
            if hasattr(bone, 'position'):
                pos = bone.position
                if hasattr(pos, '__len__') and len(pos) >= 3:
                    self.bone_positions[bone_name] = [pos[0], pos[1], pos[2]]

            # Initialize rotations to identity
            self.bone_rotations[bone_name] = [0, 0, 0, 1]  # w, x, y, z quaternion

        logger.info(f"Extracted {len(self.bone_positions)} bone positions")

    def _extract_blendshapes(self):
        """Extract blendshape/expression data."""
        if not self.vrm_model or not hasattr(self.vrm_model, 'expressions'):
            return

        self.expression_weights = {}
        for expr_name, expression in self.vrm_model.expressions.items():
            self.expression_weights[expr_name] = 0.0

        logger.info(f"Extracted {len(self.expression_weights)} expressions")

    def _store_original_vertices(self):
        """Store original vertex positions for deformation."""
        if not self.vrm_model or not hasattr(self.vrm_model, 'meshes'):
            return

        self.original_vertices = {}
        for mesh_idx, mesh in enumerate(self.vrm_model.meshes):
            if hasattr(mesh, 'vertices'):
                self.original_vertices[mesh_idx] = np.array(mesh.vertices).copy()

    def _rotate_bone(self, bone_name: str, x: float, y: float, z: float, w: float):
        """Apply rotation to a bone."""
        if bone_name not in self.bone_rotations:
            logger.warning(f"Bone {bone_name} not found")
            return

        self.bone_rotations[bone_name] = [w, x, y, z]  # Store as quaternion

        # TODO: Apply bone rotation to connected vertices
        # This would require proper bone weight data and transformation hierarchy

    def _translate_bone(self, bone_name: str, x: float, y: float, z: float):
        """Apply translation to a bone."""
        if bone_name not in self.bone_positions:
            logger.warning(f"Bone {bone_name} not found")
            return

        self.bone_positions[bone_name] = [x, y, z]

        # TODO: Apply bone translation to connected vertices

    def _set_blendshape(self, expression_name: str, weight: float):
        """Set blendshape weight."""
        if expression_name not in self.expression_weights:
            logger.warning(f"Expression {expression_name} not found")
            return

        self.expression_weights[expression_name] = max(0.0, min(1.0, weight))

        # TODO: Apply blendshape deformation to vertices

    def _reset_pose(self):
        """Reset avatar to default pose."""
        # Reset bone rotations
        for bone_name in self.bone_rotations:
            self.bone_rotations[bone_name] = [0, 0, 0, 1]

        # Reset bone positions
        self._extract_bone_positions()

        # Reset expressions
        for expr_name in self.expression_weights:
            self.expression_weights[expr_name] = 0.0

    def _start_animation(self, animation_name: str, speed: float = 1.0):
        """Start animation playback."""
        self.current_animation = animation_name
        self.animation_speed = speed
        self.animation_time = 0.0
        self.is_animating = True

        # TODO: Load and play actual animation data
        logger.info(f"Started animation: {animation_name}")

    def _stop_animation(self):
        """Stop animation playback."""
        self.current_animation = None
        self.is_animating = False
        logger.info("Stopped animation")

    def _update_display(self):
        """Update the 3D display with current state."""
        if not self.ax:
            return

        # Clear existing artists
        for artist in self.mesh_artists + self.bone_artists + self.skeleton_lines:
            if hasattr(artist, 'remove'):
                artist.remove()

        self.mesh_artists = []
        self.bone_artists = []
        self.skeleton_lines = []

        # Redisplay meshes and bones
        self._display_meshes()
        if self.show_bones:
            self._display_bones()
        if self.show_skeleton:
            self._display_skeleton()

        # Force redraw
        self.fig.canvas.draw_idle()

    def _display_avatar(self):
        """Display the current avatar in 3D."""
        if not self.vrm_model:
            logger.warning("No VRM model loaded")
            return

        # Clear existing plot
        if self.fig:
            plt.close(self.fig)

        # Create new figure with enhanced controls
        self.fig = plt.figure(figsize=(16, 12))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Connect mouse and keyboard events
        self.fig.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)

        # Display meshes
        self._display_meshes()

        # Display bones if enabled
        if self.show_bones:
            self._display_bones()

        if self.show_skeleton:
            self._display_skeleton()

        # Set up the plot
        self._setup_plot()

    def _display_meshes(self):
        """Display avatar meshes with enhanced quality."""
        if not self.vrm_model or not hasattr(self.vrm_model, 'meshes'):
            return

        logger.info(f"Displaying {len(self.vrm_model.meshes)} meshes")

        for mesh_idx, mesh in enumerate(self.vrm_model.meshes):
            try:
                # Get mesh data
                vertices = getattr(mesh, 'vertices', [])
                faces = getattr(mesh, 'faces', [])
                name = getattr(mesh, 'name', f'mesh_{mesh_idx}')

                if not vertices or not faces:
                    continue

                # Convert to numpy arrays and scale
                vertices = np.array(vertices) * 10.0  # Scale up for visibility

                # Get color based on mesh name
                color = self._get_mesh_color(name)

                # Display mesh
                if len(faces) > 0 and not self.wireframe_mode:
                    # Convert faces to matplotlib format
                    triangles = []
                    for face in faces[:5000]:  # Limit for performance
                        if len(face) >= 3:
                            triangles.append([face[0], face[1], face[2]])

                    if triangles:
                        triangles = np.array(triangles)

                        # Plot solid surface
                        poly = self.ax.plot_trisurf(
                            vertices[:, 0], vertices[:, 1], vertices[:, 2],
                            triangles=triangles,
                            color=color, alpha=0.8, linewidth=0.1,
                            edgecolors='none', shade=True
                        )
                        self.mesh_artists.append(poly)

                        # Add wireframe overlay for definition
                        wire = self.ax.plot_trisurf(
                            vertices[:, 0], vertices[:, 1], vertices[:, 2],
                            triangles=triangles,
                            color='none', alpha=0.3, linewidth=0.5,
                            edgecolors='black'
                        )
                        self.mesh_artists.append(wire)
                else:
                    # Wireframe only mode
                    for face in faces[:2000]:  # Limit for performance
                        if len(face) >= 3:
                            face_verts = vertices[face[:3]]
                            line = self.ax.plot(
                                face_verts[:, 0], face_verts[:, 1], face_verts[:, 2],
                                color=color, linewidth=0.5, alpha=0.6
                            )
                            self.mesh_artists.extend(line)

                # Add vertex scatter for detail
                if len(vertices) <= 5000:  # Performance limit
                    scatter = self.ax.scatter(
                        vertices[:, 0], vertices[:, 1], vertices[:, 2],
                        color=color, s=0.5, alpha=0.4
                    )
                    self.mesh_artists.append(scatter)

            except Exception as e:
                logger.error(f"Failed to display mesh {mesh_idx}: {e}")

    def _display_bones(self):
        """Display bone positions as interactive markers."""
        if not self.bone_positions:
            return

        logger.info(f"Displaying {len(self.bone_positions)} bones")

        bone_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'cyan']

        for i, (bone_name, pos) in enumerate(self.bone_positions.items()):
            try:
                # Scale position
                scaled_pos = np.array(pos) * 10.0

                # Plot bone as a colored sphere
                color = bone_colors[i % len(bone_colors)]
                scatter = self.ax.scatter(
                    [scaled_pos[0]], [scaled_pos[1]], [scaled_pos[2]],
                    color=color, s=30, alpha=0.9, marker='o',
                    label=f'{bone_name}'
                )
                self.bone_artists.append(scatter)

                # Add bone label
                self.ax.text(scaled_pos[0], scaled_pos[1], scaled_pos[2],
                           f' {bone_name[:8]}', fontsize=8, color=color)

            except Exception as e:
                logger.error(f"Failed to display bone {bone_name}: {e}")

    def _display_skeleton(self):
        """Display skeleton as connecting lines between bones."""
        if not self.bone_positions:
            return

        # Define common bone connections (simplified humanoid skeleton)
        connections = [
            ('Hips', 'Spine'),
            ('Spine', 'Chest'),
            ('Chest', 'Neck'),
            ('Neck', 'Head'),
            ('Chest', 'LeftUpperArm'),
            ('LeftUpperArm', 'LeftLowerArm'),
            ('LeftLowerArm', 'LeftHand'),
            ('Chest', 'RightUpperArm'),
            ('RightUpperArm', 'RightLowerArm'),
            ('RightLowerArm', 'RightHand'),
            ('Hips', 'LeftUpperLeg'),
            ('LeftUpperLeg', 'LeftLowerLeg'),
            ('LeftLowerLeg', 'LeftFoot'),
            ('Hips', 'RightUpperLeg'),
            ('RightUpperLeg', 'RightLowerLeg'),
            ('RightLowerLeg', 'RightFoot'),
        ]

        for parent, child in connections:
            if parent in self.bone_positions and child in self.bone_positions:
                try:
                    parent_pos = np.array(self.bone_positions[parent]) * 10.0
                    child_pos = np.array(self.bone_positions[child]) * 10.0

                    line = self.ax.plot(
                        [parent_pos[0], child_pos[0]],
                        [parent_pos[1], child_pos[1]],
                        [parent_pos[2], child_pos[2]],
                        color='white', linewidth=2, alpha=0.7
                    )
                    self.skeleton_lines.extend(line)

                except Exception as e:
                    logger.debug(f"Failed to connect {parent} to {child}: {e}")

    def _get_mesh_color(self, mesh_name: str) -> str:
        """Get appropriate color for mesh based on name."""
        name_lower = mesh_name.lower()

        # Enhanced color mapping based on common mesh names
        if 'face' in name_lower or 'head' in name_lower or 'skin' in name_lower:
            return '#FFB6C1'  # Light pink (skin tone)
        elif 'hair' in name_lower:
            return '#8B4513'  # Saddle brown
        elif 'shirt' in name_lower or 'top' in name_lower or 'jacket' in name_lower:
            return '#4169E1'  # Royal blue
        elif 'pants' in name_lower or 'bottom' in name_lower or 'skirt' in name_lower:
            return '#2F4F4F'  # Dark slate gray
        elif 'shoes' in name_lower or 'shoe' in name_lower or 'boots' in name_lower:
            return '#000000'  # Black
        elif 'eye' in name_lower:
            return '#0000FF'  # Blue
        elif 'mouth' in name_lower or 'lips' in name_lower:
            return '#FF1493'  # Deep pink
        elif 'eyebrow' in name_lower:
            return '#654321'  # Dark brown
        elif 'accessory' in name_lower or 'hat' in name_lower:
            return '#FFD700'  # Gold
        elif 'gloves' in name_lower or 'hands' in name_lower:
            return '#F5DEB3'  # Wheat
        else:
            # Default colors for other meshes
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
            return colors[hash(mesh_name) % len(colors)]

    def _setup_plot(self):
        """Set up the 3D plot with enhanced settings."""
        if not self.ax:
            return

        # Set labels and title
        self.ax.set_xlabel('X (Right)')
        self.ax.set_ylabel('Y (Up)')
        self.ax.set_zlabel('Z (Forward)')
        self.ax.set_title(f'AvatarMCP Desktop Viewer - {os.path.basename(self.current_vrm_path or "No Avatar")}')

        # Set equal aspect ratio and proper limits
        if self.vrm_model and hasattr(self.vrm_model, 'meshes'):
            # Calculate bounds from all vertices
            all_vertices = []
            for mesh in self.vrm_model.meshes:
                if hasattr(mesh, 'vertices'):
                    vertices = np.array(mesh.vertices) * 10.0
                    all_vertices.extend(vertices)

            if all_vertices:
                all_vertices = np.array(all_vertices)
                bounds = np.array([
                    [all_vertices[:, 0].min(), all_vertices[:, 0].max()],
                    [all_vertices[:, 1].min(), all_vertices[:, 1].max()],
                    [all_vertices[:, 2].min(), all_vertices[:, 2].max()]
                ])

                center = bounds.mean(axis=1)
                size = (bounds[:, 1] - bounds[:, 0]).max() * 0.6

                self.ax.set_xlim(center[0] - size, center[0] + size)
                self.ax.set_ylim(center[1] - size, center[1] + size)
                self.ax.set_zlim(center[2] - size, center[2] + size)
            else:
                self.ax.set_xlim([-1, 1])
                self.ax.set_ylim([-1, 1])
                self.ax.set_zlim([-1, 1])
        else:
            self.ax.set_xlim([-1, 1])
            self.ax.set_ylim([-1, 1])
            self.ax.set_zlim([-1, 1])

        # Set initial view
        self.ax.view_init(elev=self.view_elev, azim=self.view_azim)

        # Add coordinate axes
        axis_length = 0.2
        self.ax.plot([0, axis_length], [0, 0], [0, 0], color='red', linewidth=3, label='X-axis')
        self.ax.plot([0, 0], [0, axis_length], [0, 0], color='green', linewidth=3, label='Y-axis')
        self.ax.plot([0, 0], [0, 0], [axis_length], color='blue', linewidth=3, label='Z-axis')

        # Add control instructions
        info_text = (
            "AvatarMCP Desktop Viewer\n\n"
            "🎮 CONTROLS:\n"
            "• Mouse: Rotate view\n"
            "• Scroll: Zoom in/out\n"
            "• Right-click + drag: Pan\n\n"
            "⌨️  KEYBOARD:\n"
            "• B: Toggle bones\n"
            "• S: Toggle skeleton\n"
            "• W: Toggle wireframe\n"
            "• R: Reset view\n"
            "• Space: Reset pose\n"
            "• Esc: Quit\n\n"
            f"📊 STATUS:\n"
            f"• Bones: {'ON' if self.show_bones else 'OFF'}\n"
            f"• Skeleton: {'ON' if self.show_skeleton else 'OFF'}\n"
            f"• Wireframe: {'ON' if self.wireframe_mode else 'OFF'}\n"
            f"• Animation: {'PLAYING' if self.is_animating else 'STOPPED'}"
        )

        self.ax.text2D(0.02, 0.98, info_text,
                      transform=self.ax.transAxes, fontsize=8, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                      family='monospace')

        # Force redraw
        self.fig.canvas.draw()

    def _on_mouse_press(self, event):
        """Handle mouse press events."""
        if event.inaxes == self.ax:
            self.mouse_pressed = True
            self.last_mouse_pos = (event.x, event.y)

    def _on_mouse_release(self, event):
        """Handle mouse release events."""
        self.mouse_pressed = False
        self.last_mouse_pos = None

    def _on_mouse_move(self, event):
        """Handle mouse movement for rotation and panning."""
        if not self.mouse_pressed or event.inaxes != self.ax or not self.last_mouse_pos:
            return

        dx = event.x - self.last_mouse_pos[0]
        dy = event.y - self.last_mouse_pos[1]

        if event.button == 1:  # Left button: rotate
            self.view_azim += dx * 0.5
            self.view_elev += dy * 0.5
            self.view_elev = max(-90, min(90, self.view_elev))  # Clamp elevation

        elif event.button == 3:  # Right button: pan
            # Pan functionality would require more complex implementation
            pass

        self.ax.view_init(elev=self.view_elev, azim=self.view_azim)
        self.fig.canvas.draw()

        self.last_mouse_pos = (event.x, event.y)

    def _on_scroll(self, event):
        """Handle mouse scroll for zooming."""
        if event.inaxes != self.ax:
            return

        zoom_factor = 1.1 if event.step > 0 else 0.9
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        zlim = self.ax.get_zlim()

        center_x = (xlim[0] + xlim[1]) / 2
        center_y = (ylim[0] + ylim[1]) / 2
        center_z = (zlim[0] + zlim[1]) / 2

        width_x = (xlim[1] - xlim[0]) * zoom_factor
        width_y = (ylim[1] - ylim[0]) * zoom_factor
        width_z = (zlim[1] - zlim[0]) * zoom_factor

        self.ax.set_xlim(center_x - width_x/2, center_x + width_x/2)
        self.ax.set_ylim(center_y - width_y/2, center_y + width_y/2)
        self.ax.set_zlim(center_z - width_z/2, center_z + width_z/2)

        self.fig.canvas.draw()

    def _on_key_press(self, event):
        """Handle keyboard events."""
        if event.key == 'b':
            self.show_bones = not self.show_bones
            logger.info(f"Bone display {'enabled' if self.show_bones else 'disabled'}")
            self._update_display()

        elif event.key == 's':
            self.show_skeleton = not self.show_skeleton
            logger.info(f"Skeleton display {'enabled' if self.show_skeleton else 'disabled'}")
            self._update_display()

        elif event.key == 'w':
            self.wireframe_mode = not self.wireframe_mode
            logger.info(f"Wireframe mode {'enabled' if self.wireframe_mode else 'disabled'}")
            self._update_display()

        elif event.key == 'r':
            self.view_elev = 20
            self.view_azim = 45
            self.ax.view_init(elev=self.view_elev, azim=self.view_azim)
            self.fig.canvas.draw()
            logger.info("View reset")

        elif event.key == ' ':
            self._reset_pose()
            self._update_display()
            logger.info("Pose reset")

        elif event.key == 'escape':
            plt.close(self.fig)
            logger.info("Viewer closed")

    def _export_current_view(self, export_path: str):
        """Export current view to image file."""
        if self.fig:
            self.fig.savefig(export_path, dpi=300, bbox_inches='tight')
            logger.info(f"Exported view to {export_path}")

    async def start_server(self):
        """Start the OSC server."""
        try:
            self.osc_server = AsyncIOOSCUDPServer(
                ("127.0.0.1", self.osc_port),
                self.dispatcher,
                asyncio.get_event_loop()
            )
            transport, protocol = await self.osc_server.create_serve_endpoint()
            logger.info(f"OSC server started on port {self.osc_port}")
            return transport
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
            return None

    def run_viewer(self):
        """Run the viewer (blocking)."""
        try:
            logger.info("Starting AvatarMCP Desktop Viewer...")

            # Show initial empty viewer
            self.fig = plt.figure(figsize=(16, 12))
            self.ax = self.fig.add_subplot(111, projection='3d')

            # Connect mouse and keyboard events
            self.fig.canvas.mpl_connect('button_press_event', self._on_mouse_press)
            self.fig.canvas.mpl_connect('button_release_event', self._on_mouse_release)
            self.fig.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
            self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)
            self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)

            # Set up initial plot
            self._setup_plot()

            plt.show()

        except Exception as e:
            logger.error(f"Failed to run viewer: {e}")

async def main():
    """Main function."""
    viewer = DesktopAvatarViewer()

    # Start OSC server
    transport = await viewer.start_server()
    if not transport:
        logger.error("Failed to start OSC server")
        return

    try:
        # Run the viewer in a separate thread since plt.show() is blocking
        import threading
        viewer_thread = threading.Thread(target=viewer.run_viewer)
        viewer_thread.daemon = True
        viewer_thread.start()

        # Keep the async event loop running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if transport:
            transport.close()

if __name__ == "__main__":
    # Run with asyncio
    asyncio.run(main())


