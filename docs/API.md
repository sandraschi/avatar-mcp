# AvatarMCP API Reference

## Table of Contents

- [Overview](#overview)

- [Installation](#installation)


- [Quick Start](#quick-start)

- [API Reference](#api-reference)


  - [AvatarService](#avatarservice)

  - [VRM Model](#vrm-model)


  - [Animations](#animations)

- [Examples](#examples)


- [Contributing](#contributing)

## Overview

AvatarMCP provides a Python interface for managing and animating VRM avatars in a FastMCP 2.10+ environment. It supports
loading VRM models, applying animations, and handling avatar state.

## Installation

```bash

# Install from source


pip install -e .

# For development
pip install -e ".[dev]"





```

## Quick Start

```python
from avatarmcp import AvatarService






# Initialize the service
service = AvatarService()






# Load a VRM model
avatar = service.load_vrm("path/to/avatar.vrm")






# Apply an animation
service.play_animation(avatar, "wave")






# Update avatar state
service.update_pose(avatar, {





    "head": {"x": 0.1, "y": 0.2, "z": 0.0},
    "left_hand": {"gesture": "point"}
})

```


## API Reference

### AvatarService

#### `load_vrm(file_path: str) -> VRMModel`

Load a VRM model from file.

**Parameters:**

- `file_path`: Path to the .vrm file

**Returns:**

- `VRMModel` instance

#### `play_animation(avatar: VRMModel, animation_name: str, loop: bool = False) -> None`

Play an animation on the avatar.

**Parameters:**

- `avatar`: VRMModel instance

- `animation_name`: Name of the animation to play


- `loop`: Whether to loop the animation

#### `update_pose(avatar: VRMModel, pose_data: dict) -> None`

Update the avatar's pose.

**Parameters:**

- `avatar`: VRMModel instance

- `pose_data`: Dictionary containing pose information



### VRM Model

#### Properties

- `metadata`: VRM metadata (author, version, etc.)

- `meshes`: List of 3D meshes


- `materials`: List of materials

- `bones`: Skeleton bone hierarchy


- `blend_shapes`: Available facial expressions

### Animations

#### Built-in Animations

- `idle`: Default standing pose

- `wave`: Wave hello animation


- `nod`: Nod yes animation

- `shake`: Shake head no animation


- `point`: Point forward animation

## Examples

### Loading and Displaying an Avatar

```python
from avatarmcp import AvatarService






service = AvatarService()
avatar = service.load_vrm("avatar.vrm")
service.display(avatar)  # If running in a 3D viewer

```


### Creating Custom Animations

```python
from avatarmcp import Animation, Keyframe






# Create a custom animation
wave_anim = Animation("custom_wave")






# Add keyframes
wave_anim.add_keyframe(0.0, {"right_hand": {"position": [0, 0, 0]}})





wave_anim.add_keyframe(0.5, {"right_hand": {"position": [0.5, 0.5, 0]}})
wave_anim.add_keyframe(1.0, {"right_hand": {"position": [0, 0, 0]}})

# Register the animation
service.register_animation(wave_anim)






# Play the custom animation
service.play_animation(avatar, "custom_wave", loop=True)





```

## VRChat Integration

AvatarMCP provides seamless integration with VRChat avatars through the following features:

### VRChat Avatar Requirements

- **VRM 2.0 Support**: Full compatibility with VRChat's VRM 2.0 specification

- **Blendshape Mapping**: Automatic mapping of standard expressions to VRChat's blendshapes


- **Bone Structure**: Support for VRChat's humanoid bone structure

- **Parameter Naming**: Conforms to VRChat's avatar parameter naming conventions



### Example: Controlling a VRChat Avatar

```python
from avatarmcp import AvatarService






# Initialize with VRChat-specific settings
service = AvatarService(vrchat_mode=True)






# Load a VRChat-compatible VRM
avatar = service.load_vrm("path/to/vrchat_avatar.vrm")






# Play a VRChat gesture
service.update_pose(avatar, {





    "gestureLeft": "Fist",  # VRChat gesture name
    "gestureRight": "Point",
    "viseme": "Sil",  # Mouth shape for visemes
    "voice": 0.5,     # Voice volume (0.0-1.0)
})

# Control tracking data (if using full-body tracking)
service.update_pose(avatar, {





    "trackingType": "FULL",  # FULL, THREE_POINT, SITTING, etc.
    "isTracked": True,
    "hipPosition": [0, 1, 0],
    # ... other tracking points
})

```


## External Control

AvatarMCP supports various methods for external control:

### 1. OSC (Open Sound Control)

```python

# Enable OSC server


service.enable_osc(port=9000)

# Send OSC messages to control the avatar

# Example: /avatar/parameters/GestureLeft f 1.0


```

### 2. WebSocket API

```python

# Start WebSocket server


service.enable_websocket(port=8765)

# Clients can connect and send JSON messages:

# {"command": "play_animation", "name": "wave"}


```

### 3. MQTT Integration

```python

# Connect to MQTT broker


service.enable_mqtt(broker="mqtt.example.com", port=1883)

# Subscribe to control topics

# Example: avatarmcp/avatar1/pose


```

### 4. HTTP REST API

```python

# Start HTTP server


service.enable_http(port=8080)

# Endpoints:

# - POST /api/pose - Update avatar pose


# - GET /api/animations - List available animations

# - POST /api/play - Play animation


```

## Security Considerations

When enabling external control, consider these security measures:

$11. **Authentication**: Always enable authentication for external APIs

$11. **Rate Limiting**: Prevent abuse with rate limiting


$11. **Input Validation**: Validate all external inputs

$11. **Network Security**: Use TLS/SSL for all network communications


$11. **Access Control**: Restrict access to control interfaces

## Performance Optimization

For optimal performance with VRChat:

$11. **Bone Optimization**:

   - Limit number of bones to VRChat's recommended maximum


   - Use optimized bone hierarchies

   - Disable unnecessary physics on mobile platforms



$11. **Texture Optimization**:

   - Use compressed texture formats


   - Combine textures where possible

   - Use mipmaps for better performance at distance



$11. **Animation Optimization**:

   - Use animation layers for better performance


   - Optimize animation curves

   - Use animation compression where possible



## Contributing

$11. Fork the repository

$11. Create a feature branch


$11. Commit your changes

$11. Push to the branch


$11. Create a Pull Request
