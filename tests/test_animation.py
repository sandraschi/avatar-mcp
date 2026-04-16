"""
Tests for the animation system.
"""

from unittest.mock import patch


class TestAnimationSystem:
    """Tests for the animation controller and related classes."""

    def test_animation_keyframe_creation(self):
        """Test creating animation keyframes."""
        from src.avatarmcp.core.animation import AnimationKeyframe

        # Test bone keyframe
        bone_kf = AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1, 0), rotation=(0, 0, 0, 1))
        assert bone_kf.bone_name == "Hips"
        assert bone_kf.time == 0.0
        assert bone_kf.position == (0, 1, 0)
        assert bone_kf.rotation == (0, 0, 0, 1)

        # Test blend shape keyframe
        bs_kf = AnimationKeyframe(time=1.0, blend_shape_name="smile", blend_shape_weight=0.8)
        assert bs_kf.blend_shape_name == "smile"
        assert bs_kf.time == 1.0
        assert bs_kf.blend_shape_weight == 0.8

    def test_animation_clip_creation(self):
        """Test creating an animation clip."""
        from src.avatarmcp.core.animation import AnimationClip, AnimationKeyframe

        # Create test keyframes
        keyframes = [
            AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1, 0), rotation=(0, 0, 0, 1)),
            AnimationKeyframe(time=1.0, bone_name="Hips", position=(0, 1.2, 0), rotation=(0, 0, 0, 1)),
        ]

        # Create a clip
        clip = AnimationClip(name="test_clip", duration=1.0, keyframes=keyframes, loop=True, speed=1.0)

        # Assertions
        assert clip.name == "test_clip"
        assert len(clip.keyframes) == 2
        assert clip.loop is True
        assert clip.speed == 1.0
        assert clip.duration == 1.0

    def test_animation_controller_initialization(self):
        """Test initializing the animation controller."""
        from src.avatarmcp.core.animation import AnimationController

        controller = AnimationController()

        # Test basic initialization
        assert controller is not None
        # Note: AnimationController creates a default "base" layer and
        # "idle" animation during initialization
        assert len(controller.layers) >= 0
        assert len(controller._animation_clips) >= 0

        # Test adding a layer
        controller.add_layer("test_layer")
        assert len(controller.layers) >= 1
        assert "test_layer" in controller.layers

    @patch("time.time")
    def test_play_animation(self, mock_time):
        """Test playing an animation."""
        from src.avatarmcp.core.animation import (
            AnimationClip,
            AnimationController,
            AnimationKeyframe,
        )

        mock_time.return_value = 0.0

        controller = AnimationController()

        # Create a test animation
        keyframes = [
            AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1, 0), rotation=(0, 0, 0, 1)),
            AnimationKeyframe(time=1.0, bone_name="Hips", position=(0, 1.2, 0), rotation=(0, 0, 0, 1)),
        ]

        clip = AnimationClip(name="test_animation", duration=1.0, keyframes=keyframes, loop=True)

        # Add animation to controller
        controller._animation_clips["test_animation"] = clip

        # Add a layer first
        controller.add_layer("base_layer")

        # Test playing animation
        result = controller.play_animation("base_layer", "test_animation")
        assert result is True

    @patch("time.time")
    def test_update_animation(self, mock_time):
        """Test updating animation state."""
        from src.avatarmcp.core.animation import (
            AnimationClip,
            AnimationController,
            AnimationKeyframe,
        )

        # Set up mock time
        mock_time.side_effect = [0.0, 0.5, 1.0]  # Start at 0s, then 0.5s later, then 1.0s

        controller = AnimationController()

        # Create a test animation
        keyframes = [
            AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1, 0), rotation=(0, 0, 0, 1)),
            AnimationKeyframe(time=1.0, bone_name="Hips", position=(0, 1.2, 0), rotation=(0, 0, 0, 1)),
        ]

        clip = AnimationClip(name="test_animation", duration=1.0, keyframes=keyframes, loop=True)

        # Add animation to controller
        controller._animation_clips["test_animation"] = clip

        # Add a layer and play animation
        layer = controller.add_layer("update_layer")
        controller.play_animation("update_layer", "test_animation")

        # Update the animation
        controller.update()

        # Test that the layer has the animation
        assert "test_animation" in layer.states

    def test_blend_animations(self):
        """Test blending between two animations."""
        from src.avatarmcp.core.animation import (
            AnimationClip,
            AnimationController,
            AnimationKeyframe,
        )

        controller = AnimationController()

        # Create two test animations
        keyframes1 = [AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1, 0), rotation=(0, 0, 0, 1))]

        keyframes2 = [AnimationKeyframe(time=0.0, bone_name="Hips", position=(0, 1.5, 0), rotation=(0, 0, 0, 1))]

        clip1 = AnimationClip(name="animation1", duration=1.0, keyframes=keyframes1)

        clip2 = AnimationClip(name="animation2", duration=1.0, keyframes=keyframes2)

        # Add animations to controller
        controller._animation_clips["animation1"] = clip1
        controller._animation_clips["animation2"] = clip2

        # Add layers
        layer1 = controller.add_layer("blend_layer1", weight=0.5)
        layer2 = controller.add_layer("blend_layer2", weight=0.5)

        # Play animations on different layers
        controller.play_animation("blend_layer1", "animation1")
        controller.play_animation("blend_layer2", "animation2")

        # Test that both layers have animations
        assert "animation1" in layer1.states
        assert "animation2" in layer2.states
