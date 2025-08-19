"""
Standard animations for VRM avatars.

This module provides pre-defined animations for common movements like walking, dancing, etc.
"""
from typing import Dict, Any, List, Tuple, Optional
import math

# Standard animation presets
ANIMATION_PRESETS = {
    # Basic movement
    "idle": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.91, 0]},
            {"time": 2.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
        ]
    },
    
    "walk": {
        "duration": 1.0,
        "loop": True,
        "keyframes": [
            # Neutral pose
            {"time": 0.0, "bone_name": "LeftUpperLeg", "rotation": [0.1, 0, 0, 1]},
            {"time": 0.0, "bone_name": "RightUpperLeg", "rotation": [-0.1, 0, 0, 1]},
            
            # Right foot forward
            {"time": 0.25, "bone_name": "LeftUpperLeg", "rotation": [-0.5, 0, 0, 1]},
            {"time": 0.25, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0, 1]},
            
            # Neutral
            {"time": 0.5, "bone_name": "LeftUpperLeg", "rotation": [0.1, 0, 0, 1]},
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [-0.1, 0, 0, 1]},
            
            # Left foot forward
            {"time": 0.75, "bone_name": "LeftUpperLeg", "rotation": [0.5, 0, 0, 1]},
            {"time": 0.75, "bone_name": "RightUpperLeg", "rotation": [-0.5, 0, 0, 1]},
        ]
    },
    
    "run": {
        "duration": 0.5,
        "loop": True,
        "keyframes": [
            # Neutral pose
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 0.0, "bone_name": "LeftUpperLeg", "rotation": [0.2, 0, 0, 1]},
            {"time": 0.0, "bone_name": "RightUpperLeg", "rotation": [-0.2, 0, 0, 1]},
            
            # Right foot forward
            {"time": 0.125, "bone_name": "Hips", "position": [0, 0.95, 0]},
            {"time": 0.125, "bone_name": "LeftUpperLeg", "rotation": [-0.8, 0, 0, 1]},
            {"time": 0.125, "bone_name": "RightUpperLeg", "rotation": [0.8, 0, 0, 1]},
            
            # Neutral
            {"time": 0.25, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 0.25, "bone_name": "LeftUpperLeg", "rotation": [0.2, 0, 0, 1]},
            {"time": 0.25, "bone_name": "RightUpperLeg", "rotation": [-0.2, 0, 0, 1]},
            
            # Left foot forward
            {"time": 0.375, "bone_name": "Hips", "position": [0, 0.95, 0]},
            {"time": 0.375, "bone_name": "LeftUpperLeg", "rotation": [0.8, 0, 0, 1]},
            {"time": 0.375, "bone_name": "RightUpperLeg", "rotation": [-0.8, 0, 0, 1]},
        ]
    },
    
    # Dance animations
    "dance1": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Arms up
            {"time": 0.0, "bone_name": "LeftUpperArm", "rotation": [0, 0, -0.7, 1]},
            {"time": 0.0, "bone_name": "RightUpperArm", "rotation": [0, 0, 0.7, 1]},
            
            # Arms to sides
            {"time": 1.0, "bone_name": "LeftUpperArm", "rotation": [0, 0, 0, 1]},
            {"time": 1.0, "bone_name": "RightUpperArm", "rotation": [0, 0, 0, 1]},
            
            # Hips sway
            {"time": 0.5, "bone_name": "Hips", "rotation": [0, 0, 0.2, 1]},
            {"time": 1.5, "bone_name": "Hips", "rotation": [0, 0, -0.2, 1]},
        ]
    },
    
    "pirouette": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Start position
            {"time": 0.0, "bone_name": "Hips", "rotation": [0, 0, 0, 1]},
            
            # Half turn
            {"time": 0.5, "bone_name": "Hips", "rotation": [0, 0.7, 0, 0.7]},  # 180 degrees
            
            # Full turn
            {"time": 1.0, "bone_name": "Hips", "rotation": [0, 1, 0, 0]},  # 360 degrees
            
            # Continue rotating
            {"time": 1.5, "bone_name": "Hips", "rotation": [0, 0.7, 0, -0.7]},  # 540 degrees
            
            # Back to start
            {"time": 2.0, "bone_name": "Hips", "rotation": [0, 0, 0, 1]},  # 720 degrees
        ]
    },
    
    # Gestures
    "wave": {
        "duration": 1.5,
        "loop": True,
        "keyframes": [
            # Start with hand down
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 0.0, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            
            # Wave up
            {"time": 0.25, "bone_name": "RightShoulder", "rotation": [0, 0, 0.7, 0.7]},
            {"time": 0.25, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            
            # Wave down
            {"time": 0.5, "bone_name": "RightElbow", "rotation": [0.5, 0, 0, 0.8]},
            
            # Wave up again
            {"time": 0.75, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            
            # Wave down again
            {"time": 1.0, "bone_name": "RightElbow", "rotation": [0.5, 0, 0, 0.8]},
            
            # Return to start
            {"time": 1.5, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 1.5, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
        ]
    },
    
    "jump": {
        "duration": 1.0,
        "loop": False,
        "keyframes": [
            # Start
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            
            # Crouch
            {"time": 0.2, "bone_name": "Hips", "position": [0, 0.8, 0]},
            {"time": 0.2, "bone_name": "LeftUpperLeg", "rotation": [0.5, 0, 0, 1]},
            {"time": 0.2, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0, 1]},
            
            # Jump up
            {"time": 0.4, "bone_name": "Hips", "position": [0, 1.5, 0]},
            {"time": 0.4, "bone_name": "LeftUpperLeg", "rotation": [-0.2, 0, 0, 1]},
            {"time": 0.4, "bone_name": "RightUpperLeg", "rotation": [-0.2, 0, 0, 1]},
            
            # Peak
            {"time": 0.5, "bone_name": "Hips", "position": [0, 1.6, 0]},
            
            # Land
            {"time": 0.8, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 0.8, "bone_name": "LeftUpperLeg", "rotation": [0.4, 0, 0, 1]},
            {"time": 0.8, "bone_name": "RightUpperLeg", "rotation": [0.4, 0, 0, 1]},
            
            # Recover
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 1.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0, 0, 1]},
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]},
        ]
    },
    
    "sit": {
        "duration": 1.0,
        "loop": False,
        "keyframes": [
            # Start standing
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Sit down
            {"time": 0.5, "bone_name": "Hips", "position": [0, 0.5, -0.2], "rotation": [0.3, 0, 0, 1]},
            {"time": 0.5, "bone_name": "LeftUpperLeg", "rotation": [0.8, 0, 0, 1]},
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [0.8, 0, 0, 1]},
            
            # Settle
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.4, -0.1], "rotation": [0.5, 0, 0, 1]},
            {"time": 1.0, "bone_name": "LeftUpperLeg", "rotation": [1.0, 0, 0, 1]},
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [1.0, 0, 0, 1]},
        ]
    },
    
    # New animations start here
    "happy_idle": {
        "duration": 3.0,
        "loop": True,
        "keyframes": [
            # Subtle happy bobbing
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            {"time": 1.5, "bone_name": "Hips", "position": [0, 0.91, 0.05], "rotation": [0.02, 0, 0, 1]},
            {"time": 3.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Slight arm swings
            {"time": 0.0, "bone_name": "LeftUpperArm", "rotation": [0, 0, -0.1, 1]},
            {"time": 0.0, "bone_name": "RightUpperArm", "rotation": [0, 0, 0.1, 1]},
            {"time": 1.5, "bone_name": "LeftUpperArm", "rotation": [0, 0, 0.1, 1]},
            {"time": 1.5, "bone_name": "RightUpperArm", "rotation": [0, 0, -0.1, 1]},
            {"time": 3.0, "bone_name": "LeftUpperArm", "rotation": [0, 0, -0.1, 1]},
            
            # Head tilt
            {"time": 1.5, "bone_name": "Neck", "rotation": [0, 0, 0.05, 1]},
        ]
    },
    
    "sad_idle": {
        "duration": 4.0,
        "loop": True,
        "keyframes": [
            # Slumped posture
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.88, -0.05], "rotation": [-0.1, 0, 0, 1]},
            {"time": 2.0, "bone_name": "Hips", "position": [0, 0.87, -0.06], "rotation": [-0.12, 0, 0, 1]},
            {"time": 4.0, "bone_name": "Hips", "position": [0, 0.88, -0.05], "rotation": [-0.1, 0, 0, 1]},
            
            # Drooping arms
            {"time": 0.0, "bone_name": "LeftUpperArm", "rotation": [0.2, 0, -0.2, 1]},
            {"time": 0.0, "bone_name": "RightUpperArm", "rotation": [0.2, 0, 0.2, 1]},
            
            # Head down
            {"time": 0.0, "bone_name": "Neck", "rotation": [-0.2, 0, 0, 1]},
        ]
    },
    
    "excited_jump": {
        "duration": 1.2,
        "loop": False,
        "keyframes": [
            # Start
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            
            # Crouch
            {"time": 0.2, "bone_name": "Hips", "position": [0, 0.8, 0]},
            {"time": 0.2, "bone_name": "LeftUpperLeg", "rotation": [0.5, 0, 0, 1]},
            {"time": 0.2, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0, 1]},
            
            # Jump up with excitement
            {"time": 0.4, "bone_name": "Hips", "position": [0, 1.6, 0]},
            {"time": 0.4, "bone_name": "LeftUpperArm", "rotation": [0, 0, -0.8, 1]},
            {"time": 0.4, "bone_name": "RightUpperArm", "rotation": [0, 0, 0.8, 1]},
            
            # Peak
            {"time": 0.5, "bone_name": "Hips", "position": [0, 1.7, 0]},
            
            # Land
            {"time": 0.8, "bone_name": "Hips", "position": [0, 0.9, 0]},
            
            # Bounce
            {"time": 0.9, "bone_name": "Hips", "position": [0, 0.85, 0]},
            
            # Final settle
            {"time": 1.2, "bone_name": "Hips", "position": [0, 0.9, 0]},
        ]
    },
    
    "point_forward": {
        "duration": 0.5,
        "loop": False,
        "keyframes": [
            # Start
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 0.0, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            
            # Point forward
            {"time": 0.3, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 0.8]},
            {"time": 0.3, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            {"time": 0.3, "bone_name": "RightHand", "rotation": [0, 0, 0, 1]},
            
            # Hold
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 0.8]},
        ]
    },
    
    "clap": {
        "duration": 0.8,
        "loop": True,
        "keyframes": [
            # Start with hands apart
            {"time": 0.0, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.5, 1]},
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 1]},
            
            # Clap
            {"time": 0.2, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.3, 1]},
            {"time": 0.2, "bone_name": "RightShoulder", "rotation": [0, 0, 0.3, 1]},
            
            # Back out
            {"time": 0.4, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.5, 1]},
            {"time": 0.4, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 1]},
            
            # Repeat
            {"time": 0.6, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.3, 1]},
            {"time": 0.6, "bone_name": "RightShoulder", "rotation": [0, 0, 0.3, 1]},
            
            # Final position
            {"time": 0.8, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.5, 1]},
            {"time": 0.8, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 1]},
        ]
    },
    
    "nod_yes": {
        "duration": 1.0,
        "loop": True,
        "keyframes": [
            # Start
            {"time": 0.0, "bone_name": "Neck", "rotation": [0, 0, 0, 1]},
            
            # Nod down
            {"time": 0.2, "bone_name": "Neck", "rotation": [0.3, 0, 0, 1]},
            
            # Back up
            {"time": 0.4, "bone_name": "Neck", "rotation": [0, 0, 0, 1]},
            
            # Second nod down
            {"time": 0.6, "bone_name": "Neck", "rotation": [0.2, 0, 0, 1]},
            
            # Final position
            {"time": 1.0, "bone_name": "Neck", "rotation": [0, 0, 0, 1]},
        ]
    },
    
    "shake_no": {
        "duration": 1.0,
        "loop": True,
        "keyframes": [
            # Start
            {"time": 0.0, "bone_name": "Neck", "rotation": [0, 0, 0, 1]},
            
            # Shake right
            {"time": 0.2, "bone_name": "Neck", "rotation": [0, 0.2, 0, 1]},
            
            # Shake left
            {"time": 0.4, "bone_name": "Neck", "rotation": [0, -0.2, 0, 1]},
            
            # Shake right again
            {"time": 0.6, "bone_name": "Neck", "rotation": [0, 0.15, 0, 1]},
            
            # Final position
            {"time": 1.0, "bone_name": "Neck", "rotation": [0, 0, 0, 1]},
        ]
    }
}

def get_standard_animation(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a standard animation preset by name.
    
    Args:
        name: Name of the standard animation (e.g., 'walk', 'dance1', 'jump')
        
    Returns:
        Animation data dictionary or None if not found
    """
    return ANIMATION_PRESETS.get(name)

def list_standard_animations() -> List[str]:
    """
    Get a list of all available standard animation names.
    
    Returns:
        List of animation names
    """
    return list(ANIMATION_PRESETS.keys())

def create_standard_animation(name: str, model_scale: float = 1.0) -> Dict[str, Any]:
    """
    Create a standard animation with optional scaling.
    
    Args:
        name: Name of the standard animation
        model_scale: Scale factor to apply to positions
        
    Returns:
        Animation data dictionary with scaled positions
    """
    anim = ANIMATION_PRESETS.get(name)
    if not anim:
        return None
        
    # Create a deep copy to avoid modifying the original
    import copy
    result = copy.deepcopy(anim)
    
    # Scale positions if needed
    if model_scale != 1.0:
        for kf in result["keyframes"]:
            if "position" in kf:
                kf["position"] = [x * model_scale for x in kf["position"]]
    
    return result
