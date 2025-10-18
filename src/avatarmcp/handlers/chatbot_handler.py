"""
Chatbot handler for the Avatar MCP server.

This module provides an AI-powered chatbot that can engage in natural conversations
with users through speech and text interfaces.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable

from pydantic import BaseModel, Field

from .base_handler import BaseHandler
from .speech_handler import SpeechHandler

logger = logging.getLogger(__name__)

class ChatState(str, Enum):
    """Chatbot conversation states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"

class MessageRole(str, Enum):
    """Message roles in the conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    """A message in the conversation."""
    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ChatbotConfig(BaseModel):
    """Configuration for the chatbot handler."""
    enabled: bool = Field(True, description="Whether the chatbot is enabled")
    default_voice: str = Field("default", description="Default voice ID for TTS")
    wake_word: str = Field("hey avatar", description="Wake word to activate listening")
    listen_timeout: float = Field(30.0, description="Seconds to listen before timeout")
    max_history: int = Field(10, description="Maximum number of messages to keep in history")
    ai_provider: str = Field("openai", description="AI provider to use (openai, anthropic, etc.)")
    ai_model: str = Field("gpt-3.5-turbo", description="AI model to use")
    ai_temperature: float = Field(0.7, description="AI temperature (0-2)")
    ai_max_tokens: int = Field(500, description="Maximum tokens in AI response")
    voice_feedback: bool = Field(True, description="Enable/disable voice responses")
    auto_listen: bool = Field(False, description="Automatically start listening after response")

class ChatbotHandler(BaseHandler):
    """Handler for AI-powered conversations with the avatar."""
    
    def __init__(self, server: Any = None):
        """Initialize the chatbot handler."""
        super().__init__(server)
        self.state: ChatState = ChatState.IDLE
        self.config = ChatbotConfig()
        self.conversation_history: List[ChatMessage] = []
        self._speech_handler: Optional[SpeechHandler] = None
        self._current_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._wake_word_detected = asyncio.Event()
        self._on_message_callbacks: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
        self._on_state_change_callbacks: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
    
    async def _initialize(self) -> None:
        """Initialize the chatbot handler."""
        # Get reference to speech handler
        if self.server and hasattr(self.server, 'get_handler'):
            self._speech_handler = self.server.get_handler('speech')
            if not self._speech_handler:
                logger.warning("Speech handler not found. Voice features will be disabled.")
        else:
            logger.warning("Server reference not available. Some features may be limited.")
        
        # Add system message to start the conversation
        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                "You are a helpful AI assistant with a friendly and engaging personality. "
                "You are embodied in a virtual avatar that can see, hear, and speak. "
                "Keep your responses concise, natural, and conversational. "
                "You can express emotions and personality in your responses."
            )
        )
        self._add_to_history(system_message)
        
        logger.info("Chatbot handler initialized")
    
    def _add_to_history(self, message: ChatMessage) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(message)
        
        # Trim history if it exceeds max length (keep system message)
        if len(self.conversation_history) > self.config.max_history + 1:  # +1 for system message
            # Keep system message and most recent messages
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-(self.config.max_history-1):]
    
    async def start_conversation(self) -> bool:
        """Start a new conversation.
        
        Returns:
            bool: True if conversation started successfully, False otherwise
        """
        if not self.config.enabled:
            logger.warning("Chatbot is disabled in configuration")
            return False
        
        if self.state != ChatState.IDLE:
            logger.warning(f"Cannot start conversation in state: {self.state}")
            return False
        
        try:
            self.state = ChatState.LISTENING
            self._stop_event.clear()
            self._wake_word_detected.clear()
            
            # Start listening for wake word or direct speech
            self._current_task = asyncio.create_task(self._conversation_loop())
            
            logger.info("Started conversation")
            await self._notify_state_change()
            return True
            
        except Exception as e:
            self.state = ChatState.ERROR
            logger.error(f"Error starting conversation: {str(e)}", exc_info=True)
            await self._notify_state_change()
            return False
    
    async def stop_conversation(self) -> None:
        """Stop the current conversation."""
        if self.state == ChatState.IDLE:
            return
        
        logger.info("Stopping conversation")
        self._stop_event.set()
        
        # Cancel any ongoing tasks
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass
        
        # Stop any ongoing speech
        if self._speech_handler:
            await self._speech_handler.stop_listening()
        
        self.state = ChatState.IDLE
        await self._notify_state_change()
    
    async def _conversation_loop(self) -> None:
        """Main conversation loop."""
        try:
            while not self._stop_event.is_set():
                # Wait for wake word or direct input
                if not await self._wait_for_wake_word():
                    break
                
                # Listen for user input
                user_input = await self._listen_for_input()
                if not user_input or self._stop_event.is_set():
                    break
                
                # Process the input and generate a response
                await self._process_input(user_input)
                
                # If not in auto-listen mode, wait for next wake word
                if not self.config.auto_listen:
                    break
                
        except asyncio.CancelledError:
            logger.debug("Conversation loop was cancelled")
        except Exception as e:
            self.state = ChatState.ERROR
            logger.error(f"Error in conversation loop: {str(e)}", exc_info=True)
        finally:
            if self.state != ChatState.ERROR:
                self.state = ChatState.IDLE
            await self._notify_state_change()
    
    async def _wait_for_wake_word(self) -> bool:
        """Wait for the wake word to be detected.
        
        Returns:
            bool: True if wake word was detected, False if stopped or timed out
        """
        if not self.config.wake_word or not self._speech_handler:
            return True  # No wake word required or no speech handler
        
        self.state = ChatState.LISTENING
        await self._notify_state_change()
        
        logger.info(f"Waiting for wake word: '{self.config.wake_word}'")
        
        # In a real implementation, you would use a wake word detection library
        # like Porcupine, Snowboy, or a custom solution
        # For now, we'll simulate wake word detection with a simple text match
        
        try:
            # Start listening for the wake word
            self._wake_word_detected.clear()
            
            # Set up a timeout
            try:
                await asyncio.wait_for(self._wake_word_detected.wait(), timeout=self.config.listen_timeout)
                logger.info("Wake word detected")
                return True
            except asyncio.TimeoutError:
                logger.debug("Wake word detection timed out")
                return False
                
        except Exception as e:
            logger.error(f"Error in wake word detection: {str(e)}")
            return False
    
    async def _listen_for_input(self) -> Optional[str]:
        """Listen for user input and return the recognized text.
        
        Returns:
            Optional[str]: Recognized text, or None if no input was detected
        """
        if not self._speech_handler:
            logger.warning("Speech handler not available. Cannot listen for input.")
            return None
        
        self.state = ChatState.LISTENING
        await self._notify_state_change()
        
        logger.info("Listening for user input...")
        
        # In a real implementation, you would use the speech handler to listen
        # For now, we'll simulate listening with a simple input
        try:
            # Simulate listening for user input
            await asyncio.sleep(1.0)  # Simulate processing time
            
            # In a real implementation, you would use the speech handler:
            # result = await self._speech_handler.recognize_speech()
            # if result and result.text:
            #     return result.text
            
            # For now, return a placeholder response
            return "Hello, how can I help you today?"
            
        except Exception as e:
            logger.error(f"Error in speech recognition: {str(e)}")
            return None
    
    async def _process_input(self, user_input: str) -> None:
        """Process user input and generate a response.
        
        Args:
            user_input: The user's input text
        """
        if not user_input.strip():
            return
        
        # Add user message to history
        user_message = ChatMessage(role=MessageRole.USER, content=user_input)
        self._add_to_history(user_message)
        
        # Notify listeners of new user message
        await self._notify_message({
            "role": "user",
            "content": user_input,
            "timestamp": user_message.timestamp
        })
        
        # Generate AI response
        await self._generate_ai_response()
    
    async def _generate_ai_response(self) -> None:
        """Generate a response using the AI model."""
        self.state = ChatState.THINKING
        await self._notify_state_change()
        
        logger.info("Generating AI response...")
        
        try:
            # Prepare conversation history for the AI
            [
                {"role": msg.role.value, "content": msg.content}
                for msg in self.conversation_history
            ]
            
            # In a real implementation, you would call an AI API here
            # For now, we'll simulate a response
            await asyncio.sleep(1.0)  # Simulate processing time
            
            # Generate a response (placeholder)
            response_text = (
                "I'm your AI assistant. I can help answer questions, have conversations, "
                "and assist with various tasks. What would you like to know?"
            )
            
            # Add AI response to history
            ai_message = ChatMessage(role=MessageRole.ASSISTANT, content=response_text)
            self._add_to_history(ai_message)
            
            # Notify listeners of AI response
            await self._notify_message({
                "role": "assistant",
                "content": response_text,
                "timestamp": ai_message.timestamp
            })
            
            # Speak the response if voice feedback is enabled
            if self.config.voice_feedback and self._speech_handler:
                await self._speak_response(response_text)
            
        except Exception as e:
            error_msg = f"Error generating AI response: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Add error message to history
            error_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content="I'm sorry, I encountered an error processing your request.",
                metadata={"error": str(e)}
            )
            self._add_to_history(error_message)
            
            # Notify listeners of error
            await self._notify_message({
                "role": "error",
                "content": error_msg,
                "timestamp": error_message.timestamp
            })
            
            self.state = ChatState.ERROR
            await self._notify_state_change()
    
    async def _speak_response(self, text: str) -> None:
        """Speak the given text using TTS.
        
        Args:
            text: The text to speak
        """
        if not text or not self._speech_handler:
            return
        
        self.state = ChatState.SPEAKING
        await self._notify_state_change()
        
        logger.debug(f"Speaking response: {text[:100]}...")
        
        try:
            # Use the speech handler to speak the text
            await self._speech_handler.speak(
                text=text,
                voice_id=self.config.default_voice
            )
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}", exc_info=True)
        
        finally:
            self.state = ChatState.IDLE if not self.config.auto_listen else ChatState.LISTENING
            await self._notify_state_change()
    
    async def send_text_message(self, text: str) -> None:
        """Send a text message to the chatbot.
        
        Args:
            text: The text message to send
        """
        if not text.strip():
            return
        
        # If we're not in a conversation, start one
        if self.state == ChatState.IDLE and not self._current_task:
            await self.start_conversation()
        
        # Process the input
        await self._process_input(text)
    
    async def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update the chatbot configuration.
        
        Args:
            config: Dictionary with configuration updates
            
        Returns:
            Updated configuration
        """
        # Update config with new values
        self.config = ChatbotConfig(**{**self.config.dict(), **config})
        
        # Notify of config change
        await self._notify_state_change()
        
        return self.config.dict()
    
    def register_message_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a callback for new messages.
        
        Args:
            callback: Async function that takes a message dictionary
        """
        if callback not in self._on_message_callbacks:
            self._on_message_callbacks.append(callback)
    
    def register_state_change_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a callback for state changes.
        
        Args:
            callback: Async function that takes a state dictionary
        """
        if callback not in self._on_state_change_callbacks:
            self._on_state_change_callbacks.append(callback)
    
    async def _notify_message(self, message: Dict[str, Any]) -> None:
        """Notify all registered message callbacks."""
        for callback in self._on_message_callbacks:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {str(e)}", exc_info=True)
    
    async def _notify_state_change(self) -> None:
        """Notify all registered state change callbacks."""
        state_info = {
            "state": self.state.value,
            "config": self.config.dict(),
            "timestamp": time.time()
        }
        
        for callback in self._on_state_change_callbacks:
            try:
                await callback(state_info)
            except Exception as e:
                logger.error(f"Error in state change callback: {str(e)}", exc_info=True)
    
    async def shutdown(self) -> None:
        """Clean up resources used by the chatbot handler."""
        await self.stop_conversation()
        
        # Clear callbacks
        self._on_message_callbacks.clear()
        self._on_state_change_callbacks.clear()
        
        logger.info("Chatbot handler shutdown complete")
