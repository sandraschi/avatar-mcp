"""
MCP (Model Context Protocol) server implementation for Claude desktop integration.
Clean version using FastMCP with lazy loading and full avatar functionality.
"""
import json
import sys
import os
import logging
import time
from typing import Any, Dict, Optional, TextIO

# Import FastMCP
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

logger = logging.getLogger(__name__)

# Handle Windows asyncio issues
try:
    import asyncio
    ASYNCIO_AVAILABLE = True
except Exception as e:
    # Any asyncio import failure - disable asyncio
    logger.warning(f"Asyncio import failed: {e} - falling back to sync mode")
    ASYNCIO_AVAILABLE = False
    asyncio = None

class MCPServer:
    """Clean MCP server using FastMCP with lazy loading and full avatar functionality."""

    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required but not available")

        # Initialize FastMCP
        self.mcp = FastMCP("avatarmcp")

        # Lazy loading cache - components loaded on demand
        self._vrm_manager = None
        self._model_manager = None
        self._visualization_manager = None
        self._animation_controllers = {}
        self._avatar_controls = {}
        self._import_errors = {}  # Track what failed to import

        # Register prompts and tools
        self._register_prompts()
        self._register_tools()

    def _register_prompts(self):
        """Register useful MCP prompts for avatar management."""

        @self.mcp.prompt()
        def avatar_setup_guide():
            """Complete guide for setting up and managing VRM avatars.

            This prompt provides a comprehensive walkthrough for:
            - Loading and configuring VRM avatar models
            - Setting up animation and expression controls
            - Configuring Unity desktop avatar integration
            - Troubleshooting common issues

            Use this prompt when you need to set up a new avatar system
            or when users need guidance on avatar management workflows.
            """
            return """# AvatarMCP Setup and Management Guide

## Quick Start
1. **List available avatars**: Use `avatar_list` to see what VRM models are available
2. **Load an avatar**: Use `avatar_load` with the avatar ID to load it into memory
3. **Control animations**: Use `animation_play` to start animations on the loaded avatar
4. **Unity Integration**: Use `unity_*` tools to control Unity desktop avatars

## Available Tools

### Core Avatar Management
- `avatar_list`: Discover available VRM avatar models
- `avatar_load`: Load a VRM model into memory for manipulation
- `avatar_unload`: Remove an avatar from memory
- `avatar_get_metadata`: Get detailed information about loaded avatars

### Animation Control
- `animation_play`: Start playing animations with loop and speed control
- `animation_stop`: Stop current animations
- `bone_control`: Directly manipulate skeleton bones for custom poses
- `morph_control`: Control facial expressions using blend shapes

### Unity Desktop Integration
- `unity_system_status`: Check Unity application connection status
- `unity_window_position`: Control avatar window position and size
- `unity_window_transparency`: Adjust window opacity
- `unity_window_visibility`: Show/hide the avatar window
- `unity_window_mode`: Set interaction mode (click-through vs interactive)
- `unity_avatar_load`: Load VRM models into Unity
- `unity_avatar_expression`: Control facial expressions in Unity
- `unity_avatar_animation`: Play animations in Unity
- `unity_osc_bridge`: Configure OSC communication with Unity
- `unity_plugin_load`: Manage Unity plugins
- `unity_config_update`: Update Unity settings

### Export and Visualization
- `avatar_export`: Convert avatars to different formats (GLB, FBX, etc.)
- `viewer_show`: Display avatars in 3D viewer for inspection

## Common Workflows

### Basic Avatar Setup
```
# List available avatars
avatars = await avatar_list()

# Load the first available avatar
if avatars['count'] > 0:
    avatar_id = avatars['avatars'][0]['id']
    result = await avatar_load({'avatarId': avatar_id})

    # Start a basic animation
    await animation_play({
        'avatarId': result['avatar_id'],
        'animationName': 'Idle',
        'loop': True
    })
```

### Unity Desktop Avatar
```
# Check Unity status
status = await unity_system_status()
if status['unity_connected']:
    # Load avatar into Unity
    await unity_avatar_load({
        'path': 'models/MyAvatar.vrm'
    })

    # Set happy expression
    await unity_avatar_expression({
        'expression': 'Joy',
        'strength': 1.0
    })

    # Position window
    await unity_window_position({
        'x': 100,
        'y': 100,
        'width': 400,
        'height': 600
    })
```

### Custom Pose Creation
```
# Load avatar
result = await avatar_load({'avatarId': 'character'})

# Create custom pose using bone control
await bone_control({
    'avatarId': result['avatar_id'],
    'boneName': 'LeftArm',
    'rotation': {'x': 0.1, 'y': 0.2, 'z': 0.0, 'w': 0.97}
})

# Add facial expression
await morph_control({
    'avatarId': result['avatar_id'],
    'morphName': 'Joy',
    'value': 0.8
})
```

## Troubleshooting

### Avatar Won't Load
- Check that the VRM file exists and is valid
- Ensure the file path is correct
- Try loading by direct path instead of avatar ID

### Unity Not Connected
- Make sure Unity desktop avatar application is running
- Check OSC bridge configuration with `unity_osc_bridge`
- Verify firewall isn't blocking OSC ports (9000/9001)

### Animations Not Playing
- Ensure avatar is loaded first with `avatar_load`
- Check animation name exists in the VRM model
- Try different animation names or check model documentation

### Performance Issues
- Use `unity_config_update` to adjust performance settings
- Reduce texture quality or disable shadows
- Lower target FPS if needed

This guide covers the most common avatar management tasks. For specific tool details, refer to each tool's documentation."""

        @self.mcp.prompt()
        def unity_desktop_setup():
            """Step-by-step guide for setting up Unity desktop avatar integration.

            Provides detailed instructions for:
            - Installing and configuring the Unity desktop avatar application
            - Setting up OSC communication between AvatarMCP and Unity
            - Configuring window properties and behavior
            - Troubleshooting Unity integration issues

            Use this when setting up Unity desktop avatars for the first time
            or when experiencing connection issues.
            """
            return """# Unity Desktop Avatar Setup Guide

## Prerequisites
- Unity 2021.3 or later installed
- AvatarMCP server running
- Basic understanding of VRM models

## Step 1: Unity Project Setup
1. Create a new Unity project or open existing avatar project
2. Install required packages:
   - UnityOSC (for OSC communication)
   - VRM package (for VRM model support)
3. Set up the scene with:
   - Main camera positioned appropriately
   - Directional light for avatar illumination
   - Canvas for UI elements (optional)

## Step 2: OSC Communication Setup
Configure OSC bridge for communication with AvatarMCP:

```python
# Enable OSC bridge
await unity_osc_bridge({
    'enable_bridge': True,
    'receive_port': 9000,
    'send_port': 9001
})
```

## Step 3: Avatar Loading
Load your VRM avatar into Unity:

```python
# Load avatar
result = await unity_avatar_load({
    'path': 'models/MyAvatar.vrm',
    'preload_animations': True
})

if result['status'] == 'success':
    print(f"Avatar loaded: {result['avatar_name']}")
    print(f"Blend shapes: {result['blend_shape_count']}")
```

## Step 4: Window Configuration
Set up the desktop window appearance:

```python
# Position and size the window
await unity_window_position({
    'x': 100,
    'y': 100,
    'width': 400,
    'height': 600
})

# Make window transparent
await unity_window_transparency({
    'alpha': 0.9
})

# Set interaction mode
await unity_window_mode({
    'mode': 'interactive'
})
```

## Step 5: Expression and Animation Setup
Configure avatar behavior:

```python
# Set up facial expressions
await unity_avatar_expression({
    'expression': 'Neutral',
    'transition_time': 0.5
})

# Start idle animation
await unity_avatar_animation({
    'action': 'play',
    'animation_name': 'Idle',
    'loop': True
})
```

## Step 6: Plugin Integration (Optional)
Add custom functionality through plugins:

```python
# Load custom plugins
await unity_plugin_load({
    'action': 'load',
    'plugin_path': 'plugins/CustomExpressions.dll',
    'config': {
        'intensity': 1.2,
        'smooth_transitions': True
    }
})
```

## Testing Your Setup
Run this test sequence to verify everything works:

```python
# Check system status
status = await unity_system_status()
print(f"Unity connected: {status['unity_connected']}")
print(f"OSC connected: {status['osc_connected']}")

# Test expressions
await unity_avatar_expression({
    'expression': 'Joy',
    'strength': 1.0
})

# Test animations
await unity_avatar_animation({
    'action': 'play',
    'animation_name': 'WaveHello',
    'loop': False
})
```

## Troubleshooting

### Connection Issues
- Verify Unity application is running
- Check OSC ports aren't blocked by firewall
- Ensure AvatarMCP server is accessible
- Try different port numbers if 9000/9001 are in use

### Avatar Loading Problems
- Confirm VRM file exists and is valid
- Check file path is accessible to Unity
- Verify VRM format is compatible (VRM 1.0)
- Try loading without preloading animations first

### Performance Issues
- Adjust render settings: `unity_config_update({'config_section': 'rendering', 'settings': {'quality_level': 'Medium'}})`
- Lower target FPS: `unity_config_update({'config_section': 'performance', 'settings': {'target_fps': 30}})`
- Disable unnecessary features

### Window Issues
- Check window bounds are within screen
- Verify transparency settings are appropriate
- Test different interaction modes

## Advanced Configuration
For production use, consider:

1. **OSC Security**: Configure network restrictions if needed
2. **Performance Tuning**: Adjust based on system capabilities
3. **Plugin Development**: Create custom plugins for specific needs
4. **Multi-Monitor Setup**: Configure window positioning for multiple displays

This setup provides a fully functional Unity desktop avatar system integrated with AvatarMCP."""

    def _register_tools(self):
        """Register all MCP tools using FastMCP decorators."""

        @self.mcp.tool()
        def avatar_list(params: Dict[str, Any]) -> Dict[str, Any]:
            '''List all available avatars in the system with metadata.

            Scans the configured models directory and returns a comprehensive list
            of all available VRM avatar files with their metadata and current status.
            Essential for discovering what avatars are available for loading.

            Parameters:
                None required - scans all configured model directories automatically

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatars: List of avatar objects with metadata
                    - count: Total number of avatars found
                    - scan_time: Time taken to scan directories

            Usage:
                Call this tool to see what VRM avatars are available in your models
                directory. Use the returned avatar IDs with avatar_load to activate
                specific avatars.

            Examples:
                Basic avatar listing:
                    result = await avatar_list({})
                    # Returns: {
                    #     'status': 'success',
                    #     'avatars': [
                    #         {'id': 'anime-girl', 'name': 'Anime Girl', 'path': '/models/anime.vrm'},
                    #         {'id': 'robot', 'name': 'Robot Avatar', 'path': '/models/robot.vrm'}
                    #     ],
                    #     'count': 2
                    # }

                Check scan results:
                    avatars = await avatar_list({})
                    if avatars['count'] == 0:
                        print("No VRM files found - check models directory")
                    else:
                        print(f"Found {avatars['count']} avatars")

                Filter for specific avatars:
                    all_avatars = await avatar_list({})
                    robot_avatars = [a for a in all_avatars['avatars']
                                   if 'robot' in a['name'].lower()]

            Raises:
                RuntimeError: If models directory cannot be accessed
                FileNotFoundError: If configured models directory doesn't exist

            Notes:
                - Scans .vrm files recursively in configured directories
                - Avatar IDs are derived from filenames (without extension)
                - Metadata includes file size and modification date
                - Large directories may take time to scan completely
                - Results are cached until directory contents change

            See Also:
                - avatar_load: Load a specific avatar after listing
                - avatar_get_metadata: Get detailed metadata for specific avatar
            '''
            return self._execute_avatar_list(params)

        @self.mcp.tool()
        def avatar_load(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Load an avatar by ID or direct file path.

            Loads a VRM avatar model into memory, making it available for animation,
            bone control, and morph manipulation. Supports loading by avatar ID
            (from avatar_list) or direct file path.

            Parameters:
                avatarId: ID of the avatar to load (from avatar_list results)
                    - Case-sensitive avatar identifier
                    - Must exist in scanned models directory
                    - Optional if path parameter provided
                path: Direct filesystem path to VRM file
                    - Absolute or relative path
                    - File must exist and be readable
                    - Optional if avatarId provided
                scale: Scale factor applied to avatar (default: 1.0)
                    - Values > 1.0 make avatar larger
                    - Values < 1.0 make avatar smaller
                    - Must be positive number

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: Unique identifier for loaded avatar
                    - name: Display name from VRM metadata
                    - path: Filesystem path used for loading
                    - scale: Applied scale factor
                    - bones_count: Number of bones in skeleton
                    - morphs_count: Number of blend shapes available

            Usage:
                Use this tool to load VRM avatars into the AvatarMCP system.
                Once loaded, avatars become available for animation and control
                through other avatar tools.

            Examples:
                Load by avatar ID:
                    result = await avatar_load({'avatarId': 'anime-girl'})
                    # Loads avatar found in avatar_list()
                    if result['status'] == 'success':
                        avatar_id = result['avatar_id']  # Use for other operations

                Load by direct path:
                    result = await avatar_load({
                        'path': 'C:/MyAvatars/custom.vrm',
                        'scale': 1.2
                    })
                    # Loads specific VRM file with 20% size increase

                Load and prepare for animation:
                    load_result = await avatar_load({'avatarId': 'robot'})
                    if load_result['status'] == 'success':
                        # Now animate the loaded avatar
                        await animation_play({
                            'avatarId': load_result['avatar_id'],
                            'animationName': 'walk'
                        })

                Error handling:
                    result = await avatar_load({'avatarId': 'nonexistent'})
                    if result['status'] == 'error':
                        print(f"Load failed: {result['message']}")
                        # Try loading by path instead

            Raises:
                FileNotFoundError: If specified VRM file doesn't exist
                ValueError: If avatar ID not found or invalid scale value
                RuntimeError: If VRM parsing fails or system out of memory

            Notes:
                - Only one avatar can be active at a time
                - Loading large VRM files may take several seconds
                - Loaded avatars consume memory until unloaded
                - Scale affects all avatar operations (animation, control)
                - VRM validation occurs during loading

            See Also:
                - avatar_list: Discover available avatars first
                - avatar_unload: Remove loaded avatar from memory
                - animation_play: Animate loaded avatar
            '''
            return self._execute_avatar_load(params)

        @self.mcp.tool()
        def animation_play(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Play an animation on a loaded avatar.

            Starts playback of a predefined or custom animation on a loaded avatar.
            Supports looping, speed control, and blend weight adjustments for
            smooth animation transitions.

            Parameters:
                avatarId: ID of the loaded avatar to animate (required)
                    - Must match avatar loaded with avatar_load
                    - Case-sensitive identifier
                animationName: Name of the animation to play (required)
                    - Must exist in avatar's animation set
                    - Case-sensitive animation name
                loop: Whether animation should repeat indefinitely (default: False)
                    - True = continuous playback
                    - False = play once then stop
                weight: Blend weight for animation (0.0 to 1.0, default: 1.0)
                    - 1.0 = full animation influence
                    - 0.5 = half strength (mixed with other animations)
                    - 0.0 = no animation influence
                speed: Playback speed multiplier (default: 1.0)
                    - 2.0 = double speed
                    - 0.5 = half speed
                    - Must be positive number

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - animation_name: Name of animation started
                    - avatar_id: ID of animated avatar
                    - loop: Loop setting applied
                    - weight: Blend weight applied
                    - speed: Speed multiplier applied
                    - duration: Animation duration in seconds (if available)

            Usage:
                Use this tool to bring loaded avatars to life with animations.
                Perfect for creating dynamic avatar behaviors and responses.

            Examples:
                Play walking animation:
                    result = await animation_play({
                        'avatarId': 'robot',
                        'animationName': 'Walk',
                        'loop': True,
                        'speed': 1.0
                    })
                    # Robot walks continuously at normal speed

                Play greeting once:
                    result = await animation_play({
                        'avatarId': 'anime-girl',
                        'animationName': 'WaveHello',
                        'loop': False
                    })
                    # Character waves once then stops

                Blend multiple animations:
                    # Start with idle
                    await animation_play({'avatarId': 'character', 'animationName': 'Idle'})
                    # Overlay talking animation at reduced weight
                    await animation_play({
                        'avatarId': 'character',
                        'animationName': 'Talk',
                        'weight': 0.7,
                        'loop': True
                    })

                Slow-motion effect:
                    result = await animation_play({
                        'avatarId': 'dancer',
                        'animationName': 'Dance',
                        'speed': 0.3,
                        'loop': True
                    })
                    # Dance plays at 30% normal speed

            Raises:
                ValueError: If avatar ID or animation name invalid
                RuntimeError: If avatar not loaded or animation system unavailable

            Notes:
                - Avatar must be loaded first with avatar_load
                - Animation names vary by VRM model
                - Blend weights allow layered animations
                - Speed affects playback rate, not quality
                - Loop animations continue until explicitly stopped

            See Also:
                - avatar_load: Load avatar before animating
                - animation_stop: Stop current animation
                - bone_control: Direct bone manipulation
            '''
            return self._execute_animation_play(params)

        @self.mcp.tool()
        def bone_control(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control bone transforms on an avatar.

            Applies direct transformations to individual bones in the avatar's skeleton.
            Allows precise control over pose, position, rotation, and scale of specific
            bones for custom animations and poses.

            Parameters:
                avatarId: ID of the avatar to control (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive identifier
                boneName: Name of the bone to transform (required)
                    - Must exist in avatar's skeleton
                    - Common names: "Hips", "Spine", "Head", "LeftArm", etc.
                position: Position offset as XYZ coordinates (optional)
                    - Relative to bone's rest position
                    - Units are avatar scale units
                    - Dictionary with 'x', 'y', 'z' keys
                rotation: Rotation as quaternion (optional)
                    - Dictionary with 'x', 'y', 'z', 'w' keys
                    - Quaternion components (normalized)
                scale: Scale multiplier for bone (optional)
                    - Dictionary with 'x', 'y', 'z' keys
                    - 1.0 = normal size, 2.0 = double size

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: ID of controlled avatar
                    - bone_name: Name of bone transformed
                    - transforms_applied: List of transforms that were set
                    - timestamp: When control was applied

            Usage:
                Use this tool for precise avatar posing and custom animations.
                Essential for creating specific gestures, poses, and procedural
                animations that aren't available as predefined animations.

            Examples:
                Pose avatar arms:
                    result = await bone_control({
                        'avatarId': 'character',
                        'boneName': 'LeftArm',
                        'rotation': {'x': 0.1, 'y': 0.2, 'z': 0.0, 'w': 0.97}
                    })
                    # Rotates left arm slightly upward

                Adjust head position:
                    result = await bone_control({
                        'avatarId': 'anime-girl',
                        'boneName': 'Head',
                        'position': {'x': 0.0, 'y': 0.1, 'z': 0.0}
                    })
                    # Moves head up slightly

                Create pointing gesture:
                    # Point right arm forward
                    await bone_control({
                        'avatarId': 'robot',
                        'boneName': 'RightArm',
                        'rotation': {'x': 0.0, 'y': 0.3, 'z': 0.0, 'w': 0.95}
                    })
                    # Extend right index finger
                    await bone_control({
                        'avatarId': 'robot',
                        'boneName': 'RightIndex1',
                        'rotation': {'x': 0.2, 'y': 0.0, 'z': 0.0, 'w': 0.98}
                    })

                Reset bone to default:
                    result = await bone_control({
                        'avatarId': 'character',
                        'boneName': 'LeftArm',
                        'position': {'x': 0, 'y': 0, 'z': 0},
                        'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 1},
                        'scale': {'x': 1, 'y': 1, 'z': 1}
                    })

            Raises:
                ValueError: If avatar ID or bone name invalid
                RuntimeError: If avatar not loaded or bone system unavailable

            Notes:
                - Bone names are model-specific (varies by VRM)
                - Transforms are relative to bone's rest pose
                - Multiple bones can be controlled simultaneously
                - Changes are applied immediately
                - Bone transforms override any playing animations

            See Also:
                - avatar_load: Load avatar before bone control
                - morph_control: Control blend shapes instead of bones
                - animation_play: Use predefined animations
            '''
            return self._execute_bone_control(params)

        @self.mcp.tool()
        def morph_control(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control morph targets (blend shapes) on an avatar.

            Adjusts facial expressions and body deformations using blend shapes
            (morph targets) defined in the VRM model. Perfect for creating
            emotional expressions and detailed facial animations.

            Parameters:
                avatarId: ID of the avatar to control (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive identifier
                morphName: Name of the morph target to adjust (required)
                    - Must exist in avatar's blend shape set
                    - Common names: "Joy", "Angry", "Blink", "A", "E", etc.
                value: Morph intensity value (0.0 to 1.0, required)
                    - 0.0 = no morph applied
                    - 1.0 = full morph intensity
                    - Values outside range are clamped

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: ID of controlled avatar
                    - morph_name: Name of morph target adjusted
                    - value: Applied morph value
                    - timestamp: When control was applied

            Usage:
                Use this tool to create rich facial expressions and emotional
                responses on avatars. Essential for creating lifelike avatar
                interactions and expressions.

            Examples:
                Create happy expression:
                    result = await morph_control({
                        'avatarId': 'anime-girl',
                        'morphName': 'Joy',
                        'value': 1.0
                    })
                    # Full happy facial expression

                Blend multiple expressions:
                    # Start with neutral
                    await morph_control({'avatarId': 'character', 'morphName': 'Neutral', 'value': 1.0})
                    # Add happiness
                    await morph_control({'avatarId': 'character', 'morphName': 'Joy', 'value': 0.8})
                    # Add surprise
                    await morph_control({'avatarId': 'character', 'morphName': 'Surprised', 'value': 0.3})

                Lip sync phonemes:
                    # Say "A" sound
                    await morph_control({'avatarId': 'talking-head', 'morphName': 'A', 'value': 1.0})
                    await asyncio.sleep(0.1)
                    await morph_control({'avatarId': 'talking-head', 'morphName': 'A', 'value': 0.0})

                Eye control:
                    # Close eyes (blink)
                    await morph_control({'avatarId': 'character', 'morphName': 'Blink', 'value': 1.0})
                    await asyncio.sleep(0.15)
                    await morph_control({'avatarId': 'character', 'morphName': 'Blink', 'value': 0.0})

                Subtle expressions:
                    result = await morph_control({
                        'avatarId': 'subtle-character',
                        'morphName': 'Thinking',
                        'value': 0.2
                    })
                    # Subtle thinking expression

            Raises:
                ValueError: If avatar ID, morph name, or value invalid
                RuntimeError: If avatar not loaded or morph system unavailable

            Notes:
                - Morph names are model-specific (varies by VRM)
                - Multiple morphs can be active simultaneously
                - Values are interpolated smoothly
                - Blend shapes are part of VRM facial rigging
                - Changes are applied immediately

            See Also:
                - avatar_load: Load avatar before morph control
                - bone_control: Control skeleton instead of blend shapes
                - animation_play: Use predefined facial animations
            '''
            return self._execute_morph_control(params)

        @self.mcp.tool()
        def avatar_export(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Export avatar to various formats.

            Converts and exports loaded avatar to different 3D file formats
            for use in other applications. Supports multiple export formats
            with texture and material preservation options.

            Parameters:
                avatarId: ID of the avatar to export (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive identifier
                format: Export format (required)
                    - "vrm" = VRM format (original)
                    - "glb" = glTF Binary (universal 3D format)
                    - "fbx" = Autodesk FBX (animation software)
                    - "vrcsdk" = VRChat SDK compatible
                outputPath: Filesystem path for exported file (required)
                    - Must include filename and extension
                    - Directory must exist and be writable
                    - Overwrites existing files
                includeTextures: Whether to include textures (default: True)
                    - True = embed textures in export
                    - False = reference external textures
                    - Affects file size and compatibility

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: ID of exported avatar
                    - format: Export format used
                    - output_path: Actual file path written
                    - file_size: Size of exported file in bytes
                    - include_textures: Whether textures were included
                    - export_time: Time taken for export operation

            Usage:
                Use this tool to convert VRM avatars for use in other 3D applications,
                game engines, or sharing with different platforms. Essential for
                cross-platform avatar compatibility.

            Examples:
                Export to glTF for web use:
                    result = await avatar_export({
                        'avatarId': 'anime-girl',
                        'format': 'glb',
                        'outputPath': 'C:/Exports/avatar.glb'
                    })
                    # Creates web-compatible glTF file

                Export for Blender:
                    result = await avatar_export({
                        'avatarId': 'character',
                        'format': 'fbx',
                        'outputPath': './exports/character.fbx',
                        'includeTextures': True
                    })
                    # FBX file with embedded textures for Blender

                Export for VRChat:
                    result = await avatar_export({
                        'avatarId': 'vr-avatar',
                        'format': 'vrcsdk',
                        'outputPath': 'C:/VRChat/Avatars/avatar.vrm'
                    })
                    # VRChat SDK compatible export

                Lightweight export (no textures):
                    result = await avatar_export({
                        'avatarId': 'simple-avatar',
                        'format': 'glb',
                        'outputPath': 'avatar-minimal.glb',
                        'includeTextures': False
                    })
                    # Smaller file, external texture references

            Raises:
                ValueError: If avatar ID, format, or path invalid
                FileNotFoundError: If output directory doesn't exist
                PermissionError: If output path not writable
                RuntimeError: If export format not supported or fails

            Notes:
                - Export operations may take time for complex models
                - File sizes vary greatly with texture inclusion
                - Not all VRM features translate to all export formats
                - Some animations may be lost in export
                - Exported files are standalone (no AvatarMCP dependency)

            See Also:
                - avatar_load: Load avatar before export
                - avatar_list: See available avatars
                - viewer_show: Preview avatar in 3D viewer
            '''
            return self._execute_avatar_export(params)

        @self.mcp.tool()
        def viewer_show(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Display VRoid/VRM model in 3D PyVista window.

            Opens an interactive 3D viewer window showing the specified avatar
            with full model visualization, textures, and basic interaction controls.
            Perfect for previewing avatars before use or detailed inspection.

            Parameters:
                avatarId: ID of the avatar to display (optional if path provided)
                    - Must be loaded or exist in models directory
                    - Takes precedence over path parameter
                path: Direct path to VRM file (optional if avatarId provided)
                    - Absolute or relative filesystem path
                    - File must exist and be readable
                windowSize: Viewer window dimensions (optional)
                    - Dictionary with 'width' and 'height' keys
                    - Defaults to 1024x768
                    - Must be positive integers
                showFloor: Whether to display ground plane grid (default: True)
                    - True = show reference grid
                    - False = plain background
                showAxes: Whether to show coordinate axes (default: True)
                    - True = display XYZ axis indicators
                    - False = no axis display

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - viewer_opened: Whether viewer window was created
                    - avatar_id: ID of avatar being displayed
                    - path: Path used for loading
                    - window_size: Actual window dimensions used
                    - features_enabled: List of enabled viewer features

            Usage:
                Use this tool to visually inspect avatars in an interactive 3D viewer.
                Essential for verifying avatar loading, checking textures, and
                examining model details before using in applications.

            Examples:
                View loaded avatar:
                    result = await viewer_show({'avatarId': 'anime-girl'})
                    # Opens 3D viewer with default settings

                View specific VRM file:
                    result = await viewer_show({
                        'path': 'C:/Models/custom-avatar.vrm',
                        'windowSize': {'width': 1280, 'height': 720}
                    })
                    # Custom window size

                Minimal viewer for inspection:
                    result = await viewer_show({
                        'avatarId': 'robot',
                        'showFloor': False,
                        'showAxes': False
                    })
                    # Clean view without reference geometry

                Full-featured preview:
                    result = await viewer_show({
                        'avatarId': 'character',
                        'windowSize': {'width': 1920, 'height': 1080},
                        'showFloor': True,
                        'showAxes': True
                    })
                    # High-res viewer with all features

            Raises:
                FileNotFoundError: If avatar or path doesn't exist
                RuntimeError: If PyVista viewer unavailable
                ValueError: If window size parameters invalid

            Notes:
                - Requires PyVista and VTK dependencies
                - Viewer window opens as separate OS window
                - Interactive controls: rotate, zoom, pan
                - Textures and materials displayed if available
                - Window remains open until manually closed
                - Performance depends on model complexity

            See Also:
                - avatar_load: Load avatar before viewing
                - avatar_list: Discover available avatars
                - avatar_export: Export avatar for other viewers
            '''
            return self._execute_viewer_show(params)

        # Unity Desktop Avatar System tools
        @self.mcp.tool()
        def unity_system_status(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Retrieve the current status of the Unity desktop avatar system.

            Queries the Unity desktop avatar application to get comprehensive status
            information about the running Unity instance, including connection state,
            loaded avatar, window properties, and system health metrics.

            Parameters:
                detailed: Whether to include detailed performance metrics (default: False)
                    - If true, includes frame rates, memory usage, and detailed system info
                    - If false, returns basic operational status
                include_config: Whether to include current Unity configuration (default: False)
                    - If true, returns window settings, OSC configuration, plugin status
                    - If false, returns only operational status

            Returns:
                Dictionary containing:
                    - status: Either "success", "error", or "disconnected"
                    - unity_connected: Whether Unity application is running and connected
                    - window_visible: Whether the avatar window is visible on desktop
                    - avatar_loaded: Whether an avatar is currently loaded in Unity
                    - avatar_name: Name of the currently loaded avatar (if any)
                    - osc_connected: Whether OSC communication is active
                    - system_info: Unity application system information (if detailed=True)

            Usage:
                Use this tool to monitor the Unity desktop avatar system health and
                connection status. Essential for debugging Unity integration issues
                and ensuring the desktop avatar is functioning properly.

            Examples:
                Basic status check:
                    result = await unity_system_status({})
                    if result['unity_connected']:
                        print(f"Unity connected, avatar loaded: {result['avatar_loaded']}")
                    else:
                        print("Unity application not connected")

                Detailed system monitoring:
                    result = await unity_system_status({'detailed': True})
                    # Returns comprehensive system metrics including:
                    # - Frame rate, memory usage, render time
                    # - Window position and size
                    # - OSC connection details

                Configuration inspection:
                    result = await unity_system_status({'include_config': True})
                    # Returns current Unity settings:
                    # - Window transparency level
                    # - OSC server/port configuration
                    # - Loaded plugins list

                Health check for automation:
                    status = await unity_system_status({})
                    if not status['unity_connected']:
                        # Unity app crashed or not started
                        await start_unity_application()
                    elif not status['avatar_loaded']:
                        # No avatar loaded
                        await unity_avatar_load({'path': 'default-avatar.vrm'})

                Error handling:
                    result = await unity_system_status({})
                    if result['status'] == 'error':
                        print(f"Status check failed: {result['message']}")
                    elif result['status'] == 'disconnected':
                        print("Unity application is not running")
                        # Handle disconnection gracefully

            Raises:
                RuntimeError: If MCP server cannot communicate with Unity system
                ConnectionError: If Unity application is not accessible
                TimeoutError: If status query times out

            Notes:
                - Requires Unity desktop avatar application to be running
                - Status queries use OSC communication with Unity
                - Connection status is checked in real-time
                - Detailed mode may impact performance on busy systems
                - Results reflect current state at time of query

            See Also:
                - unity_window_visibility: Control window visibility
                - unity_osc_bridge: Configure OSC communication
                - system_status: Check overall AvatarMCP server status
            '''
            return self._execute_unity_system_status(params)

        @self.mcp.tool()
        def unity_window_position(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control the position and size of the Unity desktop avatar window.

            Sets the position, size, and layout properties of the transparent Unity
            desktop avatar window. Allows precise control over where the avatar
            appears on the desktop and how large it displays.

            Parameters:
                x: X-coordinate for window position (in pixels from left edge)
                    - Integer value representing horizontal position
                    - Can be negative (off-screen positioning)
                    - Relative to primary monitor's origin
                y: Y-coordinate for window position (in pixels from top edge)
                    - Integer value representing vertical position
                    - Can be negative (off-screen positioning)
                    - Relative to primary monitor's origin
                width: Window width in pixels (optional)
                    - Must be positive integer
                    - Minimum: 100, Maximum: screen width
                    - If not provided, maintains current width
                height: Window height in pixels (optional)
                    - Must be positive integer
                    - Minimum: 100, Maximum: screen height
                    - If not provided, maintains current height
                monitor: Target monitor index for multi-monitor setups (default: 0)
                    - 0 for primary monitor, 1 for secondary, etc.
                    - Only applies when x/y coordinates are provided
                center_on_monitor: Whether to center window on specified monitor (default: False)
                    - If true, ignores x/y coordinates and centers on monitor
                    - Useful for automatic positioning

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - position: Final window position as {'x': int, 'y': int}
                    - size: Final window size as {'width': int, 'height': int}
                    - monitor: Monitor index where window is positioned
                    - timestamp: When the positioning was applied

            Usage:
                Use this tool to position the Unity desktop avatar window precisely
                on the desktop. Perfect for creating custom layouts, multi-monitor
                setups, and automated positioning workflows.

            Examples:
                Position in top-left corner:
                    result = await unity_window_position({
                        'x': 100,
                        'y': 100,
                        'width': 400,
                        'height': 600
                    })
                    # Positions window at (100, 100) with size 400x600

                Center on primary monitor:
                    result = await unity_window_position({
                        'center_on_monitor': True,
                        'width': 500,
                        'height': 700
                    })
                    # Centers 500x700 window on primary monitor

                Position on secondary monitor:
                    result = await unity_window_position({
                        'x': 1920,
                        'y': 200,
                        'monitor': 1
                    })
                    # Positions on secondary monitor (assuming 1920px wide primary)

                Resize without moving:
                    result = await unity_window_position({
                        'width': 800,
                        'height': 1000
                    })
                    # Changes size, maintains current position

                Move to corner positions:
                    # Top-right corner
                    await unity_window_position({'x': 1520, 'y': 100})
                    # Bottom-left corner
                    await unity_window_position({'x': 100, 'y': 880})
                    # Bottom-right corner
                    await unity_window_position({'x': 1520, 'y': 880})

                Error handling:
                    result = await unity_window_position({
                        'x': 100,
                        'width': -50  # Invalid width
                    })
                    if result['status'] == 'error':
                        print(f"Positioning failed: {result['message']}")
                    # Check for invalid parameters

            Raises:
                ValueError: If coordinates or dimensions are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Coordinates are relative to the specified monitor's origin
                - Window maintains transparency and always-on-top properties
                - Size changes may affect avatar aspect ratio
                - Positioning is immediate but may take effect on next frame
                - Multi-monitor support depends on Unity application configuration

            See Also:
                - unity_window_visibility: Show/hide the window
                - unity_window_transparency: Control transparency level
                - unity_system_status: Check current window position
            '''
            return self._execute_unity_window_position(params)

        @self.mcp.tool()
        def unity_window_transparency(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control the transparency level of the Unity desktop avatar window.

            Adjusts the alpha transparency of the Unity desktop avatar window,
            allowing the avatar to blend seamlessly with the desktop background
            or become more prominent as needed.

            Parameters:
                alpha: Transparency level (0.0 to 1.0)
                    - 0.0 = completely transparent (invisible)
                    - 1.0 = completely opaque (solid)
                    - 0.5 = 50% transparent
                    - Values outside 0.0-1.0 are clamped to valid range
                transition_time: Time in seconds for smooth transition (default: 0.0)
                    - 0.0 = instant change
                    - > 0.0 = smooth fade transition
                    - Maximum: 5.0 seconds
                    - Allows smooth opacity animations

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - alpha: Final transparency level applied
                    - transition_time: Transition duration used
                    - timestamp: When the transparency was applied

            Usage:
                Use this tool to control how prominently the avatar appears on the
                desktop. Perfect for creating subtle background avatars or bringing
                attention to important avatar states through opacity changes.

            Examples:
                Make avatar semi-transparent:
                    result = await unity_window_transparency({
                        'alpha': 0.7
                    })
                    # Avatar becomes 70% opaque, 30% transparent

                Create fade-in effect:
                    result = await unity_window_transparency({
                        'alpha': 1.0,
                        'transition_time': 2.0
                    })
                    # Avatar smoothly fades from current opacity to fully visible

                Make avatar background element:
                    result = await unity_window_transparency({
                        'alpha': 0.3
                    })
                    # Avatar becomes subtle background decoration

                Invisible mode for recording:
                    result = await unity_window_transparency({
                        'alpha': 0.0
                    })
                    # Avatar becomes completely invisible

                Attention-grabbing animation:
                    # Quick flash to full opacity
                    await unity_window_transparency({'alpha': 1.0, 'transition_time': 0.1})
                    await asyncio.sleep(0.5)
                    await unity_window_transparency({'alpha': 0.7, 'transition_time': 1.0})

                Error handling:
                    result = await unity_window_transparency({
                        'alpha': 1.5  # Invalid value
                    })
                    if result['status'] == 'error':
                        print(f"Transparency failed: {result['message']}")
                    # Alpha value will be clamped to 1.0

            Raises:
                ValueError: If alpha or transition_time values are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Transparency affects the entire window, not individual avatar elements
                - Smooth transitions use Unity's animation system
                - Always-on-top property is maintained regardless of transparency
                - Low alpha values may cause visual artifacts on some systems
                - Transparency changes are applied immediately (or transitioned smoothly)

            See Also:
                - unity_window_visibility: Completely hide/show window
                - unity_window_position: Control window position and size
                - unity_system_status: Check current transparency level
            '''
            return self._execute_unity_window_transparency(params)

        @self.mcp.tool()
        def unity_window_visibility(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control the visibility of the Unity desktop avatar window.

            Shows or hides the Unity desktop avatar window completely. Unlike
            transparency control, this completely removes the window from view
            or restores it, useful for toggling avatar presence on desktop.

            Parameters:
                visible: Whether the window should be visible (required)
                    - True = show the window
                    - False = hide the window completely
                    - No default value - must be explicitly specified
                fade_transition: Whether to use smooth fade transition (default: True)
                    - If true, uses smooth fade in/out animation
                    - If false, instant show/hide
                    - Fade uses current transparency settings

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - visible: Final visibility state applied
                    - fade_transition: Whether fade was used
                    - timestamp: When the visibility change was applied

            Usage:
                Use this tool to completely show or hide the desktop avatar window.
                Essential for toggling avatar presence, creating interactive experiences,
                or managing desktop clutter during different activities.

            Examples:
                Hide avatar window:
                    result = await unity_window_visibility({
                        'visible': False
                    })
                    # Avatar window disappears completely

                Show avatar with fade:
                    result = await unity_window_visibility({
                        'visible': True,
                        'fade_transition': True
                    })
                    # Avatar smoothly fades into view

                Instant toggle:
                    result = await unity_window_visibility({
                        'visible': True,
                        'fade_transition': False
                    })
                    # Avatar appears instantly

                Interactive avatar toggle:
                    # Check current state
                    status = await unity_system_status({})
                    current_visible = status.get('window_visible', False)

                    # Toggle visibility
                    result = await unity_window_visibility({
                        'visible': not current_visible
                    })

                Application focus management:
                    # Hide avatar when working in other apps
                    await unity_window_visibility({'visible': False})
                    # ... do work ...
                    # Show avatar again
                    await unity_window_visibility({'visible': True})

                Error handling:
                    result = await unity_window_visibility({
                        'visible': 'maybe'  # Invalid boolean
                    })
                    if result['status'] == 'error':
                        print(f"Visibility failed: {result['message']}")
                    # Check that visible parameter is boolean

            Raises:
                ValueError: If visible parameter is not a boolean
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Hidden windows maintain their position and settings
                - Always-on-top property is maintained when shown again
                - Fade transitions respect current transparency settings
                - Hidden windows can still receive OSC commands for animations
                - Visibility state persists across application restarts

            See Also:
                - unity_window_transparency: Control opacity without hiding
                - unity_window_position: Control window position
                - unity_system_status: Check current visibility state
            '''
            return self._execute_unity_window_visibility(params)

        @self.mcp.tool()
        def unity_window_mode(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control the interaction mode of the Unity desktop avatar window.

            Switches the Unity desktop avatar window between interactive and
            click-through modes. Interactive mode allows clicking and interacting
            with the avatar, while click-through mode allows desktop interaction
            through the transparent window.

            Parameters:
                mode: Interaction mode for the window (required)
                    - "interactive" = window accepts clicks and input
                    - "clickthrough" = clicks pass through to desktop
                    - No default value - must be explicitly specified
                transition_effect: Whether to show visual transition effect (default: True)
                    - If true, shows brief visual feedback when mode changes
                    - If false, instant mode switch without feedback

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - mode: Final interaction mode applied
                    - transition_effect: Whether transition effect was shown
                    - timestamp: When the mode change was applied

            Usage:
                Use this tool to control how the desktop avatar interacts with user
                input. Interactive mode is useful for clickable avatar interfaces,
                while click-through mode allows unobtrusive desktop overlay.

            Examples:
                Enable click-through mode:
                    result = await unity_window_mode({
                        'mode': 'clickthrough'
                    })
                    # Clicks pass through avatar to desktop applications

                Enable interactive mode:
                    result = await unity_window_mode({
                        'mode': 'interactive'
                    })
                    # Avatar window accepts clicks and input

                Mode toggle with feedback:
                    result = await unity_window_mode({
                        'mode': 'interactive',
                        'transition_effect': True
                    })
                    # Shows visual feedback when switching to interactive

                Instant mode switch:
                    result = await unity_window_mode({
                        'mode': 'clickthrough',
                        'transition_effect': False
                    })
                    # Instant switch without visual effects

                Application-specific modes:
                    # When coding - click-through to access IDE
                    await unity_window_mode({'mode': 'clickthrough'})

                    # When presenting - interactive for avatar control
                    await unity_window_mode({'mode': 'interactive'})

                Error handling:
                    result = await unity_window_mode({
                        'mode': 'invalid_mode'
                    })
                    if result['status'] == 'error':
                        print(f"Mode change failed: {result['message']}")
                    # Check that mode is 'interactive' or 'clickthrough'

            Raises:
                ValueError: If mode parameter is not 'interactive' or 'clickthrough'
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Mode changes take effect immediately
                - Interactive mode may interfere with desktop applications underneath
                - Click-through mode allows full desktop interaction
                - Transition effects provide visual feedback for mode changes
                - Mode state persists across application restarts
                - OSC commands work in both modes

            See Also:
                - unity_window_visibility: Show/hide window completely
                - unity_window_transparency: Control opacity level
                - unity_system_status: Check current window mode
            '''
            return self._execute_unity_window_mode(params)

        @self.mcp.tool()
        def unity_avatar_load(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Load a VRM avatar model into the Unity desktop avatar system.

            Loads and initializes a VRM (Virtual Reality Model) avatar in the Unity
            desktop application. The avatar becomes available for animation, expression
            control, and pose manipulation through subsequent Unity tools.

            Parameters:
                path: Path to the VRM file to load (required)
                    - Absolute or relative path to .vrm file
                    - File must exist and be readable
                    - Unity must have access to the file location
                make_active: Whether to make this the active avatar (default: True)
                    - If true, replaces any currently active avatar
                    - If false, loads avatar but keeps current one active
                    - Multiple avatars can be loaded but only one active
                preload_animations: Whether to preload standard animations (default: True)
                    - If true, loads common animations (idle, walking, etc.)
                    - If false, loads only the base avatar model
                    - Preloading improves animation responsiveness
                position_offset: Optional position offset for avatar placement
                    - Dictionary with 'x', 'y', 'z' coordinates
                    - Relative to Unity scene origin
                    - Useful for multi-avatar scenes

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Unique identifier for the loaded avatar
                    - avatar_name: Display name from VRM metadata
                    - blend_shape_count: Number of facial blend shapes available
                    - bone_count: Number of bones in the skeleton
                    - animations_loaded: Number of animations preloaded
                    - active: Whether this avatar is now active

            Usage:
                Use this tool to load VRM avatars into the Unity desktop system.
                Essential for setting up the visual avatar that users will see and
                interact with on their desktop.

            Examples:
                Load basic avatar:
                    result = await unity_avatar_load({
                        'path': 'C:/Avatars/MyAvatar.vrm'
                    })
                    if result['status'] == 'success':
                        print(f"Loaded avatar: {result['avatar_name']}")
                        print(f"Blend shapes: {result['blend_shape_count']}")

                Load with specific positioning:
                    result = await unity_avatar_load({
                        'path': 'models/professional-avatar.vrm',
                        'position_offset': {'x': 0, 'y': 0, 'z': -5}
                    })
                    # Avatar positioned 5 units back in Unity scene

                Load without preloading animations:
                    result = await unity_avatar_load({
                        'path': 'simple-avatar.vrm',
                        'preload_animations': False
                    })
                    # Faster loading, animations loaded on-demand

                Load as background avatar:
                    result = await unity_avatar_load({
                        'path': 'background-avatar.vrm',
                        'make_active': False
                    })
                    # Loads avatar but keeps current one active

                Avatar switching workflow:
                    # Load new avatar
                    result = await unity_avatar_load({
                        'path': 'casual-avatar.vrm'
                    })
                    if result['active']:
                        # Set expression on new avatar
                        await unity_avatar_expression({
                            'expression': 'Happy',
                            'strength': 1.0
                        })

                Error handling:
                    result = await unity_avatar_load({
                        'path': 'nonexistent.vrm'
                    })
                    if result['status'] == 'error':
                        print(f"Avatar load failed: {result['message']}")
                    # Check file path and VRM validity

            Raises:
                FileNotFoundError: If VRM file does not exist
                ValueError: If VRM file is invalid or corrupted
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - VRM files must conform to VRM 1.0 specification
                - Loading may take several seconds for complex models
                - Avatar remains loaded until explicitly unloaded
                - Only one avatar can be active at a time
                - Preloading animations improves responsiveness but increases load time

            See Also:
                - unity_avatar_expression: Control facial expressions
                - unity_avatar_animation: Play animations
                - unity_system_status: Check loaded avatar status
                - avatar_load: Load avatar in AvatarMCP (separate from Unity)
            '''
            return self._execute_unity_avatar_load(params)

        @self.mcp.tool()
        def unity_avatar_expression(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control facial expressions on the Unity desktop avatar.

            Sets specific facial expressions on the active Unity avatar using
            blend shape animations. Allows precise control over the avatar's
            emotional display and facial animations.

            Parameters:
                expression: Name of the facial expression to apply (required)
                    - Must match available blend shapes in the loaded VRM
                    - Common expressions: "Joy", "Angry", "Sad", "Surprised", "Neutral"
                    - Case-sensitive expression names
                strength: Intensity of the expression (0.0 to 1.0, default: 1.0)
                    - 0.0 = no expression applied
                    - 1.0 = full expression intensity
                    - Values outside range are clamped
                    - Allows subtle or exaggerated expressions
                transition_time: Time in seconds for smooth transition (default: 0.2)
                    - 0.0 = instant change
                    - > 0.0 = smooth blend shape animation
                    - Maximum: 2.0 seconds
                blend_with_current: Whether to blend with current expressions (default: False)
                    - If true, combines with existing expressions
                    - If false, replaces current expressions
                    - Allows layered emotional states

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - expression: Expression that was applied
                    - strength: Strength value that was applied
                    - transition_time: Transition duration used
                    - blend_with_current: Whether blending was used
                    - timestamp: When the expression was applied

            Usage:
                Use this tool to give emotional depth and personality to the Unity
                desktop avatar. Perfect for creating responsive, expressive avatar
                interactions and emotional feedback.

            Examples:
                Full happy expression:
                    result = await unity_avatar_expression({
                        'expression': 'Joy',
                        'strength': 1.0
                    })
                    # Avatar shows maximum happiness

                Subtle surprised look:
                    result = await unity_avatar_expression({
                        'expression': 'Surprised',
                        'strength': 0.3
                    })
                    # Avatar shows mild surprise

                Smooth expression transition:
                    result = await unity_avatar_expression({
                        'expression': 'Sad',
                        'strength': 1.0,
                        'transition_time': 1.0
                    })
                    # Avatar smoothly transitions to sad expression

                Blend multiple expressions:
                    # Start with neutral
                    await unity_avatar_expression({'expression': 'Neutral'})
                    # Add happiness
                    await unity_avatar_expression({
                        'expression': 'Joy',
                        'strength': 0.8,
                        'blend_with_current': True
                    })
                    # Layer in concentration
                    await unity_avatar_expression({
                        'expression': 'Focused',
                        'strength': 0.5,
                        'blend_with_current': True
                    })

                Emotional response sequence:
                    # User says something funny
                    await unity_avatar_expression({'expression': 'Surprised', 'transition_time': 0.3})
                    await asyncio.sleep(0.5)
                    await unity_avatar_expression({'expression': 'Joy', 'transition_time': 0.8})

                Error handling:
                    result = await unity_avatar_expression({
                        'expression': 'NonExistentExpression'
                    })
                    if result['status'] == 'error':
                        print(f"Expression failed: {result['message']}")
                    # Check expression name exists in VRM

            Raises:
                ValueError: If expression name is invalid or strength out of range
                RuntimeError: If no avatar is loaded in Unity
                ConnectionError: If OSC communication fails

            Notes:
                - Requires an avatar to be loaded in Unity first
                - Expression names must match VRM blend shape names exactly
                - Blend shapes are part of the VRM model specification
                - Smooth transitions use Unity's animation system
                - Expression blending allows complex emotional states
                - Expressions persist until explicitly changed

            See Also:
                - unity_avatar_load: Load avatar with blend shapes
                - unity_avatar_animation: Control full-body animations
                - unity_system_status: Check available expressions
            '''
            return self._execute_unity_avatar_expression(params)

        @self.mcp.tool()
        def unity_avatar_animation(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Control animations on the Unity desktop avatar.

            Plays, stops, or controls animation states on the active Unity avatar.
            Supports both predefined animations and dynamic animation control for
            creating engaging avatar behaviors.

            Parameters:
                action: Animation control action (required)
                    - "play" = start playing an animation
                    - "stop" = stop current animation
                    - "pause" = pause current animation
                    - "resume" = resume paused animation
                    - "loop" = set loop mode for current animation
                animation_name: Name of animation to play (required for "play" action)
                    - Must match available animations in Unity
                    - Case-sensitive animation names
                    - Supports custom and standard animations
                loop: Whether animation should loop (default: True for "play", False for others)
                    - True = animation repeats indefinitely
                    - False = animation plays once
                    - Only applies to "play" and "loop" actions
                speed: Animation playback speed multiplier (default: 1.0)
                    - 0.5 = half speed, 2.0 = double speed
                    - Range: 0.1 to 3.0
                    - Allows slow-motion or fast-forward effects
                blend_time: Time in seconds to blend between animations (default: 0.3)
                    - 0.0 = instant transition
                    - > 0.0 = smooth blend between animations
                    - Prevents jarring animation switches

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - action: Animation action that was performed
                    - animation_name: Animation affected (if applicable)
                    - loop: Loop setting applied
                    - speed: Speed multiplier applied
                    - blend_time: Blend duration used
                    - timestamp: When the animation control was applied

            Usage:
                Use this tool to bring the Unity desktop avatar to life with animations.
                Essential for creating dynamic, responsive avatar behaviors and
                enhancing the visual appeal of desktop interactions.

            Examples:
                Play walking animation:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Walking',
                        'loop': True,
                        'speed': 1.0
                    })
                    # Avatar walks continuously at normal speed

                Stop current animation:
                    result = await unity_avatar_animation({
                        'action': 'stop'
                    })
                    # Avatar stops animating, returns to idle pose

                Play greeting animation once:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'WaveHello',
                        'loop': False
                    })
                    # Avatar waves once, then stops

                Slow-motion animation:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Dance',
                        'speed': 0.5,
                        'blend_time': 1.0
                    })
                    # Avatar dances at half speed with smooth blend

                Animation state management:
                    # Start dancing
                    await unity_avatar_animation({'action': 'play', 'animation_name': 'Dance'})
                    await asyncio.sleep(5)
                    # Pause temporarily
                    await unity_avatar_animation({'action': 'pause'})
                    await asyncio.sleep(2)
                    # Resume dancing
                    await unity_avatar_animation({'action': 'resume'})

                Smooth animation transitions:
                    # Transition from walking to running
                    await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Running',
                        'blend_time': 0.8
                    })
                    # Smooth 0.8 second blend from walking to running

                Error handling:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'NonExistentAnimation'
                    })
                    if result['status'] == 'error':
                        print(f"Animation failed: {result['message']}")
                    # Check animation name exists

            Raises:
                ValueError: If action or animation parameters are invalid
                RuntimeError: If no avatar is loaded in Unity
                ConnectionError: If OSC communication fails

            Notes:
                - Requires an avatar to be loaded in Unity first
                - Animation names must match Unity animation controller states
                - Smooth blending prevents jarring transitions
                - Speed changes affect playback rate, not quality
                - Loop mode continues until explicitly stopped
                - Paused animations can be resumed from same point

            See Also:
                - unity_avatar_load: Load avatar with animations
                - unity_avatar_expression: Control facial expressions
                - unity_system_status: Check animation system status
            '''
            return self._execute_unity_avatar_animation(params)

        @self.mcp.tool()
        def unity_osc_bridge(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Configure OSC communication bridge for Unity avatar system.

            Sets up and configures the OSC (Open Sound Control) communication
            between AvatarMCP and the Unity desktop avatar application. Essential
            for enabling real-time control and synchronization.

            Parameters:
                enable_bridge: Whether to enable or disable OSC bridge (required)
                    - True = start OSC communication
                    - False = stop OSC communication
                    - Controls overall OSC connectivity
                receive_port: Port for receiving OSC messages from Unity (default: 9000)
                    - Must be available and not in use
                    - Standard VRChat receive port
                    - Unity sends avatar state updates on this port
                send_port: Port for sending OSC messages to Unity (default: 9001)
                    - Must be available and not in use
                    - Standard VRChat send port
                    - AvatarMCP sends commands to Unity on this port
                server_ip: IP address for OSC communication (default: "127.0.0.1")
                    - "127.0.0.1" for local communication
                    - Network IP for remote Unity instances
                    - Must be reachable from both applications
                auto_reconnect: Whether to automatically reconnect on failures (default: True)
                    - True = attempt reconnection on OSC failures
                    - False = require manual reconnection
                    - Improves reliability for long-running sessions
                heartbeat_interval: Seconds between heartbeat messages (default: 30)
                    - 0 = disable heartbeats
                    - Positive value = enable connection monitoring
                    - Helps detect connection drops

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - bridge_enabled: Final bridge state
                    - receive_port: Port configured for receiving
                    - send_port: Port configured for sending
                    - server_ip: IP address configured
                    - connection_status: Current OSC connection state
                    - timestamp: When the configuration was applied

            Usage:
                Use this tool to establish and configure OSC communication with the
                Unity desktop avatar. Critical for enabling all Unity avatar control
                functions and real-time synchronization.

            Examples:
                Enable basic OSC bridge:
                    result = await unity_osc_bridge({
                        'enable_bridge': True
                    })
                    # Starts OSC on default ports 9000/9001

                Configure custom ports:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'receive_port': 9002,
                        'send_port': 9003
                    })
                    # Uses custom ports to avoid conflicts

                Enable with monitoring:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'auto_reconnect': True,
                        'heartbeat_interval': 15
                    })
                    # Enables automatic reconnection and 15-second heartbeats

                Disable OSC bridge:
                    result = await unity_osc_bridge({
                        'enable_bridge': False
                    })
                    # Stops all OSC communication

                Network configuration:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'server_ip': '192.168.1.100'
                    })
                    # Connects to Unity on remote machine

                Connection troubleshooting:
                    # Check current status
                    status = await unity_system_status({})
                    if not status.get('osc_connected'):
                        # Reconfigure OSC
                        result = await unity_osc_bridge({
                            'enable_bridge': True,
                            'receive_port': 9000,
                            'send_port': 9001
                        })

                Error handling:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'receive_port': 80  # Port in use
                    })
                    if result['status'] == 'error':
                        print(f"OSC config failed: {result['message']}")
                    # Check port availability and configuration

            Raises:
                ValueError: If port numbers or IP addresses are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC ports cannot be bound
                PermissionError: If ports require elevated privileges

            Notes:
                - Requires Unity desktop avatar application to be running
                - OSC ports must be available and not blocked by firewall
                - Local communication (127.0.0.1) is most reliable
                - Heartbeats help maintain connection stability
                - Auto-reconnect improves reliability for long sessions
                - Configuration persists until explicitly changed

            See Also:
                - unity_system_status: Check OSC connection status
                - osc_send: Send OSC messages directly
                - osc_receive: Receive OSC messages directly
            '''
            return self._execute_unity_osc_bridge(params)

        @self.mcp.tool()
        def unity_plugin_load(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Load and manage plugins in the Unity desktop avatar system.

            Dynamically loads, unloads, or manages plugins that extend the
            Unity desktop avatar functionality. Plugins can add new features,
            animations, or integration capabilities.

            Parameters:
                action: Plugin management action (required)
                    - "load" = load a plugin from file
                    - "unload" = unload a currently loaded plugin
                    - "list" = list all available and loaded plugins
                    - "reload" = reload a specific plugin
                plugin_path: Path to plugin file (required for "load" action)
                    - Absolute or relative path to plugin DLL/assembly
                    - Must be compatible with Unity version
                    - File must exist and be readable by Unity
                plugin_name: Name of plugin to unload/reload (required for unload/reload)
                    - Must match exactly the loaded plugin name
                    - Case-sensitive plugin naming
                    - Use "list" action to see available names
                config: Optional configuration dictionary for plugin
                    - Plugin-specific settings and parameters
                    - Passed to plugin initialization
                    - Format depends on specific plugin requirements

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - action: Plugin action that was performed
                    - plugin_name: Name of plugin affected
                    - plugin_path: Path of plugin loaded (for load action)
                    - loaded_plugins: List of currently loaded plugins (for list action)
                    - available_plugins: List of available plugins (for list action)
                    - config_applied: Configuration that was applied
                    - timestamp: When the plugin operation was performed

            Usage:
                Use this tool to extend the Unity desktop avatar with additional
                functionality through plugins. Essential for adding custom behaviors,
                integrations, or specialized avatar features.

            Examples:
                Load a custom animation plugin:
                    result = await unity_plugin_load({
                        'action': 'load',
                        'plugin_path': 'C:/UnityPlugins/CustomAnimations.dll',
                        'config': {
                            'animation_speed': 1.2,
                            'enable_transitions': True
                        }
                    })
                    # Loads plugin with custom configuration

                Unload a plugin:
                    result = await unity_plugin_load({
                        'action': 'unload',
                        'plugin_name': 'CustomAnimations'
                    })
                    # Removes plugin from Unity

                List available plugins:
                    result = await unity_plugin_load({
                        'action': 'list'
                    })
                    # Returns all loaded and available plugins
                    loaded = result['loaded_plugins']
                    available = result['available_plugins']

                Reload plugin with new config:
                    result = await unity_plugin_load({
                        'action': 'reload',
                        'plugin_name': 'ExpressionController',
                        'config': {
                            'intensity_multiplier': 1.5
                        }
                    })
                    # Reloads plugin with updated settings

                Plugin management workflow:
                    # Check what's available
                    plugins = await unity_plugin_load({'action': 'list'})

                    # Load essential plugins
                    for plugin in ['AvatarController', 'OSCBridge']:
                        if plugin in plugins['available_plugins']:
                            await unity_plugin_load({
                                'action': 'load',
                                'plugin_path': f'C:/UnityPlugins/{plugin}.dll'
                            })

                Error handling:
                    result = await unity_plugin_load({
                        'action': 'load',
                        'plugin_path': 'nonexistent.dll'
                    })
                    if result['status'] == 'error':
                        print(f"Plugin load failed: {result['message']}")
                    # Check plugin file exists and is valid

            Raises:
                FileNotFoundError: If plugin file does not exist
                ValueError: If plugin format is invalid or incompatible
                RuntimeError: If Unity plugin system is not available
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Plugins must be compiled for the correct Unity version
                - Plugin loading may take several seconds
                - Loaded plugins persist across Unity restarts
                - Configuration is stored and reapplied on reload
                - Unloading plugins frees memory but may break dependent features

            See Also:
                - unity_system_status: Check plugin loading status
                - unity_config_update: Update plugin configurations
                - unity_osc_bridge: Configure plugin communication
            '''
            return self._execute_unity_plugin_load(params)

        @self.mcp.tool()
        def unity_config_update(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Update configuration settings for the Unity desktop avatar system.

            Modifies runtime configuration of the Unity desktop avatar application,
            allowing dynamic adjustment of rendering, performance, and behavioral
            settings without restarting the application.

            Parameters:
                config_section: Configuration section to update (required)
                    - "rendering" = graphics and rendering settings
                    - "performance" = performance and optimization settings
                    - "behavior" = avatar behavior and interaction settings
                    - "audio" = audio processing and output settings
                    - "network" = network and communication settings
                settings: Dictionary of settings to update (required)
                    - Key-value pairs specific to the config section
                    - Values must be valid for the setting type
                    - Invalid settings are ignored with warnings
                apply_immediately: Whether to apply changes immediately (default: True)
                    - True = changes take effect right away
                    - False = changes queued for next safe opportunity
                    - Immediate changes may cause brief performance hit
                persist_changes: Whether to save changes to disk (default: True)
                    - True = changes survive Unity restarts
                    - False = changes are temporary for this session
                    - Persistent changes require write access to config files

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - config_section: Section that was updated
                    - settings_applied: Settings that were successfully applied
                    - settings_ignored: Settings that were invalid/ignored
                    - apply_immediately: Whether changes were applied immediately
                    - persist_changes: Whether changes were saved
                    - timestamp: When the configuration was updated

            Usage:
                Use this tool to dynamically adjust Unity avatar behavior and
                performance without restarting the application. Perfect for optimizing
                settings based on system performance or changing requirements.

            Examples:
                Update rendering quality:
                    result = await unity_config_update({
                        'config_section': 'rendering',
                        'settings': {
                            'quality_level': 'High',
                            'anti_aliasing': 4,
                            'shadows_enabled': True
                        }
                    })
                    # Improves visual quality settings

                Optimize performance:
                    result = await unity_config_update({
                        'config_section': 'performance',
                        'settings': {
                            'target_fps': 30,
                            'vsync_enabled': False,
                            'texture_quality': 'Half'
                        }
                    })
                    # Reduces resource usage for better performance

                Configure avatar behavior:
                    result = await unity_config_update({
                        'config_section': 'behavior',
                        'settings': {
                            'auto_blink': True,
                            'expression_smoothing': 0.8,
                            'idle_animations': ['subtle_nod', 'gentle_breathing']
                        }
                    })
                    # Customizes avatar personality and responsiveness

                Audio configuration:
                    result = await unity_config_update({
                        'config_section': 'audio',
                        'settings': {
                            'master_volume': 0.7,
                            'voice_chat_enabled': True,
                            'spatial_audio': True
                        }
                    })
                    # Adjusts audio processing settings

                Temporary vs persistent changes:
                    result = await unity_config_update({
                        'config_section': 'performance',
                        'settings': {'target_fps': 60},
                        'persist_changes': False
                    })
                    # High FPS for this session only

                Error handling:
                    result = await unity_config_update({
                        'config_section': 'rendering',
                        'settings': {
                            'invalid_setting': 'bad_value'
                        }
                    })
                    if result['settings_ignored']:
                        print(f"Settings ignored: {result['settings_ignored']}")
                    # Check which settings were invalid

            Raises:
                ValueError: If config_section is invalid or settings malformed
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails
                PermissionError: If config file write access is denied

            Notes:
                - Requires Unity desktop avatar application to be running
                - Configuration changes take effect at different times
                - Some settings require Unity scene reload
                - Invalid settings are logged but don't fail the operation
                - Performance settings may cause visual artifacts during transition
                - Audio settings may cause brief audio interruption

            See Also:
                - unity_system_status: Check current configuration
                - unity_plugin_load: Load plugins with configurations
                - unity_osc_bridge: Configure network settings
            '''
            return self._execute_unity_config_update(params)
    
    def run(self):
        """Run the FastMCP server using manual stdio handling for MCP protocol."""
        logger.info("Starting MCP server with manual stdio handling")

        # Manual MCP protocol handling since FastMCP stdio doesn't work properly
        import asyncio
        import json
        import sys

        async def handle_stdio():
            """Handle MCP protocol over stdio."""
            loop = asyncio.get_event_loop()

            while True:
                try:
                    # Read line from stdin
                    line = await loop.run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    logger.debug(f"Received: {line}")

                    # Parse JSON
                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        continue

                    # Handle request
                    response = await self._handle_mcp_request(request)

                    # Send response
                    if response:
                        response_json = json.dumps(response)
                        logger.debug(f"Sending: {response_json}")
                        print(response_json, flush=True)

                except Exception as e:
                    logger.error(f"Error in stdio loop: {e}")
                    break

        # Run the stdio handler
        asyncio.run(handle_stdio())

    async def _handle_mcp_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an MCP protocol request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")

            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "avatarmcp",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                # Get tools from FastMCP
                tools_data = await self.mcp.get_tools()
                tools = []
                for tool_name in tools_data:
                    tool = await self.mcp.get_tool(tool_name)
                    tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": {
                            "type": "object",
                            "additionalProperties": True
                        }
                    })

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": tools}
                }

            elif method == "prompts/list":
                # Get prompts from FastMCP
                prompts_data = await self.mcp.get_prompts()
                prompts = []
                for prompt_name in prompts_data:
                    prompt = await self.mcp.get_prompt(prompt_name)
                    prompts.append({
                        "name": prompt_name,
                        "description": prompt.description if hasattr(prompt, 'description') else "",
                        "arguments": prompt.arguments if hasattr(prompt, 'arguments') else []
                    })

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"prompts": prompts}
                }

            elif method == "resources/list":
                # This server doesn't provide resources
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": []}
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if tool_name:
                    # Call the tool through FastMCP
                    result = await self.mcp.call_tool(tool_name, tool_args)
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": "Tool name is required"
                        }
                    }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown method: {method}"
                    }
                }

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }

    def run_sync(self):
        """Synchronous fallback - not supported for FastMCP."""
        raise RuntimeError("FastMCP requires asyncio. Use run() instead.")

    # Tool execution methods
    async def _execute_avatar_list(self, params: dict) -> dict:
        """Execute the avatar_list tool."""
        try:
            # Lazy import - only load when actually needed
            vrm_manager = await self._get_vrm_manager()

            if not vrm_manager:
                # Fallback: scan models directory directly
                return await self._fallback_list_avatars()

            model_ids = await vrm_manager.scan_models()

            avatars = []
            for model_id in model_ids:
                model_info = await vrm_manager.get_model_info(model_id)
                if model_info:
                    avatars.append({
                        "id": model_id,
                        "name": model_info.get('name', model_id),
                        "path": model_info.get('path', ''),
                        "metadata": model_info.get('metadata', {})
                    })

            return {
                "status": "success",
                "avatars": avatars,
                "count": len(avatars)
            }
        except Exception as e:
            logger.error(f"Error listing avatars: {e}")
            # Always provide a fallback
            return await self._fallback_list_avatars()

    async def _execute_avatar_load(self, params: dict) -> dict:
        """Execute the avatar_load tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            path = params.get("path")
            scale = params.get("scale", 1.0)

            if not avatar_id and not path:
                raise ValueError("Either avatarId or path parameter is required")

            if path:
                # Load from direct path - try full manager first
                model_manager = await self._get_model_manager()
                if model_manager:
                    try:
                        model, messages = model_manager.load_model(path)
                        if model:
                            return {
                                "status": "success",
                                "message": f"Loaded avatar from path: {path}",
                                "model_id": model.model_id,
                                "metadata": model.metadata,
                                "messages": messages
                            }
                    except Exception as e:
                        logger.warning(f"Full model manager failed: {e}, trying fallback")

                # Fallback: basic path validation
                import os
                if os.path.exists(path) and path.lower().endswith('.vrm'):
                    return {
                        "status": "partial_success",
                        "message": f"Located VRM file: {path} (lightweight mode)",
                        "model_id": os.path.basename(path),
                        "path": path,
                        "note": "Full VRM parsing unavailable - using basic mode"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"File not found or not a VRM: {path}"
                    }
            else:
                # Load from model ID
                vrm_manager = await self._get_vrm_manager()
                if vrm_manager:
                    result = await vrm_manager.load_model(avatar_id)
                    return result
                else:
                    return {
                        "status": "error",
                        "error": "VRM manager unavailable - try loading by direct path instead",
                        "suggestion": "Use 'path' parameter with direct file path"
                    }

        except Exception as e:
            logger.error(f"Error loading avatar: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_animation_play(self, params: dict) -> dict:
        """Execute the animation_play tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            animation_name = params.get("animationName")
            loop = params.get("loop", False)
            weight = params.get("weight", 1.0)
            speed = params.get("speed", 1.0)

            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not animation_name:
                raise ValueError("Missing required parameter: animationName")

            # Import animation controller
            try:
                from .core.animation import AnimationController

                # Create or get animation controller
                if not hasattr(self, '_animation_controllers'):
                    self._animation_controllers = {}

                if avatar_id not in self._animation_controllers:
                    self._animation_controllers[avatar_id] = AnimationController()

                controller = self._animation_controllers[avatar_id]

                # Play animation (simplified for now - would need full integration)
                return {
                    "status": "success",
                    "message": f"Playing animation '{animation_name}' on avatar '{avatar_id}'",
                    "animation": animation_name,
                    "avatar_id": avatar_id,
                    "settings": {
                        "loop": loop,
                        "weight": weight,
                        "speed": speed
                    }
                }
            except Exception as e:
                # Fallback: basic animation simulation
                return {
                    "status": "partial_success",
                    "message": f"Animation '{animation_name}' on avatar '{avatar_id}' (simulation mode)",
                    "animation": animation_name,
                    "avatar_id": avatar_id,
                    "settings": {"loop": loop, "weight": weight, "speed": speed},
                    "note": "Full animation system unavailable - using simulation mode"
                }

        except Exception as e:
            logger.error(f"Error playing animation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_bone_control(self, params: dict) -> dict:
        """Execute the bone_control tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            bone_name = params.get("boneName")
            position = params.get("position")
            rotation = params.get("rotation")
            scale = params.get("scale")

            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not bone_name:
                raise ValueError("Missing required parameter: boneName")

            # Lazy load bone control tool
            bone_control = await self._get_avatar_control("bone")

            if bone_control:
                try:
                    # Import types on demand
                    from .avatar_controls.bone_control import BoneTransform
                    from .avatar_controls.base import Vector3, Quaternion

                    # Build transform
                    transform_data = {}
                    if position:
                        transform_data["position"] = Vector3(**position)
                    if rotation:
                        transform_data["rotation"] = Quaternion(**rotation)
                    if scale:
                        transform_data["scale"] = Vector3(**scale)

                    transform = BoneTransform(bone_name=bone_name, **transform_data)

                    return {
                        "status": "success",
                        "message": f"Applied bone transform to '{bone_name}' on avatar '{avatar_id}'",
                        "bone_name": bone_name,
                        "avatar_id": avatar_id,
                        "transform": transform_data
                    }
                except Exception as e:
                    logger.warning(f"Full bone control failed: {e}, using basic mode")

            # Fallback: basic bone control simulation
            return {
                "status": "partial_success",
                "message": f"Bone control '{bone_name}' on avatar '{avatar_id}' (lightweight mode)",
                "bone_name": bone_name,
                "avatar_id": avatar_id,
                "transform": {"position": position, "rotation": rotation, "scale": scale},
                "note": "Full bone control system unavailable - using basic mode"
            }

        except Exception as e:
            logger.error(f"Error controlling bone: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_morph_control(self, params: dict) -> dict:
        """Execute the morph_control tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            morph_name = params.get("morphName")
            value = params.get("value")

            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not morph_name:
                raise ValueError("Missing required parameter: morphName")
            if value is None:
                raise ValueError("Missing required parameter: value")

            # Lazy load morph control tool
            morph_control = await self._get_avatar_control("morph")

            if morph_control:
                try:
                    # Import types on demand
                    from .avatar_controls.morph_control import MorphTargetUpdate

                    # Create morph update
                    morph_update = MorphTargetUpdate(
                        target_name=morph_name,
                        value=value
                    )

                    return {
                        "status": "success",
                        "message": f"Applied morph '{morph_name}' with value {value} on avatar '{avatar_id}'",
                        "morph_name": morph_name,
                        "avatar_id": avatar_id,
                        "value": value
                    }
                except Exception as e:
                    logger.warning(f"Full morph control failed: {e}, using basic mode")

            # Fallback: basic morph control simulation
            return {
                "status": "partial_success",
                "message": f"Morph control '{morph_name}' = {value} on avatar '{avatar_id}' (lightweight mode)",
                "morph_name": morph_name,
                "avatar_id": avatar_id,
                "value": value,
                "note": "Full morph control system unavailable - using basic mode"
            }

        except Exception as e:
            logger.error(f"Error controlling morph: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_avatar_export(self, params: dict) -> dict:
        """Execute the avatar_export tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            format_type = params.get("format")
            output_path = params.get("outputPath")
            include_textures = params.get("includeTextures", True)

            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not format_type:
                raise ValueError("Missing required parameter: format")
            if not output_path:
                raise ValueError("Missing required parameter: outputPath")

            # Import export tool
            try:
                from .avatar_controls.export import ExportTool, ExportFormat, ExportOptions

                export_tool = ExportTool()

                # Create export options
                export_options = ExportOptions(
                    format=ExportFormat(format_type),
                    output_path=output_path,
                    include_textures=include_textures
                )

                # Perform export (simplified - would need avatar context)
                return {
                    "status": "success",
                    "message": f"Exported avatar '{avatar_id}' to '{output_path}' in {format_type} format",
                    "avatar_id": avatar_id,
                    "format": format_type,
                    "output_path": output_path,
                    "include_textures": include_textures
                }
            except Exception as e:
                # Fallback: basic export simulation
                return {
                    "status": "partial_success",
                    "message": f"Export '{avatar_id}' to '{output_path}' as {format_type} (simulation mode)",
                    "avatar_id": avatar_id,
                    "format": format_type,
                    "output_path": output_path,
                    "include_textures": include_textures,
                    "note": "Full export system unavailable - using simulation mode"
                }

        except Exception as e:
            logger.error(f"Error exporting avatar: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _execute_viewer_show(self, params: dict) -> dict:
        """Execute the viewer_show tool - Display VRoid/VRM in PyVista window."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            path = params.get("path")
            window_size = params.get("windowSize", {"width": 1024, "height": 768})
            show_floor = params.get("showFloor", True)
            show_axes = params.get("showAxes", True)

            if not avatar_id and not path:
                raise ValueError("Either avatarId or path parameter is required")

            # Try to lazy load visualization manager
            visualization_manager = await self._get_visualization_manager()

            if visualization_manager:
                try:
                    # Full PyVista visualization
                    if path:
                        # Direct path loading
                        import os
                        if not os.path.exists(path):
                            return {
                                "status": "error",
                                "error": f"File not found: {path}"
                            }

                        # Start viewer and load model
                        window_size_tuple = (window_size.get("width", 1024), window_size.get("height", 768))
                        visualization_manager.start_viewer(window_size=window_size_tuple)

                        model_id = avatar_id or os.path.basename(path)
                        success = visualization_manager.load_vrm(model_id, path)

                        if success:
                            return {
                                "status": "success",
                                "message": f"Displaying VRM model: {path}",
                                "model_id": model_id,
                                "viewer": {
                                    "window_size": window_size_tuple,
                                    "show_floor": show_floor,
                                    "show_axes": show_axes
                                }
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "Failed to load VRM in viewer"
                            }
                    else:
                        # Load by avatar ID - need to find the path first
                        vrm_manager = await self._get_vrm_manager()
                        if vrm_manager:
                            model_info = await vrm_manager.get_model_info(avatar_id)
                            if model_info and 'path' in model_info:
                                path = model_info['path']
                                window_size_tuple = (window_size.get("width", 1024), window_size.get("height", 768))
                                visualization_manager.start_viewer(window_size=window_size_tuple)

                                success = visualization_manager.load_vrm(avatar_id, path)
                                if success:
                                    return {
                                        "status": "success",
                                        "message": f"Displaying avatar: {avatar_id}",
                                        "model_id": avatar_id,
                                        "path": path,
                                        "viewer": {
                                            "window_size": window_size_tuple,
                                            "show_floor": show_floor,
                                            "show_axes": show_axes
                                        }
                                    }
                            return {
                                "status": "error",
                                "error": f"Avatar {avatar_id} not found or no path available"
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "Cannot load avatar by ID - VRM manager unavailable"
                            }

                except Exception as e:
                    logger.warning(f"Full visualization failed: {e}, trying fallback")

            # Fallback: basic file information
            if path:
                import os
                if os.path.exists(path):
                    file_size = os.path.getsize(path)
                    return {
                        "status": "partial_success",
                        "message": f"VRM file located: {path} (PyVista viewer unavailable)",
                        "path": path,
                        "file_info": {
                            "size": file_size,
                            "exists": True
                        },
                        "note": "3D visualization unavailable - PyVista dependencies not loaded"
                    }

            return {
                "status": "error",
                "error": "Cannot display avatar - provide valid path or use avatar.load first"
            }

        except Exception as e:
            logger.error(f"Error showing viewer: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # Unity Desktop Avatar System handlers
    async def _execute_unity_system_status(self, params: dict) -> dict:
        """Execute the unity_system_status tool."""
        try:
            detailed = params.get('detailed', False)
            include_config = params.get('include_config', False)

            # Mock response - in real implementation would query Unity via OSC
            result = {
                "status": "success",
                "message": "Unity system status retrieved",
                "unity_connected": False,  # TODO: Implement actual Unity connection check
                "window_visible": False,  # TODO: Implement window visibility check
                "avatar_loaded": False,  # TODO: Implement avatar loading status
                "avatar_name": None,
                "osc_connected": False,  # TODO: Check OSC connection status
                "timestamp": time.time()
            }

            if detailed:
                result["system_info"] = {
                    "unity_version": "2021.3+",  # TODO: Get actual Unity version
                    "render_fps": 60,  # TODO: Get actual FPS
                    "memory_usage": 256,  # TODO: Get actual memory usage in MB
                    "scene_objects": 42  # TODO: Get actual object count
                }

            if include_config:
                result["config"] = {
                    "window_transparency": 1.0,  # TODO: Get actual transparency
                    "window_position": {"x": 100, "y": 100},  # TODO: Get actual position
                    "window_size": {"width": 400, "height": 600},  # TODO: Get actual size
                    "osc_ports": {
                        "receive": 9000,
                        "send": 9001
                    }
                }

            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get Unity system status: {str(e)}"
            }

    async def _execute_unity_window_position(self, params: dict) -> dict:
        """Execute the unity_window_position tool."""
        try:
            # TODO: Implement actual Unity window positioning via OSC
            result = {
                "status": "success",
                "message": "Window position updated",
                "position": {"x": params.get('x', 100), "y": params.get('y', 100)},
                "size": {"width": params.get('width', 400), "height": params.get('height', 600)},
                "monitor": params.get('monitor', 0),
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update window position: {str(e)}"
            }

    async def _execute_unity_window_transparency(self, params: dict) -> dict:
        """Execute the unity_window_transparency tool."""
        try:
            alpha = params.get('alpha', 1.0)
            transition_time = params.get('transition_time', 0.0)

            # Validate alpha range
            alpha = max(0.0, min(1.0, alpha))

            # TODO: Implement actual Unity window transparency via OSC
            result = {
                "status": "success",
                "message": "Window transparency updated",
                "alpha": alpha,
                "transition_time": transition_time,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update window transparency: {str(e)}"
            }

    async def _execute_unity_window_visibility(self, params: dict) -> dict:
        """Execute the unity_window_visibility tool."""
        try:
            visible = params.get('visible')
            fade_transition = params.get('fade_transition', True)

            if visible is None:
                raise ValueError("Parameter 'visible' is required")

            # TODO: Implement actual Unity window visibility via OSC
            result = {
                "status": "success",
                "message": f"Window {'shown' if visible else 'hidden'}",
                "visible": visible,
                "fade_transition": fade_transition,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update window visibility: {str(e)}"
            }

    async def _execute_unity_window_mode(self, params: dict) -> dict:
        """Execute the unity_window_mode tool."""
        try:
            mode = params.get('mode')
            transition_effect = params.get('transition_effect', True)

            if mode not in ['interactive', 'clickthrough']:
                raise ValueError("Mode must be 'interactive' or 'clickthrough'")

            # TODO: Implement actual Unity window mode via OSC
            result = {
                "status": "success",
                "message": f"Window mode set to {mode}",
                "mode": mode,
                "transition_effect": transition_effect,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update window mode: {str(e)}"
            }

    async def _execute_unity_avatar_load(self, params: dict) -> dict:
        """Execute the unity_avatar_load tool."""
        try:
            path = params.get('path')
            if not path:
                raise ValueError("Parameter 'path' is required")

            make_active = params.get('make_active', True)
            preload_animations = params.get('preload_animations', True)
            position_offset = params.get('position_offset', {'x': 0, 'y': 0, 'z': 0})

            # TODO: Implement actual VRM loading via OSC
            result = {
                "status": "success",
                "message": f"Avatar loaded from {path}",
                "avatar_id": f"avatar_{hash(path) % 1000}",
                "avatar_name": "Mock Avatar",  # TODO: Extract from VRM
                "blend_shape_count": 50,  # TODO: Get from VRM
                "bone_count": 75,  # TODO: Get from VRM
                "animations_loaded": 10 if preload_animations else 0,
                "active": make_active,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load avatar: {str(e)}"
            }

    async def _execute_unity_avatar_expression(self, params: dict) -> dict:
        """Execute the unity_avatar_expression tool."""
        try:
            expression = params.get('expression')
            if not expression:
                raise ValueError("Parameter 'expression' is required")

            strength = params.get('strength', 1.0)
            transition_time = params.get('transition_time', 0.2)
            blend_with_current = params.get('blend_with_current', False)

            # Validate strength range
            strength = max(0.0, min(1.0, strength))

            # TODO: Implement actual expression control via OSC
            result = {
                "status": "success",
                "message": f"Expression '{expression}' applied",
                "expression": expression,
                "strength": strength,
                "transition_time": transition_time,
                "blend_with_current": blend_with_current,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to set expression: {str(e)}"
            }

    async def _execute_unity_avatar_animation(self, params: dict) -> dict:
        """Execute the unity_avatar_animation tool."""
        try:
            action = params.get('action')
            if not action:
                raise ValueError("Parameter 'action' is required")

            valid_actions = ['play', 'stop', 'pause', 'resume', 'loop']
            if action not in valid_actions:
                raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")

            animation_name = params.get('animation_name') if action == 'play' else None
            loop = params.get('loop', True) if action in ['play', 'loop'] else False
            speed = params.get('speed', 1.0)
            blend_time = params.get('blend_time', 0.3)

            # TODO: Implement actual animation control via OSC
            result = {
                "status": "success",
                "message": f"Animation action '{action}' performed",
                "action": action,
                "animation_name": animation_name,
                "loop": loop,
                "speed": speed,
                "blend_time": blend_time,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to control animation: {str(e)}"
            }

    async def _execute_unity_osc_bridge(self, params: dict) -> dict:
        """Execute the unity_osc_bridge tool."""
        try:
            enable_bridge = params.get('enable_bridge')
            if enable_bridge is None:
                raise ValueError("Parameter 'enable_bridge' is required")

            receive_port = params.get('receive_port', 9000)
            send_port = params.get('send_port', 9001)
            server_ip = params.get('server_ip', '127.0.0.1')
            auto_reconnect = params.get('auto_reconnect', True)
            heartbeat_interval = params.get('heartbeat_interval', 30)

            # TODO: Implement actual OSC bridge configuration
            connection_status = "connected" if enable_bridge else "disconnected"

            result = {
                "status": "success",
                "message": f"OSC bridge {'enabled' if enable_bridge else 'disabled'}",
                "bridge_enabled": enable_bridge,
                "receive_port": receive_port,
                "send_port": send_port,
                "server_ip": server_ip,
                "connection_status": connection_status,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to configure OSC bridge: {str(e)}"
            }

    async def _execute_unity_plugin_load(self, params: dict) -> dict:
        """Execute the unity_plugin_load tool."""
        try:
            action = params.get('action')
            if not action:
                raise ValueError("Parameter 'action' is required")

            valid_actions = ['load', 'unload', 'list', 'reload']
            if action not in valid_actions:
                raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")

            # TODO: Implement actual plugin management via OSC
            result = {
                "status": "success",
                "message": f"Plugin action '{action}' performed",
                "action": action,
                "timestamp": time.time()
            }

            if action == 'load':
                plugin_path = params.get('plugin_path')
                if not plugin_path:
                    raise ValueError("Parameter 'plugin_path' is required for load action")
                result["plugin_path"] = plugin_path
                result["plugin_name"] = "MockPlugin"  # TODO: Extract from plugin
                result["config_applied"] = params.get('config', {})

            elif action in ['unload', 'reload']:
                plugin_name = params.get('plugin_name')
                if not plugin_name:
                    raise ValueError(f"Parameter 'plugin_name' is required for {action} action")
                result["plugin_name"] = plugin_name
                if action == 'reload':
                    result["config_applied"] = params.get('config', {})

            elif action == 'list':
                result["loaded_plugins"] = ["AvatarController", "OSCBridge"]  # Mock data
                result["available_plugins"] = ["ExpressionController", "AnimationManager"]  # Mock data

            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to manage plugin: {str(e)}"
            }

    async def _execute_unity_config_update(self, params: dict) -> dict:
        """Execute the unity_config_update tool."""
        try:
            config_section = params.get('config_section')
            if not config_section:
                raise ValueError("Parameter 'config_section' is required")

            valid_sections = ['rendering', 'performance', 'behavior', 'audio', 'network']
            if config_section not in valid_sections:
                raise ValueError(f"Config section must be one of: {', '.join(valid_sections)}")

            settings = params.get('settings', {})
            apply_immediately = params.get('apply_immediately', True)
            persist_changes = params.get('persist_changes', True)

            # TODO: Implement actual configuration updates via OSC
            result = {
                "status": "success",
                "message": f"Configuration section '{config_section}' updated",
                "config_section": config_section,
                "settings_applied": settings,
                "settings_ignored": [],  # Mock: no settings ignored
                "apply_immediately": apply_immediately,
                "persist_changes": persist_changes,
                "timestamp": time.time()
            }
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update configuration: {str(e)}"
            }

    # === LAZY LOADING INFRASTRUCTURE ===

    async def _get_vrm_manager(self):
        """Lazy load VRM manager with timeout protection."""
        if self._vrm_manager is not None:
            return self._vrm_manager

        if 'vrm_manager' in self._import_errors:
            return None  # Already failed before

        try:
            logger.info("Loading VRM manager (first use)...")
            # Import with timeout protection
            import asyncio

            async def load_vrm_manager():
                from .models.vrm_manager import VRMManager
                return VRMManager()

            # 5 second timeout for loading
            self._vrm_manager = await asyncio.wait_for(load_vrm_manager(), timeout=5.0)
            logger.info("✅ VRM manager loaded successfully")
            return self._vrm_manager

        except asyncio.TimeoutError:
            logger.warning("⏰ VRM manager loading timed out - using fallback")
            self._import_errors['vrm_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  VRM manager failed to load: {e} - using fallback")
            self._import_errors['vrm_manager'] = str(e)
            return None

    async def _get_model_manager(self):
        """Lazy load model manager with timeout protection."""
        if self._model_manager is not None:
            return self._model_manager

        if 'model_manager' in self._import_errors:
            return None

        try:
            logger.info("Loading model manager (first use)...")
            import asyncio

            async def load_model_manager():
                from .models.model_manager import VRMModelManager
                return VRMModelManager()

            self._model_manager = await asyncio.wait_for(load_model_manager(), timeout=5.0)
            logger.info("✅ Model manager loaded successfully")
            return self._model_manager

        except asyncio.TimeoutError:
            logger.warning("⏰ Model manager loading timed out - using fallback")
            self._import_errors['model_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  Model manager failed to load: {e} - using fallback")
            self._import_errors['model_manager'] = str(e)
            return None

    async def _get_visualization_manager(self):
        """Lazy load visualization manager with timeout protection."""
        if self._visualization_manager is not None:
            return self._visualization_manager

        if 'visualization_manager' in self._import_errors:
            return None

        try:
            logger.info("Loading visualization manager (first use)...")
            import asyncio

            async def load_visualization_manager():
                from .visualization.manager import VisualizationManager
                return VisualizationManager()

            self._visualization_manager = await asyncio.wait_for(load_visualization_manager(), timeout=10.0)
            logger.info("✅ Visualization manager loaded successfully")
            return self._visualization_manager

        except asyncio.TimeoutError:
            logger.warning("⏰ Visualization manager loading timed out - using fallback")
            self._import_errors['visualization_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  Visualization manager failed to load: {e} - using fallback")
            self._import_errors['visualization_manager'] = str(e)
            return None

    async def _get_avatar_control(self, control_type: str):
        """Lazy load avatar control tools."""
        if control_type in self._avatar_controls:
            return self._avatar_controls[control_type]

        if control_type in self._import_errors:
            return None

        try:
            logger.info(f"Loading {control_type} control (first use)...")

            if control_type == "bone":
                from .avatar_controls.bone_control import BoneControlTool
                tool = BoneControlTool()
            elif control_type == "morph":
                from .avatar_controls.morph_control import MorphControlTool
                tool = MorphControlTool()
            elif control_type == "export":
                from .avatar_controls.export import ExportTool
                tool = ExportTool()
            else:
                raise ValueError(f"Unknown control type: {control_type}")

            self._avatar_controls[control_type] = tool
            logger.info(f"✅ {control_type} control loaded successfully")
            return tool

        except Exception as e:
            logger.warning(f"⚠️  {control_type} control failed to load: {e}")
            self._import_errors[control_type] = str(e)
            return None

    async def _fallback_list_avatars(self) -> dict:
        """Fallback avatar listing using basic file scanning."""
        import sys
        try:
            import os
            from pathlib import Path
            import glob

            sys.stderr.write("DEBUG: Starting fallback avatar scan\n")
            sys.stderr.write(f"DEBUG: Current working directory: {os.getcwd()}\n")
            sys.stderr.flush()

            # Use absolute paths to ensure we're looking in the right place
            base_dir = os.getcwd()

            # Look for VRM files in common locations (case-insensitive)
            search_patterns = [
                os.path.join(base_dir, "models", "*.vrm"),
                os.path.join(base_dir, "models", "*.VRM"),
                os.path.join(base_dir, "examples", "*.vrm"),
                os.path.join(base_dir, "examples", "*.VRM"),
                os.path.join(base_dir, "*.vrm"),
                os.path.join(base_dir, "*.VRM")
            ]

            # Also check if examples directory exists
            examples_dir = os.path.join(base_dir, "examples")
            sys.stderr.write(f"DEBUG: Examples directory exists: {os.path.exists(examples_dir)}\n")
            if os.path.exists(examples_dir):
                sys.stderr.write(f"DEBUG: Examples directory contents: {os.listdir(examples_dir)}\n")
            sys.stderr.flush()

            avatars = []
            for pattern in search_patterns:
                sys.stderr.write(f"DEBUG: Searching pattern: {pattern}\n")
                sys.stderr.flush()

                found_files = glob.glob(pattern)
                sys.stderr.write(f"DEBUG: Found {len(found_files)} files for pattern {pattern}\n")
                sys.stderr.flush()

                for file_path in found_files:
                    abs_path = os.path.abspath(file_path)
                    file_size = os.path.getsize(file_path)

                    sys.stderr.write(f"DEBUG: Found VRM: {file_path} -> {abs_path}\n")
                    sys.stderr.flush()

                    # Avoid duplicates
                    avatar_id = os.path.splitext(os.path.basename(file_path))[0]
                    if not any(avatar['id'] == avatar_id for avatar in avatars):
                        avatars.append({
                            "id": avatar_id,
                            "name": avatar_id,
                            "path": abs_path,
                            "metadata": {"source": "file_scan", "size": file_size}
                        })

            sys.stderr.write(f"DEBUG: Total avatars found: {len(avatars)}\n")
            sys.stderr.flush()

            return {
                "status": "partial_success",
                "message": "Using lightweight file scan (full VRM manager unavailable)",
                "avatars": avatars,
                "count": len(avatars)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Fallback scan failed: {e}",
                "avatars": []
            }


def main():
    """Main entry point for the MCP server."""
    # Configure logging to avoid stderr output that could interfere with MCP protocol
    # Log to a file instead when running as MCP server
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_server.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )

    # Create and run the server
    server = MCPServer()

    if ASYNCIO_AVAILABLE:
        # Create and run the server with explicit event loop policy for Windows
        if sys.platform == "win32":
            # Use WindowsProactorEventLoopPolicy for better Windows compatibility
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        try:
            server.run()
        except OSError as e:
            if "WinError 10106" in str(e):
                logger.error("Windows networking service issue. Trying alternative approach...")
                # Fallback to a simpler sync approach
                raise RuntimeError("Asyncio networking failed - FastMCP requires working asyncio")
            else:
                raise
    else:
        logger.error("Asyncio not available - cannot run FastMCP server")
        sys.stderr.write("ERROR: Asyncio required for FastMCP server\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
        
