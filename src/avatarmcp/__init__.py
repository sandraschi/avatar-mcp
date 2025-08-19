"""
AvatarMCP - MCP server for managing and animating VRM avatars.

This package provides tools for loading, animating, and managing VRM avatar models
in a FastMCP 2.10+ environment.
"""
from pathlib import Path
import logging
from typing import Optional, Dict, Any, Tuple, List, Union

# Import core components
from .service import AvatarService, VRMModel
from .server import AvatarMCP, main as server_main
from .model_manager import VRMModelManager, ModelCacheEntry
from .api import AvatarAPI, APIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Package metadata
__version__ = "0.2.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

# Public API
__all__ = [
    # Core components
    'AvatarService',
    'VRMModel',
    'AvatarMCP',
    'AvatarAPI',
    'APIError',
    
    # Model management
    'VRMModelManager',
    'ModelCacheEntry',
    'get_model_manager',
    'load_vrm',
    'unload_model',
    'clear_model_cache',
    'get_cache_info',
    'validate_vrm_file',
    
    # Server and execution
    'server_main',
    'run_server',
    'create_service'
]

# Global model manager instance
_model_manager = VRMModelManager()

# Global service instance
_service_instance: Optional[AvatarService] = None

def create_service(**kwargs) -> AvatarService:
    """
    Create and return a new AvatarService instance.
    
    Args:
        **kwargs: Additional arguments passed to the AvatarService constructor
        
    Returns:
        AvatarService: A new instance of AvatarService
        
    Example:
        # Create a service with custom settings
        service = create_service(
            max_avatars=10,
            auto_cleanup=True
        )
    """
    return AvatarService(**kwargs)


def get_model_manager() -> VRMModelManager:
    """
    Get the global VRM model manager instance.
    
    Returns:
        VRMModelManager: The global model manager instance
    """
    global _model_manager
    return _model_manager


def unload_model(file_path: Union[str, Path]) -> bool:
    """
    Unload a VRM model from the cache.
    
    Args:
        file_path: Path to the VRM file or cache key
        
    Returns:
        bool: True if the model was unloaded, False otherwise
    """
    return _model_manager.unload_model(file_path)


def clear_model_cache() -> None:
    """
    Clear all models from the model cache.
    """
    _model_manager.clear_cache()


def get_cache_info() -> Dict[str, Any]:
    """
    Get information about the model cache.
    
    Returns:
        Dict containing cache statistics and state
    """
    return _model_manager.get_cache_info()


def validate_vrm_file(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate a VRM file.
    
    Args:
        file_path: Path to the VRM file
        
    Returns:
        Tuple of (is_valid, issues) where issues is a list of validation messages
    """
    return _model_manager.validate_vrm_file(file_path)

def load_vrm(
    file_path: Union[str, Path], 
    service: Optional[AvatarService] = None,
    force_reload: bool = False,
    validate: bool = True,
    **kwargs
) -> Optional[VRMModel]:
    """
    Convenience function to load a VRM model with caching and validation.
    
    Args:
        file_path: Path to the .vrm or .glb file
        service: Optional AvatarService instance. If not provided, a global instance will be used.
        force_reload: If True, force reload the model even if it's in the cache
        validate: If True, validate the VRM file before loading
        **kwargs: Additional arguments passed to the model manager
        
    Returns:
        Optional[VRMModel]: The loaded VRM model, or None if loading failed
        
    Example:
        # Basic usage
        model = load_vrm("path/to/avatar.vrm")
        
        # Force reload and skip validation
        model = load_vrm("path/to/avatar.vrm", force_reload=True, validate=False)
    """
    global _service_instance, _model_manager
    
    try:
        # Use the model manager to load the model
        model = _model_manager.load_model(
            file_path=file_path,
            force_reload=force_reload,
            validate=validate,
            **kwargs
        )
        
        # If we have a service, register the model with it
        if model is not None and service is not None:
            service.register_model(model, str(file_path))
        
        return model
        
    except Exception as e:
        logger.error(f"Failed to load model {file_path}: {str(e)}", exc_info=True)
        return None

def run_server(host: str = "0.0.0.0", port: int = 8080, debug: bool = False) -> None:
    """
    Run the AvatarMCP API server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8080)
        debug: Enable debug mode with more verbose logging
    
    Example:
        # Run the API server
        run_server(host="0.0.0.0", port=8080)
    """
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)
    
    # Create and run the API server
    api = AvatarAPI()
    api.run(host=host, port=port)

# Add type hints for better IDE support
if False:  # pragma: no cover
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .service import AvatarService, VRMModel
        from .server import AvatarMCP
