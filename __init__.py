"""AvatarMCP - FastMCP 2.1-compliant service for controlling animated avatars.

This module provides a unified interface for controlling avatars across different
platforms (desktop, VRChat, etc.) with support for animations, expressions,
and real-time control.
"""

__version__ = "0.1.0"

from .service import AvatarMCP
from .models import Avatar, Animation, Expression
from .vrm_loader import VRMLoader

__all__ = ["AvatarMCP", "Avatar", "Animation", "Expression", "VRMLoader"]
