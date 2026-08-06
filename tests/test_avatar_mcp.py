"""
Tests for the VRM model and animation controller classes.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.avatarmcp.models.animation_controller import AnimationController
from src.avatarmcp.models.vrm_model import VRMModel


class TestAvatarMCP(unittest.TestCase):
    """Test cases for the AvatarMCP application setup."""

    def setUp(self):
        self.app = MagicMock()
        self.app.mcp = MagicMock()

    def test_create_app(self):
        self.assertIsNotNone(self.app)
        self.assertIsNotNone(self.app.mcp)


class TestVRMModel(unittest.TestCase):
    """Test cases for the VRMModel class."""

    @patch("src.avatarmcp.models.vrm_model.GLTF2")
    def test_load_vrm(self, mock_gltf_cls):
        mock_gltf = MagicMock()
        mock_gltf_cls.return_value = mock_gltf
        mock_gltf_instance = MagicMock()
        mock_gltf.load.return_value = mock_gltf_instance
        mock_gltf_instance.extensions = {
            "VRM": {
                "meta": {"title": "Test Model", "version": "1.0", "author": "Tester"},
                "blendShapeMaster": {
                    "blendShapeGroups": [
                        {"name": "A", "presetName": "joy", "binds": [{"mesh": 0, "index": 0, "weight": 100}]}
                    ]
                },
            }
        }
        mock_gltf_instance.nodes = [MagicMock(), MagicMock()]
        mock_gltf_instance.nodes[0].name = "Hips"
        mock_gltf_instance.nodes[1].name = "Spine"

        model = VRMModel("test.vrm")

        self.assertEqual(model.metadata.get("name"), "Test Model")
        self.assertEqual(len(model.get_bone_names()), 2)
        self.assertEqual(len(model.get_blend_shape_names()), 1)

    @patch("src.avatarmcp.models.vrm_model.GLTF2")
    def test_to_dict(self, mock_gltf_cls):
        mock_gltf = MagicMock()
        mock_gltf_cls.return_value = mock_gltf
        mock_instance = MagicMock()
        mock_instance.extensions = {}
        mock_instance.nodes = []
        mock_gltf.load.return_value = mock_instance

        model = VRMModel("test.vrm")
        d = model.to_dict()
        self.assertIn("model_id", d)
        self.assertIn("file_path", d)
        self.assertEqual(d["file_path"], "test.vrm")


class TestAnimationController(unittest.TestCase):
    """Test cases for the AnimationController class."""

    def setUp(self):
        self.controller = AnimationController()

    def test_play_animation(self):
        result = self.controller.play_animation(animation_name="test_anim", loop=True, weight=1.0, speed=1.0)
        self.assertEqual(result["status"], "success")
        self.assertIn("test_anim", self.controller.active_animations)

    def test_stop_animation(self):
        self.controller.play_animation("test_anim")
        result = self.controller.stop_animation("test_anim")
        self.assertEqual(result["status"], "success")
        self.assertNotIn("test_anim", self.controller.active_animations)

    def test_update_animation(self):
        self.controller.play_animation("test_anim", loop=True)
        self.controller.update(0.5)
        anim = self.controller.active_animations["test_anim"]
        self.assertGreater(anim.get("elapsed", 0), 0)

    def test_get_active_animations(self):
        self.controller.play_animation("a1", loop=True, weight=0.8)
        self.controller.play_animation("a2", loop=False, weight=0.5)
        active = self.controller.get_active_animations()
        self.assertEqual(len(active), 2)

    def test_clear(self):
        self.controller.play_animation("a1")
        self.controller.clear()
        self.assertEqual(len(self.controller.active_animations), 0)

    def test_stop_with_fade_out(self):
        self.controller.play_animation("test_anim")
        self.controller.stop_animation("test_anim", fade_out=1.0)
        anim = self.controller.active_animations["test_anim"]
        self.assertIn("fade_out", anim)
        self.assertEqual(anim["fade_out"]["duration"], 1.0)

    @patch("time.time")
    def test_fade_out_completion(self, mock_time):
        mock_time.return_value = 1000.0
        self.controller.play_animation("test_anim")
        self.controller.stop_animation("test_anim", fade_out=0.5)
        self.assertIn("test_anim", self.controller.active_animations)
        mock_time.return_value = 1001.0
        self.controller.update(1.0)
        self.assertNotIn("test_anim", self.controller.active_animations)


if __name__ == "__main__":
    unittest.main()
