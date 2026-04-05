"""Global state for AvatarMCP API."""

from ...server import AvatarMCPServer

# Global server instance
mcp_server: AvatarMCPServer | None = None


def get_server() -> AvatarMCPServer:
    """Get the global server instance."""
    global mcp_server
    if mcp_server is None:
        mcp_server = AvatarMCPServer(enable_osc=False)  # OSC handled separately if needed
    return mcp_server
