# Enhanced Animation System

This document describes the advanced animation system in AvatarMCP, which provides powerful animation capabilities for VRM models.

## Features

- **Animation Layering**: Combine multiple animations on different layers (e.g., body, face, upper body)
- **Blending Modes**: Different blending options (Override, Additive, etc.)
- **Animation Events**: Trigger actions at specific points in an animation
- **State Management**: Smooth transitions between animation states
- **Performance Optimization**: Efficient keyframe interpolation and pose calculation
- **Event System**: Respond to animation events in real-time

## VRM Animation Integration

The animation system now fully integrates with VRM models through the following implementation:

### VRM Model Loading

VRM models are loaded using the `VRMLoader` class, which extracts:
- Bone hierarchy and transforms
- Blend shape definitions
- Animation clips
- Material properties

```python
# Loading a VRM model
from avatarmcp.vrm_loader import VRMLoader

vrm_model = VRMLoader.from_file("path/to/model.vrm")
```

### Animation Types

The system supports three types of animations:

1. **VRM Animations** - Native animations embedded in the VRM file
2. **Standard Animations** - Built-in animations (idle, walk, etc.)
3. **Custom Animations** - User-defined animations in JSON format

### Animation Control

```python
# Play a VRM animation
play_animation(
    model_id="model_1",
    animation_name="vrm_animation_name",
    loop=True,
    weight=1.0,
    speed=1.0
)

# Stop an animation
stop_animation(
    model_id="model_1",
    animation_name="vrm_animation_name",
    fade_out=0.5  # Optional fade out in seconds
)
```

### Blend Shape Control

```python
# List available blend shapes
blend_shapes = list_blend_shapes("model_1")

# Set blend shape weight
set_blend_shape(
    model_id="model_1",
    blend_shape_name="Blink_L",
    weight=1.0  # 0.0 to 1.0
)
```

### Bone Control

```python
# List bones and their hierarchy
bones = list_bones("model_1")

# Set bone transform directly
set_bone_transform(
    model_id="model_1",
    bone_name="Head",
    rotation=(x, y, z, w),  # Quaternion
    position=(x, y, z),     # Optional position
    scale=(x, y, z)         # Optional scale
)
```

### Testing

Use the test script to verify VRM animation functionality:

```bash
python examples/test_animation.py path/to/your/model.vrm
```

## Core Components

### AnimationController

The main class that manages all animations and layers.

```python
from avatarmcp.animation_v2 import AnimationController

# Create a controller
controller = AnimationController()

# Add animation layers
base_layer = controller.add_layer("base", weight=1.0)
upper_body_layer = controller.add_layer("upper_body", weight=1.0)

# Load animations
controller.load_animation("idle", "animations/idle.json")
controller.load_animation("wave", "animations/wave.json")

# Play animations on different layers
controller.play_animation("base", "idle")
controller.play_animation("upper_body", "wave")

# In your game loop:
while True:
    controller.update()
    bone_poses, blend_shapes = controller.get_pose()
    # Apply poses to your model
```

### AnimationClip

Represents an animation with keyframes and metadata.

```python
from avatarmcp.animation_v2 import AnimationClip, AnimationKeyframe, AnimationEvent, AnimationEventType

# Create a simple animation
clip = AnimationClip(
    name="nod",
    duration=1.0,
    loop=True,
    blend_mode=AnimationBlendMode.ADDITIVE
)

# Add keyframes
clip.keyframes.append(AnimationKeyframe(
    time=0.0,
    bone_name="Head",
    rotation=(0, 0, 0, 1)  # x, y, z, w
))

clip.keyframes.append(AnimationKeyframe(
    time=0.5,
    bone_name="Head",
    rotation=(0.2, 0, 0, 0.98)  # Nod down
))

# Add an event
clip.events.append(AnimationEvent(
    event_type=AnimationEventType.CUSTOM,
    time=0.5,
    name="head_nod",
    data={"intensity": 0.8}
))
```

## Animation Events

Respond to events triggered during animation playback:

```python
def on_footstep(layer_name, state_name, event):
    print(f"Footstep on {layer_name} at {event.time:.2f}s")
    # Play footstep sound, spawn particles, etc.

# Register event handler
controller.add_event_handler(AnimationEventType.FOOTSTEP, on_footstep)
```

## Animation Blending

Different blend modes are supported:

- **OVERRIDE**: Completely replace previous layers
- **ADDITIVE**: Add to previous layers (e.g., for facial expressions)
- **LAYERED**: Blend with previous layers based on weight
- **MASKED**: Only affect specific bones

## Performance Tips

1. **Reuse AnimationClips**: Load once, use multiple times
2. **Use Layers Wisely**: Put frequently changing animations on separate layers
3. **Limit Active Animations**: Stop animations when not needed
4. **Batch Updates**: Update all animations in a single pass
5. **Use Events Sparingly**: Complex event handlers can impact performance

## Example: Character Controller

```python
class CharacterController:
    def __init__(self):
        self.controller = AnimationController()
        self.controller.add_layer("base", 1.0)
        self.controller.add_layer("upper_body", 0.8)
        self.controller.add_layer("face", 1.0)
        
        # Load animations
        self.controller.load_animation("idle", "animations/idle.json")
        self.controller.load_animation("walk", "animations/walk.json")
        self.controller.load_animation("wave", "animations/wave.json")
        self.controller.load_animation("blink", "animations/blink.json")
        
        # Set up event handlers
        self.controller.add_event_handler(AnimationEventType.FOOTSTEP, self._on_footstep)
        
        # Start with idle animation
        self.controller.play_animation("base", "idle")
    
    def update(self, delta_time: float):
        self.controller.update()
        return self.controller.get_pose()
    
    def set_movement(self, speed: float, turn: float):
        if speed > 0.1:
            self.controller.play_animation("base", "walk")
        else:
            self.controller.play_animation("base", "idle")
    
    def wave(self):
        self.controller.play_animation("upper_body", "wave")
    
    def _on_footstep(self, layer, state, event):
        # Play footstep sound based on surface
        pass
```

## File Format

Animations are stored in JSON format:

```json
{
  "name": "walk",
  "duration": 1.2,
  "loop": true,
  "speed": 1.0,
  "blend_mode": "OVERRIDE",
  "priority": 0,
  "keyframes": [
    {
      "time": 0.0,
      "bone_name": "Hips",
      "position": [0, 1.0, 0],
      "rotation": [0, 0, 0, 1]
    },
    {
      "time": 0.5,
      "bone_name": "RightFoot",
      "position": [0, 0.1, 0.2]
    }
  ],
  "events": [
    {
      "type": "FOOTSTEP",
      "time": 0.2,
      "name": "left_foot",
      "data": {"foot": "left"}
    },
    {
      "type": "FOOTSTEP",
      "time": 0.7,
      "name": "right_foot",
      "data": {"foot": "right"}
    }
  ]
}
```

## Best Practices

1. **Keep Animations Simple**: Use layers to combine simple animations
2. **Use Events for Gameplay**: Trigger sounds, effects, and game logic
3. **Profile Performance**: Monitor animation update times
4. **Pre-bake Complex Animations**: For complex sequences, consider pre-baking
5. **Use Additive Blending**: For overlays like facial expressions or aiming
