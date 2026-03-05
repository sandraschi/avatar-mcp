#!/usr/bin/env python3
"""
Modernized SOTA HTTP server for avatar-mcp webapp.
Integrates directly with AvatarMCPServer for live state and control.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Internal imports
from avatarmcp.server import AvatarMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global server state
mcp_srv: AvatarMCPServer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    global mcp_srv
    logger.info("Initializing AvatarMCPServer bridge...")

    # Initialize the main server logic
    # We enable OSC by default as this is the primary interactive hub
    mcp_srv = AvatarMCPServer(enable_osc=True)

    # We don't call mcp_srv.mcp.run() because that's for stdio/sse blocking.
    # Instead we call the internal start() which sets up managers.
    await mcp_srv.start()

    # Manually register tools so they are available for introspection
    mcp_srv._register_tools()

    logger.info("AvatarMCPServer bridge ACTIVE")
    yield

    # Shutdown
    if mcp_srv:
        logger.info("Shutting down AvatarMCPServer bridge...")
        await mcp_srv.stop()


app = FastAPI(
    title="AvatarMCP SOTA API",
    description="State-of-the-Art HTTP Orchestration for VRM Avatars",
    version="2026.2.17",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any]


class LaunchRequest(BaseModel):
    repo_path: str
    port: int
    app_id: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/v1/health")
async def health():
    """Server health check with system telemetry."""
    return {
        "status": "ok",
        "server": "avatarmcp-http-sota",
        "version": "2026.2.17",
        "uptime": time.time() - (mcp_srv.start_time if mcp_srv else time.time()),
        "bridge_active": mcp_srv is not None,
    }


@app.get("/api/v1/status")
async def get_status():
    """Live status summary from the AvatarMCPServer."""
    if not mcp_srv:
        return {"error": "Server not initialized"}

    # Gather live data from managers
    active_count = len(mcp_srv.loaded_models)

    return {
        "active_avatars": active_count,
        "system_load_pct": 15,  # Placeholder for real CPU/GPU metrics
        "unity_engine": "connected" if mcp_srv.osc_manager.enabled else "not_connected",
        "vrchat_bridge": "active" if mcp_srv.osc_manager.initialized else "idle",
        "osc_pipeline": "streaming" if mcp_srv.osc_manager.enabled else "idle",
        "active_model_id": mcp_srv.active_model_id,
        "models": [{"id": mid, "name": model.name} for mid, model in mcp_srv.loaded_models.items()],
    }


@app.get("/api/v1/tools")
async def list_tools():
    """Introspect and return all available MCP tools."""
    if not mcp_srv:
        return []

    tools = []
    # FastMCP stores tools in a manager
    tm = getattr(mcp_srv.mcp, "_tool_manager", None)
    if not tm:
        return []

    # Extract tools from the manager (FastMCP 2.x pattern)
    for name, tool in tm._tools.items():
        tools.append({"name": name, "description": tool.description, "parameters": tool.parameters})
    return tools


@app.post("/api/v1/tools/execute")
async def execute_tool(req: ToolExecutionRequest):
    """Direct execution of MCP tools via HTTP."""
    if not mcp_srv:
        raise HTTPException(status_code=503, detail="Server not initialized")

    # This would call mcp_srv.mcp.call_tool(req.tool_name, req.arguments)
    # But for now we'll maintain the bridge logic
    return {"message": "NOT_IMPLEMENTED", "status": "error"}


@app.post("/api/v1/fleet/launch")
async def launch_fleet_app(request: LaunchRequest):
    """
    Standardized endpoint to launch other apps in the fleet.
    Used for seamless navigation between MCP applications.
    """
    import os
    import subprocess

    repo_path = request.repo_path
    if not os.path.exists(repo_path):
        return {"error": f"Path not found: {repo_path}"}

    # Security check: only allow paths in D:/Dev/repos
    if not repo_path.replace("\\", "/").startswith("D:/Dev/repos"):
        return {"error": "Unauthorized path"}

    try:
        # Launch using the localized start.ps1 if it exists
        start_script = os.path.join(repo_path, "start.ps1")
        if not os.path.exists(start_script):
            # Try web_sota/start.ps1
            start_script = os.path.join(repo_path, "web_sota", "start.ps1")

        if os.path.exists(start_script):
            subprocess.Popen(["powershell", "-File", start_script], cwd=repo_path)
            return {"status": "launching", "app": request.app_id}
        else:
            return {"error": f"No start.ps1 found in {repo_path}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/avatars")
async def list_avatars():
    """Get list of all discovered and loaded avatars."""
    if not mcp_srv:
        return []
    return [
        {
            "id": mid,
            "name": model.name,
            "path": model.path,
            "is_active": mid == mcp_srv.active_model_id,
        }
        for mid, model in mcp_srv.loaded_models.items()
    ]
