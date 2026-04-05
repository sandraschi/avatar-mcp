"""Unified proxy endpoint for executing MCP tools via the webapp."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from avatarmcp.api.state import get_server

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/call")
async def call_tool_proxy(request: dict[str, Any]):
    """Execute a registered MCP tool by name with arguments."""
    try:
        tool_name = request.get("name")
        arguments = request.get("arguments", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")

        server_instance = get_server()
        mcp = server_instance.mcp

        # Call the tool through the FastMCP instance
        result = await mcp.call_tool(tool_name, arguments)
        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(
            f"Error calling tool proxy {tool_name if 'tool_name' in locals() else 'unknown'}: {e}"
        )
        return {"status": "error", "message": str(e)}


@router.get("/status")
async def get_system_status():
    """Get summarized system status for the dashboard."""
    try:
        server = get_server()
        # This mirrors the logic in Dashboard.tsx
        return {
            "active_avatars": len(server.vrm_manager.active_models)
            if hasattr(server, "vrm_manager")
            else 0,
            "system_load_pct": 0,  # Placeholder or real metric if available
            "unity_engine": "stable" if server.unity_integration_tool else "absent",
            "vrchat_bridge": "active",
            "osc_pipeline": "online",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
