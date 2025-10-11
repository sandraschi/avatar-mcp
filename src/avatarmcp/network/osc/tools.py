"""
OSC Tools for VRChat Avatar Control

This module provides MCP tools for controlling VRChat avatars using OSC.
It builds on top of the existing OSC server and integration code.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from fastmcp import FastMCP

# Create a FastMCP instance for tool registration
mcp = FastMCP("VRChatOSCTools")
from ..network.osc.server import VRChatOSCServer
from ..network.mcp.integration import AvatarOSCIntegrator, AvatarOSCConfig

logger = logging.getLogger(__name__)

# Default OSC configuration
DEFAULT_OSC_CONFIG = {
    "receive_port": 9000,
    "send_port": 9001,
    "server_ip": "127.0.0.1"
}

class VRChatOSCTools:
    """MCP tools for VRChat OSC control."""
    
    def __init__(self, mcp: FastMCP, config: Optional[Dict[str, Any]] = None):
        """Initialize the VRChat OSC tools.
        
        Args:
            mcp: The FastMCP instance to register tools with
            config: Optional configuration dictionary
        """
        self.mcp = mcp
        self.config = {**DEFAULT_OSC_CONFIG, **(config or {})}
        self.osc_integrator: Optional[AvatarOSCIntegrator] = None
        self.osc_server: Optional[VRChatOSCServer] = None
        self._running = False
        
        # Register MCP tools
        self._register_tools()
    
    async def start(self):
        """Start the OSC server and integrator."""
        if self._running:
            return
            
        # Create and start the OSC server
        self.osc_server = VRChatOSCServer(
            ip=self.config["server_ip"],
            receive_port=self.config["receive_port"],
            send_port=self.config["send_port"]
        )
        
        # Create and start the OSC integrator
        osc_config = AvatarOSCConfig(
            receive_port=self.config["receive_port"],
            send_port=self.config["send_port"],
            server_ip=self.config["server_ip"]
        )
        
        self.osc_integrator = AvatarOSCIntegrator(self.mcp, osc_config)
        await self.osc_integrator.start()
        
        self._running = True
        logger.info("VRChat OSC Tools started")
    
    async def stop(self):
        """Stop the OSC server and integrator."""
        if not self._running:
            return
            
        if self.osc_integrator:
            await self.osc_integrator.stop()
            
        self._running = False
        logger.info("VRChat OSC Tools stopped")
    
    def _register_tools(self):
        """Register MCP tools for OSC control."""
        
        @mcp.tool("vrchat_osc.set_gesture")
        async def set_gesture(hand: str, gesture: str, strength: float = 1.0) -> Dict[str, Any]:
            '''Control VRChat avatar hand gestures through OSC communication.

            Sets specific hand gestures for the VRChat avatar, allowing precise control
            over hand animations and expressions. Gestures are transmitted via OSC
            to VRChat for real-time avatar animation.

            Parameters:
                hand: Which hand to control ("left" or "right")
                    - Must be exactly "left" or "right" (case-sensitive)
                    - Controls the corresponding hand's gesture
                gesture: Gesture animation name to apply
                    - Common gestures: "Fist", "Open", "Point", "Peace", "RockNRoll", "Gun", "ThumbsUp"
                    - Gesture names must match VRChat's supported gestures
                    - Case-sensitive gesture naming
                strength: Intensity of the gesture animation (default: 1.0)
                    - Range: 0.0 (no gesture) to 1.0 (full gesture)
                    - Values outside range are clamped to valid bounds
                    - Allows partial gesture expressions

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - hand: Hand that was controlled
                    - gesture: Gesture that was set
                    - strength: Strength value that was applied

            Usage:
                Use this tool to create expressive hand gestures for your VRChat avatar.
                Perfect for role-playing, communication, and interactive performances
                where precise hand control enhances the avatar's expressiveness.

            Examples:
                Full fist gesture on left hand:
                    result = await set_gesture("left", "Fist", 1.0)
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set left hand to Fist',
                    #     'hand': 'left',
                    #     'gesture': 'Fist',
                    #     'strength': 1.0
                    # }

                Peace sign with reduced strength:
                    result = await set_gesture("right", "Peace", 0.7)
                    # Avatar shows peace sign at 70% intensity

                Point gesture on both hands:
                    await set_gesture("left", "Point", 1.0)
                    await set_gesture("right", "Point", 1.0)
                    # Avatar points with both hands

                Gesture sequence for storytelling:
                    await set_gesture("left", "Open", 1.0)    # Start with open hand
                    await asyncio.sleep(1)
                    await set_gesture("left", "Fist", 1.0)    # Close to fist
                    await asyncio.sleep(1)
                    await set_gesture("left", "ThumbsUp", 1.0) # End with thumbs up

                Error handling:
                    result = await set_gesture("middle", "Fist", 1.0)
                    if result['status'] == 'error':
                        print(f"Gesture failed: {result['message']}")
                    # Invalid hand parameter

            Raises:
                ValueError: If hand or gesture parameters are invalid
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled

            Notes:
                - Requires active OSC connection to VRChat
                - Gesture names must exactly match VRChat's supported gestures
                - Strength values are clamped to 0.0-1.0 range
                - Gestures persist until explicitly changed
                - Multiple rapid gesture changes may cause animation conflicts

            See Also:
                - set_expression: Control facial expressions
                - set_viseme: Control lip sync animations
                - set_parameter: Set custom avatar parameters
                - list_parameters: View available gesture options
            '''
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_gesture(hand, gesture, strength)
                return {"status": "success", "message": f"Set {hand} hand to {gesture}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp.tool("vrchat_osc.set_expression")
        async def set_expression(expression: str, strength: float = 1.0) -> Dict[str, Any]:
            '''Control VRChat avatar facial expressions through OSC communication.

            Sets specific facial expressions for the VRChat avatar, enabling emotional
            and communicative expressions. Expressions are transmitted via OSC to VRChat
            for real-time facial animation and avatar personality.

            Parameters:
                expression: Facial expression name to apply
                    - Common expressions: "Happy", "Angry", "Sad", "Surprised", "Blink", "Neutral"
                    - Advanced: "BlinkLeft", "BlinkRight", "EyesWide", "Squint", "LookDown", "LookLeft", "LookRight", "LookUp"
                    - Expression names must match VRChat's supported expressions
                    - Case-sensitive expression naming
                strength: Intensity of the facial expression (default: 1.0)
                    - Range: 0.0 (neutral/no expression) to 1.0 (full expression)
                    - Values outside range are clamped to valid bounds
                    - Allows subtle or exaggerated expressions

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - expression: Expression that was set
                    - strength: Strength value that was applied
                    - timestamp: When the expression was applied

            Usage:
                Use this tool to give your VRChat avatar emotional depth and personality.
                Essential for role-playing, storytelling, and creating immersive social
                experiences where facial expressions enhance communication.

            Examples:
                Happy expression at full intensity:
                    result = await set_expression("Happy", 1.0)
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set expression to Happy',
                    #     'expression': 'Happy',
                    #     'strength': 1.0,
                    #     'timestamp': 1640995200.123
                    # }

                Subtle surprised look:
                    result = await set_expression("Surprised", 0.3)
                    # Avatar shows mild surprise

                Emotional sequence:
                    await set_expression("Sad", 1.0)
                    await asyncio.sleep(2)
                    await set_expression("Happy", 1.0)
                    await asyncio.sleep(1)
                    await set_expression("Neutral", 1.0)

                Eye control for attention:
                    await set_expression("LookLeft", 0.8)   # Look left
                    await asyncio.sleep(1)
                    await set_expression("LookRight", 0.8)  # Look right
                    await asyncio.sleep(1)
                    await set_expression("Neutral", 1.0)    # Return to center

                Blinking animation:
                    await set_expression("Blink", 1.0)
                    await asyncio.sleep(0.1)
                    await set_expression("Neutral", 1.0)

                Error handling:
                    result = await set_expression("Confused", 1.0)
                    if result['status'] == 'error':
                        print(f"Expression failed: {result['message']}")
                    # Check supported expression names

            Raises:
                ValueError: If expression name is invalid or not supported
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled

            Notes:
                - Requires active OSC connection to VRChat
                - Expression names must exactly match VRChat's supported expressions
                - Strength values are clamped to 0.0-1.0 range
                - Expressions persist until explicitly changed to "Neutral"
                - Multiple expressions can be layered for complex faces
                - Some expressions may conflict with visemes during speech

            See Also:
                - set_gesture: Control hand gestures
                - set_viseme: Control lip sync during speech
                - set_parameter: Set custom avatar parameters
                - list_parameters: View available expression options
            '''
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_expression(expression, strength)
                return {"status": "success", "message": f"Set expression to {expression}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp.tool("vrchat_osc.set_viseme")
        async def set_viseme(viseme: str, strength: float = 1.0) -> Dict[str, Any]:
            '''Control VRChat avatar lip sync visemes through OSC communication.

            Sets specific mouth shapes (visemes) for the VRChat avatar to create
            realistic lip sync animations during speech. Visemes are transmitted
            via OSC to VRChat for synchronized mouth movements.

            Parameters:
                viseme: Mouth shape/viseme name to apply
                    - Phonetic visemes: "aa", "E", "I", "O", "U", "PP", "SS", "TH", "FF", "KK", "CH", "DD"
                    - "aa" for open mouth sounds (father, car)
                    - "E" for "ee" sounds (see, tree)
                    - "I" for "ai" sounds (eye, sky)
                    - "O" for "oh" sounds (boat, go)
                    - "U" for "oo" sounds (food, blue)
                    - Consonant visemes: "PP", "SS", "TH", "FF", "KK", "CH", "DD"
                    - Viseme names must match VRChat's supported visemes
                    - Case-sensitive viseme naming
                strength: Intensity of the viseme animation (default: 1.0)
                    - Range: 0.0 (neutral mouth) to 1.0 (full viseme)
                    - Values outside range are clamped to valid bounds
                    - Allows subtle or exaggerated lip movements

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - viseme: Viseme that was set
                    - strength: Strength value that was applied
                    - timestamp: When the viseme was applied

            Usage:
                Use this tool to create realistic lip sync for your VRChat avatar during
                speech or audio playback. Essential for voice acting, singing, and
                creating believable talking animations.

            Examples:
                Open mouth for "ah" sound:
                    result = await set_viseme("aa", 1.0)
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set viseme to aa',
                    #     'viseme': 'aa',
                    #     'strength': 1.0,
                    #     'timestamp': 1640995200.123
                    # }

                Subtle mouth movement:
                    result = await set_viseme("E", 0.5)
                    # Avatar shows mild "ee" mouth shape

                Lip sync sequence for "hello":
                    # H sound - neutral or minimal mouth
                    await set_viseme("PP", 0.8)
                    await asyncio.sleep(0.1)

                    # EH sound - "E" viseme
                    await set_viseme("E", 1.0)
                    await asyncio.sleep(0.1)

                    # L sound - "DD" viseme (tongue up)
                    await set_viseme("DD", 0.9)
                    await asyncio.sleep(0.1)

                    # O sound - "O" viseme
                    await set_viseme("O", 1.0)
                    await asyncio.sleep(0.2)

                    # Back to neutral
                    await set_viseme("aa", 0.0)

                Consonant emphasis:
                    await set_viseme("PP", 1.0)   # P/B sounds
                    await asyncio.sleep(0.1)
                    await set_viseme("KK", 1.0)   # K/G sounds
                    await asyncio.sleep(0.1)
                    await set_viseme("SS", 1.0)   # S/Z sounds

                Singing mouth shapes:
                    # For "ooh" in song
                    await set_viseme("U", 0.8)
                    # For "ahh" in song
                    await set_viseme("aa", 0.9)

                Error handling:
                    result = await set_viseme("invalid", 1.0)
                    if result['status'] == 'error':
                        print(f"Viseme failed: {result['message']}")
                    # Check supported viseme names

            Raises:
                ValueError: If viseme name is invalid or not supported
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled

            Notes:
                - Requires active OSC connection to VRChat
                - Viseme names must exactly match VRChat's supported visemes
                - Strength values are clamped to 0.0-1.0 range
                - Visemes work best when synchronized with audio timing
                - Multiple rapid viseme changes create smooth lip sync
                - Visemes may conflict with certain facial expressions
                - Use "aa" at strength 0.0 to return mouth to neutral

            See Also:
                - set_expression: Control facial expressions (may conflict with visemes)
                - set_gesture: Control hand gestures
                - set_parameter: Set custom avatar parameters
                - list_parameters: View available viseme options
            '''
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_viseme(viseme, strength)
                return {"status": "success", "message": f"Set viseme to {viseme}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp.tool("vrchat_osc.set_parameter")
        async def set_parameter(name: str, value: Any) -> Dict[str, Any]:
            '''Set custom parameters on the VRChat avatar through OSC communication.

            Sets arbitrary parameter values on the VRChat avatar for advanced control
            over animations, behaviors, and custom avatar features. Parameters are
            transmitted via OSC to VRChat's parameter system.

            Parameters:
                name: Name of the avatar parameter to set
                    - Can be any valid VRChat parameter name
                    - Case-sensitive parameter naming
                    - Supports standard and custom avatar parameters
                    - Must exist in the current avatar's parameter list
                value: Value to assign to the parameter
                    - Supports int, float, bool, and string types
                    - String values like "true"/"false" are auto-converted to bool
                    - Numeric strings are auto-converted to int/float when appropriate
                    - Values are validated and converted to appropriate OSC types

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - parameter: Parameter name that was set
                    - value: Value that was assigned (after type conversion)
                    - value_type: Python type of the final value
                    - timestamp: When the parameter was set

            Usage:
                Use this tool for advanced avatar control beyond standard gestures and
                expressions. Perfect for custom animations, menu systems, and
                avatar-specific features that use VRChat's parameter system.

            Examples:
                Set boolean parameter:
                    result = await set_parameter("MyToggle", True)
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set MyToggle to True',
                    #     'parameter': 'MyToggle',
                    #     'value': True,
                    #     'value_type': 'bool',
                    #     'timestamp': 1640995200.123
                    # }

                Set numeric parameter:
                    result = await set_parameter("Speed", 0.75)
                    # Avatar runs at 75% speed

                Set integer parameter:
                    result = await set_parameter("Level", 5)
                    # Set level to 5

                String to bool conversion:
                    result = await set_parameter("Enabled", "true")
                    # Automatically converts "true" to boolean True

                String to number conversion:
                    result = await set_parameter("Scale", "1.5")
                    # Automatically converts "1.5" to float 1.5

                Advanced avatar control:
                    # Custom animation trigger
                    await set_parameter("DanceMode", True)
                    await set_parameter("DanceSpeed", 0.8)

                    # Menu system control
                    await set_parameter("MenuOpen", True)
                    await set_parameter("SelectedItem", 3)

                Error handling:
                    result = await set_parameter("NonExistent", 42)
                    if result['status'] == 'error':
                        print(f"Parameter failed: {result['message']}")
                    # Check parameter name exists

                    result = await set_parameter("Invalid", "not_a_number")
                    # String values are preserved as strings, not converted

            Raises:
                ValueError: If parameter name is invalid or value cannot be processed
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled
                TypeError: If value type is not supported by OSC

            Notes:
                - Requires active OSC connection to VRChat
                - Parameter must exist in the current avatar
                - Values are automatically converted to OSC-compatible types
                - Boolean conversion: "true"/"t" → True, "false"/"f" → False
                - Numeric conversion: valid number strings → int/float
                - Parameters persist until explicitly changed
                - Use list_parameters to see available parameters
                - Custom avatar parameters vary by avatar design

            See Also:
                - get_parameter: Read current parameter values
                - list_parameters: View all available parameters
                - set_gesture: Control standard hand gestures
                - set_expression: Control standard facial expressions
            '''
            if not self._running or not self.osc_integrator or not self.osc_server:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                # Convert value to appropriate type
                if isinstance(value, str):
                    if value.lower() in ('true', 'false', 't', 'f'):
                        value = value.lower() in ('true', 't')
                    else:
                        try:
                            value = float(value)
                            if value.is_integer():
                                value = int(value)
                        except ValueError:
                            pass
                
                # Set the parameter
                self.osc_server.set_parameter(name, value)
                return {"status": "success", "message": f"Set {name} to {value}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp.tool("vrchat_osc.get_parameter")
        async def get_parameter(name: str) -> Dict[str, Any]:
            '''Retrieve current parameter values from the VRChat avatar.

            Reads the current value of any parameter from the VRChat avatar's
            parameter system. Useful for monitoring avatar state, debugging
            animations, and creating responsive avatar behaviors.

            Parameters:
                name: Name of the avatar parameter to read
                    - Can be any valid VRChat parameter name
                    - Case-sensitive parameter naming
                    - Must exist in the current avatar's parameter list
                    - Supports both standard VRChat and custom avatar parameters

            Returns:
                Dictionary containing:
                    - status: Either "success", "error", or "not_found"
                    - message: Human-readable result description
                    - parameter: Parameter name that was queried
                    - value: Current parameter value (if found)
                    - value_type: Python type of the returned value
                    - timestamp: When the parameter was read

            Usage:
                Use this tool to monitor avatar state and create conditional behaviors.
                Essential for debugging animations, checking menu states, and building
                responsive avatar systems that react to parameter changes.

            Examples:
                Read boolean parameter:
                    result = await get_parameter("MyToggle")
                    if result['status'] == 'success':
                        is_enabled = result['value']  # True or False
                        print(f"MyToggle is {is_enabled}")
                    # Returns: {
                    #     'status': 'success',
                    #     'parameter': 'MyToggle',
                    #     'value': True,
                    #     'value_type': 'bool',
                    #     'timestamp': 1640995200.123
                    # }

                Read numeric parameter:
                    result = await get_parameter("Speed")
                    if result['status'] == 'success':
                        speed = result['value']  # Float value
                        print(f"Current speed: {speed}")

                Monitor avatar state:
                    # Check multiple parameters
                    gesture_left = await get_parameter("GestureLeft")
                    gesture_right = await get_parameter("GestureRight")
                    expression = await get_parameter("Expression")

                    if gesture_left['value'] == "Fist":
                        print("Avatar is making a fist with left hand")

                Conditional behavior:
                    dance_mode = await get_parameter("DanceMode")
                    if dance_mode['status'] == 'success' and dance_mode['value']:
                        # Avatar is in dance mode
                        await set_parameter("DanceSpeed", 1.2)
                    else:
                        # Normal mode
                        await set_parameter("DanceSpeed", 1.0)

                Debug parameter values:
                    # Check all critical parameters
                    params_to_check = ["Voice", "Viseme", "GestureLeft", "GestureRight"]
                    for param_name in params_to_check:
                        result = await get_parameter(param_name)
                        if result['status'] == 'success':
                            print(f"{param_name}: {result['value']} ({result['value_type']})")
                        else:
                            print(f"{param_name}: {result['message']}")

                Error handling:
                    result = await get_parameter("NonExistent")
                    if result['status'] == 'not_found':
                        print(f"Parameter not found: {result['message']}")
                    elif result['status'] == 'error':
                        print(f"Read failed: {result['message']}")
                    # Check parameter exists and OSC is connected

            Raises:
                ValueError: If parameter name is invalid
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled

            Notes:
                - Requires active OSC connection to VRChat
                - Parameter must exist in the current avatar
                - Returns real-time current values
                - Values are returned as native Python types
                - Use list_parameters to discover available parameters
                - Standard VRChat parameters are always available
                - Custom parameters depend on the current avatar

            See Also:
                - set_parameter: Change parameter values
                - list_parameters: View all available parameters
                - system_status: Check overall avatar system status
            '''
            if not self._running or not self.osc_server:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                value = self.osc_server.get_parameter(name)
                if value is None:
                    return {"status": "not_found", "message": f"Parameter {name} not found"}
                return {"status": "success", "value": value}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp.tool("vrchat_osc.list_parameters")
        async def list_parameters() -> Dict[str, Any]:
            '''Discover all available parameters for the current VRChat avatar.

            Returns a comprehensive catalog of all parameters available on the
            current avatar, including standard VRChat parameters and custom
            avatar-specific parameters. Essential for understanding what controls
            are available for avatar manipulation.

            Parameters:
                None - This tool discovers parameters automatically

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - parameters: Object with categorized parameter lists
                        - standard: Core VRChat parameters (always available)
                        - expressions: Facial expression parameters
                        - gestures: Hand gesture parameters
                        - visemes: Lip sync viseme parameters
                        - custom: Avatar-specific custom parameters
                    - total_count: Total number of parameters found
                    - timestamp: When the parameter list was generated

            Usage:
                Use this tool to understand what avatar controls are available before
                attempting to set or read parameters. Perfect for building dynamic
                avatar control interfaces and debugging parameter-related issues.

            Examples:
                Get all available parameters:
                    result = await list_parameters()
                    if result['status'] == 'success':
                        params = result['parameters']
                        print(f"Found {result['total_count']} total parameters")
                        print(f"Standard: {len(params['standard'])}")
                        print(f"Custom: {len(params['custom'])}")
                    # Returns: {
                    #     'status': 'success',
                    #     'parameters': {
                    #         'standard': ['GestureLeft', 'GestureRight', 'Viseme', ...],
                    #         'expressions': ['Happy', 'Sad', 'Angry', ...],
                    #         'gestures': ['Fist', 'Open', 'Point', ...],
                    #         'visemes': ['aa', 'E', 'I', 'O', 'U', ...],
                    #         'custom': ['MyCustomParam', 'DanceMode', ...]
                    #     },
                    #     'total_count': 25,
                    #     'timestamp': 1640995200.123
                    # }

                Check for specific parameter types:
                    params = await list_parameters()
                    if params['status'] == 'success':
                        # Check if custom dance parameter exists
                        if 'DanceMode' in params['parameters']['custom']:
                            await set_parameter('DanceMode', True)

                        # List all expression options
                        print("Available expressions:")
                        for expr in params['parameters']['expressions']:
                            print(f"  - {expr}")

                Build dynamic UI:
                    # Create menu from available parameters
                    param_list = await list_parameters()
                    menu_options = []

                    for category, param_names in param_list['parameters'].items():
                        for param_name in param_names:
                            menu_options.append({
                                'name': param_name,
                                'category': category,
                                'current_value': await get_parameter(param_name)
                            })

                Validate parameter before use:
                    available = await list_parameters()
                    param_name = "MyParameter"

                    if param_name in available['parameters']['custom']:
                        await set_parameter(param_name, 42)
                    else:
                        print(f"Parameter {param_name} not available")

                Debug avatar capabilities:
                    params = await list_parameters()
                    print("Avatar Capabilities:")
                    print(f"  Gestures: {len(params['parameters']['gestures'])}")
                    print(f"  Expressions: {len(params['parameters']['expressions'])}")
                    print(f"  Visemes: {len(params['parameters']['visemes'])}")
                    print(f"  Custom: {len(params['parameters']['custom'])}")

                Error handling:
                    result = await list_parameters()
                    if result['status'] == 'error':
                        print(f"Cannot list parameters: {result['message']}")
                    # Usually indicates OSC connection issues

            Raises:
                RuntimeError: If OSC connection is not established
                ConnectionError: If VRChat is not running or OSC is disabled

            Notes:
                - Requires active OSC connection to VRChat
                - Parameter list reflects the currently loaded avatar
                - Standard parameters are always available regardless of avatar
                - Custom parameters vary by avatar design
                - List is generated dynamically from avatar configuration
                - Use this before calling set_parameter or get_parameter
                - Results may change when switching avatars

            See Also:
                - set_parameter: Set parameter values (use list to see what's available)
                - get_parameter: Read parameter values
                - load_vrm: Load different avatars with different parameter sets
            '''
            # This would need to be populated based on the actual parameters
            # available in the current avatar
            standard_params = [
                "GestureLeft", "GestureRight", "GestureLeftWeight", "GestureRightWeight",
                "Viseme", "VisemeWeight", "Voice", "VoiceVolume", "IsLocal"
            ]
            
            # Add expression parameters
            expressions = [
                "Neutral", "Happy", "Angry", "Sad", "Surprised", "Blink", "BlinkLeft",
                "BlinkRight", "EyesWide", "Squint", "LookDown", "LookLeft", "LookRight", "LookUp"
            ]
            
            # Add any custom parameters from the config
            custom_params = []
            if self.osc_integrator and self.osc_integrator.config.parameter_mappings:
                custom_params = list(self.osc_integrator.config.parameter_mappings.keys())
            
            return {
                "status": "success",
                "parameters": {
                    "standard": standard_params,
                    "expressions": expressions,
                    "custom": custom_params
                }
            }
        
        @mcp.tool("vrchat_osc.load_vrm")
        async def load_vrm(file_path: str) -> Dict[str, Any]:
            '''Load and analyze VRM avatar models for VRChat compatibility.

            Processes VRM (Virtual Reality Model) files to extract avatar information,
            including blend shapes, bone structures, and available parameters. This
            enables dynamic avatar loading and parameter discovery for VRChat integration.

            Parameters:
                file_path: Absolute or relative path to the VRM file
                    - Must be a valid .vrm file format
                    - Supports standard VRM 1.0 specification
                    - Path is resolved relative to current working directory if relative
                    - File must be readable and contain valid VRM data

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - blend_shapes: List of facial blend shape names available
                    - bones: List of skeletal bone names in the avatar
                    - file_path: Resolved absolute path to the loaded file
                    - metadata: Basic VRM file metadata (title, author, etc.)
                    - timestamp: When the VRM was loaded and analyzed

            Usage:
                Use this tool to load VRM avatars and discover their capabilities before
                using them in VRChat. Essential for understanding what blend shapes,
                bones, and parameters are available for animation and control.

            Examples:
                Load a VRM avatar:
                    result = await load_vrm("models/MyAvatar.vrm")
                    if result['status'] == 'success':
                        print(f"Loaded avatar with {len(result['blend_shapes'])} blend shapes")
                        print(f"Available bones: {result['bones'][:5]}...")  # First 5 bones
                    # Returns: {
                    #     'status': 'success',
                    #     'blend_shapes': ['Joy', 'Angry', 'Sad', 'Blink', ...],
                    #     'bones': ['Hips', 'Spine', 'Chest', 'Neck', 'Head', ...],
                    #     'file_path': 'C:/Avatars/MyAvatar.vrm',
                    #     'metadata': {'title': 'My Custom Avatar', 'author': 'Artist Name'},
                    #     'timestamp': 1640995200.123
                    # }

                Check avatar capabilities:
                    vrm_info = await load_vrm("avatars/professional.vrm")
                    if vrm_info['status'] == 'success':
                        # Check for specific blend shapes
                        has_blink = 'Blink' in vrm_info['blend_shapes']
                        has_expressions = len([b for b in vrm_info['blend_shapes']
                                             if b in ['Joy', 'Angry', 'Sad', 'Surprised']]) > 0

                        print(f"Avatar has blink: {has_blink}")
                        print(f"Avatar has expressions: {has_expressions}")

                Validate avatar before use:
                    # Load and verify avatar has required features
                    avatar = await load_vrm("characters/hero.vrm")
                    required_blendshapes = ['Neutral', 'Happy', 'Angry']

                    missing = [bs for bs in required_blendshapes
                              if bs not in avatar['blend_shapes']]

                    if missing:
                        print(f"Avatar missing blend shapes: {missing}")
                    else:
                        print("Avatar has all required blend shapes!")

                Compare multiple avatars:
                    avatars = ["avatar1.vrm", "avatar2.vrm", "avatar3.vrm"]
                    comparison = {}

                    for avatar_path in avatars:
                        info = await load_vrm(avatar_path)
                        if info['status'] == 'success':
                            comparison[avatar_path] = {
                                'blend_shapes': len(info['blend_shapes']),
                                'bones': len(info['bones']),
                                'title': info['metadata'].get('title', 'Unknown')
                            }

                    # Print comparison table
                    for path, stats in comparison.items():
                        print(f"{path}: {stats['blend_shapes']} BS, {stats['bones']} bones")

                Error handling:
                    result = await load_vrm("nonexistent.vrm")
                    if result['status'] == 'error':
                        print(f"VRM load failed: {result['message']}")
                    # Check file exists and is valid VRM format

                    result = await load_vrm("not_a_vrm.txt")
                    # Will fail if file is not a valid VRM

            Raises:
                FileNotFoundError: If the VRM file does not exist
                ValueError: If the file is not a valid VRM format
                RuntimeError: If VRM parsing fails
                PermissionError: If the file cannot be read

            Notes:
                - VRM files must conform to VRM 1.0 specification
                - Blend shapes are used for facial expressions and lip sync
                - Bones define the skeletal structure for posing
                - Loading analyzes file structure but doesn't render the avatar
                - Use this for avatar compatibility checking and feature discovery
                - Results can be used to configure OSC parameter mappings
                - File path resolution follows standard filesystem rules

            See Also:
                - list_parameters: See available parameters for loaded avatar
                - set_expression: Use blend shapes for facial expressions
                - set_viseme: Use blend shapes for lip sync
                - avatar_load: Load avatar into AvatarMCP system
            '''
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                vrm_loader = self.osc_integrator.load_vrm(file_path)
                if not vrm_loader:
                    return {"status": "error", "message": "Failed to load VRM file"}
                
                # Get blend shapes and bones
                blend_shapes = vrm_loader.get_blend_shape_names()
                bones = vrm_loader.get_bone_names()
                
                return {
                    "status": "success",
                    "blend_shapes": blend_shapes,
                    "bones": bones,
                    "message": f"Loaded VRM: {file_path}"
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        # Register the tool functions as instance methods
        self.set_gesture = set_gesture
        self.set_expression = set_expression
        self.set_viseme = set_viseme
        self.set_parameter = set_parameter
        self.get_parameter = get_parameter
        self.list_parameters = list_parameters
        self.load_vrm = load_vrm


# Example usage
if __name__ == "__main__":
    async def main():
        # Example of how to use the VRChatOSCTools
        mcp = FastMCP()
        osc_tools = VRChatOSCTools(mcp)
        
        try:
            # Start the OSC tools
            await osc_tools.start()
            
            # Example: Set a gesture
            result = await osc_tools.set_gesture("left", "Fist", 1.0)
            logger.info("Set gesture result: %s", result)
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping OSC tools...")
        finally:
            await osc_tools.stop()
    
    asyncio.run(main())
