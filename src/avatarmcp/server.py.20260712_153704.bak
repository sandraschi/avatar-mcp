"""
AvatarMCP - FastMCP 3.1+ Server Implementation

This module implements the MCP (Model Context Protocol) server for AvatarMCP,
following the FastMCP 3.x API standards (name, version, lifespan, instructions).
"""

import asyncio
import fnmatch
import inspect
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP
from fastmcp.server import create_proxy

from avatarmcp.handlers.chatbot_handler import ChatbotHandler
from avatarmcp.metrics import MetricsCollector
from avatarmcp.models.vrm_manager import VRMManager
from avatarmcp.models.vrm_model import VRMModel
from avatarmcp.tools.chat_tools import ChatTool

# Portmanteau-only: core tools (CoreAvatarTools, CoreSystemTools, CoreUnityIntegrationTools)
# are not registered; use system_monitor(operation="initialize"|"shutdown") and portmanteau tools.

logger = logging.getLogger(__name__)


class OSCConfig:
    def __init__(
        self,
        client_address: str = "127.0.0.1",
        client_port: int = 9000,
        server_address: str = "127.0.0.1",
        server_port: int = 9001,
    ):
        self.client_address = client_address
        self.client_port = client_port
        self.server_address = server_address
        self.server_port = server_port


def oscmethod(address_pattern):
    """Decorator to mark methods as OSC message handlers."""

    def decorator(func):
        func._osc_address = address_pattern
        return func

    return decorator


class OSCManager:
    def __init__(self, osc_config: OSCConfig | None = None, enabled: bool = True):
        self.enabled = enabled
        self.initialized = False
        self.osc_config = osc_config or OSCConfig()
        self.osc_server = None
        self.osc_client = None
        self.dispatcher = None
        self.transport = None

        if not self.enabled:
            logger.warning("OSC is disabled. No OSC server will be started.")
            return

    async def initialize(self):
        """Asynchronously initialize the OSC server components."""
        if not self.enabled or self.initialized:
            return

        try:
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import AsyncIOOSCUDPServer
            from pythonosc.udp_client import SimpleUDPClient

            self.dispatcher = Dispatcher()
            # Use get_running_loop() as this is called within a running loop
            self.osc_server = AsyncIOOSCUDPServer(
                (self.osc_config.server_address, self.osc_config.server_port),
                self.dispatcher,
                loop=asyncio.get_running_loop(),
            )
            self.osc_client = SimpleUDPClient(self.osc_config.client_address, self.osc_config.client_port)

            self.dispatcher.map("/*", self._handle_osc_message)
            self.initialized = True
            logger.info(f"OSC server initialized on {self.osc_config.server_address}:{self.osc_config.server_port}")
        except Exception as e:
            logger.error(f"Failed to initialize OSC server: {e}")
            self.enabled = False

    async def start(self):
        """Start the OSC server."""
        if not self.enabled:
            return

        if not self.initialized:
            await self.initialize()

        if not self.initialized:
            return

        try:
            # For testing, we might want to skip actual server startup
            import os

            if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in str(os.getenv("_", "")):
                logger.info("Skipping OSC server start during testing")
                return

            self.transport, _ = await self.osc_server.create_serve_endpoint()
            logger.info("OSC server started and listening")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
            self.enabled = False

    async def stop(self):
        """Stop the OSC server."""
        if not self.enabled or not self.initialized:
            return

        try:
            if self.transport:
                self.transport.close()
                self.transport = None
            logger.info("OSC server stopped")
        except Exception as e:
            logger.error(f"Failed to stop OSC server: {e}")

    async def _handle_osc_message(self, address, *args):
        """Internal handler for OSC messages."""
        logger.info(f"Received OSC message: {address} {args}")

        # Call the appropriate handler method if it exists
        for _name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_osc_address"):
                if fnmatch.fnmatch(address, method._osc_address):
                    return await method(address, *args)

    @oscmethod("/avatar/osc/*")
    async def handle_osc_message(self, address, *args):
        """Handle OSC messages matching /avatar/osc/* pattern."""
        logger.info(f"Handling OSC message: {address} {args}")
        # Add your OSC message handling logic here


