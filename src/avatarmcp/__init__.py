"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 2.10+ environment with VRChat OSC integration.
"""

import asyncio
import logging
import sys
import os
from typing import Optional, Dict, Any, Tuple, List, Union

# Configure logging before any other imports
logging.basicConfig(
    level=logging.DEBUG,  # More verbose logging for debugging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('avatarmcp.log', mode='w')
    ]
)

# Set higher log level for asyncio to reduce noise
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Import core components after logging is configured
from .core.app import AvatarMCP  # noqa: E402
from .core.mcp_server import MCPServer  # noqa: E402
from .network.osc.vrc_connector import VRChatOSC  # noqa: E402

# Package metadata
__version__ = "0.2.0"

# Re-export for easier access
__all__ = [
    'AvatarMCP', 
    'MCPServer', 
    'VRChatOSC',
    'start_server'
]

# Global server instance for singleton pattern
_server_instance = None
logger = logging.getLogger(__name__)
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
