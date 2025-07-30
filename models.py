"""Data models for AvatarMCP.

This module defines the core data structures used by the AvatarMCP service.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import numpy as np

class AnimationType(Enum):
    """Types of animations supported by the avatar system."""
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    DANCE = auto()
    GESTURE = auto()
    EMOTE = auto()
    CUSTOM = auto()

class ExpressionType(Enum):
    """Types of facial expressions and blendshapes."""
    NEUTRAL = auto()
    HAPPY = auto()
    SAD = auto()
    ANGRY = auto()
    SURPRISED = auto()
    BLINK = auto()
    BLINK_L = auto()
    BLINK_R = auto()
    LOOK_UP = auto()
    LOOK_DOWN = auto()
    LOOK_LEFT = auto()
    LOOK_RIGHT = auto()
    MOUTH_A = auto()  # "Ah" sound
    MOUTH_I = auto()  # "Ee" sound
    MOUTH_U = auto()  # "Oo" sound
    MOUTH_E = auto()  # "Eh" sound
    MOUTH_O = auto()  # "Oh" sound
    CUSTOM = auto()

@dataclass
class Animation:
    """Represents an animation that can be played on an avatar."""
    name: str
    animation_type: AnimationType
    duration: float  # in seconds
    loop: bool = False
    speed: float = 1.0
    data: Any = None  # Animation data (format depends on implementation)
    
    def __post_init__(self):
        """Validate animation data."""
        if self.duration <= 0:
            raise ValueError("Animation duration must be positive")
        if self.speed <= 0:
            raise ValueError("Animation speed must be positive")

@dataclass
class Expression:
    """Represents a facial expression or blendshape for an avatar."""
    name: str
    expression_type: ExpressionType
    weight: float = 0.0  # 0.0 to 1.0
    blend_shape_name: Optional[str] = None  # Optional name for blendshape in the model
    
    def __post_init__(self):
        """Validate expression weight."""
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("Expression weight must be between 0.0 and 1.0")

@dataclass
class BoneTransform:
    """Represents the transform of a bone in 3D space."""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # Quaternion (x, y, z, w)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    
    @property
    def position_array(self) -> np.ndarray:
        """Get position as a numpy array."""
        return np.array(self.position, dtype=np.float32)
    
    @property
    def rotation_quat(self) -> np.ndarray:
        """Get rotation as a quaternion numpy array."""
        return np.array(self.rotation, dtype=np.float32)
    
    @property
    def scale_array(self) -> np.ndarray:
        """Get scale as a numpy array."""
        return np.array(self.scale, dtype=np.float32)

class AvatarState(BaseModel):
    """Represents the complete state of an avatar at a point in time."""
    position: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Position in 3D space (x, y, z)"
    )
    rotation: Tuple[float, float, float, float] = Field(
        default=(0.0, 0.0, 0.0, 1.0),
        description="Rotation as a quaternion (x, y, z, w)"
    )
    scale: Tuple[float, float, float] = Field(
        default=(1.0, 1.0, 1.0),
        description="Scale factors (x, y, z)"
    )
    bone_transforms: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Bone transforms by bone name"
    )
    expression_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Expression weights by expression name"
    )
    current_animation: Optional[str] = Field(
        default=None,
        description="Name of the currently playing animation"
    )
    animation_time: float = Field(
        default=0.0,
        description="Current time in the animation (in seconds)"
    )
    is_visible: bool = Field(
        default=True,
        description="Whether the avatar is currently visible"
    )

@dataclass
class Avatar:
    """Represents a 3D avatar with animations and expressions."""
    name: str
    model_data: Any  # Raw model data (format depends on loader)
    animations: Dict[str, Animation] = field(default_factory=dict)
    expressions: Dict[str, Expression] = field(default_factory=dict)
    bones: Dict[str, BoneTransform] = field(default_factory=dict)
    current_state: AvatarState = field(default_factory=AvatarState)
    
    async def play_animation(self, name: str, loop: bool = False, speed: float = 1.0):
        """Play an animation on this avatar."""
        if name not in self.animations:
            raise ValueError(f"Animation '{name}' not found")
            
        animation = self.animations[name]
        animation.loop = loop
        animation.speed = speed
        self.current_state.current_animation = name
        self.current_state.animation_time = 0.0
        
        # In a real implementation, this would start the animation playback
        # and update the avatar's state over time
        
    def stop_animation(self):
        """Stop the current animation."""
        self.current_state.current_animation = None
        self.current_state.animation_time = 0.0
        
    async def set_expression(self, name: str, weight: float = 1.0):
        """Set an expression weight on this avatar."""
        if name not in self.expressions:
            raise ValueError(f"Expression '{name}' not found")
            
        self.expressions[name].weight = weight
        self.current_state.expression_weights[name] = weight
        
    def get_state(self) -> AvatarState:
        """Get the current state of the avatar."""
        return self.current_state
        
    async def set_state(self, state: AvatarState):
        """Set the state of the avatar."""
        self.current_state = state
        
        # Update expressions
        for name, weight in state.expression_weights.items():
            if name in self.expressions:
                self.expressions[name].weight = weight
                
        # In a real implementation, this would update the avatar's
        # transforms, bone positions, etc. based on the new state
