"""
FastMCP 2.10.1 server implementation for AvatarMCP.

This module implements the MCP protocol for communication with clients.
"""
import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, Callable, Awaitable

from ..models.vrm_model import VRMModel
from ..models.animation_controller import AnimationController

logger = logging.getLogger(__name__)

class MCPServer:
    """FastMCP 2.10.1 server implementation."""
    
    def __init__(self, app):
        """Initialize the MCP server.
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.running = False
        self.message_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        self.command_handlers = {}
        
        # Register default command handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default command handlers."""
        self.register_handler("echo", self._handle_echo)
        self.register_handler("list_commands", self._handle_list_commands)
        self.register_handler("get_version", self._handle_get_version)
    
    def register_handler(self, command: str, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        """Register a command handler.
        
        Args:
            command: Command name
            handler: Async function that takes a message and returns a response
        """
        self.command_handlers[command] = handler
    
    async def start(self):
        """Start the MCP server."""
        self.running = True
        logger.info("Starting MCP server on stdio")
        
        # Set up stdio
        self.reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self.reader)
        transport, _ = await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        self.writer_transport, self.writer = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin,
            asyncio.streams.StreamWriterProtocol(
                asyncio.StreamReader(),
                asyncio.StreamWriter(
                    transport=sys.stdout.buffer,
                    protocol=None,
                    reader=None,
                    loop=asyncio.get_event_loop()
                )
            )
        )
        
        # Start message processing
        asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
    
    async def _process_messages(self):
        """Process incoming messages."""
        while self.running and self.reader:
            try:
                # Read message length (4 bytes, big-endian)
                length_bytes = await self.reader.readexactly(4)
                length = int.from_bytes(length_bytes, byteorder='big')
                
                # Read message data
                data = await self.reader.readexactly(length)
                message = json.loads(data.decode('utf-8'))
                
                # Process message
                asyncio.create_task(self._handle_message(message))
                
            except asyncio.IncompleteReadError:
                # Connection closed
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle an incoming MCP message.
        
        Args:
            message: The message to handle
        """
        try:
            message_id = message.get('id')
            command = message.get('command')
            params = message.get('params', {})
            
            # Handle response to a request
            if 'result' in message or 'error' in message:
                if message_id in self.pending_requests:
                    future = self.pending_requests.pop(message_id)
                    if 'error' in message:
                        future.set_exception(Exception(message['error'].get('message', 'Unknown error')))
                    else:
                        future.set_result(message.get('result'))
                return
            
            # Handle command
            if not command:
                await self._send_error(message_id, "No command specified")
                return
            
            handler = self.command_handlers.get(command)
            if not handler:
                await self._send_error(message_id, f"Unknown command: {command}")
                return
            
            try:
                result = await handler(params)
                await self._send_response(message_id, result)
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}", exc_info=True)
                await self._send_error(message_id, str(e))
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _send_response(self, message_id: Optional[int], result: Any):
        """Send a response to a message.
        
        Args:
            message_id: The ID of the message being responded to
            result: The result to send
        """
        response = {
            'jsonrpc': '2.0',
            'id': message_id
        }
        
        if isinstance(result, Exception):
            response['error'] = {
                'code': -32603,
                'message': str(result)
            }
        else:
            response['result'] = result
        
        await self._send_json(response)
    
    async def _send_error(self, message_id: Optional[int], message: str, code: int = -32603):
        """Send an error response.
        
        Args:
            message_id: The ID of the message being responded to
            message: The error message
            code: The error code
        """
        response = {
            'jsonrpc': '2.0',
            'id': message_id,
            'error': {
                'code': code,
                'message': message
            }
        }
        await self._send_json(response)
    
    async def _send_json(self, data: Dict[str, Any]):
        """Send a JSON message.
        
        Args:
            data: The data to send
        """
        if not self.writer:
            return
            
        try:
            message = json.dumps(data).encode('utf-8')
            length = len(message).to_bytes(4, byteorder='big')
            self.writer.write(length + message)
            await self.writer.drain()
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
    
    # Command Handlers
    async def _handle_echo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Echo a message back to the client."""
        return {'message': params.get('message', '')}
    
    async def _handle_list_commands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available commands."""
        return {'commands': list(self.command_handlers.keys())}
    
    async def _handle_get_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the server version."""
        return {
            'name': 'AvatarMCP',
            'version': '1.0.0',
            'mcp_version': '2.10.1',
            'features': ['osc', 'vrm', 'animation']
        }
