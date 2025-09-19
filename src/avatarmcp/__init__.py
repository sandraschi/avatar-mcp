"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 2.10+ environment with VRChat OSC integration.
"""

import asyncio
import logging
import sys
import os
from typing import Optional, Dict, Any, Tuple, List, Union, TYPE_CHECKING

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

# Only import type hints when type checking to avoid circular imports
if TYPE_CHECKING:
    from .server import AvatarMCPServer

# Public API
__all__ = [
    'AvatarMCPServer',
    'run_server',
]

# Conditional imports to avoid loading heavy dependencies during package import
# Only import when not in MCP mode or when explicitly needed

_heavy_imports_loaded = False
_mcp_mode = '--mcp' in sys.argv or 'mcp_main.py' in sys.argv[0] if sys.argv else False

def _ensure_heavy_imports():
    """Load heavy imports only when needed."""
    global _heavy_imports_loaded, AvatarMCP, AvatarMCPServer, run_server, VRChatOSC
    
    if not _heavy_imports_loaded and not _mcp_mode:
        try:
            from .core.app import AvatarMCP  # noqa: E402
            from .server import AvatarMCPServer, run_server  # noqa: E402  
            from .network.osc.vrc_connector import VRChatOSC  # noqa: E402
            _heavy_imports_loaded = True
        except ImportError as e:
            # If heavy imports fail, define stub classes
            class AvatarMCP:
                def __init__(self): raise ImportError(f"Heavy dependencies not available: {e}")
            class AvatarMCPServer:
                def __init__(self): raise ImportError(f"Heavy dependencies not available: {e}")
            def run_server(): raise ImportError(f"Heavy dependencies not available: {e}")
            class VRChatOSC:
                def __init__(self): raise ImportError(f"Heavy dependencies not available: {e}")

# Always available lightweight components
try:
    # These should always be importable
    pass
except ImportError:
    pass

# Only load heavy components if not in MCP mode
if not _mcp_mode:
    _ensure_heavy_imports()

# Package metadata
__version__ = "0.2.0"

# Re-export for easier access
__all__ = [
    'AvatarMCP',
    'AvatarMCPServer',
    'VRChatOSC',
    'run_server'
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
