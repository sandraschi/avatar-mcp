"""
Core Tools for AvatarMCP - Basic Avatar Operations

This module contains fundamental avatar operations including loading, listing,
basic animation control, and core avatar management functionality.
"""

import os
import time
from typing import Dict, Any


class CoreTools:
    """Container for all core avatar MCP tools."""

    def __init__(self, mcp_server):
        """Initialize core tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all core avatar tools with the MCP server."""
        # Register avatar_list tool
        @self.mcp_server.mcp.tool()
        def avatar_list(params: Dict[str, Any]) -> Dict[str, Any]:
            """List all available avatars in the system with metadata.

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
                        logger.warning("No VRM files found - check models directory")
                    else:
                        logger.info(f"Found {avatars['count']} avatars")

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
            """
            # Implementation for avatar_list
            import os
            import time
            start_time = time.time()

            try:
                # Get models directory from project root (relative to this script)
                # Script is at src/avatarmcp/tools/core/core_tools.py
                # Project root is two levels up: ../../../../
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
                models_dir = os.path.join(project_root, "models")

                if not os.path.exists(models_dir):
                    return {
                        'status': 'error',
                        'message': f'Models directory not found: {models_dir}',
                        'avatars': [],
                        'count': 0,
                        'scan_time': time.time() - start_time
                    }

                avatars = []
                for root, dirs, files in os.walk(models_dir):
                    for file in files:
                        if file.lower().endswith('.vrm'):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, models_dir)

                            # Create avatar ID from filename (without extension)
                            avatar_id = os.path.splitext(file)[0]
                            avatar_name = avatar_id.replace('_', ' ').replace('-', ' ').title()

                            try:
                                stat = os.stat(full_path)
                                avatars.append({
                                    'id': avatar_id,
                                    'name': avatar_name,
                                    'path': rel_path,
                                    'size': stat.st_size,
                                    'modified': stat.st_mtime,
                                    'full_path': full_path
                                })
                            except OSError:
                                # Skip files we can't stat
                                continue

                return {
                    'status': 'success',
                    'avatars': avatars,
                    'count': len(avatars),
                    'scan_time': time.time() - start_time
                }

            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Failed to scan avatars: {str(e)}',
                    'avatars': [],
                    'count': 0,
                    'scan_time': time.time() - start_time
                }

        # Register avatar_load tool
        @self.mcp_server.mcp.tool()
        def avatar_load(params: Dict[str, Any]) -> Dict[str, Any]:
            """Load a VRM avatar into the system for manipulation and animation.

            Loads a specified VRM avatar file from the models directory and prepares
            it for animation, expression control, and interaction. This is the primary
            way to make an avatar available for use in the system.

            Parameters:
                avatar_id: Identifier of the avatar to load (required)
                    - Must match an ID from avatar_list results
                    - Case-sensitive avatar identifier
                    - Corresponds to VRM filename without extension
                load_options: Optional loading configuration (optional)
                    - lighting_setup: Initial lighting configuration
                    - animation_state: Initial pose/animation to apply
                    - expression_preset: Initial facial expression
                    - performance_mode: Quality vs performance trade-off

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: ID of the loaded avatar
                    - load_time: Time taken to load the avatar
                    - model_info: Basic information about the loaded model
                    - capabilities: What features are available for this avatar

            Usage:
                Use this tool to activate avatars for animation and interaction.
                All animation and expression tools require an avatar to be loaded first.

            Examples:
                Basic avatar loading:
                    result = await avatar_load({'avatar_id': 'nekomimi_chan'})
                    # Loads Nekomimi-chan and makes her ready for animation

                Load with custom options:
                    result = await avatar_load({
                        'avatar_id': 'hero_character',
                        'load_options': {
                            'lighting_setup': 'dramatic',
                            'animation_state': 'power_pose',
                            'performance_mode': 'high_quality'
                        }
                    })
                    # Loads hero with dramatic lighting and power pose

                Error handling:
                    result = await avatar_load({'avatar_id': 'nonexistent'})
                    if result['status'] == 'error':
                        logger.error(f"Failed to load avatar: {result['message']}")
                        # Check avatar exists with avatar_list first

                Check loading success:
                    load_result = await avatar_load({'avatar_id': 'anime_girl'})
                    if load_result['status'] == 'success':
                        logger.info(f"Successfully loaded {load_result['avatar_id']}")
                        logger.info(f"Model has {len(load_result['capabilities'])} features")

            Raises:
                ValueError: If avatar_id is invalid or malformed
                FileNotFoundError: If VRM file cannot be found
                RuntimeError: If avatar loading system is unavailable

            Notes:
                - Loading large avatars may take several seconds
                - Multiple avatars can be loaded simultaneously
                - Loaded avatars consume memory and processing resources
                - Use avatar_unload to free resources when done
                - Loading status can be checked with avatar_get_metadata

            See Also:
                - avatar_list: Discover available avatars before loading
                - avatar_unload: Remove loaded avatar from memory
                - avatar_get_metadata: Get detailed information about loaded avatar
                - animation_play: Animate loaded avatar
            """
            # Implementation for avatar_load
            avatar_id = params.get('avatar_id')
            if not avatar_id:
                return {
                    'status': 'error',
                    'message': 'avatar_id parameter is required'
                }

            # Find the full path to the VRM file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
            models_dir = os.path.join(project_root, "models")
            vrm_path = os.path.join(models_dir, f"{avatar_id}.vrm")

            if not os.path.exists(vrm_path):
                return {
                    'status': 'error',
                    'message': f'VRM file not found: {vrm_path}'
                }

            # Send OSC message to Unity desktop avatar to load the avatar
            osc_address = "/avatar/load"
            if self.mcp_server._send_osc_message(osc_address, str(vrm_path)):
                return {
                    'status': 'success',
                    'avatar_id': avatar_id,
                    'vrm_path': vrm_path,
                    'osc_message': f'{osc_address} {vrm_path}',
                    'capabilities': [
                        'animation',
                        'expressions',
                        'bone_control',
                        'morph_control'
                    ]
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send load command to Unity desktop avatar'
                }

        # Register animation_play tool
        @self.mcp_server.mcp.tool()
        def animation_play(params: Dict[str, Any]) -> Dict[str, Any]:
            """Play an animation on a loaded avatar.

            Triggers playback of a specified animation on a loaded avatar with
            configurable playback options including looping, speed control, and blending.

            Parameters:
                avatar_id: Avatar to animate (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                animation_name: Name of animation to play (required)
                    - Must be available for the avatar
                    - Case-sensitive animation identifier
                playback_options: Animation playback configuration (optional)
                    - loop: Whether to loop the animation (default: False)
                    - speed: Playback speed multiplier (default: 1.0)
                    - blend_time: Transition blend duration in seconds (default: 0.5)
                    - layer: Animation layer for blending (default: "base")
                    - priority: Animation priority for conflict resolution (default: "normal")

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: Avatar being animated
                    - animation_name: Animation that was started
                    - playback_id: Unique identifier for this playback instance
                    - duration: Expected animation duration in seconds

            Usage:
                Use this tool to bring avatars to life with movement and expression.
                Essential for creating dynamic, engaging avatar experiences.

            Examples:
                Basic animation playback:
                    result = await animation_play({
                        'avatar_id': 'nekomimi_chan',
                        'animation_name': 'wave_hello'
                    })
                    # Plays wave animation once on Nekomimi-chan

                Looping dance animation:
                    result = await animation_play({
                        'avatar_id': 'dancer',
                        'animation_name': 'disco_dance',
                        'playback_options': {
                            'loop': True,
                            'speed': 1.2,
                            'blend_time': 1.0
                        }
                    })
                    # Plays dance animation in loop at 120% speed

                Layered animation with blending:
                    result = await animation_play({
                        'avatar_id': 'character',
                        'animation_name': 'subtle_nod',
                        'playback_options': {
                            'layer': 'expressions',
                            'priority': 'high',
                            'blend_time': 0.3
                        }
                    })
                    # Plays subtle nod on expression layer with high priority

                Error handling:
                    result = await animation_play({
                        'avatar_id': 'loaded_avatar',
                        'animation_name': 'nonexistent_animation'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Animation failed: {result['message']}")
                    # Check animation exists for the avatar

                Animation sequencing:
                    await animation_play({'avatar_id': 'actor', 'animation_name': 'bow'})
                    time.sleep(2)  # Wait for bow to complete
                    await animation_play({'avatar_id': 'actor', 'animation_name': 'dance'})

            Raises:
                ValueError: If avatar_id or animation_name invalid
                RuntimeError: If animation system unavailable
                KeyError: If avatar not loaded or animation not found

            Notes:
                - Animations play asynchronously - don't block other operations
                - Multiple animations can play simultaneously on different layers
                - Higher priority animations can interrupt lower priority ones
                - Blend time controls smooth transitions between animations
                - Speed affects both playback rate and blend timing
                - Use animation_stop to halt playing animations

            See Also:
                - animation_stop: Stop playing animation
                - animation_list: Discover available animations
                - avatar_load: Load avatar before animating
                - animation_sequence_create: Create complex animation sequences
            """
            # Implementation for animation_play
            avatar_id = params.get('avatar_id')
            animation_name = params.get('animation_name')
            loop = params.get('loop', False)
            speed = params.get('speed', 1.0)

            if not avatar_id or not animation_name:
                return {
                    'status': 'error',
                    'message': 'Both avatar_id and animation_name parameters are required'
                }

            # Send OSC message to Unity desktop avatar to play animation
            osc_address = "/avatar/animation/play"
            if self.mcp_server._send_osc_message(osc_address, animation_name, int(loop), float(speed)):
                return {
                    'status': 'success',
                    'avatar_id': avatar_id,
                    'animation_name': animation_name,
                    'loop': loop,
                    'speed': speed,
                    'osc_message': f'{osc_address} {animation_name} {int(loop)} {float(speed)}'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send animation play command to Unity desktop avatar'
                }

        # Register bone_control tool
        @self.mcp_server.mcp.tool()
        def bone_control(params: Dict[str, Any]) -> Dict[str, Any]:
            """Control individual bones of an avatar for precise posing.

            Manipulates specific bones of a loaded avatar to achieve precise poses,
            gestures, and movements that go beyond canned animations.

            Parameters:
                avatar_id: Avatar to control (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                bone_name: Name of bone to control (required)
                    - Must be a valid bone in the avatar's skeleton
                    - Common bones: "head", "neck", "left_arm", "right_arm", etc.
                bone_transform: New transformation for the bone (required)
                    - position: New position as [x, y, z] coordinates
                    - rotation: New rotation as quaternion [w, x, y, z] or euler angles
                    - scale: New scale as [x, y, z] multipliers
                control_options: Additional control parameters (optional)
                    - coordinate_space: "local" or "world" coordinate system
                    - interpolation_mode: "immediate", "linear", "smooth"
                    - duration: Time in seconds for the movement
                    - blend_weight: How strongly to apply the control (0.0-1.0)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: Avatar being controlled
                    - bone_name: Bone that was controlled
                    - transform_applied: The transform that was applied
                    - control_id: Unique identifier for this control instance

            Usage:
                Use this tool for fine-grained control over avatar posing and gestures,
                enabling precise movements that canned animations can't achieve.

            Examples:
                Head rotation for attention:
                    result = await bone_control({
                        'avatar_id': 'listener',
                        'bone_name': 'head',
                        'bone_transform': {
                            'rotation': {'y': 0.3}  # Look slightly to the side
                        },
                        'control_options': {
                            'interpolation_mode': 'smooth',
                            'duration': 0.5
                        }
                    })
                    # Turns head smoothly to show attention

                Arm gesture with precise positioning:
                    result = await bone_control({
                        'avatar_id': 'speaker',
                        'bone_name': 'left_arm',
                        'bone_transform': {
                            'rotation': {'x': 0.2, 'z': -0.1},
                            'position': {'x': 0.05}
                        },
                        'control_options': {
                            'coordinate_space': 'local',
                            'blend_weight': 0.8
                        }
                    })
                    # Precise arm positioning for gesture

                Spine adjustment for posture:
                    result = await bone_control({
                        'avatar_id': 'character',
                        'bone_name': 'spine',
                        'bone_transform': {
                            'rotation': {'z': -0.1}  # Slight lean back
                        },
                        'control_options': {
                            'interpolation_mode': 'linear',
                            'duration': 1.0
                        }
                    })
                    # Adjusts posture with smooth interpolation

                Error handling:
                    result = await bone_control({
                        'avatar_id': 'avatar',
                        'bone_name': 'nonexistent_bone',
                        'bone_transform': {'rotation': {'x': 0.1}}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Bone control failed: {result['message']}")
                    # Check bone name exists in avatar skeleton

                Sequential bone controls:
                    # Control multiple bones for complex pose
                    await bone_control({'avatar_id': 'dancer', 'bone_name': 'left_arm', 'bone_transform': {'rotation': {'x': 1.5}}})
                    await bone_control({'avatar_id': 'dancer', 'bone_name': 'right_arm', 'bone_transform': {'rotation': {'x': -1.5}}})
                    await bone_control({'avatar_id': 'dancer', 'bone_name': 'torso', 'bone_transform': {'rotation': {'z': 0.3}}})

            Raises:
                ValueError: If avatar_id, bone_name, or transform invalid
                RuntimeError: If bone control system unavailable
                KeyError: If avatar not loaded or bone not found

            Notes:
                - Bone control provides direct manipulation of avatar skeleton
                - Coordinate spaces affect how transforms are interpreted
                - Interpolation modes control movement smoothness
                - Blend weights allow partial application of controls
                - Controls can be combined with animations for enhanced results
                - Use avatar bone hierarchy knowledge for best results

            See Also:
                - morph_control: Control facial expressions and body shapes
                - animation_play: Play canned animations
                - interactive_pose_control: Real-time pose manipulation
                - avatar_load: Load avatar before bone control
            """
            # Implementation for bone_control
            avatar_id = params.get('avatar_id')
            bone_name = params.get('bone_name')
            rotation = params.get('rotation')
            translation = params.get('translation')

            if not avatar_id or not bone_name:
                return {
                    'status': 'error',
                    'message': 'avatar_id and bone_name parameters are required'
                }

            if not rotation and not translation:
                return {
                    'status': 'error',
                    'message': 'Either rotation or translation parameter must be provided'
                }

            # Send OSC message to Unity desktop avatar for bone control
            success = True
            messages_sent = []

            if rotation:
                # Send rotation as quaternion (x, y, z, w)
                if isinstance(rotation, list) and len(rotation) == 4:
                    osc_address = f"/avatar/bone/{bone_name}/rotation"
                    if self.mcp_server._send_osc_message(osc_address, *rotation):
                        messages_sent.append(f'{osc_address} {rotation}')
                    else:
                        success = False
                else:
                    return {
                        'status': 'error',
                        'message': 'rotation must be a list of 4 quaternion values [x, y, z, w]'
                    }

            if translation:
                # Send translation as vector (x, y, z)
                if isinstance(translation, list) and len(translation) == 3:
                    osc_address = f"/avatar/bone/{bone_name}/translation"
                    if self.mcp_server._send_osc_message(osc_address, *translation):
                        messages_sent.append(f'{osc_address} {translation}')
                    else:
                        success = False
                else:
                    return {
                        'status': 'error',
                        'message': 'translation must be a list of 3 vector values [x, y, z]'
                    }

            if success:
                return {
                    'status': 'success',
                    'avatar_id': avatar_id,
                    'bone_name': bone_name,
                    'applied_rotation': rotation,
                    'applied_translation': translation,
                    'osc_messages': messages_sent
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send bone control commands to Unity desktop avatar'
                }

        # Register morph_control tool
        @self.mcp_server.mcp.tool()
        def morph_control(params: Dict[str, Any]) -> Dict[str, Any]:
            """Control morph targets (blend shapes) for facial expressions and body deformation.

            Manipulates blend shape morph targets on a loaded avatar to create facial
            expressions, body deformations, and other shape-based animations.

            Parameters:
                avatar_id: Avatar to control morphs for (required)
                    - Must be loaded with avatar_load
                    - Must have blend shape morph targets
                    - Case-sensitive avatar identifier
                morph_targets: Dictionary of morph target names and weights (required)
                    - Keys are morph target names (e.g., "mouth_smile", "eye_blink")
                    - Values are weights between 0.0 and 1.0
                    - Multiple morphs can be controlled simultaneously
                control_options: Morph control configuration (optional)
                    - interpolation_mode: "immediate", "linear", "smooth"
                    - duration: Time in seconds for morph changes
                    - blend_mode: How multiple morphs interact ("additive", "override")
                    - priority: Control priority for conflict resolution

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: Avatar being controlled
                    - morphs_applied: List of morph targets that were set
                    - control_id: Unique identifier for this control instance

            Usage:
                Use this tool to create rich facial expressions and body deformations
                that bring avatars to life with emotional and physical expression.

            Examples:
                Basic facial expression:
                    result = await morph_control({
                        'avatar_id': 'character',
                        'morph_targets': {
                            'mouth_smile': 0.8,
                            'eye_happy': 0.6,
                            'brow_raised': 0.4
                        },
                        'control_options': {
                            'interpolation_mode': 'smooth',
                            'duration': 0.3
                        }
                    })
                    # Creates happy facial expression with smooth transition

                Emotional expression combination:
                    result = await morph_control({
                        'avatar_id': 'actor',
                        'morph_targets': {
                            'mouth_frown': 0.7,
                            'brow_furrowed': 0.5,
                            'eye_sad': 0.8,
                            'cheek_tense': 0.3
                        },
                        'control_options': {
                            'blend_mode': 'additive',
                            'duration': 1.0
                        }
                    })
                    # Combines multiple morphs for complex sad expression

                Body deformation for gesture:
                    result = await morph_control({
                        'avatar_id': 'flexible_character',
                        'morph_targets': {
                            'body_flex': 0.6,
                            'muscle_tense': 0.4,
                            'posture_confident': 0.7
                        }
                    })
                    # Applies body morphs for confident posture

                Error handling:
                    result = await morph_control({
                        'avatar_id': 'avatar',
                        'morph_targets': {'nonexistent_morph': 0.5}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Morph control failed: {result['message']}")
                    # Check morph target names exist for avatar

                Sequential expressions:
                    # Happy to surprised transition
                    await morph_control({'avatar_id': 'actor', 'morph_targets': {'mouth_smile': 1.0}})
                    time.sleep(2)
                    await morph_control({'avatar_id': 'actor', 'morph_targets': {'mouth_open': 0.8, 'eye_wide': 1.0}})

            Raises:
                ValueError: If avatar_id or morph_targets invalid
                RuntimeError: If morph control system unavailable
                KeyError: If avatar not loaded or morph target not found

            Notes:
                - Morph targets provide shape-based deformation control
                - Blend modes determine how multiple morphs interact
                - Interpolation provides smooth transitions between expressions
                - Morph weights can be animated over time for dynamic expressions
                - Some avatars may have limited or no morph targets available
                - Use avatar metadata to discover available morph targets

            See Also:
                - bone_control: Control skeletal posing
                - emotion_micro_expressions: Apply subtle emotional cues
                - avatar_load: Load avatar before morph control
                - animation_play: Combine with animation for full control
            """
            # Implementation for morph_control
            avatar_id = params.get('avatar_id')
            morph_name = params.get('morph_name')
            weight = params.get('weight', 1.0)

            if not avatar_id or morph_name is None:
                return {
                    'status': 'error',
                    'message': 'avatar_id and morph_name parameters are required'
                }

            if not isinstance(weight, (int, float)) or not (0.0 <= weight <= 1.0):
                return {
                    'status': 'error',
                    'message': 'weight must be a number between 0.0 and 1.0'
                }

            # Send OSC message to Unity desktop avatar for morph control
            osc_address = f"/avatar/expression/blendshape"
            if self.mcp_server._send_osc_message(osc_address, morph_name, float(weight)):
                return {
                    'status': 'success',
                    'avatar_id': avatar_id,
                    'morph_name': morph_name,
                    'applied_weight': weight,
                    'osc_message': f'{osc_address} {morph_name} {float(weight)}'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send morph control command to Unity desktop avatar'
                }

        # Register avatar_export tool
        @self.mcp_server.mcp.tool()
        def avatar_export(params: Dict[str, Any]) -> Dict[str, Any]:
            """Export avatar in various formats with current pose and configuration.

            Saves the current state of a loaded avatar including pose, morphs, and
            configuration to a file for later use or sharing.

            Parameters:
                avatar_id: Avatar to export (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                export_path: File path for exported avatar (required)
                    - Full path including filename and extension
                    - Supported formats: .vrm, .gltf, .glb, .fbx, .obj
                    - Directory must exist and be writable
                export_options: Export configuration options (optional)
                    - format: Output format override (if not determined by extension)
                    - include_animations: Include current animation state
                    - include_morphs: Include current morph target values
                    - include_textures: Include texture data inline
                    - optimize_meshes: Apply mesh optimization
                    - compression_level: File compression (0-9, higher = smaller files)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - avatar_id: Avatar that was exported
                    - export_path: Path where avatar was saved
                    - file_size: Size of exported file in bytes
                    - export_time: Time taken to complete export
                    - format_used: Format of the exported file

            Usage:
                Use this tool to save avatar states, create backups, or prepare
                avatars for sharing and external use.

            Examples:
                Basic VRM export with current state:
                    result = await avatar_export({
                        'avatar_id': 'nekomimi_chan',
                        'export_path': '/exports/nekomimi_current.vrm'
                    })
                    # Exports Nekomimi-chan with current pose and morphs

                Optimized GLTF export:
                    result = await avatar_export({
                        'avatar_id': 'character',
                        'export_path': '/exports/character_optimized.gltf',
                        'export_options': {
                            'include_animations': True,
                            'include_morphs': True,
                            'optimize_meshes': True,
                            'compression_level': 6
                        }
                    })
                    # Exports with animations, morphs, and optimization

                FBX export for game engines:
                    result = await avatar_export({
                        'avatar_id': 'game_character',
                        'export_path': '/exports/game_character.fbx',
                        'export_options': {
                            'format': 'fbx',
                            'include_animations': True,
                            'include_textures': False
                        }
                    })
                    # Exports in FBX format for Unity/Unreal

                Error handling:
                    result = await avatar_export({
                        'avatar_id': 'avatar',
                        'export_path': '/readonly/readonly.vrm'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Export failed: {result['message']}")
                    # Check export path is writable

                Batch export preparation:
                    avatars = ['char1', 'char2', 'char3']
                    for avatar_id in avatars:
                        result = await avatar_export({
                            'avatar_id': avatar_id,
                            'export_path': f'/exports/{avatar_id}_backup.vrm'
                        })
                        if result['status'] == 'success':
                            logger.info(f"Exported {avatar_id}")

            Raises:
                ValueError: If avatar_id or export_path invalid
                FileNotFoundError: If avatar not loaded
                PermissionError: If export path not writable
                RuntimeError: If export system unavailable

            Notes:
                - Export preserves current avatar state including pose and morphs
                - Different formats have different capabilities and file sizes
                - Optimization can reduce file size but may affect quality
                - Export operations may take time for complex avatars
                - Use appropriate formats for target applications
                - Exported files are standalone and don't require AvatarMCP to view

            See Also:
                - avatar_load: Load avatar before exporting
                - avatar_list: Discover avatars to export
                - animation_play: Set up desired pose before export
                - morph_control: Apply morphs before export
            """
            # Implementation for avatar_export
            avatar_id = params.get('avatar_id')
            export_format = params.get('export_format', 'gltf')
            output_path = params.get('output_path')
            include_pose = params.get('include_pose', True)

            if not avatar_id:
                return {
                    'status': 'error',
                    'message': 'avatar_id parameter is required'
                }

            if not output_path:
                return {
                    'status': 'error',
                    'message': 'output_path parameter is required'
                }

            # Send OSC message to Unity desktop avatar for export
            osc_address = "/avatar/export"
            export_config = f"{export_format},{output_path},{int(include_pose)}"
            if self.mcp_server._send_osc_message(osc_address, export_config):
                return {
                    'status': 'success',
                    'avatar_id': avatar_id,
                    'export_format': export_format,
                    'output_path': output_path,
                    'include_pose': include_pose,
                    'osc_message': f'{osc_address} {export_config}'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send export command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def bone_control(params: Dict[str, Any]) -> Dict[str, Any]:
            """Control individual bones for posing and animation.

            Manipulates specific bones in the avatar's skeleton to create poses,
            gestures, and animations. Essential for creating natural character movements
            and expressions through direct bone manipulation.

            Parameters:
                bone_name (str): Name of the bone to control (e.g., 'head', 'left_arm', 'spine')
                rotation (dict, optional): Rotation as quaternion {'x': float, 'y': float, 'z': float, 'w': float}
                translation (dict, optional): Translation vector {'x': float, 'y': float, 'z': float}
                scale (dict, optional): Scale vector {'x': float, 'y': float, 'z': float}
                relative (bool, optional): Whether transform is relative to parent bone (default: True)
                smooth (bool, optional): Whether to interpolate movement smoothly (default: True)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - bone_name: Name of the controlled bone
                    - transform_applied: Type of transform applied
                    - current_pose: Current bone transform state
                    - affected_children: Number of child bones affected
                    - animation_time: Time taken to apply pose change

            Usage:
                Pose the avatar's head:
                    result = await bone_control({
                        'bone_name': 'head',
                        'rotation': {'x': 0.0, 'y': 0.1, 'z': 0.0, 'w': 0.995}
                    })

                Move the left arm:
                    result = await bone_control({
                        'bone_name': 'left_arm',
                        'rotation': {'x': 0.2, 'y': 0.0, 'z': 0.0, 'w': 0.98},
                        'translation': {'x': 0.1, 'y': 0.0, 'z': 0.0}
                    })

            Notes:
                - Bone names follow VRM/humanoid naming conventions
                - Rotations use quaternion representation for smooth interpolation
                - Transforms can be absolute or relative to parent bones
                - Smooth interpolation prevents jarring pose changes
                - Child bones automatically follow parent transformations
                - Pose changes persist until explicitly reset

            Examples:
                Head rotation:
                    await bone_control({'bone_name': 'head', 'rotation': {'x': 0, 'y': 0.1, 'z': 0, 'w': 0.995}})

                Arm gesture:
                    await bone_control({'bone_name': 'left_arm', 'rotation': {'x': 0.3, 'y': 0, 'z': 0, 'w': 0.95}})

            See Also:
                - animation_play: For pre-defined animation sequences
                - morph_control: For facial expressions and blendshapes
            """
            try:
                bone_name = params.get('bone_name', '')
                if not bone_name:
                    return {
                        'status': 'error',
                        'message': 'bone_name parameter is required'
                    }

                # Handle rotation
                if 'rotation' in params:
                    rot = params['rotation']
                    if isinstance(rot, dict) and all(k in rot for k in ['x', 'y', 'z', 'w']):
                        # Send quaternion rotation
                        osc_address = f"/avatar/bone/{bone_name}/rotation"
                        self.mcp_server._send_osc_message(osc_address,
                                                        rot['x'], rot['y'], rot['z'], rot['w'])
                        return {
                            'status': 'success',
                            'message': f'Applied rotation to bone {bone_name}',
                            'bone_name': bone_name,
                            'transform_type': 'rotation',
                            'rotation': rot
                        }

                # Handle translation
                if 'translation' in params:
                    trans = params['translation']
                    if isinstance(trans, dict) and all(k in trans for k in ['x', 'y', 'z']):
                        # Send translation
                        osc_address = f"/avatar/bone/{bone_name}/translation"
                        self.mcp_server._send_osc_message(osc_address,
                                                        trans['x'], trans['y'], trans['z'])
                        return {
                            'status': 'success',
                            'message': f'Applied translation to bone {bone_name}',
                            'bone_name': bone_name,
                            'transform_type': 'translation',
                            'translation': trans
                        }

                return {
                    'status': 'error',
                    'message': 'No valid rotation or translation parameters provided'
                }

            except Exception as e:
                logger.error(f"Bone control failed: {e}")
                return {
                    'status': 'error',
                    'message': f'Bone control failed: {str(e)}'
                }
