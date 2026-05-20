"""
Integration tests for the AvatarMCP server.
"""

import asyncio
import logging
import os
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from avatarmcp.server import AvatarMCPServer

logger = logging.getLogger(__name__)

TEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "test_assets", "test_avatar.vrm")


@pytest.fixture
def server():
    srv = AvatarMCPServer(enable_osc=False)
    return srv


@pytest.fixture(scope="module")
def test_assets_dir():
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "test_assets")
    os.makedirs(assets_dir, exist_ok=True)
    return assets_dir


@pytest.mark.asyncio
async def test_server_start_stop(server):
    await server.start()
    assert server.running is True
    await server.stop()
    assert server.running is False


@pytest.mark.asyncio
async def test_vrm_loading(test_assets_dir):
    from avatarmcp.models.vrm_manager import VRMManager

    test_vrm_path = os.path.join(test_assets_dir, "test_avatar.vrm")
    if not os.path.exists(test_vrm_path):
        with open(test_vrm_path, "wb") as f:
            f.write(b"VRM" + b"\0" * 100)

    manager = VRMManager(models_dir=test_assets_dir)
    model_ids = await manager.scan_models()
    assert isinstance(model_ids, list)

    if model_ids:
        model_id = model_ids[0]
        model_info = await manager.get_model_info(model_id)
        assert model_info is not None
        assert model_info["id"] == model_id


@pytest.mark.asyncio
async def test_osc_communication():
    from pythonosc import dispatcher, udp_client
    from pythonosc.osc_server import AsyncIOOSCUDPServer

    server_port = 9002
    client_port = 9002

    osc_client = udp_client.SimpleUDPClient("127.0.0.1", client_port)
    received_messages = []

    def handle_osc_message(address: str, *args):
        received_messages.append({"address": address, "args": args})

    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.set_default_handler(handle_osc_message)

    loop = asyncio.get_event_loop()
    osc_server = AsyncIOOSCUDPServer(("127.0.0.1", server_port), osc_dispatcher, loop)
    transport, protocol = await osc_server.create_serve_endpoint()

    try:
        test_address = "/avatar/parameters/TestParam"
        osc_client.send_message(test_address, 1.0)
        await asyncio.sleep(0.2)
        assert len(received_messages) > 0, (
            f"No OSC message received. Client sent to port {client_port}, server on {server_port}."
        )
        assert received_messages[0]["address"] == test_address
        assert received_messages[0]["args"][0] == 1.0
    finally:
        transport.close()
