"""
AvatarMCP API Module

This module provides a comprehensive API for interacting with AvatarMCP,
including RESTful endpoints, WebSocket support, and event streaming.
"""
import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Awaitable, Set

import aiohttp
import aiohttp.web
import aiohttp_cors
from aiohttp import WSMsgType, web
from fastmcp import FastMCP

# Create a FastMCP instance for the API
mcp = FastMCP("AvatarAPI")

from .animation_v2 import AnimationController, AnimationClip
from ..models.model_manager import VRMModelManager
from ..interfaces.service import AvatarService

logger = logging.getLogger(__name__)

# Type aliases
JsonDict = Dict[str, Any]
RequestHandler = Callable[[aiohttp.web.Request], Awaitable[aiohttp.web.Response]]

class APIError(Exception):
    """Base exception for API-related errors."""
    def __init__(self, message: str, status: int = 400, code: str = None, details: JsonDict = None):
        self.message = message
        self.status = status
        self.code = code or f"ERR_{status}"
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> JsonDict:
        """Convert the error to a dictionary for JSON serialization."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "status": self.status
            }
        }

class AvatarAPI:
    """
    Main API class for AvatarMCP, providing RESTful and WebSocket interfaces.
    """
    
    def __init__(self, model_manager: Optional[VRMModelManager] = None, service: Optional[AvatarService] = None):
        """Initialize the API with optional model manager and service instances."""
        self.model_manager = model_manager or VRMModelManager()
        self.service = service or AvatarService()
        self.animation_controllers: Dict[str, AnimationController] = {}
        self.websockets: Set[web.WebSocketResponse] = set()
        self.app = self._create_app()
        self._setup_routes()
    
    def _create_app(self) -> aiohttp.web.Application:
        """Create and configure the aiohttp web application."""
        app = web.Application(client_max_size=1024**3)  # 1GB max upload size
        
        # Configure CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            )
        })
        
        # Add CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
        
        # Add middleware for error handling and logging
        app.middlewares.append(self._error_middleware)
        app.middlewares.append(self._logging_middleware)
        
        # Add cleanup on shutdown
        app.on_shutdown.append(self._on_shutdown)
        
        return app
    
    @web.middleware
    async def _error_middleware(self, request: aiohttp.web.Request, handler: RequestHandler) -> aiohttp.web.Response:
        """Middleware for handling exceptions and formatting error responses."""
        try:
            return await handler(request)
        except APIError as e:
            return web.json_response(e.to_dict(), status=e.status)
        except Exception as e:
            logger.exception(f"Unhandled exception in {request.path}")
            error = APIError("Internal server error", status=500, details={"exception": str(e)})
            return web.json_response(error.to_dict(), status=error.status)
    
    @web.middleware
    async def _logging_middleware(self, request: aiohttp.web.Request, handler: RequestHandler) -> aiohttp.web.Response:
        """Middleware for request logging."""
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.path}")
        
        try:
            response = await handler(request)
            process_time = time.time() - start_time
            logger.info(f"Response: {request.method} {request.path} -> {response.status} ({process_time:.3f}s)")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error in {request.path}: {str(e)} ({process_time:.3f}s)")
            raise
    
    def _setup_routes(self) -> None:
        """Set up all API routes."""
        # Model management
        self.app.router.add_route('GET', '/api/v1/models', self.list_models)
        self.app.router.add_route('POST', '/api/v1/models', self.upload_model)
        self.app.router.add_route('GET', '/api/v1/models/{model_id}', self.get_model)
        self.app.router.add_route('DELETE', '/api/v1/models/{model_id}', self.delete_model)
        
        # Animation
        self.app.router.add_route('GET', '/api/v1/animations', self.list_animations)
        self.app.router.add_route('POST', '/api/v1/animations', self.upload_animation)
        self.app.router.add_route('GET', '/api/v1/animations/{anim_id}', self.get_animation)
        self.app.router.add_route('DELETE', '/api/v1/animations/{anim_id}', self.delete_animation)
        
        # Avatar instances
        self.app.router.add_route('GET', '/api/v1/avatars', self.list_avatars)
        self.app.router.add_route('POST', '/api/v1/avatars', self.create_avatar)
        self.app.router.add_route('GET', '/api/v1/avatars/{avatar_id}', self.get_avatar)
        self.app.router.add_route('PUT', '/api/v1/avatars/{avatar_id}', self.update_avatar)
        self.app.router.add_route('DELETE', '/api/v1/avatars/{avatar_id}', self.delete_avatar)
        
        # Animation control
        self.app.router.add_route('POST', '/api/v1/avatars/{avatar_id}/play', self.play_animation)
        self.app.router.add_route('POST', '/api/v1/avatars/{avatar_id}/stop', self.stop_animation)
        self.app.router.add_route('POST', '/api/v1/avatars/{avatar_id}/blend-shape', self.set_blend_shape)
        
        # WebSocket for real-time updates
        self.app.router.add_route('GET', '/ws', self.websocket_handler)
        
        # Static files (for web UI)
        self.app.router.add_static('/static', 'static', follow_symlinks=True)
        
        # Serve index.html for all other routes (SPA support)
        self.app.router.add_route('GET', '/{path:.*}', self.serve_static)
    
    async def _on_shutdown(self, app: aiohttp.web.Application) -> None:
        """Clean up resources on server shutdown."""
        # Close all WebSocket connections
        for ws in list(self.websockets):
            await ws.close()
        
        # Clean up model manager and service
        await self.model_manager.cleanup()
        await self.service.cleanup()
    
    # Model management endpoints
    async def list_models(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """List all loaded VRM models."""
        models = []
        for model_id, entry in self.model_manager.get_cache_info().get('entries', {}).items():
            models.append({
                'id': model_id,
                'name': entry.get('name', 'Unknown'),
                'file_path': entry.get('file_path'),
                'size_mb': entry.get('size_bytes', 0) / (1024 * 1024),
                'load_time': entry.get('load_time', 0),
                'last_accessed': entry.get('last_accessed', 0)
            })
        
        return web.json_response({
            'status': 'success',
            'data': {
                'models': models,
                'count': len(models)
            }
        })
    
    async def upload_model(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Upload and load a new VRM model."""
        # Check if the post request has the file part
        if not request.has_body or 'file' not in (await request.post()):
            raise APIError("No file part in the request", status=400)
        
        data = await request.post()
        file_field = data['file']
        
        if not file_field.filename:
            raise APIError("No selected file", status=400)
        
        if not file_field.filename.lower().endswith('.vrm'):
            raise APIError("Invalid file type. Only .vrm files are supported.", status=400)
        
        # Save the uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file_field.filename
        file_path.write_bytes(file_field.file.read())
        
        # Load the model
        try:
            model = self.model_manager.load_model(str(file_path), validate=True)
            
            return web.json_response({
                'status': 'success',
                'data': {
                    'model_id': str(file_path),
                    'name': model.metadata.get('name', 'Unnamed'),
                    'version': model.metadata.get('version', '1.0'),
                    'bones_count': len(model.bones),
                    'materials_count': len(model.materials)
                }
            })
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise APIError(f"Failed to load model: {str(e)}", status=500)
    
    async def get_model(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Get details about a specific model."""
        model_id = request.match_info.get('model_id')
        if not model_id:
            raise APIError("Model ID is required", status=400)
        
        # Get model from cache or load it
        model = self.model_manager.get_model(model_id)
        if not model:
            raise APIError("Model not found", status=404)
        
        return web.json_response({
            'status': 'success',
            'data': {
                'id': model_id,
                'name': model.metadata.get('name', 'Unnamed'),
                'version': model.metadata.get('version', '1.0'),
                'bones': [{'name': b.name, 'parent': b.parent} for b in model.bones],
                'materials': [{'name': m.name} for m in model.materials],
                'metadata': model.metadata
            }
        })
    
    async def delete_model(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Unload a model from memory."""
        model_id = request.match_info.get('model_id')
        if not model_id:
            raise APIError("Model ID is required", status=400)
        
        if self.model_manager.unload_model(model_id):
            return web.json_response({'status': 'success'})
        else:
            raise APIError("Failed to unload model", status=500)
    
    # Animation endpoints
    async def list_animations(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """List all available animations."""
        # TODO: Implement animation listing
        return web.json_response({
            'status': 'success',
            'data': {
                'animations': [],
                'count': 0
            }
        })
    
    async def upload_animation(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Upload a new animation."""
        # TODO: Implement animation upload
        raise APIError("Not implemented", status=501)
    
    async def get_animation(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Get details about a specific animation."""
        # TODO: Implement getting animation details
        raise APIError("Not implemented", status=501)
    
    async def delete_animation(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Delete an animation."""
        # TODO: Implement animation deletion
        raise APIError("Not implemented", status=501)
    
    # Avatar instance endpoints
    async def list_avatars(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """List all avatar instances."""
        # TODO: Implement avatar listing
        return web.json_response({
            'status': 'success',
            'data': {
                'avatars': [],
                'count': 0
            }
        })
    
    async def create_avatar(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Create a new avatar instance."""
        data = await request.json()
        model_id = data.get('model_id')
        
        if not model_id:
            raise APIError("model_id is required", status=400)
        
        # Load the model if not already loaded
        model = self.model_manager.get_model(model_id)
        if not model:
            model = self.model_manager.load_model(model_id)
            if not model:
                raise APIError(f"Failed to load model: {model_id}", status=400)
        
        # Create a new avatar instance
        avatar_id = str(uuid.uuid4())
        self.service.create_avatar(avatar_id, model)
        
        # Create an animation controller for this avatar
        self.animation_controllers[avatar_id] = AnimationController()
        
        return web.json_response({
            'status': 'success',
            'data': {
                'avatar_id': avatar_id,
                'model_id': model_id,
                'created_at': datetime.utcnow().isoformat()
            }
        }, status=201)
    
    async def get_avatar(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Get details about a specific avatar instance."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        avatar = self.service.get_avatar(avatar_id)
        if not avatar:
            raise APIError("Avatar not found", status=404)
        
        # Get animation state if available
        anim_state = {}
        if avatar_id in self.animation_controllers:
            anim_controller = self.animation_controllers[avatar_id]
            anim_state = {
                'active_animations': [
                    {
                        'name': name,
                        'time': state.time,
                        'weight': state.weight,
                        'loop': state.loop,
                        'speed': state.speed
                    }
                    for name, state in anim_controller.states.items()
                ]
            }
        
        return web.json_response({
            'status': 'success',
            'data': {
                'id': avatar_id,
                'model_id': avatar.model_id,
                'position': avatar.position,
                'rotation': avatar.rotation,
                'scale': avatar.scale,
                'blend_shapes': avatar.blend_shapes,
                'animation': anim_state,
                'created_at': avatar.created_at.isoformat() if hasattr(avatar, 'created_at') else None,
                'updated_at': avatar.updated_at.isoformat() if hasattr(avatar, 'updated_at') else None
            }
        })
    
    async def update_avatar(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Update avatar properties."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        data = await request.json()
        avatar = self.service.get_avatar(avatar_id)
        if not avatar:
            raise APIError("Avatar not found", status=404)
        
        # Update position if provided
        if 'position' in data:
            avatar.position = data['position']
        
        # Update rotation if provided
        if 'rotation' in data:
            avatar.rotation = data['rotation']
        
        # Update scale if provided
        if 'scale' in data:
            avatar.scale = data['scale']
        
        # Update blend shapes if provided
        if 'blend_shapes' in data:
            for name, value in data['blend_shapes'].items():
                avatar.set_blend_shape(name, value)
        
        return web.json_response({
            'status': 'success',
            'data': {
                'id': avatar_id,
                'updated': True
            }
        })
    
    async def delete_avatar(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Delete an avatar instance."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        if self.service.delete_avatar(avatar_id):
            # Clean up animation controller
            if avatar_id in self.animation_controllers:
                del self.animation_controllers[avatar_id]
            
            return web.json_response({'status': 'success'})
        else:
            raise APIError("Avatar not found", status=404)
    
    # Animation control endpoints
    async def play_animation(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Play an animation on an avatar."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        data = await request.json()
        animation_name = data.get('animation')
        loop = data.get('loop', False)
        fade_time = data.get('fade_time', 0.1)
        
        if not animation_name:
            raise APIError("Animation name is required", status=400)
        
        if avatar_id not in self.animation_controllers:
            raise APIError("Avatar not found or no animation controller", status=404)
        
        # TODO: Load animation clip if not already loaded
        # For now, we'll just create a simple animation
        clip = AnimationClip(
            name=animation_name,
            duration=1.0,
            loop=loop
        )
        
        # Play the animation
        anim_controller = self.animation_controllers[avatar_id]
        anim_controller.play_animation("base", clip, fade_time=fade_time)
        
        return web.json_response({
            'status': 'success',
            'data': {
                'avatar_id': avatar_id,
                'animation': animation_name,
                'loop': loop,
                'fade_time': fade_time
            }
        })
    
    async def stop_animation(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Stop all animations on an avatar."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        if avatar_id not in self.animation_controllers:
            raise APIError("Avatar not found or no animation controller", status=404)
        
        # Stop all animations
        anim_controller = self.animation_controllers[avatar_id]
        anim_controller.stop_all_animations()
        
        return web.json_response({
            'status': 'success',
            'data': {
                'avatar_id': avatar_id,
                'stopped': True
            }
        })
    
    async def set_blend_shape(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Set a blend shape value on an avatar."""
        avatar_id = request.match_info.get('avatar_id')
        if not avatar_id:
            raise APIError("Avatar ID is required", status=400)
        
        data = await request.json()
        name = data.get('name')
        value = data.get('value')
        
        if not name or value is None:
            raise APIError("Name and value are required", status=400)
        
        avatar = self.service.get_avatar(avatar_id)
        if not avatar:
            raise APIError("Avatar not found", status=404)
        
        # Set the blend shape value
        avatar.set_blend_shape(name, value)
        
        return web.json_response({
            'status': 'success',
            'data': {
                'avatar_id': avatar_id,
                'blend_shape': name,
                'value': value
            }
        })
    
    # WebSocket handler for real-time updates
    async def websocket_handler(self, request: aiohttp.web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info(f"New WebSocket connection (total: {len(self.websockets)})")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_json({
                            'type': 'error',
                            'error': 'Invalid JSON'
                        })
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {str(e)}")
                        await ws.send_json({
                            'type': 'error',
                            'error': str(e)
                        })
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        finally:
            self.websockets.discard(ws)
            logger.info(f"WebSocket disconnected (total: {len(self.websockets)})")
        
        return ws
    
    async def _handle_websocket_message(self, ws: web.WebSocketResponse, data: dict) -> None:
        """Handle incoming WebSocket messages."""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # Handle subscription to updates
            await self._handle_subscription(ws, data)
        elif msg_type == 'unsubscribe':
            # Handle unsubscription
            await self._handle_unsubscription(ws, data)
        elif msg_type == 'command':
            # Handle command execution
            await self._handle_command(ws, data)
        else:
            await ws.send_json({
                'type': 'error',
                'error': 'Unknown message type',
                'data': data
            })
    
    async def _handle_subscription(self, ws: web.WebSocketResponse, data: dict) -> None:
        """Handle subscription requests."""
        # TODO: Implement subscription logic
        await ws.send_json({
            'type': 'subscribed',
            'data': {
                'message': 'Subscription not yet implemented'
            }
        })
    
    async def _handle_unsubscription(self, ws: web.WebSocketResponse, data: dict) -> None:
        """Handle unsubscription requests."""
        # TODO: Implement unsubscription logic
        await ws.send_json({
            'type': 'unsubscribed',
            'data': {
                'message': 'Unsubscription not yet implemented'
            }
        })
    
    async def _handle_command(self, ws: web.WebSocketResponse, data: dict) -> None:
        """Handle command execution requests."""
        command = data.get('command')
        data.get('params', {})
        
        # TODO: Implement command handling
        await ws.send_json({
            'type': 'command_result',
            'data': {
                'command': command,
                'status': 'not_implemented',
                'result': None
            }
        })
    
    async def serve_static(self, request: aiohttp.web.Request) -> aiohttp.web.FileResponse:
        """Serve static files for the web UI."""
        # Default to index.html for SPA routing
        path = request.match_info['path']
        if not path or path == '/':
            path = 'index.html'
        
        static_dir = Path('static')
        file_path = static_dir / path
        
        if not file_path.exists() or not file_path.is_file():
            # For SPA, return index.html for all routes
            file_path = static_dir / 'index.html'
            if not file_path.exists():
                raise web.HTTPNotFound()
        
        return web.FileResponse(file_path)
    
    def run(self, host: str = '0.0.0.0', port: int = 8080) -> None:
        """Run the API server."""
        logger.info(f"Starting AvatarMCP API server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)

# Command-line interface
def main():
    """Run the API server from the command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AvatarMCP API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    
    # Create and run the API server
    api = AvatarAPI()
    api.run(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
