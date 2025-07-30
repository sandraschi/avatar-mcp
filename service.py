"""AvatarMCP service implementation for FastMCP 2.1.

This module provides the main service class for controlling avatars with support
for animations, expressions, and real-time control.
"""

from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

from fastmcp import FastMCP, MCPModel, MCPService

from .models import Avatar, Animation, Expression, AvatarState
from .vrm_loader import VRMLoader

logger = logging.getLogger(__name__)

@dataclass
class AvatarMCP(MCPService):
    """Main service class for AvatarMCP.
    
    This service provides control over animated avatars with support for:
    - Loading and managing VRM/VRoid models
    - Playing animations and managing animation states
    - Controlling expressions and blendshapes
    - Real-time parameter control
    """
    
    # Service metadata
    name: str = "AvatarMCP"
    version: str = "0.1.0"
    description: str = "FastMCP 2.1 service for controlling animated avatars"
    
    # Runtime state
    avatars: Dict[str, Avatar] = field(default_factory=dict)
    active_avatar: Optional[Avatar] = None
    vrm_loader: VRMLoader = field(default_factory=VRMLoader)
    
    def __post_init__(self):
        """Initialize the service and register RPC methods."""
        super().__post_init__()
        self.register_methods(self)
    
    # Avatar Management
    
    async def load_avatar(self, path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Load an avatar from a VRM/VRoid file.
        
        Args:
            path: Path to the VRM/VRoid file
            name: Optional name for the avatar (defaults to filename)
            
        Returns:
            Dict containing avatar metadata
        """
        try:
            avatar = await asyncio.get_event_loop().run_in_executor(
                None, self.vrm_loader.load, path
            )
            
            if not name:
                name = Path(path).stem
                
            self.avatars[name] = avatar
            
            if not self.active_avatar:
                self.active_avatar = avatar
                
            return {
                "status": "success",
                "name": name,
                "path": str(path),
                "animations": [a.name for a in avatar.animations],
                "expressions": [e.name for e in avatar.expressions]
            }
            
        except Exception as e:
            logger.error(f"Failed to load avatar: {e}")
            return {"status": "error", "message": str(e)}
    
    async def set_active_avatar(self, name: str) -> Dict[str, Any]:
        """Set the active avatar by name.
        
        Args:
            name: Name of the avatar to activate
            
        Returns:
            Status of the operation
        """
        if name not in self.avatars:
            return {"status": "error", "message": f"Avatar '{name}' not found"}
            
        self.active_avatar = self.avatars[name]
        return {"status": "success", "active_avatar": name}
    
    # Animation Control
    
    async def play_animation(self, name: str, loop: bool = False, speed: float = 1.0) -> Dict[str, Any]:
        """Play an animation on the active avatar.
        
        Args:
            name: Name of the animation to play
            loop: Whether to loop the animation
            speed: Playback speed multiplier
            
        Returns:
            Status of the operation
        """
        if not self.active_avatar:
            return {"status": "error", "message": "No active avatar"}
            
        try:
            await self.active_avatar.play_animation(name, loop, speed)
            return {"status": "success", "animation": name}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def stop_animation(self) -> Dict[str, Any]:
        """Stop the current animation on the active avatar.
        
        Returns:
            Status of the operation
        """
        if not self.active_avatar:
            return {"status": "error", "message": "No active avatar"}
            
        self.active_avatar.stop_animation()
        return {"status": "success"}
    
    # Expression Control
    
    async def set_expression(self, name: str, weight: float = 1.0) -> Dict[str, Any]:
        """Set an expression on the active avatar.
        
        Args:
            name: Name of the expression to set
            weight: Expression weight (0.0 to 1.0)
            
        Returns:
            Status of the operation
        """
        if not self.active_avatar:
            return {"status": "error", "message": "No active avatar"}
            
        try:
            await self.active_avatar.set_expression(name, weight)
            return {"status": "success", "expression": name, "weight": weight}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # State Management
    
    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the active avatar.
        
        Returns:
            Current avatar state
        """
        if not self.active_avatar:
            return {"status": "error", "message": "No active avatar"}
            
        state = self.active_avatar.get_state()
        return {
            "status": "success",
            "avatar": self.active_avatar.name,
            "state": state.dict()
        }
    
    async def set_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Set the state of the active avatar.
        
        Args:
            state: State to apply to the avatar
            
        Returns:
            Status of the operation
        """
        if not self.active_avatar:
            return {"status": "error", "message": "No active avatar"}
            
        try:
            avatar_state = AvatarState(**state)
            await self.active_avatar.set_state(avatar_state)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create a default instance for easy use
service = AvatarMCP()
