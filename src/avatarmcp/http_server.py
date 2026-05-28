#!/usr/bin/env python3
"""
Modernized SOTA HTTP server for avatar-mcp webapp.
Integrates directly with AvatarMCPServer for live state and control.
"""

import asyncio
import logging
import os
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

# In-memory LLM settings (Ollama model selection for webapp/chat)
_llm_settings: dict[str, Any] = {"provider": "ollama", "model": ""}
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


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

    if hasattr(mcp_srv, "_register_tools"):
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


class ThumbnailRequest(BaseModel):
    icon_path: str


class LaunchRequest(BaseModel):
    repo_path: str
    port: int
    app_id: str


class LLMSettingsUpdate(BaseModel):
    model: str = ""


# ---------------------------------------------------------------------------
# Ollama / LLM discovery (for Settings page model selector)
# ---------------------------------------------------------------------------


async def _ollama_get(path: str) -> dict[str, Any] | None:
    """GET from Ollama API; returns None on failure."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL.rstrip('/')}{path}")
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        logger.debug("Ollama request failed: %s", e)
    return None


@app.get("/api/v1/settings/ollama/status")
async def ollama_status():
    """Check if Ollama is reachable (for Settings page)."""
    data = await _ollama_get("/api/version")
    return {
        "connected": data is not None,
        "base_url": OLLAMA_BASE_URL,
    }


@app.get("/api/v1/settings/ollama/models")
async def ollama_models():
    """List models discovered from Ollama (for Settings page dropdown)."""
    data = await _ollama_get("/api/tags")
    if data is None:
        return {"models": [], "error": "Ollama unreachable"}
    raw = data.get("models") or []
    models = [
        {"name": m.get("name") or m.get("model", ""), "size": m.get("size"), "modified_at": m.get("modified_at")}
        for m in raw
    ]
    return {"models": models}


@app.get("/api/v1/settings/llm")
async def get_llm_settings():
    """Current LLM provider and selected model (for chat/settings)."""
    return {"provider": _llm_settings.get("provider", "ollama"), "model": _llm_settings.get("model", "")}


@app.put("/api/v1/settings/llm")
async def update_llm_settings(body: LLMSettingsUpdate):
    """Set selected Ollama model (persists in process memory)."""
    _llm_settings["model"] = body.model or ""
    return {"provider": "ollama", "model": _llm_settings["model"]}


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


def _system_load_pct() -> float | None:
    """Return CPU load 0-100 if psutil available, else None."""
    try:
        import psutil

        return round(psutil.cpu_percent(interval=0.1) or 0, 1)
    except ImportError:
        return None


@app.get("/api/v1/status")
async def get_status():
    """Live status summary from the AvatarMCPServer."""
    if not mcp_srv:
        return {"error": "Server not initialized"}

    active_count = len(mcp_srv.loaded_models)
    payload = {
        "active_avatars": active_count,
        "unity_engine": "connected" if mcp_srv.osc_manager.enabled else "not_connected",
        "vrchat_bridge": "active" if mcp_srv.osc_manager.initialized else "idle",
        "osc_pipeline": "streaming" if mcp_srv.osc_manager.enabled else "idle",
        "active_model_id": mcp_srv.active_model_id,
        "models": [
            {"id": mid, "name": getattr(model, "metadata", {}).get("name") or getattr(model, "model_id", mid)}
            for mid, model in mcp_srv.loaded_models.items()
        ],
    }
    load = _system_load_pct()
    if load is not None:
        payload["system_load_pct"] = load
    return payload


@app.get("/api/v1/tools")
async def list_tools():
    """Introspect and return all available MCP tools (FastMCP 3.x list_tools API)."""
    if not mcp_srv:
        return []

    try:
        raw = mcp_srv.mcp.list_tools()
        tools_list = await raw if asyncio.iscoroutine(raw) else raw
        return [
            {
                "name": getattr(t, "name", ""),
                "description": getattr(t, "description", ""),
                "parameters": getattr(t, "parameters", {}),
            }
            for t in (tools_list or [])
        ]
    except (AttributeError, TypeError):
        tools = []
        tm = getattr(mcp_srv.mcp, "_tool_manager", None)
        if tm and hasattr(tm, "_tools"):
            for name, tool in tm._tools.items():
                tools.append(
                    {
                        "name": name,
                        "description": getattr(tool, "description", ""),
                        "parameters": getattr(tool, "parameters", {}),
                    }
                )
        return tools


@app.post("/api/v1/tools/execute")
async def execute_tool(req: ToolExecutionRequest):
    """Direct execution of MCP tools via HTTP."""
    if not mcp_srv:
        raise HTTPException(status_code=503, detail="Server not initialized")

    try:
        mcp = mcp_srv.mcp
        raw = mcp.call_tool(req.tool_name, req.arguments)
        result = await raw if asyncio.iscoroutine(raw) else raw
        # Normalize for JSON: extract content from result object or use as-is
        if hasattr(result, "content"):
            out = result.content
        elif hasattr(result, "data"):
            out = result.data
        else:
            out = result
        if isinstance(out, list) and out and hasattr(out[0], "text"):
            out = [getattr(c, "text", str(c)) for c in out]
        elif isinstance(out, list) and len(out) == 1:
            out = out[0].text if hasattr(out[0], "text") else out[0]
        return {"status": "success", "result": out}
    except Exception as e:
        logger.exception("Tool %s failed", req.tool_name)
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/v1/intelligence/loops")
async def get_agent_loops():
    """Predefined agentic loops for the webapp Loops page (SOTA backend)."""
    return {
        "loops": [
            {
                "id": "perception_loop",
                "name": "Perception-Action Loop",
                "description": "Analyze situational context and adapt behavior.",
                "tools": ["behavior_manager.analyze", "behavior_manager.adapt"],
                "status": "active",
            },
            {
                "id": "emotion_sync",
                "name": "Emotional Resonance",
                "description": "Sync avatar emotions with user sentiment.",
                "tools": ["emotion_manager.state_machine", "audio_manager.singing_synthesize"],
                "status": "ready",
            },
            {
                "id": "robotics_bridge",
                "name": "OpenFang Telemetry",
                "description": "Bridge robotics sensor data to avatar bones.",
                "tools": ["unity_integration.control_animation", "performance_manager.monitor"],
                "status": "connected",
            },
        ]
    }


@app.get("/api/v1/intelligence/trifecta")
async def get_intelligence_trifecta():
    """Trifecta intelligence status: OpenFang, AvatarMCP, BlackFang."""
    if not mcp_srv:
        return {"error": "Server not initialized"}
    return {
        "openfang": {
            "status": "simulated",
            "telemetry": "heartbeat_ok",
            "latency_ms": 12,
        },
        "avatarmcp_connectors": {
            "status": "online",
            "active_portmanteaus": 16,
            "api_proxy": "active",
        },
        "blackfang_agents": {
            "status": "idle",
            "connected_agents": 3,
            "current_loop": "perception_loop",
        },
    }


@app.get("/api/v1/avatars")
async def list_avatars():
    """Get list of all discovered and loaded avatars."""
    if not mcp_srv:
        return []
    return [
        {
            "id": mid,
            "name": getattr(model, "metadata", {}).get("name") or getattr(model, "model_id", mid),
            "path": getattr(model, "file_path", ""),
            "is_active": mid == mcp_srv.active_model_id,
        }
        for mid, model in mcp_srv.loaded_models.items()
    ]


@app.post("/api/v1/avatars/{avatar_id}/thumbnail")
async def set_avatar_thumbnail(avatar_id: str, req: ThumbnailRequest):
    """Set avatar model thumbnail from a PNG path on disk."""
    if not mcp_srv:
        raise HTTPException(status_code=503, detail="Server not initialized")
    try:
        result = await mcp_srv.vrm_manager.set_model_thumbnail(avatar_id, req.icon_path)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Thumbnail import failed"))
        return {"status": "success", **result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("set_avatar_thumbnail failed avatar_id=%s", avatar_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
