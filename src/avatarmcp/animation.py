"""
Animation System for VRM Models

This module provides functionality for loading, playing, and blending animations
for VRM avatar models.
"""
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
import time
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AnimationKeyframe:
    """Represents a single keyframe in an animation."""
    time: float
    bone_name: str
    rotation: Optional[Tuple[float, float, float, float]] = None  # quaternion (x, y, z, w)
    position: Optional[Tuple[float, float, float]] = None
    scale: Optional[Tuple[float, float, float]] = None
    blend_shape_name: Optional[str] = None
    blend_shape_weight: Optional[float] = None

@dataclass
class AnimationClip:
    """Represents an animation clip with multiple keyframes."""
    name: str
    duration: float
    keyframes: List[AnimationKeyframe] = field(default_factory=list)
    loop: bool = False
    speed: float = 1.0

class AnimationController:
    """
    Controls animation playback for VRM avatars.
    
    This class handles loading animation clips, managing their playback state,
    and applying the animations to avatar poses.
    """
    
    def __init__(self):
        """Initialize the AnimationController."""
        self.animations: Dict[str, AnimationClip] = {}
        self.active_animations: Dict[str, Dict] = {}  # animation_name -> {start_time, weight, loop, speed}
        self.last_update_time = time.time()
        
        # Load default animations
        self._load_default_animations()
    
    def load_animation(self, name: str, file_path: str) -> bool:
        """
        Load an animation from a file.
        
        Args:
            name: Name to give the animation
            file_path: Path to the animation file (JSON)
            
        Returns:
            bool: True if the animation was loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Create animation clip
            clip = AnimationClip(
                name=name,
                duration=data.get('duration', 1.0),
                loop=data.get('loop', False)
            )
            
            # Add keyframes
            for kf_data in data.get('keyframes', []):
                keyframe = AnimationKeyframe(
                    time=kf_data.get('time', 0.0),
                    bone_name=kf_data.get('bone_name', '')
                )
                
                if 'rotation' in kf_data:
                    keyframe.rotation = tuple(kf_data['rotation'])
                if 'position' in kf_data:
                    keyframe.position = tuple(kf_data['position'])
                if 'scale' in kf_data:
                    keyframe.scale = tuple(kf_data['scale'])
                if 'blend_shape_name' in kf_data:
                    keyframe.blend_shape_name = kf_data['blend_shape_name']
                    keyframe.blend_shape_weight = kf_data.get('blend_shape_weight', 1.0)
                
                clip.keyframes.append(keyframe)
            
            # Sort keyframes by time
            clip.keyframes.sort(key=lambda kf: kf.time)
            
            self.animations[name] = clip
            logger.info(f"Loaded animation '{name}' from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load animation from {file_path}: {str(e)}")
            return False
    
    def play_animation(self, name: str, weight: float = 1.0, loop: bool = False, speed: float = 1.0) -> bool:
        """
        Start playing an animation.
        
        Args:
            name: Name of the animation to play
            weight: Blend weight (0.0 to 1.0)
            loop: Whether to loop the animation
            speed: Playback speed multiplier
            
        Returns:
            bool: True if the animation was started, False if not found
        """
        if name not in self.animations:
            logger.warning(f"Animation not found: {name}")
            return False
            
        self.active_animations[name] = {
            'start_time': time.time(),
            'weight': max(0.0, min(1.0, weight)),
            'loop': loop,
            'speed': max(0.01, speed)  # Prevent division by zero
        }
        
        logger.info(f"Playing animation '{name}' (weight={weight}, loop={loop}, speed={speed})")
        return True
    
    def stop_animation(self, name: str) -> bool:
        """
        Stop playing an animation.
        
        Args:
            name: Name of the animation to stop
            
        Returns:
            bool: True if the animation was stopped, False if not found
        """
        if name in self.active_animations:
            del self.active_animations[name]
            logger.info(f"Stopped animation '{name}'")
            return True
        return False
    
    def stop_all_animations(self) -> None:
        """Stop all currently playing animations."""
        self.active_animations.clear()
        logger.info("Stopped all animations")
    
    def get_pose(self, current_time: Optional[float] = None) -> Tuple[Dict, Dict]:
        """
        Get the current pose based on active animations.
        
        Args:
            current_time: Current time in seconds. If None, uses system time.
            
        Returns:
            Tuple containing:
                - bone_poses: Dict mapping bone names to (rotation, position, scale) tuples
                - blend_shapes: Dict mapping blend shape names to weights
        """
        if current_time is None:
            current_time = time.time()
            
        bone_poses = {}
        blend_shapes = {}
        
        # Process each active animation
        for anim_name, anim_state in list(self.active_animations.items()):
            if anim_name not in self.animations:
                continue
                
            clip = self.animations[anim_name]
            weight = anim_state['weight']
            speed = anim_state['speed']
            anim_time = (current_time - anim_state['start_time']) * speed
            
            # Handle looping
            if clip.loop or anim_state['loop']:
                anim_time = anim_time % clip.duration
            elif anim_time >= clip.duration:
                # Animation has finished and doesn't loop
                del self.active_animations[anim_name]
                continue
                
            # Get the current frame and next frame for interpolation
            prev_kf, next_kf = self._get_surrounding_keyframes(clip, anim_time)
            
            if prev_kf is None or next_kf is None:
                continue
                
            # Calculate interpolation factor (0 to 1)
            if prev_kf.time == next_kf.time:
                t = 0.0
            else:
                t = (anim_time - prev_kf.time) / (next_kf.time - prev_kf.time)
            t = max(0.0, min(1.0, t))  # Clamp to [0, 1]
            
            # Apply this animation's pose with its weight
            self._apply_keyframe(prev_kf, next_kf, t, weight, bone_poses, blend_shapes)
        
        return bone_poses, blend_shapes
    
    def _get_surrounding_keyframes(self, clip: AnimationClip, time: float) -> Tuple[Optional[AnimationKeyframe], Optional[AnimationKeyframe]]:
        """
        Get the keyframes that surround the specified time.
        
        Args:
            clip: The animation clip to search in
            time: Current time in the animation
            
        Returns:
            Tuple of (previous_keyframe, next_keyframe). Either may be None.
        """
        if not clip.keyframes:
            return None, None
            
        # Find the two keyframes that surround the current time
        prev_kf = None
        next_kf = None
        
        for kf in clip.keyframes:
            if kf.time <= time:
                if prev_kf is None or kf.time > prev_kf.time:
                    prev_kf = kf
            if kf.time >= time:
                if next_kf is None or kf.time < next_kf.time:
                    next_kf = kf
        
        # If we didn't find a next keyframe, use the last one
        if next_kf is None and prev_kf is not None:
            next_kf = prev_kf
        # If we didn't find a previous keyframe, use the first one
        elif prev_kf is None and next_kf is not None:
            prev_kf = next_kf
            
        return prev_kf, next_kf
    
    def _apply_keyframe(self, prev_kf: AnimationKeyframe, next_kf: AnimationKeyframe,
                       t: float, weight: float,
                       bone_poses: Dict, blend_shapes: Dict) -> None:
        """
        Apply a keyframe to the current pose with interpolation.
        
        Args:
            prev_kf: Previous keyframe
            next_kf: Next keyframe
            t: Interpolation factor (0 to 1)
            weight: Blend weight (0 to 1)
            bone_poses: Dict to store bone poses
            blend_shapes: Dict to store blend shape weights
        """
        # Handle bone transforms
        if prev_kf.bone_name and prev_kf.rotation and next_kf.rotation:
            # Slerp between rotations
            rot1 = np.array(prev_kf.rotation, dtype=np.float32)
            rot2 = np.array(next_kf.rotation, dtype=np.float32)
            
            # Normalize quaternions
            rot1 = rot1 / np.linalg.norm(rot1)
            rot2 = rot2 / np.linalg.norm(rot2)
            
            # Slerp
            dot = np.dot(rot1, rot2)
            dot = np.clip(dot, -1.0, 1.0)  # Clamp for numerical stability
            
            # If the dot product is negative, the quaternions are more than 90 degrees apart,
            # so we need to negate one to take the shorter path
            if dot < 0.0:
                rot2 = -rot2
                dot = -dot
                
            # If the quaternions are very close, use linear interpolation
            if dot > 0.9995:
                result = rot1 + t * (rot2 - rot1)
            else:
                # Calculate the angle between the quaternions
                theta_0 = np.arccos(dot)
                theta = theta_0 * t
                
                # Compute the interpolation coefficients
                s1 = np.cos(theta) - dot * np.sin(theta) / np.sin(theta_0)
                s2 = np.sin(theta) / np.sin(theta_0)
                
                # Interpolate
                result = s1 * rot1 + s2 * rot2
            
            # Normalize the result
            result = result / np.linalg.norm(result)
            
            # Apply weight
            if prev_kf.bone_name in bone_poses:
                # Blend with existing pose
                existing_rot, existing_pos, existing_scale = bone_poses[prev_kf.bone_name]
                blended_rot = self._blend_quaternions(existing_rot, result, weight)
                bone_poses[prev_kf.bone_name] = (blended_rot, existing_pos, existing_scale)
            else:
                # New pose
                bone_poses[prev_kf.bone_name] = (result, None, None)
        
        # Handle blend shapes
        if prev_kf.blend_shape_name and prev_kf.blend_shape_weight is not None:
            # Simple linear interpolation for blend shapes
            weight1 = prev_kf.blend_shape_weight
            weight2 = next_kf.blend_shape_weight if next_kf.blend_shape_name == prev_kf.blend_shape_name else 0.0
            
            value = weight1 + t * (weight2 - weight1)
            
            # Apply weight and blend with existing value
            if prev_kf.blend_shape_name in blend_shapes:
                blend_shapes[prev_kf.blend_shape_name] += value * weight
            else:
                blend_shapes[prev_kf.blend_shape_name] = value * weight
    
    def _blend_quaternions(self, q1: np.ndarray, q2: np.ndarray, t: float) -> np.ndarray:
        """
        Blend between two quaternions.
        
        Args:
            q1: First quaternion (w, x, y, z)
            q2: Second quaternion (w, x, y, z)
            t: Blend factor (0 = all q1, 1 = all q2)
            
        Returns:
            Blended quaternion
        """
        # Simple linear interpolation (nlerp) for now
        result = (1.0 - t) * q1 + t * q2
        return result / np.linalg.norm(result)
    
    def _load_default_animations(self) -> None:
        """Load default animations that are built into the system."""
        # This would load from a default animations file or define them in code
        # For now, we'll just create a simple idle animation
        
        # Create a simple idle animation
        idle_anim = AnimationClip(
            name="idle",
            duration=2.0,
            loop=True
        )
        
        # Add some subtle breathing motion
        idle_anim.keyframes.extend([
            AnimationKeyframe(time=0.0, bone_name="Hips", position=(0.0, 0.0, 0.0)),
            AnimationKeyframe(time=1.0, bone_name="Hips", position=(0.0, 0.02, 0.0)),
            AnimationKeyframe(time=2.0, bone_name="Hips", position=(0.0, 0.0, 0.0)),
            
            # Add some subtle head movement
            AnimationKeyframe(time=0.0, bone_name="Neck", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=1.0, bone_name="Neck", rotation=(0.02, 0.0, 0.0, 0.99)),
            AnimationKeyframe(time=2.0, bone_name="Neck", rotation=(0.0, 0.0, 0.0, 1.0)),
        ])
        
        self.animations["idle"] = idle_anim
        
        # Create a simple wave animation
        wave_anim = AnimationClip(
            name="wave",
            duration=1.5,
            loop=True
        )
        
        wave_anim.keyframes.extend([
            # Arm starts down
            AnimationKeyframe(time=0.0, bone_name="RightArm", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=0.0, bone_name="RightForeArm", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=0.0, bone_name="RightHand", rotation=(0.0, 0.0, 0.0, 1.0)),
            
            # Arm raises
            AnimationKeyframe(time=0.3, bone_name="RightArm", rotation=(0.0, 0.0, 0.7, 0.7)),
            AnimationKeyframe(time=0.3, bone_name="RightForeArm", rotation=(0.0, 0.0, 0.0, 1.0)),
            
            # Wave motion
            AnimationKeyframe(time=0.5, bone_name="RightHand", rotation=(0.0, 0.0, 0.7, 0.7)),
            AnimationKeyframe(time=0.7, bone_name="RightHand", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=0.9, bone_name="RightHand", rotation=(0.0, 0.0, 0.7, 0.7)),
            AnimationKeyframe(time=1.1, bone_name="RightHand", rotation=(0.0, 0.0, 0.0, 1.0)),
            
            # Return to rest
            AnimationKeyframe(time=1.5, bone_name="RightArm", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=1.5, bone_name="RightForeArm", rotation=(0.0, 0.0, 0.0, 1.0)),
            AnimationKeyframe(time=1.5, bone_name="RightHand", rotation=(0.0, 0.0, 0.0, 1.0)),
        ])
        
        self.animations["wave"] = wave_anim
