"""
Tests for the AvatarMCP server.
"""
import unittest
from unittest.mock import MagicMock, patch

from src.avatarmcp.core.app import AvatarMCP
from src.avatarmcp.models.vrm_model import VRMModel
from src.avatarmcp.models.animation_controller import AnimationController

class TestAvatarMCP(unittest.TestCase):
    """Test cases for the AvatarMCP server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = AvatarMCP()
        
        # Mock the FastMCP instance
        self.app.mcp = MagicMock()
        
    def test_create_app(self):
        """Test creating the AvatarMCP application."""
        self.assertIsNotNone(self.app)
        self.assertIsNotNone(self.app.mcp)
        
    def test_register_commands(self):
        """Test registering commands."""
        # Mock the command modules
        with patch('src.avatarmcp.commands.model_commands') as mock_model_cmds, \
             patch('src.avatarmcp.commands.animation_commands') as mock_anim_cmds, \
             patch('src.avatarmcp.commands.help_commands') as mock_help_cmds:
            
            # Create a mock registry
            mock_registry = MagicMock()
            mock_registry.app = self.app
            
            # Call register_commands
            from src.avatarmcp.commands import register_commands
            register_commands(mock_registry)
            
            # Verify command modules were imported and register_commands was called
            mock_model_cmds.register_commands.assert_called_once_with(mock_registry)
            mock_anim_cmds.register_commands.assert_called_once_with(mock_registry)
            mock_help_cmds.register_commands.assert_called_once_with(mock_registry)
    
    def test_help_command(self):
        """Test the help command."""
        # Mock the command registry
        mock_registry = MagicMock()
        mock_registry.list_commands.return_value = [
            {'name': 'load_vrm', 'description': 'Load a VRM model'},
            {'name': 'list_models', 'description': 'List all loaded models'}
        ]
        mock_registry.get_command_help.return_value = {
            'name': 'load_vrm',
            'description': 'Load a VRM model',
            'examples': ["load_vrm('path/to/model.vrm')"]
        }
        
        # Import and call the help command
        from src.avatarmcp.commands.help_commands import register_commands
        register_commands(mock_registry)
        
        # Get the help command function
        help_cmd = None
        for call in mock_registry.register.mock_calls:
            if call[1][0] == 'help':
                help_cmd = call[2]['function']
                break
                
        self.assertIsNotNone(help_cmd, "Help command not registered")
        
        # Test listing all commands
        result = help_cmd()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['commands']), 2)
        
        # Test getting help for a specific command
        result = help_cmd('load_vrm')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['command']['name'], 'load_vrm')
        
        # Test unknown command
        mock_registry.get_command_help.return_value = None
        result = help_cmd('unknown_command')
        self.assertEqual(result['status'], 'error')


class TestVRMModel(unittest.TestCase):
    """Test cases for the VRMModel class."""
    
    @patch('pygltflib.GLTF2')
    def test_load_vrm(self, mock_gltf):
        """Test loading a VRM model."""
        # Mock GLTF data
        mock_gltf.return_value = MagicMock()
        mock_gltf.return_value.model = MagicMock()
        mock_gltf.return_value.model.extensions = {
            'VRM': {
                'meta': {
                    'title': 'Test Model',
                    'version': '1.0',
                    'author': 'Tester'
                },
                'humanoid': {
                    'humanBones': [
                        {'bone': 'Hips', 'node': 0},
                        {'bone': 'Spine', 'node': 1}
                    ]
                },
                'blendShapeMaster': {
                    'blendShapeGroups': [
                        {
                            'name': 'A',
                            'presetName': 'joy',
                            'binds': [
                                {'mesh': 0, 'index': 0, 'weight': 100}
                            ]
                        }
                    ]
                }
            }
        }
        
        # Test loading a VRM model
        model = VRMModel.load('test.vrm')
        self.assertEqual(model.metadata['title'], 'Test Model')
        self.assertEqual(len(model.bone_names), 2)
        self.assertEqual(len(model.blend_shape_names), 1)
        
        # Test getting bone transforms
        transforms = model.get_bone_transforms()
        self.assertEqual(len(transforms), 2)
        
        # Test getting blend shape weights
        weights = model.get_blend_shape_weights()
        self.assertEqual(len(weights), 1)
        
        # Test setting blend shape weights
        model.set_blend_shape_weights({'A': 0.5})
        weights = model.get_blend_shape_weights()
        self.assertEqual(weights['A'], 0.5)


class TestAnimationController(unittest.TestCase):
    """Test cases for the AnimationController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model = MagicMock()
        self.controller = AnimationController(self.model)
        
    def test_play_animation(self):
        """Test playing an animation."""
        # Mock animation data
        animation = {
            'duration': 1.0,
            'loop': True,
            'keyframes': [
                {'time': 0.0, 'bone_name': 'Hips', 'position': [0, 1, 0]},
                {'time': 1.0, 'bone_name': 'Hips', 'position': [0, 1.1, 0]}
            ]
        }
        
        # Test playing an animation
        result = self.controller.play_animation(
            animation_name='test_anim',
            animation_data=animation,
            loop=True,
            weight=1.0,
            speed=1.0
        )
        
        self.assertTrue(result)
        self.assertIn('test_anim', self.controller.active_animations)
        
        # Test stopping the animation
        result = self.controller.stop_animation('test_anim')
        self.assertTrue(result)
        self.assertNotIn('test_anim', self.controller.active_animations)
        
        # Test updating the animation
        self.controller.update(0.5)  # Shouldn't raise any exceptions


if __name__ == '__main__':
    unittest.main()
