"""
Standard animations for VRM avatars.

This module provides pre-defined animations for common movements like walking, dancing, etc.
"""
from typing import Dict, Any, List, Optional

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
            {"time": 0.0, "bone_name": "Head", "rotation": [0, 0, 0, 1]},
            
            # Shake left
            {"time": 0.25, "bone_name": "Head", "rotation": [0, 0.5, 0, 0.9]},
            
            # Shake right
            {"time": 0.5, "bone_name": "Head", "rotation": [0, -0.5, 0, 0.9]},
            
            # Shake left
            {"time": 0.75, "bone_name": "Head", "rotation": [0, 0.5, 0, 0.9]},
            
            # Return to center
            {"time": 1.0, "bone_name": "Head", "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Japanese Idol Dance (Kawaii Style)
    "idol_dance": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Start pose - V sign with right hand
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 0.9]},
            {"time": 0.0, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            {"time": 0.0, "bone_name": "RightHand", "rotation": [0, 0, 0.5, 0.9]},
            
            # Move hand to side
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0.3, 0.3, 0.3, 0.9]},
            
            # Switch to left hand V sign
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 1.0, "bone_name": "LeftShoulder", "rotation": [0, 0, -0.5, 0.9]},
            {"time": 1.0, "bone_name": "LeftHand", "rotation": [0, 0, -0.5, 0.9]},
            
            # Move left hand to side
            {"time": 1.5, "bone_name": "LeftShoulder", "rotation": [0.3, -0.3, -0.3, 0.9]},
            
            # Return to start
            {"time": 2.0, "bone_name": "LeftShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 2.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0.5, 0.9]}
        ]
    },
    
    # Breakdance Top Rock
    "breakdance_toprock": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Start pose - legs apart
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            {"time": 0.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0, -0.2, 1]},
            {"time": 0.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0.2, 1]},
            
            # Step right
            {"time": 0.5, "bone_name": "LeftUpperLeg", "rotation": [0, 0, -0.4, 1]},
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0.0, 1]},
            
            # Step left
            {"time": 1.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0, 0.0, 1]},
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0.4, 1]},
            
            # Cross step
            {"time": 1.5, "bone_name": "LeftUpperLeg", "rotation": [0, 0, 0.3, 1]},
            {"time": 1.5, "bone_name": "RightUpperLeg", "rotation": [0, 0, -0.3, 1]},
            
            # Return to start
            {"time": 2.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0, -0.2, 1]},
            {"time": 2.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0.2, 1]}
        ]
    },
    
    # K-Pop Style Dance
    "kpop_dance": {
        "duration": 3.0,
        "loop": True,
        "keyframes": [
            # Start pose - arms crossed
            {"time": 0.0, "bone_name": "LeftShoulder", "rotation": [0.5, 0, -0.3, 0.9]},
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0.5, 0, 0.3, 0.9]},
            
            # Open arms
            {"time": 1.0, "bone_name": "LeftShoulder", "rotation": [0.2, -0.5, -0.2, 0.9]},
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [0.2, 0.5, 0.2, 0.9]},
            
            # Point left
            {"time": 2.0, "bone_name": "LeftShoulder", "rotation": [0.1, -0.7, -0.1, 0.9]},
            {"time": 2.0, "bone_name": "LeftElbow", "rotation": [0, 0, 0, 1]},
            {"time": 2.0, "bone_name": "RightShoulder", "rotation": [0.1, 0.3, 0.1, 0.9]},
            
            # Point right
            {"time": 2.5, "bone_name": "RightShoulder", "rotation": [0.1, 0.7, 0.1, 0.9]},
            {"time": 2.5, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            {"time": 2.5, "bone_name": "LeftShoulder", "rotation": [0.1, -0.3, -0.1, 0.9]},
            
            # Return to start
            {"time": 3.0, "bone_name": "LeftShoulder", "rotation": [0.5, 0, -0.3, 0.9]},
            {"time": 3.0, "bone_name": "RightShoulder", "rotation": [0.5, 0, 0.3, 0.9]}
        ]
    },
    
    # Square Dance (Basic Do-Si-Do)
    "square_dance": {
        "duration": 4.0,
        "loop": True,
        "keyframes": [
            # Start position - partners facing
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Step to the right
            {"time": 1.0, "bone_name": "Hips", "position": [0.5, 0.9, 0], "rotation": [0, 0.2, 0, 1]},
            
            # Move behind partner (right shoulder to right shoulder)
            {"time": 2.0, "bone_name": "Hips", "position": [0.5, 0.9, 0.5], "rotation": [0, 1.57, 0, 1]},
            
            # Step to the left
            {"time": 3.0, "bone_name": "Hips", "position": [-0.5, 0.9, 0.5], "rotation": [0, 3.14, 0, 1]},
            
            # Return to start
            {"time": 4.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Waltz (Basic Box Step)
    "waltz": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Start position - right foot forward
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Step forward right
            {"time": 0.33, "bone_name": "Hips", "position": [0, 0.9, 0.3], "rotation": [0, 0, 0, 1]},
            
            # Step to side left
            {"time": 0.67, "bone_name": "Hips", "position": [0.3, 0.9, 0.3], "rotation": [0, 0, 0, 1]},
            
            # Close right foot to left
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.9, 0.3], "rotation": [0, 0, 0, 1]},
            
            # Step back left
            {"time": 1.33, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Step to side right
            {"time": 1.67, "bone_name": "Hips", "position": [-0.3, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Close left foot to right
            {"time": 2.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Minuet (Basic Steps)
    "minuet": {
        "duration": 3.0,
        "loop": True,
        "keyframes": [
            # Start position - first position
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Right foot point forward
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [0, 0.3, 0, 1]},
            
            # Right foot to side
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0.3, 1]},
            
            # Right foot point back
            {"time": 1.5, "bone_name": "RightUpperLeg", "rotation": [0, -0.3, 0, 1]},
            
            # Right foot return to first position
            {"time": 2.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]},
            
            # Bow/curtsey
            {"time": 2.5, "bone_name": "Hips", "position": [0, 0.8, 0], "rotation": [0.2, 0, 0, 1]},
            
            # Return to start
            {"time": 3.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Tango (Basic 8-Count Basic)
    "tango": {
        "duration": 4.0,
        "loop": True,
        "keyframes": [
            # Start position - closed position
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Step forward left (slow)
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.9, 0.4], "rotation": [0, 0, 0, 1]},
            
            # Step forward right (slow)
            {"time": 2.0, "bone_name": "Hips", "position": [0, 0.9, 0.8], "rotation": [0, 0, 0, 1]},
            
            # Step left (quick)
            {"time": 2.33, "bone_name": "Hips", "position": [0.4, 0.9, 0.8], "rotation": [0, 0.2, 0, 1]},
            
            # Close right to left (quick)
            {"time": 2.66, "bone_name": "Hips", "position": [0, 0.9, 0.8], "rotation": [0, 0, 0, 1]},
            
            # Step back right (slow)
            {"time": 3.0, "bone_name": "Hips", "position": [0, 0.9, 0.4], "rotation": [0, 0, 0, 1]},
            
            # Step right (quick)
            {"time": 3.33, "bone_name": "Hips", "position": [-0.4, 0.9, 0.4], "rotation": [0, -0.2, 0, 1]},
            
            # Close left to right (quick)
            {"time": 3.66, "bone_name": "Hips", "position": [0, 0.9, 0.4], "rotation": [0, 0, 0, 1]},
            
            # Return to start
            {"time": 4.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Ballet - Basic Plié and Relevé
    "ballet_basic": {
        "duration": 3.0,
        "loop": True,
        "keyframes": [
            # First position - heels together, toes out
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            {"time": 0.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0.3, 0, 1]},
            {"time": 0.0, "bone_name": "RightUpperLeg", "rotation": [0, -0.3, 0, 1]},
            
            # Demi-plié (half bend)
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.8, 0], "rotation": [0.2, 0, 0, 1]},
            
            # Relevé (rise on toes)
            {"time": 2.0, "bone_name": "Hips", "position": [0, 1.1, 0], "rotation": [0, 0, 0, 1]},
            
            # Return to first position
            {"time": 3.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Ballet - Arabesque
    "ballet_arabesque": {
        "duration": 4.0,
        "loop": True,
        "keyframes": [
            # Start position
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Lift right leg back
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [-0.8, 0, 0, 1]},
            {"time": 1.0, "bone_name": "RightLowerLeg", "rotation": [0, 0, 0, 1]},
            
            # Extend arms
            {"time": 1.5, "bone_name": "LeftShoulder", "rotation": [0, -0.5, -0.3, 0.9]},
            {"time": 1.5, "bone_name": "RightShoulder", "rotation": [0, 0.5, 0.3, 0.9]},
            
            # Hold
            {"time": 3.0, "bone_name": "RightUpperLeg", "rotation": [-0.6, 0, 0, 1]},
            
            # Return to start
            {"time": 4.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]},
            {"time": 4.0, "bone_name": "LeftShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 4.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Alpine (Schuhplattler) - Traditional Bavarian Dance
    "alpine_schuhplattler": {
        "duration": 3.0,
        "loop": True,
        "keyframes": [
            # Start position - arms up
            {"time": 0.0, "bone_name": "LeftShoulder", "rotation": [0, -0.5, -0.5, 0.9]},
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0, 0.5, 0.5, 0.9]},
            
            # Slap thighs
            {"time": 0.5, "bone_name": "LeftShoulder", "rotation": [0.5, -0.2, -0.2, 0.9]},
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0.5, 0.2, 0.2, 0.9]},
            
            # Jump and click heels
            {"time": 1.0, "bone_name": "Hips", "position": [0, 1.1, 0], "rotation": [0, 0, 0, 1]},
            {"time": 1.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0.5, 0, 1]},
            {"time": 1.0, "bone_name": "RightUpperLeg", "rotation": [0, -0.5, 0, 1]},
            
            # Land
            {"time": 1.2, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Arm circles
            {"time": 2.0, "bone_name": "LeftShoulder", "rotation": [0.2, -0.7, -0.2, 0.9]},
            {"time": 2.0, "bone_name": "RightShoulder", "rotation": [0.2, 0.7, 0.2, 0.9]},
            
            # Return to start
            {"time": 3.0, "bone_name": "LeftShoulder", "rotation": [0, -0.5, -0.5, 0.9]},
            {"time": 3.0, "bone_name": "RightShoulder", "rotation": [0, 0.5, 0.5, 0.9]}
        ]
    },
    
    # Irish Dance - Basic Step
    "irish_step": {
        "duration": 1.5,
        "loop": True,
        "keyframes": [
            # Start position - arms at sides
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Lift right leg with pointed toe
            {"time": 0.25, "bone_name": "RightUpperLeg", "rotation": [0, 0.3, 0, 1]},
            {"time": 0.25, "bone_name": "RightLowerLeg", "rotation": [-0.5, 0, 0, 1]},
            
            # Stomp right foot
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]},
            
            # Hop on right foot, lift left leg
            {"time": 0.75, "bone_name": "Hips", "position": [0, 1.0, 0]},
            {"time": 0.75, "bone_name": "LeftUpperLeg", "rotation": [0, -0.3, 0, 1]},
            {"time": 0.75, "bone_name": "LeftLowerLeg", "rotation": [-0.5, 0, 0, 1]},
            
            # Stomp left foot
            {"time": 1.0, "bone_name": "Hips", "position": [0, 0.9, 0]},
            {"time": 1.0, "bone_name": "LeftUpperLeg", "rotation": [0, 0, 0, 1]},
            
            # Quick steps
            {"time": 1.25, "bone_name": "Hips", "position": [0.2, 0.9, 0]},
            {"time": 1.5, "bone_name": "Hips", "position": [0, 0.9, 0]}
        ]
    },
    
    # Irish Dance - Céilí (group dance) move
    "irish_ceili": {
        "duration": 4.0,
        "loop": True,
        "keyframes": [
            # Start position - hold hands in circle
            {"time": 0.0, "bone_name": "LeftShoulder", "rotation": [0.2, -0.3, -0.2, 0.9]},
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0.2, 0.3, 0.2, 0.9]},
            
            # Side step right
            {"time": 1.0, "bone_name": "Hips", "position": [0.5, 0.9, 0], "rotation": [0, 0.2, 0, 1]},
            
            # Side step left
            {"time": 2.0, "bone_name": "Hips", "position": [-0.5, 0.9, 0], "rotation": [0, -0.2, 0, 1]},
            
            # Turn in circle
            {"time": 3.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 3.14, 0, 1]},
            
            # Return to start
            {"time": 4.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Japanese Sword (Katana) - Basic Stance (Kamae)
    "kenjutsu_kamae": {
        "duration": 2.0,
        "loop": False,
        "keyframes": [
            # Start in natural stance
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Right hand grip (as if holding a sword)
            {"time": 0.5, "bone_name": "RightHand", "rotation": [0, 0, 0.5, 0.9]},
            
            # Left hand supporting the blade
            {"time": 1.0, "bone_name": "LeftShoulder", "rotation": [0, -0.3, -0.2, 0.9]},
            
            # Final kamae position
            {"time": 2.0, "bone_name": "RightShoulder", "rotation": [0.3, 0.5, 0.2, 0.9]},
            {"time": 2.0, "bone_name": "LeftElbow", "rotation": [-0.2, 0, 0, 1]}
        ]
    },
    
    # Kenjutsu - Basic Cut (Shomen Uchi)
    "kenjutsu_shomen": {
        "duration": 1.5,
        "loop": True,
        "keyframes": [
            # Starting position (jodan no kamae)
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0.5, 0.5, 0.3, 0.9]},
            {"time": 0.0, "bone_name": "RightElbow", "rotation": [0, 0, 0, 1]},
            
            # Begin cut
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0.2, 0.2, 0.1, 0.9]},
            
            # Complete cut
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [-0.2, -0.1, -0.1, 0.9]},
            
            # Return to position
            {"time": 1.5, "bone_name": "RightShoulder", "rotation": [0.5, 0.5, 0.3, 0.9]}
        ]
    },
    
    # Kenjutsu - Side Cut (Yoko Giri)
    "kenjutsu_yoko": {
        "duration": 1.5,
        "loop": True,
        "keyframes": [
            # Starting position (chudan no kamae)
            {"time": 0.0, "bone_name": "RightShoulder", "rotation": [0.2, 0.3, 0.2, 0.9]},
            {"time": 0.0, "bone_name": "LeftShoulder", "rotation": [0.2, -0.2, -0.2, 0.9]},
            
            # Draw sword to side
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0.1, 0.5, 0.5, 0.9]},
            
            # Execute side cut
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [0.1, -0.3, 0.2, 0.9]},
            
            # Return to position
            {"time": 1.5, "bone_name": "RightShoulder", "rotation": [0.2, 0.3, 0.2, 0.9]}
        ]
    },
    
    # Karate - Basic Punch (Oi Zuki)
    "karate_oi_zuki": {
        "duration": 1.0,
        "loop": True,
        "keyframes": [
            # Ready stance (zenkutsu dachi)
            {"time": 0.0, "bone_name": "RightUpperLeg", "rotation": [0, 0.3, 0, 1]},
            {"time": 0.0, "bone_name": "LeftUpperLeg", "rotation": [0, -0.3, 0, 1]},
            
            # Chamber right hand
            {"time": 0.2, "bone_name": "RightShoulder", "rotation": [0.1, -0.2, 0.1, 0.9]},
            
            # Extend punch
            {"time": 0.5, "bone_name": "RightShoulder", "rotation": [0.1, 0.3, 0.1, 0.9]},
            
            # Return to chamber
            {"time": 0.8, "bone_name": "RightShoulder", "rotation": [0.1, -0.2, 0.1, 0.9]},
            
            # Return to stance
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Karate - Front Kick (Mae Geri)
    "karate_mae_geri": {
        "duration": 1.5,
        "loop": True,
        "keyframes": [
            # Ready stance
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Chamber kick
            {"time": 0.3, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0, 1]},
            
            # Extend kick
            {"time": 0.6, "bone_name": "RightLowerLeg", "rotation": [-0.8, 0, 0, 1]},
            
            # Rechamber
            {"time": 0.9, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0, 1]},
            
            # Return to stance
            {"time": 1.2, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]},
            {"time": 1.5, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Kung Fu - Tiger Claw
    "kungfu_tiger_claw": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Starting stance
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Prepare claw
            {"time": 0.5, "bone_name": "RightWrist", "rotation": [0, 0, 0.5, 0.9]},
            {"time": 0.5, "bone_name": "RightHand", "rotation": [0.5, 0, 0, 0.9]},
            
            # Strike forward
            {"time": 1.0, "bone_name": "RightShoulder", "rotation": [0.2, 0.3, 0.1, 0.9]},
            
            # Pull back
            {"time": 1.5, "bone_name": "RightShoulder", "rotation": [0.2, -0.1, 0.1, 0.9]},
            
            # Return to stance
            {"time": 2.0, "bone_name": "RightShoulder", "rotation": [0, 0, 0, 1]},
            {"time": 2.0, "bone_name": "RightWrist", "rotation": [0, 0, 0, 1]},
            {"time": 2.0, "bone_name": "RightHand", "rotation": [0, 0, 0, 1]}
        ]
    },
    
    # Taekwondo - Side Kick (Yop Chagi)
    "taekwondo_side_kick": {
        "duration": 2.0,
        "loop": True,
        "keyframes": [
            # Ready stance
            {"time": 0.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            
            # Chamber kick
            {"time": 0.5, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0.5, 1]},
            
            # Extend kick
            {"time": 1.0, "bone_name": "RightLowerLeg", "rotation": [-0.5, 0, 0, 1]},
            
            # Hold extension
            {"time": 1.2, "bone_name": "Hips", "rotation": [0, 0.2, 0, 1]},
            
            # Rechamber
            {"time": 1.5, "bone_name": "RightUpperLeg", "rotation": [0.5, 0, 0.5, 1]},
            
            # Return to stance
            {"time": 2.0, "bone_name": "Hips", "position": [0, 0.9, 0], "rotation": [0, 0, 0, 1]},
            {"time": 2.0, "bone_name": "RightUpperLeg", "rotation": [0, 0, 0, 1]}
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
