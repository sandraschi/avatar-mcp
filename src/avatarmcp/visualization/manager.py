"""
Visualization manager for the AvatarMCP server.

This module provides a thread-safe interface for managing the 3D visualization
of VRM models using PyVista.
"""
import asyncio
import threading
from typing import Dict, Any, Optional, Tuple
import logging

from .viewer import VRMViewer

logger = logging.getLogger(__name__)

class VisualizationManager:
    """Manages 3D visualization of VRM models."""
    
    def __init__(self):
        """Initialize the visualization manager."""
        self.viewer: Optional[VRMViewer] = None
        self._viewer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
    def start_viewer(self, window_size: Tuple[int, int] = (1024, 768)) -> None:
        """Start the visualization in a separate thread.
        
        Args:
            window_size: Window dimensions (width, height)
        """
        if self._viewer_thread is not None and self._viewer_thread.is_alive():
            logger.warning("Viewer is already running")
            return
            
        self._stop_event.clear()
        self._viewer_thread = threading.Thread(
            target=self._run_viewer,
            args=(window_size,),
            daemon=True
        )
        self._viewer_thread.start()
        logger.info("Started 3D viewer")
        
    def _run_viewer(self, window_size: Tuple[int, int]) -> None:
        """Run the viewer in a separate thread."""
        try:
            self.viewer = VRMViewer(window_size=window_size)
            
            # Main viewer loop
            while not self._stop_event.is_set():
                if self.viewer:
                    self.viewer.update()
                    # Small delay to prevent high CPU usage
                    self._stop_event.wait(0.016)  # ~60 FPS
                    
        except Exception as e:
            logger.error(f"Error in viewer thread: {e}", exc_info=True)
        finally:
            if self.viewer:
                self.viewer.close()
                self.viewer = None
                
    def stop_viewer(self) -> None:
        """Stop the visualization."""
        self._stop_event.set()
        if self._viewer_thread and self._viewer_thread.is_alive():
            self._viewer_thread.join(timeout=2.0)
        self._viewer_thread = None
        logger.info("Stopped 3D viewer")
        
    def load_vrm(self, model_id: str, file_path: str) -> bool:
        """Load a VRM model into the viewer.
        
        Args:
            model_id: Unique identifier for the model
            file_path: Path to the VRM file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.viewer:
            logger.warning("Viewer is not running")
            return False
            
        with self._lock:
            return self.viewer.load_vrm(model_id, file_path)
            
    def unload_vrm(self, model_id: str) -> bool:
        """Unload a VRM model from the viewer.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.viewer:
            return False
            
        with self._lock:
            return self.viewer.unload_vrm(model_id)
            
    def play_animation(self, model_id: str, animation_name: str) -> bool:
        """Play an animation on a model.
        
        Args:
            model_id: ID of the model
            animation_name: Name of the animation to play
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.viewer:
            return False
            
        with self._lock:
            return self.viewer.play_animation(model_id, animation_name)
            
    def stop_animation(self, model_id: str, animation_name: str) -> bool:
        """Stop a playing animation.
        
        Args:
            model_id: ID of the model
            animation_name: Name of the animation to stop
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.viewer:
            return False
            
        with self._lock:
            return self.viewer.stop_animation(model_id, animation_name)
            
    def is_running(self) -> bool:
        """Check if the viewer is running.
        
        Returns:
            bool: True if the viewer thread is running, False otherwise
        """
        return self._viewer_thread is not None and self._viewer_thread.is_alive()
