"""
Chat Manager Portmanteau Tool for AvatarMCP

Consolidates all chat session management operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ChatManagerTool:
    """Portmanteau tool for comprehensive chat session management."""

    def __init__(self, mcp_server):
        """Initialize chat manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self.chat_sessions = {}  # Store active chat sessions
        self._register_tool()

    def _register_tool(self):
        """Register the chat manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def chat_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive chat session management tool.

            Provides unified interface for all chat-related operations including
            starting chat sessions, sending messages, stopping sessions, and
            retrieving session state. This portmanteau tool consolidates chat
            functionality into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "start_session": Start a new chat session with the avatar chatbot
                    - "send_message": Send a message to the active chat session
                    - "stop_session": Stop the current chat session
                    - "get_state": Get the current state of chat sessions

                Additional parameters depend on the operation:
                    - For "start_session": session_id (optional), context (optional)
                    - For "send_message": message (required), session_id (optional)
                    - For "stop_session": session_id (optional)
                    - For "get_state": session_id (optional)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Start new chat session:
                    result = await chat_manager({
                        "operation": "start_session",
                        "session_id": "chat_1",
                        "context": "general"
                    })

                Send message to chat:
                    result = await chat_manager({
                        "operation": "send_message",
                        "message": "Hello, how are you?",
                        "session_id": "chat_1"
                    })

                Stop chat session:
                    result = await chat_manager({
                        "operation": "stop_session",
                        "session_id": "chat_1"
                    })

                Get chat state:
                    result = await chat_manager({
                        "operation": "get_state",
                        "session_id": "chat_1"
                    })

            Notes:
                - All operations require server to be initialized
                - Session IDs are auto-generated if not provided
                - Multiple chat sessions can be active simultaneously
                - Messages maintain conversation context within sessions
                - Chat responses are generated using simplified logic
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "start_session":
                    return self._handle_start_session(params)
                elif operation == "send_message":
                    return self._handle_send_message(params)
                elif operation == "stop_session":
                    return self._handle_stop_session(params)
                elif operation == "get_state":
                    return self._handle_get_state(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: start_session, send_message, stop_session, get_state",
                    }

            except Exception as e:
                logger.error(f"Chat manager operation failed: {e!s}", exc_info=True)
                return {"status": "error", "message": f"Chat manager operation failed: {e!s}"}

    def _handle_start_session(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat session start operation."""
        try:
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
                "operation": "start_session",
                "session_id": session_id,
                "context": context,
                "active_sessions": len(self.chat_sessions),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to start chat session: {e!s}"}

    def _handle_send_message(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat message send operation."""
        try:
            message = params.get("message")
            if not message:
                return {
                    "status": "error",
                    "message": "Message content is required for send_message operation",
                }

            session_id = params.get("session_id")
            if not session_id:
                # Use the most recent active session
                if not self.chat_sessions:
                    return {
                        "status": "error",
                        "message": "No active chat sessions. Call start_session first.",
                    }
                session_id = max(self.chat_sessions.keys(), key=lambda k: self.chat_sessions[k]["start_time"])

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
                {"role": "assistant", "content": response, "timestamp": __import__("time").time()}
            )

            return {
                "status": "success",
                "message": "Message processed",
                "operation": "send_message",
                "session_id": session_id,
                "response": response,
                "message_count": len(self.chat_sessions[session_id]["messages"]),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to send chat message: {e!s}"}

    def _handle_stop_session(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat session stop operation."""
        try:
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
                    "operation": "stop_session",
                    "stopped_sessions": stopped_count,
                }

            if session_id not in self.chat_sessions:
                return {"status": "error", "message": f"Chat session '{session_id}' not found"}

            # Stop specific session
            self.chat_sessions[session_id]["active"] = False

            return {
                "status": "success",
                "message": f"Chat session '{session_id}' stopped",
                "operation": "stop_session",
                "session_id": session_id,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to stop chat session: {e!s}"}

    def _handle_get_state(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat state get operation."""
        try:
            session_id = params.get("session_id")

            if session_id:
                # Get specific session state
                if session_id not in self.chat_sessions:
                    return {"status": "error", "message": f"Chat session '{session_id}' not found"}

                session = self.chat_sessions[session_id]
                return {
                    "status": "success",
                    "message": f"Retrieved state for session '{session_id}'",
                    "operation": "get_state",
                    "session_id": session_id,
                    "active": session["active"],
                    "context": session["context"],
                    "message_count": len(session["messages"]),
                    "start_time": session["start_time"],
                    "duration": __import__("time").time() - session["start_time"],
                }
            else:
                # Get all sessions state
                active_sessions = [sid for sid, session in self.chat_sessions.items() if session["active"]]
                total_messages = sum(len(session["messages"]) for session in self.chat_sessions.values())

                return {
                    "status": "success",
                    "message": "Retrieved all chat sessions state",
                    "operation": "get_state",
                    "total_sessions": len(self.chat_sessions),
                    "active_sessions": len(active_sessions),
                    "total_messages": total_messages,
                    "session_ids": list(self.chat_sessions.keys()),
                }

        except Exception as e:
            return {"status": "error", "message": f"Failed to get chat state: {e!s}"}

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
