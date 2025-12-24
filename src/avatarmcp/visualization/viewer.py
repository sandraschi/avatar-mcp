"""
3D visualization for VRM models using PyVista.

STATUS: DORMANT - This PyVista viewer has been abandoned in favor of Unity 3D desktop avatar.
The Unity desktop avatar provides superior VRM support, bone animation, facial expressions,
desktop integration, and VRChat compatibility. This file is kept for reference only.

See: unity-desktop-avatar/ for the active Unity-based viewer implementation.
"""

import logging

import pyvista as pv

logger = logging.getLogger(__name__)


class VRMViewer:
    """3D viewer for VRM models using PyVista."""

    def __init__(self, window_size=(1024, 768)):
        """Initialize the VRM viewer.

        Args:
            window_size: Tuple of (width, height) for the window
        """
        import time

        self.plotter = pv.Plotter(window_size=window_size)
        self.models = {}
        self.current_model = None
        self.is_playing = False
        self.animation_speed = 1.0
        self.current_frame = 0
        self.animation_fps = 60
        self.animation_actors = {}
        self.active_animations = {}
        self.animation_callbacks = {}
        self.animation_time = 0.0

        # Set up the plotter
        self.plotter.enable_terrain_style()
        self.plotter.add_axes()
        self.plotter.add_floor(color="lightgray")

        # Animation box properties
        self.animation_box = None
        self.animation_box_visible = False
        self.animation_box_position = [0, 0, 0]
        self.animation_box_size = [1.0, 1.0, 1.0]

        # Animation state
        self._last_update_time = time.time()
        self._animation_timer = None

    def load_vrm(self, model_id: str, file_path: str) -> bool:
        """Load a VRM model into the viewer.

        Args:
            model_id: Unique identifier for the model
            file_path: Path to the VRM file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # For now, we'll use a simple sphere as a placeholder
            # In a real implementation, you would load the VRM file here
            mesh = pv.Sphere()
            self.models[model_id] = self.plotter.add_mesh(
                mesh, color="lightblue", name=model_id, show_edges=True
            )
            self.plotter.reset_camera()
            return True

        except Exception as e:
            logger.error(f"Failed to load VRM {file_path}: {e}")
            return False

    def unload_vrm(self, model_id: str) -> bool:
        """Unload a VRM model from the viewer.

        Args:
            model_id: ID of the model to unload

        Returns:
            bool: True if successful, False otherwise
        """
        if model_id in self.models:
            self.plotter.remove_actor(self.models[model_id])
            del self.models[model_id]
            return True
        return False

    def play_animation(self, model_id: str, animation_name: str) -> bool:
        """Play an animation on a model.

        Args:
            model_id: ID of the model
            animation_name: Name of the animation to play

        Returns:
            bool: True if successful, False otherwise
        """
        # Animation playback would be implemented here
        logger.info(f"Playing animation '{animation_name}' on model '{model_id}'")
        self.is_playing = True
        return True

    def stop_animation(self, model_id: str, animation_name: str) -> bool:
        """Stop a playing animation.

        Args:
            model_id: ID of the model
            animation_name: Name of the animation to stop

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Stopping animation '{animation_name}' on model '{model_id}'")
        self.is_playing = False
        return True

    def update(self):
        """Update the viewer state and redraw the scene."""
        if not hasattr(self, "plotter") or self.plotter is None:
            return False

        try:
            # Check if render window is ready
            if (
                hasattr(self.plotter, "render_window")
                and self.plotter.render_window
                and hasattr(self.plotter, "iren")
                and self.plotter.iren
                and hasattr(self.plotter.iren, "GetInitialized")
                and self.plotter.iren.GetInitialized()
            ):
                # Only update if the plotter is visible and active
                if hasattr(self.plotter, "is_active") and not self.plotter.is_active:
                    return False

                self.plotter.update()
                self.plotter.render()
                return True
            return False
        except Exception as e:
            logger.debug(f"Error updating viewer: {e}")
            return False

    def _update_animations(self):
        """Update all active animations using the time module."""
        import time

        try:
            # Check if we should continue animating
            if not self.is_playing or not self.active_animations:
                return

            # Check if plotter is still valid
            if not hasattr(self, "plotter") or self.plotter is None:
                self.is_playing = False
                return

            current_time = time.time()
            delta_time = current_time - self._last_update_time
            self._last_update_time = current_time

            # Cap delta time to avoid large jumps when window is inactive
            delta_time = min(delta_time, 0.1)  # Cap at 100ms

            # Update animation time
            self.animation_time += delta_time * self.animation_speed

            # Update all active animations
            for model_id, animation_data in list(self.active_animations.items()):
                if model_id in self.models:
                    try:
                        # Get the actor for this model
                        actor = self.models[model_id]

                        # If we have an actual animation object, update it
                        if hasattr(animation_data, "update"):
                            animation_data.update(self.animation_time)

                        # Update blend shapes if any
                        if hasattr(animation_data, "blend_shapes") and hasattr(
                            actor, "set_blend_shape_weight"
                        ):
                            for shape_name, weight_curve in animation_data.blend_shapes.items():
                                weight = weight_curve.evaluate(self.animation_time)
                                actor.set_blend_shape_weight(shape_name, weight)

                        # Apply the animation to the model
                        self._apply_animation(model_id, animation_data)

                    except Exception as e:
                        logger.error(f"Error updating animation for {model_id}: {e}")
                        self.stop_animation(model_id)

            # Update the display if we have a valid plotter
            if hasattr(self, "plotter") and self.plotter is not None:
                self.update()

            # Schedule the next update if we're still playing and have animations
            if self.is_playing and self.active_animations:
                # Use a try/except to prevent any timer-related errors from breaking
                # the animation loop
                try:
                    if hasattr(self.plotter, "app") and self.plotter.app:
                        self.plotter.app.process_events()
                    if hasattr(self.plotter, "iren") and hasattr(self.plotter.iren, "create_timer"):
                        self.plotter.iren.create_timer(16, self._update_animations)  # ~60 FPS
                except Exception as e:
                    logger.error(f"Error scheduling next animation frame: {e}")
                    self.is_playing = False

        except Exception as e:
            logger.error(f"Unexpected error in animation loop: {e}")
            self.is_playing = False

    def show(self):
        """Show the viewer window."""
        # Set up animation callback if not already done
        if not hasattr(self, "_animation_callback_id"):
            self._animation_callback_id = self.plotter.add_callback(
                self.update,
                interval=16,  # ~60 FPS
            )
        self.plotter.show()

    def close(self):
        """Close the viewer and clean up resources."""
        self.plotter.close()


# Example usage
if __name__ == "__main__":
    viewer = VRMViewer()

    # Example: Load a model
    viewer.load_vrm("test_model", "path/to/your/model.vrm")

    # Show the viewer
    viewer.show()
