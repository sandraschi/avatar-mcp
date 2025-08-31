"""
MCP Tools for chat functionality.

This module provides MCP-compatible tools for interacting with the chatbot handler.
"""

from typing import Dict, Any, Optional, List, Union
import asyncio
import logging
from dataclasses import dataclass, field

from ..handlers.chatbot_handler import ChatbotHandler, ChatState, ChatMessage, MessageRole

logger = logging.getLogger(__name__)

@dataclass
class ChatTool:
    """MCP Tool for chat functionality."""
    
    name: str = "chat"
    description: str = "Tools for interacting with the AI chatbot"
    chatbot_handler: Optional[ChatbotHandler] = None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of available chat tools.
        
        Returns:
            List of tool definitions in MCP format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "start_chat",
                    "description": "Start a chat conversation with the AI",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "wake_word": {
                                "type": "string",
                                "description": "Optional wake word to activate listening"
                            },
                            "auto_listen": {
                                "type": "boolean",
                                "description": "Automatically start listening after response"
                            },
                            "voice_feedback": {
                                "type": "boolean",
                                "description": "Enable/disable voice responses"
                            }
                        }
                    },
                    "required": []
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_message",
                    "description": "Send a text message to the AI",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to send to the AI"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stop_chat",
                    "description": "Stop the current chat conversation",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_chat_state",
                    "description": "Get the current state of the chat",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a chat tool.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Dictionary with the result of the tool execution
        """
        if not self.chatbot_handler:
            return {"error": "Chatbot handler not initialized"}
        
        try:
            if tool_name == "start_chat":
                return await self._start_chat(**parameters)
            elif tool_name == "send_message":
                return await self._send_message(**parameters)
            elif tool_name == "stop_chat":
                return await self._stop_chat()
            elif tool_name == "get_chat_state":
                return await self._get_chat_state()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing chat tool {tool_name}: {str(e)}", exc_info=True)
            return {"error": f"Error executing tool: {str(e)}"}
    
    async def _start_chat(
        self,
        wake_word: Optional[str] = None,
        auto_listen: Optional[bool] = None,
        voice_feedback: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Start a chat conversation.
        
        Args:
            wake_word: Optional wake word to use
            auto_listen: Whether to automatically listen after response
            voice_feedback: Whether to enable voice feedback
            
        Returns:
            Dictionary with the result of the operation
        """
        # Update config if parameters are provided
        config_updates = {}
        if wake_word is not None:
            config_updates["wake_word"] = wake_word
        if auto_listen is not None:
            config_updates["auto_listen"] = auto_listen
        if voice_feedback is not None:
            config_updates["voice_feedback"] = voice_feedback
        
        if config_updates:
            await self.chatbot_handler.update_config(config_updates)
        
        # Start the conversation
        success = await self.chatbot_handler.start_conversation()
        
        return {
            "success": success,
            "message": "Chat started" if success else "Failed to start chat",
            "state": self.chatbot_handler.state.value
        }
    
    async def _send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the chatbot.
        
        Args:
            message: The message to send
            
        Returns:
            Dictionary with the result of the operation
        """
        if not message or not isinstance(message, str):
            return {"error": "Message must be a non-empty string"}
        
        await self.chatbot_handler.send_text_message(message)
        
        return {
            "success": True,
            "message": "Message sent",
            "state": self.chatbot_handler.state.value
        }
    
    async def _stop_chat(self) -> Dict[str, Any]:
        """Stop the current chat conversation.
        
        Returns:
            Dictionary with the result of the operation
        """
        await self.chatbot_handler.stop_conversation()
        
        return {
            "success": True,
            "message": "Chat stopped",
            "state": self.chatbot_handler.state.value
        }
    
    async def _get_chat_state(self) -> Dict[str, Any]:
        """Get the current state of the chat.
        
        Returns:
            Dictionary with the current chat state
        """
        return {
            "state": self.chatbot_handler.state.value,
            "config": self.chatbot_handler.config.dict(),
            "history": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in self.chatbot_handler.conversation_history
            ]
        }
