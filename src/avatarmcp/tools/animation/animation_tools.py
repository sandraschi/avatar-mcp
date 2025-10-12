"""
Animation Tools for AvatarMCP - Advanced Animation & Choreography

This module contains tools for advanced animation control, choreography,
and complex animation sequences for VRM avatars.
"""

import os
import time
from typing import Dict, Any, List


class AnimationTools:
    """Container for all animation-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize animation tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all animation tools with the MCP server."""
        # Register animation_sequence_create tool
        @self.mcp_server.mcp.tool()
        def animation_sequence_create(params: Dict[str, Any]) -> Dict[str, Any]:
            """Create complex multi-step animation sequences for avatars.

            Defines choreographed animation sequences with timing, transitions,
            and blending for professional avatar performances. Perfect for creating
            dance routines, storytelling sequences, and interactive performances
            that go beyond simple single animations.

            Parameters:
                sequence_name: Unique name for the animation sequence (required)
                    - Case-sensitive identifier for the sequence
                    - Must be unique within the avatar system
                    - Used to reference the sequence in playback
                steps: Array of animation steps with detailed timing (required)
                    - Each step defines an animation segment
                    - Must contain at least one step
                    - Steps execute in array order
                    - Supports overlapping/blended transitions
                loop: Whether the sequence should repeat indefinitely (default: False)
                    - True = sequence loops continuously
                    - False = sequence plays once then stops
                    - Loop point is at the end of the last step
                transitions: Timing and blending settings between steps (optional)
                    - Defines how steps blend into each other
                    - Controls transition duration and easing
                    - Prevents jarring animation cuts
                avatar_id: Specific avatar to create sequence for (optional)
                    - If provided, validates animations exist for this avatar
                    - If not provided, sequence can be used with any compatible avatar
                    - Allows avatar-specific sequence optimization

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - sequence_name: Name of the created sequence
                    - steps_count: Number of steps in the sequence
                    - total_duration: Total duration of the sequence in seconds
                    - loop_enabled: Whether looping is enabled
                    - avatar_optimized: Avatar ID if sequence was optimized for specific avatar
                    - sequence_id: Unique identifier for the sequence
                    - created_at: Timestamp when sequence was created

            Usage:
                Use this tool to create complex, multi-step animation sequences that
                tell stories, perform dances, or create interactive experiences.
                Essential for professional avatar choreography and performance art.

            Examples:
                Create a simple dance sequence:
                    result = await animation_sequence_create({
                        'sequence_name': 'happy_dance',
                        'steps': [
                            {
                                'animation': 'Idle',
                                'duration': 1.0,
                                'blend_in': 0.3,
                                'weight': 1.0
                            },
                            {
                                'animation': 'DanceTwist',
                                'duration': 2.0,
                                'blend_in': 0.5,
                                'weight': 1.0
                            },
                            {
                                'animation': 'DanceSpin',
                                'duration': 1.5,
                                'blend_in': 0.3,
                                'weight': 1.0
                            }
                        ],
                        'loop': True
                    })
                    # Creates a looping dance sequence

                Create storytelling sequence with transitions:
                    result = await animation_sequence_create({
                        'sequence_name': 'story_greeting',
                        'steps': [
                            {'animation': 'Idle', 'duration': 0.5},
                            {'animation': 'WaveHello', 'duration': 1.5},
                            {'animation': 'Idle', 'duration': 1.0},
                            {'animation': 'Thinking', 'duration': 2.0},
                            {'animation': 'NodYes', 'duration': 1.0}
                        ],
                        'transitions': {
                            'default_blend_time': 0.3,
                            'easing': 'smooth'
                        }
                    })
                    # Creates a narrative sequence with smooth transitions

                Avatar-specific sequence:
                    result = await animation_sequence_create({
                        'sequence_name': 'robot_moves',
                        'avatar_id': 'robot_avatar',
                        'steps': [
                            {'animation': 'RobotWalk', 'duration': 3.0},
                            {'animation': 'RobotDance', 'duration': 2.0},
                            {'animation': 'RobotIdle', 'duration': 1.0}
                        ]
                    })
                    # Creates sequence optimized for robot avatar

                Complex choreography with weights:
                    result = await animation_sequence_create({
                        'sequence_name': 'layered_performance',
                        'steps': [
                            {
                                'animation': 'WalkCycle',
                                'duration': 4.0,
                                'weight': 0.8
                            },
                            {
                                'animation': 'DanceMoves',
                                'duration': 4.0,
                                'weight': 0.6,
                                'start_offset': 1.0
                            },
                            {
                                'animation': 'FacialExpressions',
                                'duration': 4.0,
                                'weight': 1.0,
                                'start_offset': 0.5
                            }
                        ],
                        'loop': True
                    })
                    # Creates layered performance with overlapping animations

                Error handling:
                    result = await animation_sequence_create({
                        'sequence_name': '',
                        'steps': []
                    })
                    if result['status'] == 'error':
                        logger.error(f"Sequence creation failed: {result['message']}")
                    # Check sequence_name and steps are provided

            Raises:
                ValueError: If sequence_name is empty or steps array is invalid
                RuntimeError: If avatar system is unavailable or animation validation fails
                FileNotFoundError: If avatar_id is specified but avatar doesn't exist

            Notes:
                - Sequences are stored persistently and can be reused
                - Animation names must exist in the target avatar's animation set
                - Blend timing prevents jarring transitions between steps
                - Complex sequences may require more processing resources
                - Sequences can be modified after creation
                - Supports both linear and looped playback modes
                - Timing is frame-accurate for professional performance
                - Avatar-specific optimization improves playback performance

            See Also:
                - animation_sequence_play: Execute created sequences
                - animation_blend_layers: Layer animations with weights
                - avatar_load: Load avatars before creating sequences
                - animation_play: Play individual animations
            """
            return self.mcp_server._execute_animation_sequence_create(params)

        @self.mcp_server.mcp.tool()
        def animation_sequence_play(params: Dict[str, Any]) -> Dict[str, Any]:
            """Execute saved animation sequences with real-time control.

            Plays choreographed animation sequences created with animation_sequence_create,
            providing real-time control over playback, speed, and transitions. Essential
            for live performances, interactive experiences, and precise animation timing.

            Parameters:
                sequence_name: Name of the sequence to play (required)
                    - Must match sequence created with animation_sequence_create
                    - Case-sensitive sequence identifier
                    - Sequence must exist in the system
                avatar_id: Avatar to perform the sequence (required)
                    - Must be loaded with avatar_load
                    - Avatar must be compatible with sequence animations
                    - Case-sensitive avatar identifier
                speed_multiplier: Playback speed adjustment (default: 1.0)
                    - 2.0 = double speed, 0.5 = half speed
                    - Range: 0.1 to 3.0
                    - Affects all timing in the sequence
                start_step: Begin at specific step in sequence (default: 0)
                    - 0-based index of step to start from
                    - Allows resuming sequences mid-playback
                    - Must be valid step index for the sequence
                loop_count: How many times to repeat the sequence (default: 1)
                    - 0 = play once (respect sequence loop setting)
                    - Positive number = repeat that many times
                    - -1 = loop indefinitely (override sequence setting)
                blend_override: Override default blending settings (optional)
                    - Custom blend timing between steps
                    - Override sequence's transition settings
                    - Useful for live performance adjustments

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - sequence_name: Name of sequence being played
                    - avatar_id: Avatar performing the sequence
                    - playback_id: Unique identifier for this playback instance
                    - total_steps: Number of steps in the sequence
                    - current_step: Starting step index
                    - loop_count: Number of loops configured
                    - speed_multiplier: Playback speed applied
                    - estimated_duration: Total playback time in seconds
                    - started_at: Timestamp when playback began

            Usage:
                Use this tool to bring choreographed animation sequences to life with
                precise timing and real-time control. Perfect for performances, storytelling,
                and interactive avatar experiences that require complex animation coordination.

            Examples:
                Play sequence at normal speed:
                    result = await animation_sequence_play({
                        'sequence_name': 'happy_dance',
                        'avatar_id': 'nekomimi'
                    })
                    # Starts the dance sequence on Nekomimi avatar

                Play at half speed for dramatic effect:
                    result = await animation_sequence_play({
                        'sequence_name': 'story_greeting',
                        'avatar_id': 'character',
                        'speed_multiplier': 0.5
                    })
                    # Plays greeting sequence in slow motion

                Loop sequence indefinitely:
                    result = await animation_sequence_play({
                        'sequence_name': 'idle_loop',
                        'avatar_id': 'background_char',
                        'loop_count': -1
                    })
                    # Loops idle animation forever

                Start from middle of sequence:
                    result = await animation_sequence_play({
                        'sequence_name': 'complex_dance',
                        'avatar_id': 'dancer',
                        'start_step': 2
                    })
                    # Begins dance from the third step

                Fast-forward performance:
                    result = await animation_sequence_play({
                        'sequence_name': 'performance',
                        'avatar_id': 'performer',
                        'speed_multiplier': 1.5,
                        'blend_override': {'blend_time': 0.1}
                    })
                    # Speeds up performance with faster transitions

                Multiple avatars synchronized:
                    # Start sequences on multiple avatars
                    avatar1 = await animation_sequence_play({
                        'sequence_name': 'duet_part1',
                        'avatar_id': 'singer1'
                    })
                    avatar2 = await animation_sequence_play({
                        'sequence_name': 'duet_part2',
                        'avatar_id': 'singer2'
                    })
                    # Both avatars perform their parts simultaneously

                Error handling:
                    result = await animation_sequence_play({
                        'sequence_name': 'nonexistent',
                        'avatar_id': 'avatar1'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Playback failed: {result['message']}")
                    # Check sequence exists and avatar is loaded

            Raises:
                ValueError: If sequence_name or avatar_id are invalid
                RuntimeError: If avatar is not loaded or animation system fails
                IndexError: If start_step is out of sequence bounds

            Notes:
                - Avatar must be loaded before sequence playback
                - Sequences play independently of other avatar activities
                - Speed changes affect all timing proportionally
                - Blend overrides allow live performance adjustments
                - Multiple sequences can play on different avatars simultaneously
                - Playback continues until completion or explicit stop
                - Performance depends on sequence complexity and avatar capabilities
                - Real-time control allows pausing/resuming during playback

            See Also:
                - animation_sequence_create: Create sequences before playing
                - animation_stop: Stop sequence playback
                - avatar_load: Load avatars before sequence playback
                - bone_control: Direct pose manipulation during sequences
            """
            return self.mcp_server._execute_animation_sequence_play(params)

        @self.mcp_server.mcp.tool()
        def animation_blend_layers(params: Dict[str, Any]) -> Dict[str, Any]:
            """Layer multiple animations with different weights and priorities.

            Combines multiple animations simultaneously on the same avatar using
            blending weights and priority systems. Perfect for creating complex,
            layered performances where different body parts or motion types
            need to work together seamlessly.

            Parameters:
                avatar_id: Avatar to apply layered animations to (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                    - Supports complex animation layering
                layers: Array of animation layers with settings (required)
                    - Each layer defines an animation and its properties
                    - Must contain at least one layer
                    - Layers blend according to priority and weights
                blend_mode: How layers combine together (default: "additive")
                    - "additive" = layers add together (walking + waving)
                    - "override" = higher priority layers replace lower ones
                    - "mask" = layers only affect specified bone groups
                    - "lerp" = linear interpolation between layers
                transition_time: Time in seconds for layer changes (default: 0.3)
                    - 0.0 = instant layer changes
                    - > 0.0 = smooth transitions between layer states
                    - Prevents jarring animation switches

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar receiving layered animations
                    - layers_applied: Number of animation layers applied
                    - blend_mode: Blending method used
                    - layer_ids: Array of layer identifiers for control
                    - transition_time: Transition duration applied
                    - total_weight: Sum of all layer weights
                    - applied_at: Timestamp when layering was applied

            Usage:
                Use this tool to create rich, complex avatar behaviors by layering
                multiple animations together. Essential for realistic character
                performances where different aspects of movement need to coexist.

            Examples:
                Basic walking + waving combination:
                    result = await animation_blend_layers({
                        'avatar_id': 'character',
                        'layers': [
                            {
                                'animation': 'WalkCycle',
                                'weight': 0.8,
                                'priority': 1
                            },
                            {
                                'animation': 'WaveHello',
                                'weight': 0.6,
                                'priority': 2,
                                'bone_mask': ['RightArm', 'RightHand']
                            }
                        ],
                        'blend_mode': 'additive'
                    })
                    # Character walks while waving hello

                Breathing + emotional expression:
                    result = await animation_blend_layers({
                        'avatar_id': 'performer',
                        'layers': [
                            {
                                'animation': 'IdleBreathing',
                                'weight': 0.3,
                                'priority': 0
                            },
                            {
                                'animation': 'JoyExpression',
                                'weight': 1.0,
                                'priority': 1,
                                'bone_mask': ['Head', 'Face']
                            }
                        ],
                        'blend_mode': 'mask'
                    })
                    # Breathing continues while showing joyful expression

                Dance with multiple elements:
                    result = await animation_blend_layers({
                        'avatar_id': 'dancer',
                        'layers': [
                            {
                                'animation': 'DanceBase',
                                'weight': 1.0,
                                'priority': 0
                            },
                            {
                                'animation': 'ArmFlair',
                                'weight': 0.7,
                                'priority': 1,
                                'bone_mask': ['LeftArm', 'RightArm']
                            },
                            {
                                'animation': 'HeadBob',
                                'weight': 0.4,
                                'priority': 2,
                                'bone_mask': ['Head', 'Neck']
                            }
                        ],
                        'blend_mode': 'additive',
                        'transition_time': 0.5
                    })
                    # Complex dance with base movement, arm flourishes, and head bobbing

                Override blending for state changes:
                    result = await animation_blend_layers({
                        'avatar_id': 'robot',
                        'layers': [
                            {
                                'animation': 'RobotWalk',
                                'weight': 1.0,
                                'priority': 0
                            },
                            {
                                'animation': 'RobotError',
                                'weight': 1.0,
                                'priority': 10,
                                'bone_mask': ['Head', 'Torso']
                            }
                        ],
                        'blend_mode': 'override'
                    })
                    # Error animation overrides walking when triggered

                Smooth layer transitions:
                    result = await animation_blend_layers({
                        'avatar_id': 'actor',
                        'layers': [
                            {'animation': 'Neutral', 'weight': 1.0, 'priority': 0},
                            {'animation': 'Surprised', 'weight': 0.0, 'priority': 1}
                        ],
                        'blend_mode': 'lerp',
                        'transition_time': 1.0
                    })
                    # Smooth transition from neutral to surprised over 1 second

                Error handling:
                    result = await animation_blend_layers({
                        'avatar_id': 'avatar1',
                        'layers': []
                    })
                    if result['status'] == 'error':
                        logger.error(f"Layering failed: {result['message']}")
                    # Check layers array is not empty

            Raises:
                ValueError: If avatar_id is invalid or layers array is malformed
                RuntimeError: If avatar is not loaded or blending system fails
                IndexError: If layer priorities or weights are out of bounds

            Notes:
                - Avatar must be loaded before applying animation layers
                - Layer priorities determine which animations take precedence
                - Bone masks allow targeting specific body parts
                - Weights control the influence of each layer
                - Blend modes affect how layers interact
                - Transitions prevent jarring animation changes
                - Complex layering may impact performance
                - Layers can be modified in real-time
                - Supports up to 8 simultaneous layers per avatar

            See Also:
                - animation_sequence_play: Play choreographed sequences
                - bone_control: Direct bone manipulation
                - morph_control: Control facial expressions
                - avatar_load: Load avatars before layering
            """
            return self.mcp_server._execute_animation_blend_layers(params)
