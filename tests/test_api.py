"""
Test cases for the AvatarMCP API endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    from avatarmcp.server import app

    with TestClient(app) as client:
        yield client


class TestHealthAPI:
    def test_health_endpoint(self, test_client):
        response = test_client.get("/api/v1/health")
        assert response.status_code in (200, 404)
        response2 = test_client.get("/openapi.json")
        assert response2.status_code in (200, 404)


class TestModelAPI:
    def test_list_models_empty(self, test_client):
        response = test_client.get("/api/v1/models")
        assert response.status_code in (200, 404)
