"""
Voice and chatbot controller for avatar interactions.
Handles speech recognition, text-to-speech, and chatbot integration.
"""
import asyncio
import json
from typing import Dict, Optional, Callable, Any
import speech_recognition as sr
import pyttsx3
from dataclasses import dataclass
from queue import Queue
from threading import Thread

@dataclass
class VoiceConfig:
    """Configuration for voice and speech settings."""
    voice_id: str = "english"
    rate: int = 150
    volume: float = 1.0
    listen_timeout: int = 5
    phrase_time_limit: int = 5

class VoiceController:
    def __init__(self, mcp_client, config: Optional[VoiceConfig] = None):
        self.mcp = mcp_client
        self.config = config or VoiceConfig()
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.message_queue = Queue()
        self.animation_map = {
            'hello': 'wave',
            'dance': 'kpop_dance',
            'happy': 'happy_idle',
            'angry': 'angry'
        }
        
    async def speak(self, text: str, block: bool = True):
        """Make the avatar speak the given text."""
        # Set speech properties
        self.engine.setProperty('rate', self.config.rate)
        self.engine.setProperty('volume', self.config.volume)
        
        # Trigger lip sync animation (if supported by your VRM)
        await self.mcp.send_command({
            "jsonrpc": "2.0",
            "method": "visualization.animate",
            "params": {
                "model_id": "vrm1",
                "animation_name": "speak",
                "loop": True
            },
            "id": "speak_anim"
        })
        
        # Speak the text
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
            
        # Run in a separate thread to not block
        if block:
            _speak()
        else:
            Thread(target=_speak, daemon=True).start()
        
        # Stop lip sync when done
        await asyncio.sleep(len(text) * 0.05)  # Rough estimate of speech duration
        await self.mcp.send_command({
            "jsonrpc": "2.0",
            "method": "visualization.stop_animation",
            "params": {"model_id": "vrm1"},
            "id": "stop_speak"
        })
    
    async def listen(self) -> Optional[str]:
        """Listen for speech input and return recognized text."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            # Show listening animation
            await self.mcp.send_command({
                "jsonrpc": "2.0",
                "method": "visualization.animate",
                "params": {
                    "model_id": "vrm1",
                    "animation_name": "listen",
                    "loop": True
                },
                "id": "listen_anim"
            })
            
            try:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.config.listen_timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )
                
                # Recognize speech using Google Web Speech API
                text = self.recognizer.recognize_google(audio)
                return text.lower()
                
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return ""
            finally:
                # Stop listening animation
                await self.mcp.send_command({
                    "jsonrpc": "2.0",
                    "method": "visualization.stop_animation",
                    "params": {"model_id": "vrm1"},
                    "id": "stop_listen"
                })
    
    async def process_command(self, text: str) -> bool:
        """Process voice commands and trigger appropriate actions."""
        text = text.lower()
        
        # Check for animation triggers
        for trigger, anim in self.animation_map.items():
            if trigger in text:
                await self.mcp.send_command({
                    "jsonrpc": "2.0",
                    "method": "visualization.animate",
                    "params": {
                        "model_id": "vrm1",
                        "animation_name": anim,
                        "loop": "dance" in anim
                    },
                    "id": f"anim_{anim}"
                })
                return True
                
        # Add more command processing here
        return False
    
    async def run_chatbot_loop(self):
        """Main loop for voice-controlled chatbot."""
        await self.speak("Hello! I'm your avatar assistant. How can I help you?")
        
        while True:
            try:
                # Listen for user input
                text = await self.listen()
                if not text:
                    continue
                    
                print(f"Heard: {text}")
                
                # Process command
                if not await self.process_command(text):
                    # Default response if no command matched
                    await self.speak(f"I heard you say: {text}")
                    
            except Exception as e:
                print(f"Error in chatbot loop: {e}")
                await asyncio.sleep(1)