class AvatarMCPServer:
    """MCP server implementation for AvatarMCP using FastMCP 3.1+ API."""

    @asynccontextmanager
    async def lifespan(self, mcp: Any):
        """Lifecycle hook for startup and shutdown."""
        self.logger.info("AvatarMCPServer lifecycle starting...")
        try:
            # Start OSC manager if enabled
            await self.osc_manager.start()
            yield
        finally:
            # Stop OSC manager if enabled
            await self.osc_manager.stop()
            self.logger.info("AvatarMCPServer lifecycle ending...")

    def __init__(
        self,
        osc_config: OSCConfig | None = None,
        models_dir: str | None = None,
        enable_osc: bool = False,
    ):
        """Initialize the MCP server."""
        self.mcp = FastMCP(
            name="avatarmcp",
            version="0.1.0",
            lifespan=self.lifespan,
            instructions="""State-of-the-art MCP server for VRM avatar management and animation.

CAPABILITIES:
• VRM avatar loading and visualization
• Real-time bone and morph target animation
• OSC communication for Unity/VRChat integration
• 3D model export and conversion
• AI-powered chatbot integration
• Voice and speech synthesis
• Computer vision processing

CONVERSATIONAL CAPABILITIES:
• All tools return structured responses with a 'message' field for natural language interaction.
• Error responses include 'suggestions' for recovery.

AGENTIC WORKFLOWS (SEP-1577):
• Use agentic_avatar_workflow() for complex, multi-step avatar automation.
• Use intelligent_animation_assistant() for LLM-driven animation operations.

USAGE: Load VRM models, animate avatars, and integrate with external applications.""",
        )

        # ── MCP Bridge (ProxyProvider) ────────────────────────────────────────────
        _bridge_proxies: list[str] = []
        bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
        if bridge_urls:
            for url in bridge_urls.split(","):
                url = url.strip()
                if url:
                    try:
                        self.mcp.add_provider(create_proxy(url))
                        _bridge_proxies.append(url)
                    except Exception:
                        pass
        self.running = False
        self.osc_manager = OSCManager(osc_config, enabled=enable_osc)
        self._message_id = 0

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Initialize VRM manager
        self.vrm_manager = VRMManager(models_dir)
        self.loaded_models: dict[str, VRMModel] = {}
        self.active_model_id: str | None = None

        # Initialize portmanteau tool classes
        from .tools.portmanteau.animation_manager_tool import AnimationManagerTool
        from .tools.portmanteau.artifact_manager_tool import ArtifactManagerTool
        from .tools.portmanteau.audio_manager_tool import AudioManagerTool
        from .tools.portmanteau.avatar_manager_tool import AvatarManagerTool
        from .tools.portmanteau.avatar_pipeline_tool import AvatarPipelineTool
        from .tools.portmanteau.avatar_sampling_tool import AvatarSamplingTool
        from .tools.portmanteau.behavior_manager_tool import BehaviorManagerTool
        from .tools.portmanteau.chat_manager_tool import ChatManagerTool
        from .tools.portmanteau.collaboration_manager_tool import CollaborationManagerTool
        from .tools.portmanteau.content_manager_tool import ContentManagerTool
        from .tools.portmanteau.emotion_manager_tool import EmotionManagerTool
        from .tools.portmanteau.interaction_manager_tool import InteractionManagerTool
        from .tools.portmanteau.performance_manager_tool import PerformanceManagerTool
        from .tools.portmanteau.system_monitor_tool import SystemMonitorTool
        from .tools.portmanteau.unity_config_manager_tool import UnityConfigManagerTool
        from .tools.portmanteau.unity_integration_tool import UnityIntegrationTool
        from .tools.portmanteau.unity_window_manager_tool import UnityWindowManagerTool

        self.avatar_manager_tool = AvatarManagerTool(self)
        self.avatar_pipeline_tool = AvatarPipelineTool(self)
        self.avatar_sampling_tool = AvatarSamplingTool(self)
        self.animation_manager_tool = AnimationManagerTool(self)
        self.emotion_manager_tool = EmotionManagerTool(self)
        self.artifact_manager_tool = ArtifactManagerTool(self)
        self.audio_manager_tool = AudioManagerTool(self)
        self.behavior_manager_tool = BehaviorManagerTool(self)
        self.collaboration_manager_tool = CollaborationManagerTool(self)
        self.content_manager_tool = ContentManagerTool(self)
        self.interaction_manager_tool = InteractionManagerTool(self)
        self.performance_manager_tool = PerformanceManagerTool(self)
        self.unity_integration_tool = UnityIntegrationTool(self)
        self.unity_window_manager_tool = UnityWindowManagerTool(self)
        self.unity_config_manager_tool = UnityConfigManagerTool(self)
        self.chat_manager_tool = ChatManagerTool(self)
        self.system_monitor_tool = SystemMonitorTool(self)

        # FastMCP 3.1 prompts (avatar workflow and animation assistant)
        from avatarmcp.prompts import register_prompts

        register_prompts(self.mcp)

        # Initialize chat components
        self.chatbot_handler = ChatbotHandler()
        self.chat_tool = ChatTool()
        self.chat_tool.chatbot_handler = self.chatbot_handler

        # Initialize metrics collection
        # Port 10790 (metrics-only; 10791 is reserved for docs_mcp / fleet starts UI)
        metrics_port = int(os.getenv("METRICS_PORT", "10790"))
        self.metrics = MetricsCollector(port=metrics_port, enabled=True)
        if self.metrics.info is not None:
            self.metrics.info.info(
                {
                    "version": "1.0.0",
                    "service": "avatarmcp",
                    "environment": os.getenv("ENV", "development"),
                }
            )

        # Track server state
        self.start_time = time.time()
        self.initialized = False

    async def start(self):
        """Start the MCP server."""
        if self.running:
            return

        self.logger.info("Starting AvatarMCPServer...")
        self.running = True
        # NOTE: Lifecycle logic (OSC) is now handled via lifespan context manager
        # mcp.run() will trigger the lifespan

    async def stop(self):
        """Stop the MCP server."""
        if not self.running:
            return

        self.logger.info("Stopping AvatarMCPServer...")

        try:
            # Stop OSC manager
            await self.osc_manager.stop()

            self.running = False
            self.initialized = False

            self.logger.info("AvatarMCPServer stopped")

        except Exception as e:
            self.logger.error(f"Error stopping AvatarMCPServer: {e}", exc_info=True)

    def _send_osc_message(self, address: str, *args) -> bool:
        """Send an OSC message via the OSC client. Returns True on success."""
        try:
            if self.osc_manager and self.osc_manager.osc_client:
                self.osc_manager.osc_client.send_message(address, *args)
                return True
        except Exception as e:
            self.logger.warning(f"Failed to send OSC message: {e}")
        return False


def run_server(
    host: str = "0.0.0.0",
    port: int = 10793,
    enable_loki: bool = False,
    loki_url: str = None,
    enable_osc: bool = False,
):
    """Run the AvatarMCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    logger.info("Starting AvatarMCP server (FastMCP 2.11.3+ compatible)")

    try:
        # Create the server
        server = AvatarMCPServer(enable_osc=enable_osc)

        # Start the server using mcp.run()
        # The lifespan context manager will handle OSC initialization
        # show_banner=False: banner on stdout breaks stdio MCP (Cursor/Claude)
        server.mcp.run(show_banner=False)

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1

    return 0


def main():
    """Main entry point for the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="AvatarMCP Server (FastMCP 2.11.3+ compatible)")
    parser.add_argument("--enable-osc", action="store_true", help="Enable OSC server")

    args = parser.parse_args()

    # Run the server
    return run_server(enable_osc=args.enable_osc)


# ASGI app for uvicorn (e.g. web_sota backend)
_web_server = AvatarMCPServer(enable_osc=False)
app = _web_server.mcp.http_app()

if __name__ == "__main__":
    sys.exit(main())
