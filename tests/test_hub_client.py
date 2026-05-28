"""Tests for VRoid Hub client (no live API)."""

from pathlib import Path

import pytest

from avatarmcp.pipeline.hub_client import VRoidHubClient


def test_hub_auth_status(tmp_path: Path) -> None:
    client = VRoidHubClient(tmp_path)
    status = client.auth_status()
    assert "authenticated" in status
    assert status["authenticated"] is False


def test_hub_auth_start_missing_client_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VROID_HUB_CLIENT_ID", raising=False)
    client = VRoidHubClient(tmp_path)
    client.client_id = ""
    result = client.auth_start()
    assert result["success"] is False


def test_hub_set_token(tmp_path: Path) -> None:
    client = VRoidHubClient(tmp_path)
    result = client.auth_set_token("test-token-abc")
    assert result["success"] is True
    assert client.get_access_token() == "test-token-abc"
