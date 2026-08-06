"""
Tests for the VRM loader module.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_gltf():
    """Create a properly structured mock GLTF2 object for VRM tests."""
    gltf = MagicMock()
    gltf.accessors = []
    gltf.meshes = []
    gltf.materials = []
    gltf.textures = []
    gltf.nodes = []
    gltf.skins = []
    gltf.scenes = []
    gltf.asset = MagicMock()
    gltf.asset.version = "2.0"
    gltf.asset.generator = "test"
    gltf.asset.copyright = None
    return gltf


class TestVRMLoader:
    """Tests for the VRM loader functionality."""

    def test_load_vrm_file_not_found(self, tmp_path):
        from src.avatarmcp.models.vrm_loader import VRMLoader

        non_existent_file = tmp_path / "nonexistent.vrm"
        with pytest.raises(FileNotFoundError):
            VRMLoader.from_file(str(non_existent_file))

    @patch("src.avatarmcp.models.vrm_loader.GLTF2.load_binary")
    def test_load_vrm_invalid_file(self, mock_load_binary, tmp_path):
        from src.avatarmcp.models.vrm_loader import VRMLoader

        mock_load_binary.side_effect = Exception("Invalid VRM file")

        test_file = tmp_path / "test.vrm"
        test_file.write_bytes(b"invalid vrm data")

        with pytest.raises(ValueError):
            VRMLoader.from_file(str(test_file))

    @patch("src.avatarmcp.models.vrm_loader.GLTF2.load_binary")
    def test_load_vrm_success(self, mock_load_binary, mock_gltf):
        from src.avatarmcp.models.vrm_loader import VRMLoader

        mock_gltf.extensions = {}
        mock_load_binary.return_value = mock_gltf

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.suffix", ".vrm"),
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"mock"
            mock_open.return_value = mock_file

            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        assert vrm_model is not None
        assert isinstance(vrm_model.metadata, dict)

    @patch("src.avatarmcp.models.vrm_loader.GLTF2.load_binary")
    def test_extract_metadata(self, mock_load_binary, mock_gltf):
        from src.avatarmcp.models.vrm_loader import VRMLoader

        mock_gltf.extensions = {"VRM": {"meta": {"title": "Test", "version": "1.0", "author": "Tester"}}}
        mock_load_binary.return_value = mock_gltf

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.suffix", ".vrm"),
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"mock"
            mock_open.return_value = mock_file

            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        assert vrm_model.metadata["extensions"]["VRM"]["meta"]["title"] == "Test"
        assert vrm_model.metadata["extensions"]["VRM"]["meta"]["version"] == "1.0"

    @patch("src.avatarmcp.models.vrm_loader.GLTF2.load_binary")
    def test_load_bones(self, mock_load_binary, mock_gltf):
        from src.avatarmcp.models.vrm_loader import VRMLoader

        mock_gltf.extensions = {}
        node_a = MagicMock()
        node_a.name = "Hips"
        node_b = MagicMock()
        node_b.name = "Spine"
        mock_gltf.nodes = [node_a, node_b]
        mock_load_binary.return_value = mock_gltf

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.suffix", ".vrm"),
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"mock"
            mock_open.return_value = mock_file

            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        assert isinstance(vrm_model.bones, dict)
