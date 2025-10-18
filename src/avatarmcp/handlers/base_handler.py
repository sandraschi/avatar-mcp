"""
Base handler class for all MCP request handlers.

This module provides the BaseHandler class that serves as a foundation for all
MCP request handlers in the AvatarMCP system. It includes common functionality
for initialization, error handling, and response formatting.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseHandler:
    """
    Base class for all MCP request handlers.
    
    This class provides common functionality for handling MCP requests,
    including initialization, error handling, and response formatting.
    """
    
    def __init__(self, server: Any = None):
        """
        Initialize the base handler.
        
        Args:
            server: Reference to the main server instance
        """
        self.server = server
        self.initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize the handler.
        
        This method should be called after instantiation to perform any
        required asynchronous initialization.
        """
        if not self.initialized:
            await self._initialize()
            self.initialized = True
    
    async def _initialize(self) -> None:
        """
        Perform handler-specific initialization.
        
        Subclasses should override this method to implement their own
        initialization logic.
        """
        pass
    
    def _check_initialized(self) -> None:
        """
        Verify that the handler has been properly initialized.
        
        Raises:
            RuntimeError: If the handler has not been initialized
        """
        if not self.initialized:
            raise RuntimeError("Handler not initialized. Call 'initialize()' first.")
    
    def _create_error_response(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            **kwargs: Additional error details
            
        Returns:
            Dictionary containing error response
        """
        response = {
            "status": "error",
            "message": message
        }
        response.update(kwargs)
        return response
    
    def _create_success_response(self, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            **kwargs: Response data
            
        Returns:
            Dictionary containing success response
        """
        response = {
            "status": "success"
        }
        response.update(kwargs)
        return response
    
    async def shutdown(self) -> None:
        """
        Clean up resources used by the handler.
        
        Subclasses should override this method to perform any necessary cleanup.
        """
        self.initialized = False
