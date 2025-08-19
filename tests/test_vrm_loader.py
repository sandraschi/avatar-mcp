"""
Tests for the VRM loader module.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestVRMLoader:
    """Tests for the VRM loader functionality."""
    
    def test_load_vrm_file_not_found(self, tmp_path):
        """Test loading a non-existent VRM file raises FileNotFoundError."""
        from avatarmcp.vrm_loader import VRMLoader, VRMError
        
        non_existent_file = tmp_path / "nonexistent.vrm"
        with pytest.raises(FileNotFoundError):
            VRMLoader.from_file(str(non_existent_file))
    
    @patch('pygltflib.GLTF2.load')
    def test_load_vrm_invalid_file(self, mock_load, tmp_path):
        """Test loading an invalid VRM file raises VRMError."""
        from avatarmcp.vrm_loader import VRMLoader, VRMError
        
        # Create a mock for the GLTF2.load method to raise an exception
        mock_load.side_effect = Exception("Invalid VRM file")
        
        # Create a test VRM file
        test_file = tmp_path / "test.vrm"
        test_file.write_bytes(b"invalid vrm data")
        
        with pytest.raises(VRMError):
            VRMLoader.from_file(str(test_file))
    
    @patch('pygltflib.GLTF2.load')
    def test_load_vrm_success(self, mock_load, mock_gltf):
        """Test successfully loading a VRM file."""
        from avatarmcp.vrm_loader import VRMLoader
        
        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file
            
            # Call the method under test
            vrm_model = VRMLoader.from_file("dummy_path.vrm")
        
        # Assertions
        assert vrm_model is not None
        assert vrm_model.metadata["title"] == "Test Avatar"
        assert vrm_model.metadata["author"] == "Test Author"
        assert len(vrm_model.meshes) > 0
        assert len(vrm_model.materials) > 0
    
    @patch('pygltflib.GLTF2.load')
    def test_extract_metadata(self, mock_load, mock_gltf):
        """Test extracting metadata from a VRM file."""
        from avatarmcp.vrm_loader import VRMLoader
        
        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf
        
        # Call the method under test
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file
            
            vrm_model = VRMLoader.from_file("dummy_path.vrm")
        
        # Assertions
        assert "title" in vrm_model.metadata
        assert "author" in vrm_model.metadata
        assert "version" in vrm_model.metadata
    
    @patch('pygltflib.GLTF2.load')
    def test_load_bones(self, mock_load, mock_gltf):
        """Test loading bones from a VRM file."""
        from avatarmcp.vrm_loader import VRMLoader
        
        # Configure the mock to return our test GLTF object
        mock_load.return_value = mock_gltf
        
        # Call the method under test
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.read.return_value = b"VRM 2.0 mock data"
            mock_open.return_value = mock_file
            
            vrm_model = VRMLoader.from_file("dummy_path.vrm")
        
        # Assertions
        assert len(vrm_model.bones) > 0
        assert any(bone.name == "Hips" for bone in vrm_model.bones)
