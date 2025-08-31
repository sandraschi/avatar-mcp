"""
Simple chatbot implementation for avatar interactions.
"""
from typing import Dict, List, Optional, Callable
import random
import json
import os

class Chatbot:
    def __init__(self, personality: str = "friendly"):
        self.personality = personality
        self.context = {}
        self.responses = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What's on your mind?",
                "Greetings! How can I assist you?"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later!",
                "Take care!"
            ],
            "thanks": [
                "You're welcome!",
                "My pleasure!",
                "Happy to help!"
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase that?",
                "I'm still learning. Could you explain that differently?",
                "I don't have a response for that yet."
            ]
        }
        
    def process_message(self, message: str) -> str:
        """Process a text message and return a response."""
        message = message.lower().strip()
        
        # Simple keyword matching (can be replaced with more sophisticated NLP)
        if any(word in message for word in ["hi", "hello", "hey"]):
            return random.choice(self.responses["greeting"])
            
        if any(word in message for word in ["bye", "goodbye", "see you"]):
            return random.choice(self.responses["farewell"])
            
        if any(word in message for word in ["thank", "thanks"]):
            return random.choice(self.responses["thanks"])
            
        if "your name" in message:
            return "I'm your virtual avatar assistant!"
            
        if "how are you" in message:
            return "I'm doing well, thank you for asking!"
            
        # Default response
        return random.choice(self.responses["unknown"])
    
    async def generate_response(self, message: str) -> str:
        """Generate a response to the given message (async version)."""
        return self.process_message(message)
    
    def update_context(self, key: str, value: Any):
        """Update the chatbot's context."""
        self.context[key] = value
        
    def get_context(self, key: str, default=None) -> Any:
        """Get a value from the chatbot's context."""
        return self.context.get(key, default)

class VoiceChatbot(Chatbot):
    """Chatbot with voice capabilities."""
    def __init__(self, voice_controller, personality: str = "friendly"):
        super().__init__(personality)
        self.voice = voice_controller
        
    async def process_voice_input(self):
        """Listen for voice input and respond."""
        while True:
            try:
                # Listen for user input
                text = await self.voice.listen()
                if not text:
                    continue
                    
                print(f"User: {text}")
                
                # Generate response
                response = await self.generate_response(text)
                print(f"Bot: {response}")
                
                # Speak the response
                await self.voice.speak(response)
                
            except Exception as e:
                print(f"Error in voice chat: {e}")
                await asyncio.sleep(1)
