"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 2.10+ environment with VRChat OSC integration.
"""
__version__ = "0.1.0"

import asyncio
import logging
from typing import Optional, Dict, Any, Tuple, List, Union

# Configure logging before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Import core components after logging is configured
from .core.app import AvatarMCP  # noqa: E402

# Re-export for easier access
__all__ = ['AvatarMCP', 'start_server']

# Global server instance for singleton pattern
_server_instance = None
logger = logging.getLogger(__name__)

# Package metadata
__version__ = "0.2.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

# Public API
__all__ = [
    # Core components
    'VRMModel',
    
    # Server and execution
    'server_main'
]

if __name__ == "__main__":
    server_main()
