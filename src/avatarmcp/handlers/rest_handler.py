"""
REST API handler for the Avatar MCP server.

This module provides a FastAPI-based REST API for controlling the Avatar MCP server
and its components through HTTP requests.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status, Depends, Header
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

# Pydantic models for request/response validation
class StatusResponse(BaseModel):
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Additional status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class AvatarLoadRequest(BaseModel):
    path: Optional[str] = Field(None, description="Path to the avatar file")
    model_id: Optional[str] = Field(None, description="ID of an existing model to load")
    make_active: bool = Field(True, description="Whether to make this the active avatar")

class AnimationPlayRequest(BaseModel):
    name: str = Field(..., description="Name of the animation to play")
    loop: bool = Field(False, description="Whether to loop the animation")
    speed: float = Field(1.0, description="Playback speed multiplier")
    blend_time: float = Field(0.2, description="Time to blend to this animation")

class AnimationStopRequest(BaseModel):
    blend_time: float = Field(0.2, description="Time to blend out the current animation")

class APIVersion(str, Enum):
    V1 = "v1"

class RESTConfig(BaseModel):
    """Configuration for the REST API server."""
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api"
    cors_origins: List[str] = ["*"]
    api_keys: List[str] = []
    enable_swagger: bool = True
    enable_redoc: bool = False

class RESTHandler(BaseHandler):
    """Handles REST API requests for the Avatar MCP server."""
    
    def __init__(self, server: Any = None):
        """Initialize the REST handler.
        
        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.app = None
        self.config = None
        self._server = None
    
    async def _initialize(self) -> None:
        """Initialize the FastAPI application and routes."""
        # Load configuration
        self.config = self._load_config()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Avatar MCP API",
            description="REST API for controlling the Avatar MCP server",
            version="1.0.0",
            docs_url="/docs" if self.config.enable_swagger else None,
            redoc_url="/redoc" if self.config.enable_redoc else None,
            default_response_class=JSONResponse,
            responses={
                status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
                status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
                status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
                status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
            },
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add exception handlers
        self._add_exception_handlers()
        
        # Add middleware for request logging
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            logger.info(f"Request: {request.method} {request.url}")
            response = await call_next(request)
            logger.info(f"Response: {request.method} {request.url} - {response.status_code}")
            return response
        
        # Add startup and shutdown events
        self.app.add_event_handler("startup", self._on_startup)
        self.app.add_event_handler("shutdown", self._on_shutdown)
        
        # Register API routes
        self._register_routes()
        
        logger.info("REST handler initialized")
    
    def _load_config(self) -> RESTConfig:
        """Load REST API configuration."""
        # In a real implementation, this would load from a config file or environment variables
        return RESTConfig()
    
    def _add_exception_handlers(self) -> None:
        """Add exception handlers to the FastAPI app."""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail.get("error", "http_error"),
                    "message": str(exc.detail.get("message", exc.detail)),
                    "details": exc.detail.get("details", {})
                },
            )
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": {"exception": str(exc)}
                },
            )
    
    async def _on_startup(self) -> None:
        """Handle application startup."""
        logger.info("Starting REST API server...")
    
    async def _on_shutdown(self) -> None:
        """Handle application shutdown."""
        logger.info("Shutting down REST API server...")
    
    def _register_routes(self) -> None:
        """Register API routes."""
        # Health check endpoint
        @self.app.get("/health", tags=["System"])
        async def health_check() -> StatusResponse:
            """Check if the API is running."""
            return {
                "status": "ok",
                "message": "API is running",
                "data": {
                    "version": "1.0.0",
                    "status": "operational"
                }
            }
        
        # API key verification dependency
        async def verify_api_key(api_key: str = Header(None, alias="X-API-Key")) -> None:
            """Verify the API key."""
            if self.config.api_keys and (not api_key or api_key not in self.config.api_keys):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "unauthorized",
                        "message": "Invalid or missing API key"
                    }
                )
        
        # API v1 routes
        api_router = self.app.router
        
        # Avatar endpoints
        @api_router.post(
            "/v1/avatars/load",
            response_model=StatusResponse,
            tags=["Avatars"]
        )
        async def load_avatar(
            request: AvatarLoadRequest,
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """Load an avatar."""
            if not hasattr(self.server, 'avatar_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Avatar handler not available"
                    }
                )
            
            try:
                response = await self.server.avatar_handler.handle_avatar_load({
                    "path": request.path,
                    "model_id": request.model_id,
                    "make_active": request.make_active
                })
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "avatar_load_failed",
                            "message": response.get("message", "Failed to load avatar")
                        }
                    )
                
                return {
                    "status": "success",
                    "message": "Avatar loaded successfully",
                    "data": {
                        "model_id": response.get("model_id"),
                        "active": response.get("active", False),
                        "metadata": response.get("metadata", {})
                    }
                }
                
            except Exception as e:
                logger.error(f"Error loading avatar: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to load avatar: {str(e)}"
                    }
                )
        
        @api_router.post(
            "/v1/avatars/{model_id}/unload",
            response_model=StatusResponse,
            tags=["Avatars"]
        )
        async def unload_avatar(
            model_id: str,
            force: bool = False,
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """Unload an avatar."""
            if not hasattr(self.server, 'avatar_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Avatar handler not available"
                    }
                )
            
            try:
                response = await self.server.avatar_handler.handle_avatar_unload({
                    "id": model_id,
                    "force": force
                })
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "avatar_unload_failed",
                            "message": response.get("message", "Failed to unload avatar")
                        }
                    )
                
                return {
                    "status": "success",
                    "message": "Avatar unloaded successfully",
                    "data": {
                        "model_id": model_id,
                        "was_loaded": response.get("was_loaded", False)
                    }
                }
                
            except Exception as e:
                logger.error(f"Error unloading avatar: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to unload avatar: {str(e)}"
                    }
                )
        
        @api_router.get(
            "/v1/avatars",
            response_model=StatusResponse,
            tags=["Avatars"]
        )
        async def list_avatars(
            loaded_only: bool = False,
            include_metadata: bool = False,
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """List available avatars."""
            if not hasattr(self.server, 'avatar_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Avatar handler not available"
                    }
                )
            
            try:
                response = await self.server.avatar_handler.handle_avatar_list({
                    "loaded_only": loaded_only,
                    "include_metadata": include_metadata
                })
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "list_avatars_failed",
                            "message": response.get("message", "Failed to list avatars")
                        }
                    )
                
                return {
                    "status": "success",
                    "data": response.get("avatars", {})
                }
                
            except Exception as e:
                logger.error(f"Error listing avatars: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to list avatars: {str(e)}"
                    }
                )
        
        # Animation endpoints
        @api_router.post(
            "/v1/animations/play",
            response_model=StatusResponse,
            tags=["Animations"]
        )
        async def play_animation(
            request: AnimationPlayRequest,
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """Play an animation on the active avatar."""
            if not hasattr(self.server, 'animation_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Animation handler not available"
                    }
                )
            
            try:
                response = await self.server.animation_handler.handle_animation_play({
                    "name": request.name,
                    "loop": request.loop,
                    "speed": request.speed,
                    "blend_time": request.blend_time
                })
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "play_animation_failed",
                            "message": response.get("message", "Failed to play animation")
                        }
                    )
                
                return {
                    "status": "success",
                    "message": "Animation started",
                    "data": {
                        "animation": request.name,
                        "loop": request.loop,
                        "speed": request.speed
                    }
                }
                
            except Exception as e:
                logger.error(f"Error playing animation: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to play animation: {str(e)}"
                    }
                )
        
        @api_router.post(
            "/v1/animations/stop",
            response_model=StatusResponse,
            tags=["Animations"]
        )
        async def stop_animation(
            request: AnimationStopRequest = None,
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """Stop the current animation on the active avatar."""
            if not hasattr(self.server, 'animation_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Animation handler not available"
                    }
                )
            
            try:
                blend_time = request.blend_time if request else 0.2
                
                response = await self.server.animation_handler.handle_animation_stop({
                    "blend_time": blend_time
                })
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "stop_animation_failed",
                            "message": response.get("message", "Failed to stop animation")
                        }
                    )
                
                return {
                    "status": "success",
                    "message": "Animation stopped",
                    "data": {
                        "was_playing": response.get("was_playing", False)
                    }
                }
                
            except Exception as e:
                logger.error(f"Error stopping animation: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to stop animation: {str(e)}"
                    }
                )
        
        @api_router.get(
            "/v1/animations",
            response_model=StatusResponse,
            tags=["Animations"]
        )
        async def list_animations(
            api_key: str = Depends(verify_api_key) if self.config.api_keys else None
        ) -> StatusResponse:
            """List available animations for the active avatar."""
            if not hasattr(self.server, 'animation_handler'):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "service_unavailable",
                        "message": "Animation handler not available"
                    }
                )
            
            try:
                response = await self.server.animation_handler.handle_animation_list({})
                
                if response.get("status") != "success":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "list_animations_failed",
                            "message": response.get("message", "Failed to list animations")
                        }
                    )
                
                return {
                    "status": "success",
                    "data": {
                        "animations": response.get("animations", []),
                        "current_animation": response.get("current_animation")
                    }
                }
                
            except Exception as e:
                logger.error(f"Error listing animations: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "internal_error",
                        "message": f"Failed to list animations: {str(e)}"
                    }
                )
    
    async def start_server(self) -> None:
        """Start the REST API server."""
        import uvicorn
        
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
            reload=False,
            workers=1
        )
        
        self._server = uvicorn.Server(config)
        await self._server.serve()
    
    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        if hasattr(self, '_server') and self._server:
            self._server.should_exit = True
            self._server.force_exit = True
            
            # Give the server a moment to shut down
            await asyncio.sleep(0.1)
            
            self._server = None
        
        self.app = None
        self.config = None
        
        logger.info("REST handler shutdown complete")
