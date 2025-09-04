"""
MCP Tools for 3D Visualization (FastMCP 2.11.3+).

This module provides FastMCP 2.11.3+ compatible tools for 3D visualization.
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union

from ..core.mcp_tools import MCPTools as BaseTools
from .manager import VisualizationManager
from ..ai.voice_controller import VoiceController, VoiceConfig
from ..ai.chatbot import VoiceChatbot

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """Configuration for voice and speech settings."""
    voice_id: str = "english"
    rate: int = 150
    volume: float = 1.0
    listen_timeout: int = 5
    phrase_time_limit: int = 5

class VisualizationTools(BaseTools):
    """MCP Tools for 3D visualization, animation, and interaction."""
    
    def __init__(self, mcp_server, vrc_osc, visualization_manager: VisualizationManager):
        """Initialize visualization tools.
        
        Args:
            mcp_server: The MCP server instance
            vrc_osc: The VRChat OSC connector
            visualization_manager: The visualization manager instance
        """
        super().__init__(mcp_server, vrc_osc)
        self.visualization = visualization_manager
        self.active_animations = {}
        self.voice_enabled = False
        self.chatbot_enabled = False
        self.voice_controller = None
        self.chatbot = None
        
        # Initialize voice-related attributes
        self.voice_controller = None
        self.voice_enabled = False
        
        self._register_commands()
        
        # Dance animation state
        self.dance_tasks = {}  # model_id -> dance_task
    
    def show_viewer(self, *args, **kwargs):
        """Show the visualization viewer.
        
        Args:
            *args: Positional arguments (unused)
            **kwargs: Keyword arguments (unused)
            
        Returns:
            dict: Status of the operation
        """
        try:
            self.visualization.show()
            return {"status": "success", "message": "Visualization viewer shown"}
        except Exception as e:
            logger.error(f"Failed to show visualization viewer: {str(e)}")
            return {"status": "error", "message": f"Failed to show viewer: {str(e)}"}
            
    def hide_viewer(self, *args, **kwargs):
        """Hide the visualization viewer.
        
        Args:
            *args: Positional arguments (unused)
            **kwargs: Keyword arguments (unused)
            
        Returns:
            dict: Status of the operation
        """
        try:
            self.visualization.hide()
            return {"status": "success", "message": "Visualization viewer hidden"}
        except Exception as e:
            logger.error(f"Failed to hide visualization viewer: {str(e)}")
            return {"status": "error", "message": f"Failed to hide viewer: {str(e)}"}
            
    def animate(self, model_id: str, animation_name: str, loop: bool = False, speed: float = 1.0, **kwargs):
        """Animate a 3D model.
        
        Args:
            model_id: ID of the model to animate
            animation_name: Name of the animation to play
            loop: Whether to loop the animation
            speed: Playback speed multiplier
            **kwargs: Additional animation parameters
            
        Returns:
            dict: Status of the animation
        """
        try:
            if model_id not in self.visualization.models:
                return {"status": "error", "message": f"Model {model_id} not found"}
                
            # Stop any existing animation for this model
            if model_id in self.active_animations:
                self.stop_animation(model_id)
                
            # Start the new animation
            self.visualization.animate_model(model_id, animation_name, loop=loop, speed=speed, **kwargs)
            self.active_animations[model_id] = animation_name
            
            return {
                "status": "success",
                "message": f"Started animation '{animation_name}' on model '{model_id}'",
                "model_id": model_id,
                "animation": animation_name,
                "loop": loop,
                "speed": speed
            }
            
        except Exception as e:
            logger.error(f"Failed to animate model {model_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to animate model {model_id}: {str(e)}",
                "model_id": model_id,
                "animation": animation_name
            }
            
    def stop_animation(self, model_id: str) -> dict:
        """Stop animation for a model.
        
        Args:
            model_id: ID of the model to stop animating
            
        Returns:
            dict: Status of the operation
        """
        try:
            if model_id not in self.visualization.models:
                return {"status": "error", "message": f"Model {model_id} not found"}
                
            # Stop the animation in the visualization
            self.visualization.stop_animation(model_id)
            
            # Remove from active animations if present
            if model_id in self.active_animations:
                del self.active_animations[model_id]
                
            return {
                "status": "success",
                "message": f"Stopped animation on model '{model_id}'",
                "model_id": model_id
            }
            
        except Exception as e:
            logger.error(f"Failed to stop animation on model {model_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to stop animation on model {model_id}: {str(e)}",
                "model_id": model_id
            }
            
    def set_transform(self, model_id: str, position: list = None, rotation: list = None, scale: list = None) -> dict:
        """Set the transform (position, rotation, scale) of a model.
        
        Args:
            model_id: ID of the model to transform
            position: [x, y, z] position (optional)
            rotation: [x, y, z] rotation in degrees (optional)
            scale: [x, y, z] scale (optional)
            
        Returns:
            dict: Status of the operation
        """
        try:
            if model_id not in self.visualization.models:
                return {"status": "error", "message": f"Model {model_id} not found"}
                
            # Update position if provided
            if position is not None:
                self.visualization.set_model_position(model_id, position)
                
            # Update rotation if provided (convert from degrees to radians if needed)
            if rotation is not None:
                self.visualization.set_model_rotation(model_id, rotation)
                
            # Update scale if provided
            if scale is not None:
                self.visualization.set_model_scale(model_id, scale)
                
            return {
                "status": "success",
                "message": f"Updated transform for model '{model_id}'",
                "model_id": model_id,
                "position": position,
                "rotation": rotation,
                "scale": scale
            }
            
        except Exception as e:
            logger.error(f"Failed to set transform for model {model_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to set transform for model {model_id}: {str(e)}",
                "model_id": model_id
            }
            
    async def make_avatar_dance(self, model_id: str, dance_style: str = "default") -> dict:
        """Make an avatar perform a dance animation.
        
        Args:
            model_id: ID of the avatar model
            dance_style: Style of dance to perform (default, hiphop, salsa, etc.)
            
        Returns:
            dict: Status of the dance operation
        """
        try:
            if model_id not in self.visualization.models:
                return {"status": "error", "message": f"Model {model_id} not found"}
                
            # Cancel any existing dance task for this model
            if model_id in self.dance_tasks:
                self.dance_tasks[model_id].cancel()
                try:
                    await self.dance_tasks[model_id]
                except asyncio.CancelledError:
                    pass
                
            # Start a new dance task
            self.dance_tasks[model_id] = asyncio.create_task(
                self._dance_routine(model_id, dance_style)
            )
            
            return {
                "status": "success",
                "message": f"Started {dance_style} dance for model '{model_id}'",
                "model_id": model_id,
                "dance_style": dance_style
            }
            
        except Exception as e:
            logger.error(f"Failed to start dance for model {model_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to start dance for model {model_id}: {str(e)}",
                "model_id": model_id
            }
            
    async def _dance_routine(self, model_id: str, dance_style: str):
        """Background task to handle dance animations.
        
        Args:
            model_id: ID of the model to animate
            dance_style: Style of dance to perform
        """
        try:
            # Define dance moves based on style
            dance_moves = self._get_dance_moves(dance_style)
            
            # Loop through dance moves
            while True:
                for move in dance_moves:
                    if model_id not in self.visualization.models:
                        return  # Stop if model was removed
                        
                    # Apply the dance move
                    if "animation" in move:
                        self.visualization.animate_model(
                            model_id, 
                            move["animation"], 
                            loop=move.get("loop", False),
                            speed=move.get("speed", 1.0)
                        )
                    
                    # Wait for the move duration
                    await asyncio.sleep(move.get("duration", 2.0))
                    
        except asyncio.CancelledError:
            # Clean up when cancelled
            if model_id in self.dance_tasks:
                del self.dance_tasks[model_id]
            raise
            
    def _get_dance_moves(self, dance_style: str) -> list:
        """Get a sequence of dance moves for a given style.
        
        Args:
            dance_style: Style of dance
            
        Returns:
            list: Sequence of dance moves with parameters
        """
        # Default dance moves (can be expanded)
        if dance_style == "hiphop":
            return [
                {"animation": "dance_hiphop_1", "duration": 3.0, "loop": False},
                {"animation": "dance_hiphop_2", "duration": 3.0, "loop": False},
                {"animation": "dance_hiphop_3", "duration": 2.0, "loop": True, "speed": 1.2}
            ]
        elif dance_style == "salsa":
            return [
                {"animation": "dance_salsa_1", "duration": 4.0, "loop": False},
                {"animation": "dance_salsa_2", "duration": 4.0, "loop": False},
                {"animation": "dance_salsa_3", "duration": 3.0, "loop": True}
            ]
        else:  # default
            return [
                {"animation": "dance_default_1", "duration": 2.0, "loop": True},
                {"animation": "dance_default_2", "duration": 2.0, "loop": True}
            ]

    # ===== Voice Methods =====
    
    async def enable_voice(self, enable: bool = True, **kwargs) -> dict:
        """Enable or disable voice capabilities.
        
        Args:
            enable: Whether to enable voice
            **kwargs: Additional voice settings
                - voice_id: Voice ID to use
                - rate: Speech rate (words per minute)
                - volume: Volume level (0.0 to 1.0)
                - language: Language code (e.g., 'en-US')
                
        Returns:
            dict: Status of the operation
        """
        try:
            if enable:
                if self.voice_controller is None:
                    from ..ai.voice_controller import VoiceController
                    self.voice_controller = VoiceController()
                    await self.voice_controller.initialize()
                    logger.info("Voice controller initialized")
                
                # Update voice settings if provided
                if kwargs:
                    await self.voice_controller.update_config(**kwargs)
                
                self.voice_enabled = True
                return {"status": "success", "message": "Voice enabled"}
            else:
                if self.voice_controller is not None:
                    await self.voice_controller.cleanup()
                    self.voice_controller = None
                self.voice_enabled = False
                return {"status": "success", "message": "Voice disabled"}
                
        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} voice: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to {'enable' if enable else 'disable'} voice: {str(e)}"
            }
    
    async def set_voice_settings(self, **kwargs) -> dict:
        """Update voice settings.
        
        Args:
            **kwargs: Voice settings to update
                - voice_id: Voice ID to use
                - rate: Speech rate (words per minute)
                - volume: Volume level (0.0 to 1.0)
                - language: Language code
                
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            await self.voice_controller.update_config(**kwargs)
            return {"status": "success", "message": "Voice settings updated"}
            
        except Exception as e:
            logger.error(f"Failed to update voice settings: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update voice settings: {str(e)}"
            }
    
    async def speak(self, text: str, wait: bool = False, **kwargs) -> dict:
        """Convert text to speech.
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
            **kwargs: Additional parameters for speech
                - voice_id: Override default voice
                - rate: Override speech rate
                - volume: Override volume
                
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            if wait:
                await self.voice_controller.speak(text, **kwargs)
            else:
                asyncio.create_task(self.voice_controller.speak(text, **kwargs))
                
            return {"status": "success", "message": "Speech started"}
            
        except Exception as e:
            logger.error(f"Failed to speak text: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to speak text: {str(e)}"
            }
    
    async def start_listening(self, **kwargs) -> dict:
        """Start listening for voice commands.
        
        Args:
            **kwargs: Additional parameters for voice recognition
                - language: Language code (e.g., 'en-US')
                - continuous: Whether to listen continuously
                - interim_results: Whether to return interim results
                
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            await self.voice_controller.start_listening(**kwargs)
            return {"status": "success", "message": "Started listening"}
            
        except Exception as e:
            logger.error(f"Failed to start listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to start listening: {str(e)}"
            }
    
    async def stop_listening(self) -> dict:
        """Stop listening for voice commands.
        
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            await self.voice_controller.stop_listening()
            return {"status": "success", "message": "Stopped listening"}
            
        except Exception as e:
            logger.error(f"Failed to stop listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to stop listening: {str(e)}"
            }
    
    async def listen(self, duration: float = None, **kwargs) -> dict:
        """Listen for speech and transcribe it.
        
        Args:
            duration: Maximum duration to listen in seconds (None for no limit)
            **kwargs: Additional parameters for voice recognition
                - language: Language code (e.g., 'en-US')
                - interim_results: Whether to include interim results
                
        Returns:
            dict: Transcription result with status and text
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {
                    "status": "error",
                    "message": "Voice is not enabled. Call voice.enable first."
                }
                
            # Start listening
            await self.voice_controller.start_listening(**kwargs)
            
            # Wait for the specified duration if provided
            if duration is not None and duration > 0:
                await asyncio.sleep(duration)
                await self.voice_controller.stop_listening()
            
            # Get the transcription result
            result = await self.voice_controller.get_transcription()
            return {
                "status": "success",
                "text": result.get("text", ""),
                "language": result.get("language", kwargs.get("language", "en-US")),
                "is_final": result.get("is_final", True)
            }
            
        except Exception as e:
            logger.error(f"Error during voice listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Error during voice listening: {str(e)}"
            }
    
    # ===== Chatbot Methods =====
    
    async def enable_chatbot(self, enable: bool = True, **kwargs) -> dict:
        """Enable or disable the chatbot.
        
        Args:
            enable: Whether to enable or disable the chatbot
            **kwargs: Additional chatbot configuration
                - model: Model name (e.g., 'gpt-4')
                - system_prompt: System prompt for the chatbot
                - temperature: Temperature for text generation
                - max_tokens: Maximum number of tokens to generate
                
        Returns:
            dict: Status of the operation
        """
        try:
            if enable:
                if self.chatbot is None:
                    from ..ai.chatbot import Chatbot
                    self.chatbot = Chatbot(
                        model=kwargs.get('model', 'gpt-4'),
                        system_prompt=kwargs.get('system_prompt', 'You are a helpful assistant.'),
                        temperature=kwargs.get('temperature', 0.7),
                        max_tokens=kwargs.get('max_tokens', 1000)
                    )
                    await self.chatbot.initialize()
                    logger.info("Chatbot initialized and enabled")
                return {"status": "success", "message": "Chatbot enabled"}
            else:
                if self.chatbot is not None:
                    await self.chatbot.cleanup()
                    self.chatbot = None
                    logger.info("Chatbot disabled")
                return {"status": "success", "message": "Chatbot disabled"}
                
        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} chatbot: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to {'enable' if enable else 'disable'} chatbot: {str(e)}"
            }
    
    async def chat(self, message: str, **kwargs) -> dict:
        """Send a message to the chatbot and get a response.
        
        Args:
            message: The message to send to the chatbot
            **kwargs: Additional parameters for the chat
                - model: Override default model
                - temperature: Override default temperature
                - max_tokens: Override default max tokens
                
        Returns:
            dict: Chat response with status and message
        """
        try:
            if self.chatbot is None:
                return {
                    "status": "error",
                    "message": "Chatbot is not enabled. Call chatbot.enable first."
                }
                
            response = await self.chatbot.chat(message, **kwargs)
            return {
                "status": "success",
                "message": response.get("message", ""),
                "tokens_used": response.get("tokens_used", 0)
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "status": "error",
                "message": f"Error in chat: {str(e)}"
            }
            
    async def process_chat(self, message: str, context: dict = None, **kwargs) -> dict:
        """Process a chat message with additional context.
        
        This is a more advanced version of the chat method that supports additional
        context and processing options.
        
        Args:
            message: The message to process
            context: Additional context for the chat (e.g., user info, session data)
            **kwargs: Additional parameters for processing
                - model: Override default model
                - temperature: Override default temperature
                - max_tokens: Override default max tokens
                - stream: Whether to stream the response
                - functions: List of functions available to the model
                - function_call: Controls how the model responds to function calls
                
        Returns:
            dict: Response with status, message, and any additional data
        """
        try:
            if self.chatbot is None:
                return {
                    "status": "error",
                    "message": "Chatbot is not enabled. Call chatbot.enable first."
                }
                
            # Prepare the chat context
            chat_context = {
                "message": message,
                "context": context or {},
                **kwargs
            }
            
            # Process the chat using the chatbot
            response = await self.chatbot.process(chat_context)
            
            # Format the response
            result = {
                "status": "success",
                "message": response.get("message", ""),
                "tokens_used": response.get("tokens_used", 0),
                "metadata": response.get("metadata", {})
            }
            
            # Add any function calls if present
            if "function_call" in response:
                result["function_call"] = response["function_call"]
                
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing chat: {str(e)}"
            }
    
    # ===== Animation Box Methods =====
    
    async def set_animation_box(self, visible: bool = True, **kwargs) -> dict:
        """Show or hide the animation box.
        
        Args:
            visible: Whether to show or hide the animation box
            **kwargs: Additional parameters for the animation box
                - position: [x, y, z] position
                - rotation: [x, y, z] rotation in degrees
                - scale: [x, y, z] scale
                - color: [r, g, b, a] color (0-1 range)
                
        Returns:
            dict: Status of the operation
        """
        try:
            if not hasattr(self.visualization, 'set_animation_box'):
                return {"status": "error", "message": "Animation box not supported by visualization"}
                
            await self.visualization.set_animation_box(visible=visible, **kwargs)
            return {"status": "success", "message": f"Animation box {'shown' if visible else 'hidden'}"}
            
        except Exception as e:
            logger.error(f"Failed to set animation box: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to set animation box: {str(e)}"
            }
    
    async def show_animation_box(self, **kwargs) -> dict:
        """Show the animation box.
        
        Args:
            **kwargs: Additional parameters for the animation box
                
        Returns:
            dict: Status of the operation
        """
        return await self.set_animation_box(True, **kwargs)
    
    async def hide_animation_box(self) -> dict:
        """Hide the animation box.
        
        Returns:
            dict: Status of the operation
        """
        return await self.set_animation_box(False)
    
    async def get_animation_box_properties(self) -> dict:
        """Get the current properties of the animation box.
        
        Returns:
            dict: Animation box properties with status
        """
        try:
            if not hasattr(self.visualization, 'get_animation_box_properties'):
                return {
                    "status": "error",
                    "message": "Animation box properties not supported by visualization"
                }
                
            properties = await self.visualization.get_animation_box_properties()
            return {
                "status": "success",
                "properties": properties
            }
            
        except Exception as e:
            logger.error(f"Failed to get animation box properties: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get animation box properties: {str(e)}"
            }
            
    # Voice-related methods
    
    async def enable_voice(self, enable: bool = True, voice_id: str = None, rate: int = None, 
                          volume: float = None) -> dict:
        """Enable or disable voice capabilities.
        
        Args:
            enable: Whether to enable voice
            voice_id: Voice ID to use
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            dict: Status of the operation
        """
        try:
            if enable:
                # Initialize voice controller if not already done
                if self.voice_controller is None:
                    from ..ai.voice_controller import VoiceController
                    self.voice_controller = VoiceController()
                
                # Update voice settings if provided
                config = {}
                if voice_id is not None:
                    config['voice_id'] = voice_id
                if rate is not None:
                    config['rate'] = rate
                if volume is not None:
                    config['volume'] = volume
                    
                if config:
                    await self.voice_controller.update_config(**config)
                
                # Start listening if not already
                if not self.voice_controller.is_listening():
                    await self.voice_controller.start_listening()
                
                self.voice_enabled = True
                return {"status": "success", "message": "Voice enabled"}
                
            else:
                # Disable voice
                if self.voice_controller is not None:
                    await self.voice_controller.stop_listening()
                self.voice_enabled = False
                return {"status": "success", "message": "Voice disabled"}
                
        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} voice: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to {'enable' if enable else 'disable'} voice: {str(e)}"
            }
            
    async def set_voice_settings(self, voice_id: str = None, rate: int = None, 
                               volume: float = None) -> dict:
        """Update voice settings.
        
        Args:
            voice_id: Voice ID to use
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            config = {}
            if voice_id is not None:
                config['voice_id'] = voice_id
            if rate is not None:
                config['rate'] = rate
            if volume is not None:
                config['volume'] = volume
                
            if not config:
                return {"status": "error", "message": "No settings provided"}
                
            await self.voice_controller.update_config(**config)
            return {"status": "success", "message": "Voice settings updated"}
            
        except Exception as e:
            logger.error(f"Failed to update voice settings: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update voice settings: {str(e)}"
            }
            
    async def speak(self, text: str, wait: bool = False) -> dict:
        """Convert text to speech.
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
            
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            if wait:
                await self.voice_controller.speak(text)
            else:
                asyncio.create_task(self.voice_controller.speak(text))
                
            return {"status": "success", "message": "Speech started"}
            
        except Exception as e:
            logger.error(f"Failed to speak text: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to speak text: {str(e)}"
            }
            
    async def start_listening(self) -> dict:
        """Start listening for voice commands.
        
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            await self.voice_controller.start_listening()
            return {"status": "success", "message": "Listening started"}
            
        except Exception as e:
            logger.error(f"Failed to start listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to start listening: {str(e)}"
            }
            
    async def stop_listening(self) -> dict:
        """Stop listening for voice commands.
        
        Returns:
            dict: Status of the operation
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {"status": "error", "message": "Voice is not enabled"}
                
            await self.voice_controller.stop_listening()
            return {"status": "success", "message": "Listening stopped"}
            
        except Exception as e:
            logger.error(f"Failed to stop listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to stop listening: {str(e)}"
            }
            
    async def listen(self, duration: float = None, language: str = "en-US") -> dict:
        """Listen for voice input and transcribe it.
        
        Args:
            duration: Maximum duration to listen in seconds (None for no limit)
            language: Language code for speech recognition (default: en-US)
            
        Returns:
            dict: Transcription result with status and text
        """
        try:
            if not self.voice_enabled or self.voice_controller is None:
                return {
                    "status": "error",
                    "message": "Voice is not enabled. Call voice.enable first."
                }
                
            if not hasattr(self.voice_controller, 'listen'):
                return {
                    "status": "error",
                    "message": "Voice controller does not support listening"
                }
                
            # Start listening
            await self.voice_controller.start_listening()
            
            # If duration is specified, set a timeout
            if duration is not None and duration > 0:
                await asyncio.sleep(duration)
                await self.voice_controller.stop_listening()
                
            # Get the transcription result
            if hasattr(self.voice_controller, 'get_transcription'):
                result = await self.voice_controller.get_transcription()
                return {
                    "status": "success",
                    "text": result.get("text", ""),
                    "language": result.get("language", language),
                    "is_final": result.get("is_final", True)
                }
            else:
                return {
                    "status": "success",
                    "message": "Listening completed, but no transcription available"
                }
                
        except Exception as e:
            logger.error(f"Error during voice listening: {str(e)}")
            return {
                "status": "error",
                "message": f"Error during voice listening: {str(e)}"
            }
            
    async def enable_chatbot(self, enable: bool = True, **kwargs) -> dict:
        """Enable or disable the chatbot functionality.
        
        Args:
            enable: Whether to enable or disable the chatbot
            **kwargs: Additional chatbot configuration options
                - model: The model to use (e.g., 'gpt-4', 'claude-3-opus')
                - system_prompt: System prompt for the chatbot
                - temperature: Temperature for text generation
                - max_tokens: Maximum number of tokens to generate
                
        Returns:
            dict: Status of the operation
        """
        try:
            if enable:
                if self.chatbot is None:
                    from ..ai.chatbot import Chatbot
                    self.chatbot = Chatbot(
                        model=kwargs.get('model', 'gpt-4'),
                        system_prompt=kwargs.get('system_prompt', 'You are a helpful assistant.'),
                        temperature=kwargs.get('temperature', 0.7),
                        max_tokens=kwargs.get('max_tokens', 1000)
                    )
                    await self.chatbot.initialize()
                    logger.info("Chatbot initialized and enabled")
                return {"status": "success", "message": "Chatbot enabled"}
            else:
                if self.chatbot is not None:
                    await self.chatbot.cleanup()
                    self.chatbot = None
                    logger.info("Chatbot disabled")
                return {"status": "success", "message": "Chatbot disabled"}
                
        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} chatbot: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to {'enable' if enable else 'disable'} chatbot: {str(e)}"
            }
            
    def _register_commands(self):
        """Register MCP commands."""
        self.commands = {
            # Visualization commands
            "visualization.show": self.show_viewer,
            "visualization.hide": self.hide_viewer,
            "visualization.animate": self.animate,
            "visualization.stop_animation": self.stop_animation,
            "visualization.set_transform": self.set_transform,
            "visualization.dance": self.make_avatar_dance,
            
            # Voice commands
            "voice.enable": self.enable_voice,
            "voice.disable": lambda *args, **kwargs: self.enable_voice(False, *args, **kwargs),
            "voice.settings": self.set_voice_settings,
            "voice.speak": self.speak,
            "voice.start_listening": self.start_listening,
            "voice.stop_listening": self.stop_listening,
            "voice.listen": self.listen,
            
            # Animation box commands
            "animation_box.set": self.set_animation_box,
            "animation_box.show": self.show_animation_box,
            "animation_box.hide": self.hide_animation_box,
            "animation_box.get_properties": self.get_animation_box_properties,
            
            # Chatbot commands
            "chatbot.enable": self.enable_chatbot,
            "chatbot.disable": lambda *args, **kwargs: self.enable_chatbot(False, *args, **kwargs),
            "chatbot.chat": self.chat,
            "chatbot.process": self.process_chat
        }
    
    async def show_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show the 3D visualization window.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to show
                - window_size: Optional [width, height] for the window
                
        Returns:
            Response with status and window information
        """
        try:
            model_id = params.get('model_id')
            window_size = params.get('window_size', [1024, 768])
            
            if not model_id:
                return self._error_response("model_id is required")
                
            success = await self.visualization.show_model(model_id, window_size)
            if not success:
                return self._error_response(f"Failed to show model {model_id}")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'window_size': window_size
            }
        except Exception as e:
            logger.exception("Error showing visualization")
            return self._error_response(str(e))
    
    async def hide_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hide the 3D visualization window.
        
        Args:
            params: Request parameters
                - model_id: Optional ID of the model to hide (hides all if not specified)
                
        Returns:
            Response with status
        """
        try:
            model_id = params.get('model_id')
            
            if model_id:
                await self.visualization.hide_model(model_id)
            else:
                await self.visualization.hide_all()
                
            return {'status': 'success'}
        except Exception as e:
            logger.exception("Error hiding visualization")
            return self._error_response(str(e))
    
    async def animate_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Animate a 3D model.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to animate
                - animation_name: Name of the animation to play
                - loop: Whether to loop the animation (default: true)
                - speed: Playback speed multiplier (default: 1.0)
                - fade_in: Fade in duration in seconds (default: 0.0)
                
        Returns:
            Response with status and animation details
        """
        try:
            model_id = params['model_id']
            animation_name = params['animation_name']
            loop = params.get('loop', True)
            speed = float(params.get('speed', 1.0))
            fade_in = float(params.get('fade_in', 0.0))
            
            success = await self.visualization.play_animation(
                model_id=model_id,
                animation_name=animation_name,
                loop=loop,
                speed=speed,
                fade_in=fade_in
            )
            
            if not success:
                return self._error_response(f"Failed to play animation '{animation_name}'")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'animation': animation_name,
                'loop': loop,
                'speed': speed
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error animating model")
            return self._error_response(str(e))
    
    async def stop_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop animation on a model.
        
        Args:
            params: Request parameters
                - model_id: ID of the model
                - animation_name: Optional name of the animation to stop (stops all if not specified)
                - fade_out: Fade out duration in seconds (default: 0.0)
                
        Returns:
            Response with status
        """
        try:
            model_id = params['model_id']
            animation_name = params.get('animation_name')
            fade_out = float(params.get('fade_out', 0.0))
            
            success = await self.visualization.stop_animation(
                model_id=model_id,
                animation_name=animation_name,
                fade_out=fade_out
            )
            
            if not success:
                return self._error_response("Failed to stop animation")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'stopped_animation': animation_name or 'all',
                'fade_out': fade_out
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error stopping animation")
            return self._error_response(str(e))
    
    async def set_model_transform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set model transform in the 3D view.
        
        Args:
            params: Request parameters
                - model_id: ID of the model
                - position: Optional [x, y, z] position
                - rotation: Optional [x, y, z, w] quaternion rotation
                - scale: Optional [x, y, z] scale
                
        Returns:
            Response with status and transform information
        """
        try:
            model_id = params['model_id']
            position = params.get('position')
            rotation = params.get('rotation')
            scale = params.get('scale')
            
            if not any([position, rotation, scale]):
                return self._error_response("At least one of position, rotation, or scale must be provided")
            
            success = await self.visualization.set_model_transform(
                model_id=model_id,
                position=position,
                rotation=rotation,
                scale=scale
            )
            
            if not success:
                return self._error_response("Failed to set model transform")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'transform': {
                    'position': position,
                    'rotation': rotation,
                    'scale': scale
                }
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error setting model transform")
            return self._error_response(str(e))
    
    async def set_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set the animation box properties.
        
        Args:
            position: [x, y, z] position of the box center
            size: [width, height, depth] of the box
            visible: Whether to show the box outline (optional)
        """
        try:
            position = params.get("position", [0, 0, 0])
            size = params.get("size", [1.0, 1.0, 1.0])
            visible = params.get("visible", True)
            
            # Update the viewer's animation box
            if self.visualization_manager.viewer:
                self.visualization_manager.viewer.set_animation_box(
                    position=position,
                    size=size,
                    visible=visible
                )
                
            return {
                "status": "success",
                "message": "Animation box updated",
                "position": position,
                "size": size,
                "visible": visible
            }
            
        except Exception as e:
            logger.error(f"Error setting animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def show_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show the animation box with current properties."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            self.visualization_manager.viewer.set_animation_box(
                position=self.visualization_manager.viewer.animation_box_position,
                size=self.visualization_manager.viewer.animation_box_size,
                visible=True
            )
            
            return {"status": "success", "message": "Animation box shown"}
            
        except Exception as e:
            logger.error(f"Error showing animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def hide_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hide the animation box."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            self.visualization_manager.viewer.set_animation_box(
                position=self.visualization_manager.viewer.animation_box_position,
                size=self.visualization_manager.viewer.animation_box_size,
                visible=False
            )
            
            return {"status": "success", "message": "Animation box hidden"}
            
        except Exception as e:
            logger.error(f"Error hiding animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_animation_box_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current animation box properties."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            return {
                "status": "success",
                "position": self.visualization_manager.viewer.animation_box_position,
                "size": self.visualization_manager.viewer.animation_box_size,
                "visible": self.visualization_manager.viewer.animation_box_visible
            }
            
        except Exception as e:
            logger.error(f"Error getting animation box properties: {e}")
            return {"status": "error", "message": str(e)}
    
    async def make_avatar_dance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an avatar dance by playing random dance animations.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to animate
                - intensity: Optional dance intensity (0.5 to 2.0, default: 1.0)
                - duration: Optional dance duration in seconds (0 for infinite, default: 0)
                
        Returns:
            Response with status and dance information
        """
        try:
            model_id = params['model_id']
            intensity = float(params.get('intensity', 1.0))
            duration = float(params.get('duration', 0))
            
            # Get available animations
            animations_result = await self.mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "list_animations",
                "params": {"model_id": model_id},
                "id": "dance_query"
            })
            
            if 'error' in animations_result:
                return self._error_response(f"Failed to get animations: {animations_result['error']}")
                
            # Find dance animations (assuming they contain 'dance' in the name)
            dance_anims = []
            for anim_type, anims in animations_result.get('result', {}).get('animations', {}).items():
                dance_anims.extend([
                    anim['name'] for anim in anims 
                    if 'dance' in anim['name'].lower()
                ])
            
            if not dance_anims:
                # Fallback to any looping animations if no dance animations found
                for anim_type, anims in animations_result.get('result', {}).get('animations', {}).items():
                    dance_anims.extend([
                        anim['name'] for anim in anims 
                        if anim.get('loop', False)
                    ])
            
            if not dance_anims:
                return self._error_response("No suitable dance animations found")
            
            # Cancel any existing dance for this model
            await self._stop_dancing(model_id)
            
            # Create dance task
            self.dance_tasks[model_id] = asyncio.create_task(
                self._dance_sequence(model_id, dance_anims, intensity, duration)
            )
            
            return {
                'status': 'success',
                'model_id': model_id,
                'dance_animations': dance_anims,
                'intensity': intensity,
                'duration': duration
            }
            
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error making avatar dance")
            return self._error_response(str(e))
    
    async def _dance_sequence(self, model_id: str, animations: List[str], 
                            intensity: float, duration: float):
        """Run the dance sequence."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check if we should stop
                if model_id not in self.dance_tasks:
                    break
                    
                # Check duration
                if duration > 0 and (asyncio.get_event_loop().time() - start_time) > duration:
                    break
                
                # Pick a random dance animation
                anim = random.choice(animations)
                speed = 0.8 + (random.random() * 0.4) * intensity  # 0.8-1.2 * intensity
                
                # Play the animation
                await self.mcp.handle_message({
                    "jsonrpc": "2.0",
                    "method": "visualization.animate",
                    "params": {
                        "model_id": model_id,
                        "animation_name": anim,
                        "loop": False,
                        "speed": speed,
                        "fade_in": 0.3
                    },
                    "id": f"dance_{int(asyncio.get_event_loop().time())}"
                })
                
                # Random dance move duration (2-5 seconds)
                move_duration = 2.0 + (random.random() * 3.0) / intensity
                await asyncio.sleep(move_duration)
                
        except asyncio.CancelledError:
            # Clean up
            await self.mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "visualization.stop_animation",
                "params": {"model_id": model_id},
                "id": "dance_cleanup"
            })
        except Exception as e:
            logger.error(f"Error in dance sequence: {e}")
        finally:
            self.dance_tasks.pop(model_id, None)
    
    async def _stop_dancing(self, model_id: str):
        """Stop any active dance sequence for a model."""
        if model_id in self.dance_tasks:
            task = self.dance_tasks[model_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
    def _error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create an error response."""
        response = {
            'status': 'error',
            'error': message
        }
        if details:
            response['details'] = details
        return response
