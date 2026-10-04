"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 3.1+ environment with optional VRChat OSC integration.
"""

import logging
import os
import sys
from pathlib import Path

# Absolute paths: a bare filename lands in whatever cwd the MCP host used (e.g. D:\Dev\repos)
APP_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "avatar-mcp"
LOG_FILE = APP_DIR / "logs" / "avatarmcp.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure logging before any other imports
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE, mode="w")],
)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Always-available exports (canonical FastMCP 3.1 server)
from .models.vrm import VRMModel
from .server import AvatarMCPServer, run_server

__version__ = "0.3.0"
__author__ = "AvatarMCP Team"
__license__ = "MIT"

__all__ = [
    "AvatarMCPServer",
    "VRMModel",
    "__version__",
    "run_server",
    "server_main",
]


def server_main() -> int:
    """Main entry point for the server (blocking)."""
    return run_server()


logger = logging.getLogger(__name__)
