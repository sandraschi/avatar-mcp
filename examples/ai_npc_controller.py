"""
AI NPC Controller for VRChat

This script demonstrates how to create an AI-controlled NPC in VRChat
with speech, listening, and vision capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AINPCController:
    """AI NPC Controller for VRChat."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI NPC controller."""
        self.config = {
            "osc_ip": "127.0.0.1",
            "osc_receive_port": 9000,
            "osc_send_port": 9001,
            "stt_model": "base",  # or "small", "medium", "large"
            "tts_voice": "en_0",  # Default voice
            "ai_model": "gpt-4",  # or local model path
            "vision_enabled": True,
            "speech_enabled": True,
            **(config or {})
        }
        
        self.is_running = False
        self.conversation_history: List[Dict[str, str]] = []
        self.current_context: Dict[str, Any] = {}
        
        # Initialize components
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all components."""
        # Import here to avoid circular imports
        from avatarmcp.osc_tools import VRChatOSCTools
        from fastmcp import FastMCP
        
        # Initialize MCP and OSC tools
        self.mcp = FastMCP()
        self.osc_tools = VRChatOSCTools(
            self.mcp,
            {
                "receive_port": self.config["osc_receive_port"],
                "send_port": self.config["osc_send_port"],
                "server_ip": self.config["osc_ip"]
            }
        )
        
        # Initialize other components
        self.initialize_speech()
        self.initialize_vision()
        self.initialize_ai()
    
    def initialize_speech(self):
        """Initialize speech components."""
        if not self.config["speech_enabled"]:
            return
            
        try:
            # Try to import speech modules
            import speech_recognition as sr
            import pygame
            
            self.speech_recognizer = sr.Recognizer()
            self.speech_recognizer.pause_threshold = 0.5
            self.speech_recognizer.energy_threshold = 300
            
            # Initialize pygame for audio playback
            pygame.mixer.init()
            
            logger.info("Speech components initialized")
            
        except ImportError as e:
            logger.warning(f"Speech components not available: {e}")
            self.config["speech_enabled"] = False
    
    def initialize_vision(self):
        """Initialize vision components."""
        if not self.config["vision_enabled"]:
            return
            
        try:
            # Try to import vision modules
            import mss
            
            self.screen_capture = mss.mss()
            logger.info("Vision components initialized")
            
        except ImportError as e:
            logger.warning(f"Vision components not available: {e}")
            self.config["vision_enabled"] = False
    
    def initialize_ai(self):
        """Initialize AI components."""
        try:
            # This would be replaced with actual AI model loading
            logger.info(f"Initializing AI model: {self.config['ai_model']}")
            
            # For now, we'll use a simple mock
            class MockAIModel:
                async def generate_response(self, prompt: str, context: Dict) -> str:
                    return "I'm an AI NPC. This is a mock response."
                    
            self.ai_model = MockAIModel()
            
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            raise
    
    async def start(self):
        """Start the AI NPC controller."""
        if self.is_running:
            return
            
        logger.info("Starting AI NPC controller...")
        
        # Start OSC tools
        await self.osc_tools.start()
        
        # Start main loop
        self.is_running = True
        asyncio.create_task(self.main_loop())
        
        logger.info("AI NPC controller started")
    
    async def stop(self):
        """Stop the AI NPC controller."""
        if not self.is_running:
            return
            
        logger.info("Stopping AI NPC controller...")
        
        # Stop all components
        self.is_running = False
        
        # Stop OSC tools
        await self.osc_tools.stop()
        
        logger.info("AI NPC controller stopped")
    
    async def main_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                # Process speech input
                if self.config["speech_enabled"]:
                    await self.process_speech_input()
                
                # Process vision input
                if self.config["vision_enabled"]:
                    await self.process_vision_input()
                
                # Small delay to prevent high CPU usage
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Prevent tight error loop
    
    async def process_speech_input(self):
        """Process speech input from the microphone."""
        try:
            # This is a placeholder for actual speech recognition
            # In a real implementation, you would use the microphone
            # and a speech recognition library
            text = await self.recognize_speech()
            
            if text:
                logger.info(f"Heard: {text}")
                await self.process_text_input(text, source="speech")
                
        except Exception as e:
            logger.error(f"Error in speech processing: {e}")
    
    async def recognize_speech(self) -> Optional[str]:
        """Recognize speech from the microphone."""
        # This is a placeholder for actual speech recognition
        # In a real implementation, you would use a speech recognition library
        # like SpeechRecognition, Vosk, or Whisper
        await asyncio.sleep(1)  # Simulate processing time
        return None  # Return None if no speech was detected
    
    async def process_vision_input(self):
        """Process vision input from the screen or webcam."""
        try:
            # Capture screen
            screenshot = await self.capture_screen()
            
            if screenshot is not None:
                # Process the screenshot (e.g., object detection, text recognition)
                # This is a placeholder for actual vision processing
                await self.analyze_vision(screenshot)
                
        except Exception as e:
            logger.error(f"Error in vision processing: {e}")
    
    async def capture_screen(self) -> Optional[np.ndarray]:
        """Capture the screen or webcam."""
        try:
            # This is a placeholder for actual screen capture
            # In a real implementation, you would use a library like mss or OpenCV
            return None
            
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return None
    
    async def analyze_vision(self, image: np.ndarray):
        """Analyze the captured image."""
        # This is a placeholder for actual vision analysis
        # In a real implementation, you would use a computer vision library
        # like OpenCV, YOLO, or a pre-trained model
        pass
    
    async def process_text_input(self, text: str, source: str = "chat"):
        """Process text input from speech or chat."""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": text, "source": source})
            
            # Generate response
            response = await self.generate_ai_response(text)
            
            # Speak the response
            if response and self.config["speech_enabled"]:
                await self.speak(response)
            
            # Send to chat (if not from chat)
            if source != "chat" and response:
                await self.send_chat_message(response)
                
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
    
    async def generate_ai_response(self, prompt: str) -> str:
        """Generate a response using the AI model."""
        try:
            # Prepare context
            context = {
                "conversation_history": self.conversation_history[-10:],  # Last 10 messages
                "current_context": self.current_context,
                "avatar_state": await self.get_avatar_state()
            }
            
            # Generate response
            response = await self.ai_model.generate_response(prompt, context)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    async def speak(self, text: str):
        """Convert text to speech and play it."""
        try:
            # This is a placeholder for actual text-to-speech
            # In a real implementation, you would use a TTS library
            # like gTTS, pyttsx3, or a cloud service
            logger.info(f"Speaking: {text}")
            
            # Update avatar's mouth movement for lip-sync
            await self.update_lip_sync(text)
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    async def update_lip_sync(self, text: str):
        """Update avatar's mouth movement based on speech."""
        try:
            # This is a simplified example
            # In a real implementation, you would analyze the phonemes in the text
            # and map them to visemes for lip-sync
            
            # Example: Simple mouth movement based on vowels
            vowels = "aeiouAEIOU"
            mouth_open = any(vowel in text for vowel in vowels)
            
            # Send viseme parameter to VRChat
            if mouth_open:
                await self.osc_tools.set_viseme("aa", 0.8)  # Open mouth
            else:
                await self.osc_tools.set_viseme("sil", 0.0)  # Close mouth
                
        except Exception as e:
            logger.error(f"Error in lip-sync: {e}")
    
    async def send_chat_message(self, message: str):
        """Send a chat message in VRChat."""
        try:
            # This is a placeholder for sending chat messages
            # In a real implementation, you would use the VRChat API or OSC
            logger.info(f"Sending chat: {message}")
            
            # Example: Send a chat message via OSC
            # await self.osc_tools.set_parameter("ChatBox", message)
            
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
    
    async def get_avatar_state(self) -> Dict[str, Any]:
        """Get the current state of the avatar."""
        try:
            # Get current parameters from VRChat
            # This is a simplified example
            return {
                "gesture_left": await self.osc_tools.get_parameter("GestureLeft"),
                "gesture_right": await self.osc_tools.get_parameter("GestureRight"),
                # Add more parameters as needed
            }
        except Exception as e:
            logger.error(f"Error getting avatar state: {e}")
            return {}


async def main():
    """Main entry point."""
    # Create and start the AI NPC controller
    npc_controller = AINPCController({
        "speech_enabled": True,
        "vision_enabled": True,
        "ai_model": "gpt-4"  # or local model
    })
    
    try:
        # Start the controller
        await npc_controller.start()
        
        # Keep the script running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        await npc_controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
