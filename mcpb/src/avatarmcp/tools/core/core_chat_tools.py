"""
Core Chat Tools for AvatarMCP

This module contains the core chat interaction tools that are actually implemented
and working for chatbot functionality.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreChatTools:
    """Core chat tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core chat tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self.chat_sessions = {}  # Store active chat sessions
        self._register_tools()

    def _register_tools(self):
        """Register core chat tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def chat_start(params: dict[str, Any]) -> dict[str, Any]:
            """Start a new chat session with the avatar chatbot.

            Initializes a fresh conversation context and prepares the chatbot
            for interaction with the avatar.

            Parameters:
                session_id: Optional session identifier (auto-generated if not provided)
                context: Optional context information for the chat

            Returns:
                Dictionary with chat session details
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                session_id = params.get("session_id", f"chat_{len(self.chat_sessions) + 1}")
                context = params.get("context", "general")

                # Initialize chat session
                self.chat_sessions[session_id] = {
                    "id": session_id,
                    "context": context,
                    "messages": [],
                    "start_time": __import__("time").time(),
                    "active": True,
                }

                return {
                    "status": "success",
                    "message": f"Chat session '{session_id}' started",
                    "session_id": session_id,
                    "context": context,
                    "active_sessions": len(self.chat_sessions),
                }

            except Exception as e:
                logger.error(f"Failed to start chat session: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to start chat session: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def chat_send_message(params: dict[str, Any]) -> dict[str, Any]:
            """Send a message to the active chat session.

            Sends a user message to the chatbot and receives a response,
            maintaining conversation context.

            Parameters:
                message: User message to send (required)
                session_id: Chat session ID (uses most recent if not provided)

            Returns:
                Dictionary with chatbot response
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                message = params.get("message")
                if not message:
                    return {"status": "error", "message": "Message content is required"}

                session_id = params.get("session_id")
                if not session_id:
                    # Use the most recent active session
                    if not self.chat_sessions:
                        return {
                            "status": "error",
                            "message": "No active chat sessions. Call chat_start first.",
                        }
                    session_id = max(
                        self.chat_sessions.keys(), key=lambda k: self.chat_sessions[k]["start_time"]
                    )

                if session_id not in self.chat_sessions:
                    return {"status": "error", "message": f"Chat session '{session_id}' not found"}

                # Add user message to session
                self.chat_sessions[session_id]["messages"].append(
                    {"role": "user", "content": message, "timestamp": __import__("time").time()}
                )

                # Generate chatbot response (simplified implementation)
                response = self._generate_chat_response(message, session_id)

                # Add bot response to session
                self.chat_sessions[session_id]["messages"].append(
                    {
                        "role": "assistant",
                        "content": response,
                        "timestamp": __import__("time").time(),
                    }
                )

                return {
                    "status": "success",
                    "message": "Message processed",
                    "session_id": session_id,
                    "response": response,
                    "message_count": len(self.chat_sessions[session_id]["messages"]),
                }

            except Exception as e:
                logger.error(f"Failed to send chat message: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to send chat message: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def chat_stop(params: dict[str, Any]) -> dict[str, Any]:
            """Stop the current chat session.

            Terminates the active chat session and cleans up resources.

            Parameters:
                session_id: Chat session ID to stop (optional)

            Returns:
                Dictionary with session termination status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                session_id = params.get("session_id")
                if not session_id:
                    # Stop all active sessions
                    stopped_count = 0
                    for sid in list(self.chat_sessions.keys()):
                        if self.chat_sessions[sid]["active"]:
                            self.chat_sessions[sid]["active"] = False
                            stopped_count += 1

                    return {
                        "status": "success",
                        "message": f"Stopped {stopped_count} chat sessions",
                        "stopped_sessions": stopped_count,
                    }

                if session_id not in self.chat_sessions:
                    return {"status": "error", "message": f"Chat session '{session_id}' not found"}

                # Stop specific session
                self.chat_sessions[session_id]["active"] = False

                return {
                    "status": "success",
                    "message": f"Chat session '{session_id}' stopped",
                    "session_id": session_id,
                }

            except Exception as e:
                logger.error(f"Failed to stop chat session: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to stop chat session: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def chat_get_state(params: dict[str, Any]) -> dict[str, Any]:
            """Get the current state of chat sessions.

            Returns information about active chat sessions, message counts,
            and conversation statistics.

            Parameters:
                session_id: Optional specific session ID to get state for

            Returns:
                Dictionary with chat state information
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                session_id = params.get("session_id")

                if session_id:
                    # Get specific session state
                    if session_id not in self.chat_sessions:
                        return {
                            "status": "error",
                            "message": f"Chat session '{session_id}' not found",
                        }

                    session = self.chat_sessions[session_id]
                    return {
                        "status": "success",
                        "session_id": session_id,
                        "active": session["active"],
                        "context": session["context"],
                        "message_count": len(session["messages"]),
                        "start_time": session["start_time"],
                        "duration": __import__("time").time() - session["start_time"],
                    }
                else:
                    # Get all sessions state
                    active_sessions = [
                        sid for sid, session in self.chat_sessions.items() if session["active"]
                    ]
                    total_messages = sum(
                        len(session["messages"]) for session in self.chat_sessions.values()
                    )

                    return {
                        "status": "success",
                        "total_sessions": len(self.chat_sessions),
                        "active_sessions": len(active_sessions),
                        "total_messages": total_messages,
                        "session_ids": list(self.chat_sessions.keys()),
                    }

            except Exception as e:
                logger.error(f"Failed to get chat state: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to get chat state: {str(e)}"}

    def _generate_chat_response(self, message: str, session_id: str) -> str:
        """Generate a chatbot response (simplified implementation)."""
        # This is a basic implementation - in a real system, this would
        # integrate with a proper chatbot/LLM service

        message_lower = message.lower()

        # Simple keyword-based responses
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm your avatar assistant. How can I help you today?"
        elif "avatar" in message_lower:
            return "I can help you control your avatar! Try asking me to play animations, set expressions, or load different avatars."
        elif "animation" in message_lower:
            return "I can play animations on your avatar. What animation would you like to see?"
        elif "expression" in message_lower or "face" in message_lower:
            return "I can control facial expressions! What expression would you like your avatar to show?"
        elif "help" in message_lower:
            return "I can help you with avatar control, animations, expressions, and Unity integration. What would you like to do?"
        else:
            return f"I understand you said: '{message}'. I'm here to help with avatar control and interactions. What would you like to do with your avatar?"
