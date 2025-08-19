"""
Pytest configuration and fixtures for AvatarMCP tests.
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture
def mock_vrm_file(tmp_path):
    """Create a mock VRM file for testing."""
    vrm_path = tmp_path / "test_avatar.vrm"
    vrm_path.write_bytes(b"VRM 2.0 mock data")
    return str(vrm_path)

@pytest.fixture
def avatar_service():
    """Create an instance of AvatarService for testing."""
    from avatarmcp.service import AvatarService
    return AvatarService()

@pytest.fixture
def animation_controller():
    """Create an instance of AnimationController for testing."""
    from avatarmcp.animation import AnimationController
    return AnimationController()

@pytest.fixture
def mock_gltf():
    """Create a mock GLTF object for testing."""
    mock_gltf = MagicMock()
    mock_gltf.model = {
        "extensions": {
            "VRMC_vrm": {
                "meta": {
                    "title": "Test Avatar",
                    "version": "1.0",
                    "author": "Test Author"
                }
            }
        },
        "nodes": [
            {"name": "Hips", "children": [1, 2]},
            {"name": "LeftLeg"},
            {"name": "RightLeg"}
        ],
        "meshes": [
            {
                "primitives": [
                    {
                        "attributes": {
                            "POSITION": 0,
                            "NORMAL": 1,
                            "TEXCOORD_0": 2
                        },
                        "indices": 3,
                        "material": 0
                    }
                ]
            }
        ],
        "materials": [
            {
                "name": "Material.001",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
                    "metallicFactor": 0.5,
                    "roughnessFactor": 0.5
                }
            }
        ],
        "buffers": [{"byteLength": 1024}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 1024}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 100, "type": "VEC3"},  # POSITION
            {"bufferView": 0, "componentType": 5126, "count": 100, "type": "VEC3"},  # NORMAL
            {"bufferView": 0, "componentType": 5126, "count": 100, "type": "VEC2"},  # TEXCOORD_0
            {"bufferView": 0, "componentType": 5123, "count": 300, "type": "SCALAR"}  # INDICES
        ]
    }
    return mock_gltf
