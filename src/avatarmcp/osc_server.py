"""
OSC Server for VRChat Integration

This module provides OSC (Open Sound Control) server functionality for
receiving and processing VRChat avatar parameters in real-time.
"""
import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
import logging
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

logger = logging.getLogger(__name__)

@dataclass
class VRChatOSCServer:
    """OSC server for handling VRChat avatar parameters."""
    
    ip: str = "127.0.0.1"
    receive_port: int = 9000
    send_port: int = 9001
    _dispatcher: Dispatcher = field(default_factory=Dispatcher)
    _server: Optional[AsyncIOOSCUDPServer] = None
    _client: Optional[SimpleUDPClient] = None
    _callbacks: Dict[str, List[Callable]] = field(default_factory=dict)
    _parameters: Dict[str, Any] = field(default_factory=dict)
    _running: bool = False
    _loop: Optional[asyncio.AbstractEventLoop] = None

    def __post_init__(self):
        """Initialize the OSC server and client."""
        self._dispatcher.set_default_handler(self._handle_osc_message)
        self._client = SimpleUDPClient(self.ip, self.send_port)

    def on_parameter_change(self, parameter: str):
        """Decorator to register a callback for parameter changes."""
        def decorator(callback):
            if parameter not in self._callbacks:
                self._callbacks[parameter] = []
            self._callbacks[parameter].append(callback)
            return callback
        return decorator

    async def start(self):
        """Start the OSC server."""
        if self._running:
            return
            
        self._loop = asyncio.get_running_loop()
        self._server = AsyncIOOSCUDPServer(
            (self.ip, self.receive_port),
            self._dispatcher,
            self._loop
        )
        
        transport, _ = await self._server.create_serve_endpoint()
        self._running = True
        logger.info(f"OSC Server started on {self.ip}:{self.receive_port}")
        return transport

    async def stop(self):
        """Stop the OSC server."""
        if not self._running or not self._server:
            return
            
        self._server.close()
        self._running = False
        logger.info("OSC Server stopped")

    def _handle_osc_message(self, address: str, *args):
        """Handle incoming OSC messages."""
        if not address.startswith("/avatar/parameters/"):
            return
            
        parameter = address.split("/")[-1]
        value = args[0] if args else None
        
        # Update parameter value
        self._parameters[parameter] = value
        
        # Trigger callbacks
        if parameter in self._callbacks:
            for callback in self._callbacks[parameter]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(parameter, value))
                    else:
                        callback(parameter, value)
                except Exception as e:
                    logger.error(f"Error in OSC callback for {parameter}: {e}")
        
        logger.debug(f"OSC Parameter updated: {parameter} = {value}")

    def get_parameter(self, parameter: str, default=None) -> Any:
        """Get the current value of a parameter."""
        return self._parameters.get(parameter, default)
    
    def set_parameter(self, parameter: str, value: Any):
        """Set a parameter value and send it via OSC."""
        if not self._client:
            logger.warning("OSC client not initialized")
            return
            
        address = f"/avatar/parameters/{parameter}"
        self._parameters[parameter] = value
        self._client.send_message(address, value)
        logger.debug(f"OSC Parameter sent: {parameter} = {value}")

    async def send_gesture(self, hand: str, gesture: str, strength: float = 1.0):
        """Send a gesture command to VRChat."""
        if hand.lower() not in ["left", "right"]:
            raise ValueError("Hand must be 'left' or 'right'")
            
        gesture = gesture.capitalize()
        valid_gestures = ["Fist", "Open", "Point", "Peace", "RockNRoll", 
                         "Gun", "ThumbsUp"]
                          
        if gesture not in valid_gestures:
            raise ValueError(f"Invalid gesture. Must be one of: {valid_gestures}")
            
        parameter = f"Gesture{hand.capitalize()}"
        self.set_parameter(parameter, gesture)
        
        # For analog gestures, also set the weight
        if gesture in ["Fist", "Open"]:
            self.set_parameter(f"Gesture{hand.capitalize()}Weight", strength)

    async def send_expression(self, expression: str, strength: float = 1.0):
        """Send a facial expression to VRChat."""
        valid_expressions = [
            "Neutral", "Angry", "Happy", "Sad", "Surprised",
            "Blink", "BlinkLeft", "BlinkRight", "EyesWide",
            "Squint", "LookDown", "LookLeft", "LookRight", "LookUp"
        ]
        
        if expression not in valid_expressions:
            raise ValueError(f"Invalid expression. Must be one of: {valid_expressions}")
            
        self.set_parameter(expression, float(strength))

    async def send_viseme(self, viseme: str, strength: float = 1.0):
        """Send a viseme value to VRChat."""
        valid_visemes = [
            "Sil", "PP", "FF", "TH", "DD", "kk", "CH", "SS", "nn", "RR", "aa", 
            "E", "I", "O", "U"
        ]
        
        if viseme not in valid_visemes:
            raise ValueError(f"Invalid viseme. Must be one of: {valid_visemes}")
            
        self.set_parameter("Viseme", viseme)
        self.set_parameter("VisemeWeight", float(strength))
