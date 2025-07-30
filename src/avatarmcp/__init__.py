"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 2.10+ environment.
"""
from pathlib import Path
from typing import Optional, Dict, Any

# Import core components
from .service import AvatarService, VRMModel
from .server import AvatarMCP, main as server_main

# Package metadata
__version__ = "0.1.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

# Public API
__all__ = [
    'AvatarService',
    'VRMModel',
    'AvatarMCP',
    'server_main',
    'load_vrm',
    'create_service'
]

# Global service instance
_service_instance: Optional[AvatarService] = None

def create_service() -> AvatarService:
    """
    Create and return a new AvatarService instance.
    
    Returns:
        AvatarService: A new instance of AvatarService
    """
    return AvatarService()

def load_vrm(file_path: str, service: Optional[AvatarService] = None) -> VRMModel:
    """
    Convenience function to load a VRM model.
    
    Args:
        file_path: Path to the .vrm file
        service: Optional AvatarService instance. If not provided, a global instance will be used.
        
    Returns:
        VRMModel: The loaded VRM model
    """
    global _service_instance
    
    if service is None:
        if _service_instance is None:
            _service_instance = AvatarService()
        service = _service_instance
    
    return service.load_vrm(file_path)

def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Run the AvatarMCP server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8000)
    """
    server = AvatarMCP()
    server.run(host=host, port=port)

# Add type hints for better IDE support
if False:  # pragma: no cover
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .service import AvatarService, VRMModel
        from .server import AvatarMCP
