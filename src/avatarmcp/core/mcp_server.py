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
        if self.running:
            return
            
        self.running = True
        logger.info("Starting MCP server on stdio")
        
        try:
            # Get the current event loop
            loop = asyncio.get_running_loop()
            
            # For Windows, we'll use a simpler approach with StreamReader/Writer
            if sys.platform == 'win32':
                # Create a StreamReader for stdin
                self.reader = asyncio.StreamReader()
                
                # Create a StreamWriter for stdout
                # We'll use a custom transport that writes directly to sys.stdout
                class StdoutTransport(asyncio.Transport):
                    def __init__(self, loop=None):
                        super().__init__(extra={'peername': ('<stdio>', 0)})
                        self._loop = loop or asyncio.get_event_loop()
                        self._closing = False
                        self._protocol = None
                    
                    def write(self, data):
                        if not self._closing:
                            try:
                                sys.stdout.buffer.write(data)
                                sys.stdout.buffer.flush()
                            except Exception as e:
                                logger.error(f"Error writing to stdout: {e}")
                    
                    def is_closing(self):
                        return self._closing
                    
                    def close(self):
                        if not self._closing:
                            self._closing = True
                            if self._protocol:
                                self._loop.call_soon(self._protocol.connection_lost, None)
                    
                    def abort(self):
                        self.close()
                
                # Create the transport and protocol for stdout
                transport = StdoutTransport(loop=loop)
                protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader())
                transport._protocol = protocol
                protocol.connection_made(transport)
                
                # Create the StreamWriter
                self.writer = asyncio.StreamWriter(transport, protocol, None, loop)
                
                # Start a task to read from stdin
                async def read_stdin():
                    while self.running:
                        try:
                            line = await loop.run_in_executor(None, sys.stdin.readline)
                            if not line:  # EOF
                                break
                            await self.reader.feed_data(line.encode())
                        except Exception as e:
                            logger.error(f"Error reading from stdin: {e}")
                            break
                    
                loop.create_task(read_stdin())
                
            else:
                # Non-Windows platforms can use the standard approach
                self.reader = asyncio.StreamReader()
                protocol = asyncio.StreamReaderProtocol(self.reader)
                
                # Connect to stdin
                transport, _ = await loop.connect_read_pipe(
                    lambda: protocol, sys.stdin
                )
                
                # Create a StreamWriter for stdout
                write_protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader())
                self.writer_transport, _ = await loop.connect_write_pipe(
                    lambda: write_protocol, sys.stdout.buffer
                )
                
                # Create the writer
                self.writer = asyncio.StreamWriter(
                    transport=self.writer_transport,
                    protocol=write_protocol,
                    reader=None
                )
                self._write_stdout = None
            
            # Start message processing
            self._process_task = asyncio.create_task(self._process_messages())
            logger.info("MCP server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self.running = False
            raise
    
    async def stop(self):
        """Stop the MCP server."""
        if not self.running:
            return
            
        logger.info("Stopping MCP server...")
        self.running = False
        
        # Cancel the process task
        if hasattr(self, '_process_task') and self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
            
        # Close the writer
        if self.writer:
            try:
                if sys.platform == 'win32':
                    # For Windows, we need to handle the custom transport
                    if hasattr(self.writer, 'transport') and hasattr(self.writer.transport, 'close'):
                        self.writer.transport.close()
                else:
                    # For non-Windows, use standard close
                    self.writer.close()
                    try:
                        await self.writer.wait_closed()
                    except Exception as e:
                        logger.error(f"Error closing writer: {e}")
            except Exception as e:
                logger.error(f"Error during writer close: {e}")
        
        # Close the reader
        if self.reader:
            self.reader.feed_eof()
            
        # Clean up any pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()
            
        logger.info("MCP server stopped")
    
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
        """Send a JSON message."""
        if not self.writer:
            return
            
        try:
            message = json.dumps(data).encode('utf-8')
            if hasattr(self, '_write_stdout') and self._write_stdout:
                # Use direct write for Windows
                self._write_stdout(message + b'\n')
            else:
                # Use StreamWriter for other platforms
                self.writer.write(message + b'\n')
                await self.writer.drain()
        except Exception as e:
            logger.error(f"Error sending JSON: {e}")
            raise
    
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
