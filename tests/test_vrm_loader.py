"""
Tests for the VRM loader module.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestVRMLoader:
    """Tests for the VRM loader functionality."""

    def test_load_vrm_file_not_found(self, tmp_path):
        """Test loading a non-existent VRM file raises FileNotFoundError."""
        from src.avatarmcp.models.vrm_loader import VRMLoader

        non_existent_file = tmp_path / "nonexistent.vrm"
        with pytest.raises(FileNotFoundError):
            VRMLoader.from_file(str(non_existent_file))

    @patch("pygltflib.GLTF2.load")
    def test_load_vrm_invalid_file(self, mock_load, tmp_path):
        """Test loading an invalid VRM file raises ValueError."""
        from src.avatarmcp.models.vrm_loader import VRMLoader

        # Create a mock for the GLTF2.load method to raise an exception
        mock_load.side_effect = Exception("Invalid VRM file")

        # Create a test VRM file
        test_file = tmp_path / "test.vrm"
        test_file.write_bytes(b"invalid vrm data")

        with pytest.raises(ValueError):
            VRMLoader.from_file(str(test_file))

    @patch("pygltflib.GLTF2.load")
    def test_load_vrm_success(self, mock_load, mock_gltf):
        """Test successfully loading a VRM file."""
        from src.avatarmcp.models.vrm_loader import VRMLoader

        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf

        # Mock file operations
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file

            # Call the method under test
            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        # Assertions
        assert vrm_model is not None
        assert isinstance(vrm_model.metadata, dict)
        assert isinstance(vrm_model.meshes, list)
        assert isinstance(vrm_model.materials, list)

    @patch("pygltflib.GLTF2.load")
    def test_extract_metadata(self, mock_load, mock_gltf):
        """Test extracting metadata from a VRM file."""
        from src.avatarmcp.models.vrm_loader import VRMLoader

        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf

        # Call the method under test
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file

            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        # Assertions
        assert isinstance(vrm_model.metadata, dict)

    @patch("pygltflib.GLTF2.load")
    def test_load_bones(self, mock_load, mock_gltf):
        """Test loading bones from a VRM file."""
        from src.avatarmcp.models.vrm_loader import VRMLoader

        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf

        # Call the method under test
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file

            vrm_model = VRMLoader.from_file("test_assets/test_avatar.vrm")

        # Assertions
        assert isinstance(vrm_model.bones, list)
