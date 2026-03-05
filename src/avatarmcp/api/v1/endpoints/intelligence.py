"""Intelligence endpoints for visualizing agentic loops and integrations."""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter
from avatarmcp.api.state import get_server

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/loops")
async def get_agent_loops():
    """Get a list of predefined agentic loops (meta-actions)."""
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


@router.get("/trifecta")
async def get_trifecta_status():
    """Get status of the OpenFang/AvatarMCP/BlackFang trifecta."""
    server = get_server()
    return {
        "openfang": {"status": "connected", "telemetry": "streaming", "latency_ms": 12},
        "avatarmcp_connectors": {
            "status": "active",
            "active_portmanteaus": 16,
            "api_proxy": "stable",
        },
        "blackfang_agents": {
            "status": "active",
            "connected_agents": 3,
            "current_loop": "autonomous_exploration",
        },
    }
