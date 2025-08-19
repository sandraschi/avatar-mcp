"""
AI NPC Controller

This module provides an AI-controlled NPC system with speech recognition, 
computer vision, and avatar control capabilities for VRChat.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union

# Import our modules
from ..ai.speech import SpeechProcessor, SpeechConfig, SpeechBackend
from ..ai.vision import VisionProcessor, VisionConfig, VisionBackend, Detection
from ..network.osc.tools import VRChatOSCController

logger = logging.getLogger(__name__)

class NPCState(Enum):
    """Possible states for the AI NPC."""
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()
    OBSERVING = auto()
    INTERACTING = auto()
    ERROR = auto()

class AINPC:
    """AI NPC controller that integrates speech, vision, and avatar control."""
    
    def __init__(
        self,
        name: str = "AI_NPC",
        config_path: Optional[str] = None,
        speech_config: Optional[SpeechConfig] = None,
        vision_config: Optional[VisionConfig] = None,
        osc_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the AI NPC.
        
        Args:
            name: Name of the NPC.
            config_path: Path to a JSON config file.
            speech_config: Speech processing configuration.
            vision_config: Vision processing configuration.
            osc_config: OSC controller configuration.
        """
        self.name = name
        self.state = NPCState.IDLE
        self.last_state_change = time.time()
        self.memory = {}
        self.personality = self._load_default_personality()
        
        # Load config from file if provided
        if config_path and os.path.exists(config_path):
            self.config = self._load_config(config_path)
        else:
            self.config = {
                "speech": {},
                "vision": {},
                "osc": {}
            }
        
        # Initialize components with provided configs or defaults
        self.speech = SpeechProcessor(
            speech_config or SpeechConfig(**self.config.get("speech", {}))
        )
        
        self.vision = VisionProcessor(
            vision_config or VisionConfig(**self.config.get("vision", {}))
        )
        
        # Initialize OSC controller for VRChat
        osc_config = osc_config or self.config.get("osc", {})
        self.osc = VRChatOSCController(**osc_config)
        
        # State management
        self._stop_event = asyncio.Event()
        self._state_handlers = {
            NPCState.IDLE: self._handle_idle,
            NPCState.LISTENING: self._handle_listening,
            NPCState.THINKING: self._handle_thinking,
            NPCState.SPEAKING: self._handle_speaking,
            NPCState.OBSERVING: self._handle_observing,
            NPCState.INTERACTING: self._handle_interacting,
            NPCState.ERROR: self._handle_error
        }
        
        # Conversation context
        self.conversation_history = []
        self.max_history = 10  # Keep last 10 messages in history
        
        # Register callbacks
        self.speech.add_callback(self._on_speech_detected)
        self.vision.add_callback(self._on_vision_update)
        
        logger.info(f"Initialized AI NPC: {self.name}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _load_default_personality(self) -> Dict[str, Any]:
        """Load the default personality for the NPC."""
        return {
            "name": self.name,
            "mood": "neutral",
            "traits": {
                "friendliness": 0.7,
                "extroversion": 0.6,
                "empathy": 0.8,
                "openness": 0.9,
                "conscientiousness": 0.5,
                "neuroticism": 0.3
            },
            "interests": ["technology", "gaming", "AI", "virtual reality"],
            "speech_style": "friendly and engaging",
            "catchphrases": [
                "That's interesting!",
                "Tell me more about that.",
                "I see what you mean.",
                "Fascinating!"
            ]
        }
    
    async def start(self):
        """Start the AI NPC system."""
        if self.state != NPCState.IDLE:
            logger.warning("AI NPC is already running")
            return
        
        logger.info("Starting AI NPC...")
        self._stop_event.clear()
        
        # Start OSC controller
        self.osc.start()
        
        # Start vision processing
        await self.vision.start_processing()
        
        # Start the main loop
        asyncio.create_task(self._run())
        logger.info("AI NPC started")
    
    async def stop(self):
        """Stop the AI NPC system."""
        logger.info("Stopping AI NPC...")
        self._stop_event.set()
        
        # Stop vision processing
        await self.vision.stop_processing()
        
        # Stop speech processing
        await self.speech.stop_listening()
        
        # Stop OSC controller
        self.osc.stop()
        
        self._set_state(NPCState.IDLE)
        logger.info("AI NPC stopped")
    
    def _set_state(self, new_state: NPCState):
        """Update the NPC's state."""
        if self.state != new_state:
            logger.debug(f"State change: {self.state.name} -> {new_state.name}")
            self.last_state_change = time.time()
            self.state = new_state
    
    async def _run(self):
        """Main loop for the AI NPC."""
        try:
            # Start in idle state
            self._set_state(NPCState.IDLE)
            
            while not self._stop_event.is_set():
                # Get the current state handler and execute it
                handler = self._state_handlers.get(self.state)
                if handler:
                    await handler()
                
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in AI NPC main loop: {e}")
            self._set_state(NPCState.ERROR)
    
    # === State Handlers ===
    
    async def _handle_idle(self):
        """Handle the idle state."""
        # In idle state, we can transition to listening or observing
        if self._should_listen():
            self._set_state(NPCState.LISTENING)
        elif self._should_observe():
            self._set_state(NPCState.OBSERVING)
        else:
            # Small delay to prevent busy waiting
            await asyncio.sleep(1.0)
    
    async def _handle_listening(self):
        """Handle the listening state."""
        # Start listening for speech
        if not self.speech.is_listening:
            await self.speech.start_listening()
        
        # Check if we should stop listening
        if self._should_stop_listening():
            await self.speech.stop_listening()
            self._set_state(NPCState.IDLE)
    
    async def _handle_thinking(self):
        """Handle the thinking state."""
        # Process the last interaction and decide on a response
        if self.conversation_history:
            last_message = self.conversation_history[-1]
            
            # Simple response logic - in a real implementation, this would use an AI model
            response = self._generate_response(last_message["content"])
            
            # Add response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": time.time()
            })
            
            # Transition to speaking state
            self._set_state(NPCState.SPEAKING)
        else:
            # No conversation history, go back to idle
            self._set_state(NPCState.IDLE)
    
    async def _handle_speaking(self):
        """Handle the speaking state."""
        if not self.conversation_history:
            self._set_state(NPCState.IDLE)
            return
        
        # Get the last assistant message
        last_message = next(
            (msg for msg in reversed(self.conversation_history) 
             if msg["role"] == "assistant"),
            None
        )
        
        if last_message:
            # Animate the avatar for speaking
            await self.osc.set_parameter("Viseme", 1.0)  # Example: Open mouth
            
            # Convert text to speech
            await self.speech.text_to_speech(last_message["content"])
            
            # Reset animation
            await self.osc.set_parameter("Viseme", 0.0)
        
        # Transition back to idle
        self._set_state(NPCState.IDLE)
    
    async def _handle_observing(self):
        """Handle the observing state."""
        # In this state, the NPC is actively observing its environment
        if not self.vision.is_processing:
            await self.vision.start_processing()
        
        # Check if we should stop observing
        if self._should_stop_observing():
            await self.vision.stop_processing()
            self._set_state(NPCState.IDLE)
    
    async def _handle_interacting(self):
        """Handle the interacting state."""
        # This state is for more complex interactions that require
        # both speech and vision (e.g., following someone with gaze)
        if not self.speech.is_listening:
            await self.speech.start_listening()
        
        if not self.vision.is_processing:
            await self.vision.start_processing()
        
        # Check if we should stop interacting
        if self._should_stop_interacting():
            await self.speech.stop_listening()
            await self.vision.stop_processing()
            self._set_state(NPCState.IDLE)
    
    async def _handle_error(self):
        """Handle the error state."""
        # Log the error and try to recover
        logger.error("AI NPC is in error state")
        
        # Try to reset components
        try:
            await self.speech.stop_listening()
            await self.vision.stop_processing()
            self.osc.stop()
            
            # Wait a bit before restarting
            await asyncio.sleep(5.0)
            
            # Restart the system
            await self.start()
            
        except Exception as e:
            logger.error(f"Failed to recover from error: {e}")
            # If we can't recover, stop the system
            self._stop_event.set()
    
    # === Helper Methods ===
    
    def _should_listen(self) -> bool:
        """Determine if the NPC should start listening."""
        # Simple logic: listen if we haven't heard anything in a while
        if not self.conversation_history:
            return True
        
        last_message_time = max(
            msg["timestamp"] for msg in self.conversation_history
        )
        return (time.time() - last_message_time) > 10.0  # 10 seconds since last message
    
    def _should_observe(self) -> bool:
        """Determine if the NPC should observe its environment."""
        # Simple logic: observe if we haven't done so in a while
        if not hasattr(self, '_last_observation_time'):
            self._last_observation_time = 0
        
        return (time.time() - self._last_observation_time) > 30.0  # Every 30 seconds
    
    def _should_stop_listening(self) -> bool:
        """Determine if the NPC should stop listening."""
        # Stop listening after 10 seconds of inactivity
        return (time.time() - self.last_state_change) > 10.0
    
    def _should_stop_observing(self) -> bool:
        """Determine if the NPC should stop observing."""
        # Observe for 5 seconds
        return (time.time() - self.last_state_change) > 5.0
    
    def _should_stop_interacting(self) -> bool:
        """Determine if the NPC should stop interacting."""
        # Interact for 30 seconds max
        return (time.time() - self.last_state_change) > 30.0
    
    def _generate_response(self, user_input: str) -> str:
        """Generate a response to user input."""
        # Simple rule-based response generation
        # In a real implementation, this would use an AI language model
        
        # Check for greetings
        greetings = ["hello", "hi", "hey", "greetings", "howdy"]
        if any(word in user_input.lower() for word in greetings):
            return f"{np.random.choice(['Hello!', 'Hi there!', 'Hey!'])} How can I help you today?"
        
        # Check for questions
        if "?" in user_input:
            responses = [
                "That's an interesting question.",
                "I'm not sure about that.",
                "Let me think about that for a moment.",
                "I'd be happy to help with that!"
            ]
            return np.random.choice(responses)
        
        # Default response
        default_responses = [
            "I see.",
            "That's interesting.",
            "Tell me more about that.",
            "I understand.",
            "Thanks for sharing that with me."
        ]
        return np.random.choice(default_responses)
    
    # === Event Handlers ===
    
    async def _on_speech_detected(self, text: str):
        """Handle detected speech."""
        logger.info(f"Detected speech: {text}")
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": text,
            "timestamp": time.time()
        })
        
        # Keep only the most recent messages
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user/assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
        
        # Transition to thinking state
        self._set_state(NPCState.THINKING)
    
    async def _on_vision_update(self, detections: List[Detection], frame: np.ndarray):
        """Handle updated vision data."""
        # Update last observation time
        self._last_observation_time = time.time()
        
        # Simple interaction based on what's detected
        for detection in detections:
            # If we see a person, look at them
            if detection.label.lower() in ["person", "face"]:
                # Calculate the center of the detection
                x, y, w, h = detection.bbox
                center_x = x + w / 2
                center_y = y + h / 2
                
                # Normalize coordinates to [-1, 1] range for head movement
                norm_x = (center_x / frame.shape[1]) * 2 - 1
                norm_y = (center_y / frame.shape[0]) * 2 - 1
                
                # Move head to look at the person (invert y for VRChat)
                asyncio.create_task(self.osc.set_parameter("LookHorizontal", norm_x))
                asyncio.create_task(self.osc.set_parameter("LookVertical", -norm_y))
                
                # If we're not already in an interaction, start one
                if self.state not in [NPCState.INTERACTING, NPCState.SPEAKING]:
                    self._set_state(NPCState.INTERACTING)
                
                # Only process the first person for now
                break

# Example usage
if __name__ == "__main__":
    import asyncio
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    async def main():
        # Create and start the AI NPC
        npc = AINPC(name="Ava")
        
        try:
            # Start the NPC
            await npc.start()
            
            # Run for 5 minutes
            print("AI NPC is running. Press Ctrl+C to stop.")
            await asyncio.sleep(300)
            
        except KeyboardInterrupt:
            print("\nStopping AI NPC...")
        finally:
            # Stop the NPC
            await npc.stop()
    
    # Run the main function
    asyncio.run(main())
