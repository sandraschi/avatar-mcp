"""
Base classes and utilities for avatar controls.

This module provides the foundation for all avatar control tools,
including common types, enums, and base classes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, Field


class ControlType(str, Enum):
    """Types of avatar controls."""

    BONE = "bone"
    MORPH = "morph"
    EXPORT = "export"
    ANIMATION = "animation"


class ControlSpace(str, Enum):
    """Coordinate space for transforms."""

    LOCAL = "local"
    WORLD = "world"


class ControlMode(str, Enum):
    """Control modes for avatar manipulation."""

    POSITION = "position"
    ROTATION = "rotation"
    SCALE = "scale"
    MORPH = "morph"
    ANIMATION = "animation"
    EXPRESSION = "expression"


class Vector3(BaseModel):
    """3D vector representation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Quaternion(BaseModel):
    """Quaternion representation for rotations."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


class Transform(BaseModel):
    """Complete transform data for bones or objects."""

    position: Vector3 = Field(default_factory=Vector3)
    rotation: Quaternion = Field(default_factory=Quaternion)
    scale: Vector3 = Field(default_factory=lambda: Vector3(x=1.0, y=1.0, z=1.0))
    space: ControlSpace = ControlSpace.LOCAL


@dataclass
class ControlResult:
    """Result of a control operation."""

    success: bool
    message: str = ""
    data: dict[str, Any] | None = None
    error: str | None = None

    @classmethod
    def success(cls, message: str, data: dict | None = None) -> "ControlResult":
        """Create a success result."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def create_error(cls, message: str, error: str | None = None) -> "ControlResult":
        """Create an error result."""
        return cls(success=False, message=message, error=error or message)


class AvatarControlBase:
    """Base class for all avatar control tools."""

    @property
    def control_type(self) -> ControlType:
        """Type of this control."""
        raise NotImplementedError

    async def execute(self, **kwargs) -> ControlResult:
        """Execute the control operation."""
        raise NotImplementedError

    def validate_input(self, **kwargs) -> str | None:
        """Validate input parameters. Returns None if valid, error message otherwise."""
        return None


# Type variable for control tool classes
T = TypeVar("T", bound=AvatarControlBase)

# Alias for backward compatibility
BaseControlTool = AvatarControlBase
