"""
Tests for the animation system.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

class TestAnimationSystem:
    """Tests for the animation controller and related classes."""
    
    def test_animation_keyframe_creation(self):
        """Test creating animation keyframes."""
        from avatarmcp.animation import AnimationKeyframe
        
        # Test bone keyframe
        bone_kf = AnimationKeyframe.create_bone_keyframe("Hips", 0.0, position=[0, 1, 0], rotation=[0, 0, 0, 1])
        assert bone_kf.target == "Hips"
        assert bone_kf.time == 0.0
        assert bone_kf.position == [0, 1, 0]
        assert bone_kf.rotation == [0, 0, 0, 1]
        
        # Test blend shape keyframe
        bs_kf = AnimationKeyframe.create_blend_shape_keyframe("smile", 1.0, 0.8)
        assert bs_kf.target == "smile"
        assert bs_kf.time == 1.0
        assert bs_kf.weight == 0.8
    
    def test_animation_clip_creation(self):
        """Test creating an animation clip."""
        from avatarmcp.animation import AnimationClip, AnimationKeyframe
        
        # Create test keyframes
        keyframes = [
            AnimationKeyframe.create_bone_keyframe("Hips", 0.0, [0, 1, 0], [0, 0, 0, 1]),
            AnimationKeyframe.create_bone_keyframe("Hips", 1.0, [0, 1.2, 0], [0, 0, 0, 1])
        ]
        
        # Create a clip
        clip = AnimationClip("test_clip", keyframes, loop=True, speed=1.0)
        
        # Assertions
        assert clip.name == "test_clip"
        assert len(clip.keyframes) == 2
        assert clip.loop is True
        assert clip.speed == 1.0
        assert clip.duration == 1.0
    
    def test_animation_controller_initialization(self):
        """Test initializing the animation controller."""
        from avatarmcp.animation import AnimationController
        
        controller = AnimationController()
        assert controller.current_animation is None
        assert controller.animation_queue == []
        assert controller.animation_speed == 1.0
    
    @patch('time.time')
    def test_play_animation(self, mock_time):
        """Test playing an animation."""
        from avatarmcp.animation import AnimationController, AnimationClip, AnimationKeyframe
        
        # Set up mock time
        mock_time.return_value = 0.0
        
        # Create a test clip
        keyframe = AnimationKeyframe.create_bone_keyframe("Hips", 1.0, [0, 1, 0], [0, 0, 0, 1])
        clip = AnimationClip("test_anim", [keyframe])
        
        # Create controller and play animation
        controller = AnimationController()
        controller.play_animation(clip)
        
        # Assertions
        assert controller.current_animation == clip
        assert controller.animation_start_time == 0.0
    
    @patch('time.time')
    def test_update_animation(self, mock_time):
        """Test updating animation state."""
        from avatarmcp.animation import AnimationController, AnimationClip, AnimationKeyframe
        
        # Set up mock time
        mock_time.side_effect = [0.0, 0.5]  # Start at 0s, then 0.5s later
        
        # Create a test clip with two keyframes
        keyframe1 = AnimationKeyframe.create_bone_keyframe("Hips", 0.0, [0, 1, 0], [0, 0, 0, 1])
        keyframe2 = AnimationKeyframe.create_bone_keyframe("Hips", 1.0, [0, 1.2, 0], [0, 0, 0, 1])
        clip = AnimationClip("test_anim", [keyframe1, keyframe2])
        
        # Create controller and play animation
        controller = AnimationController()
        controller.play_animation(clip)
        
        # Mock the apply_pose method
        apply_pose_mock = MagicMock()
        controller.apply_pose = apply_pose_mock
        
        # Update the animation
        controller.update()
        
        # Assertions
        assert apply_pose_mock.called
        # Check that we're halfway through the animation
        assert 0.4 < controller.get_animation_progress() < 0.6
    
    def test_blend_animations(self):
        """Test blending between two animations."""
        from avatarmcp.animation import AnimationController, AnimationClip, AnimationKeyframe
        
        # Create two test clips
        clip1 = AnimationClip("clip1", [
            AnimationKeyframe.create_bone_keyframe("Hips", 0.0, [0, 1, 0], [0, 0, 0, 1]),
            AnimationKeyframe.create_bone_keyframe("Hips", 1.0, [0, 1.2, 0], [0, 0, 0, 1])
        ])
        
        clip2 = AnimationClip("clip2", [
            AnimationKeyframe.create_bone_keyframe("Hips", 0.0, [0, 1, 0], [0, 0, 0, 1]),
            AnimationKeyframe.create_bone_keyframe("Hips", 1.0, [0, 1.0, 1.0], [0, 0, 0, 1])
        ])
        
        # Create controller and blend animations
        controller = AnimationController()
        blended_clip = controller.blend_animations(clip1, clip2, weight=0.5, name="blended")
        
        # Assertions
        assert blended_clip.name == "blended"
        assert len(blended_clip.keyframes) > 0
        # The blended position should be between the two animations
        assert blended_clip.keyframes[1].position[2] > 0.4  # Some Z movement from clip2
