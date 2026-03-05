"""
Audio Manager Portmanteau Tool for AvatarMCP

Consolidates singing synthesis and future audio-related avatar tools.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AudioManagerTool:
    """Portmanteau tool for managing avatar audio and vocal performance."""

    def __init__(self, mcp_server):
        """Initialize audio manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the audio manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def audio_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for avatar audio and vocal performance.

            Parameters:
                operation: The specific operation to perform (required)
                    - "singing_synthesize": Generate singing from lyrics and melody

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "singing_synthesize":
                    return self._handle_singing_synthesize(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Audio manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_singing_synthesize(self, params: dict[str, Any]) -> dict[str, Any]:
        lyrics = params.get("lyrics")
        voice_style = params.get("voice_style", "natural")
        emotion = params.get("emotion", "neutral")
        tempo = params.get("tempo", 120)
        key = params.get("key", "C")

        if not lyrics:
            return {"status": "error", "message": "lyrics parameter is required"}

        osc_address = "/avatar/audio/singing/synthesize"
        singing_config = f"{lyrics}|{voice_style}|{emotion}|{tempo}|{key}"
        if self.mcp_server._send_osc_message(osc_address, singing_config):
            return {
                "status": "success",
                "message": "Singing synthesis command sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
