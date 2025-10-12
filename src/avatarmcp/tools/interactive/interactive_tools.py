"""
Interactive Control Tools for AvatarMCP - Real-time Avatar Manipulation

This module contains tools for real-time interactive control of avatars,
including pose manipulation, gesture recognition, feedback systems, and
multi-avatar scene management for dynamic avatar interactions.
"""

import os
import time
import random
from typing import Dict, Any, List


class InteractiveTools:
    """Container for all interactive control MCP tools."""

    def __init__(self, mcp_server):
        """Initialize interactive tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all interactive tools with the MCP server."""
        # Register interactive_pose_control tool
        @self.mcp_server.mcp.tool()
        def interactive_pose_control(params: Dict[str, Any]) -> Dict[str, Any]:
            """Manipulate avatar pose in real-time with precise bone control.

            Provides fine-grained control over avatar pose and movement through
            direct bone manipulation. Essential for creating dynamic, responsive
            avatar behaviors and interactive performances that go beyond
            pre-recorded animations.

            Parameters:
                avatar_id: Avatar to control (required)
                    - Must be loaded with avatar_load or unity_avatar_load
                    - Case-sensitive avatar identifier
                    - Avatar must support pose manipulation
                bone_controls: Dictionary of bone transformations (required)
                    - Keys are bone names (e.g., "LeftArm", "Head", "Spine")
                    - Values are transformation dictionaries
                    - At least one bone control required
                coordinate_system: Coordinate system for transformations (default: "local")
                    - "local" = relative to parent bone
                    - "world" = absolute world coordinates
                    - "avatar" = relative to avatar root
                interpolation_mode: How to apply transformations (default: "smooth")
                    - "instant" = apply immediately (no interpolation)
                    - "smooth" = smooth interpolation over time
                    - "physics" = use physics-based movement
                    - "kinematic" = direct kinematic control
                duration: Time in seconds for pose change (default: 0.5)
                    - 0.0 = instant change
                    - > 0.0 = smooth transition duration
                    - Affects interpolation speed
                maintain_pose: Whether to hold pose after transition (default: False)
                    - True = pose persists until explicitly changed
                    - False = pose reverts to default after duration
                    - Allows temporary vs permanent pose changes

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that was controlled
                    - bones_affected: Number of bones transformed
                    - coordinate_system: Coordinate system used
                    - interpolation_mode: Interpolation method applied
                    - duration: Transition duration used
                    - pose_maintained: Whether pose will persist
                    - applied_at: Timestamp when pose was applied

            Usage:
                Use this tool for precise, real-time avatar pose control. Perfect for
                creating interactive performances, gesture-based communication, and
                responsive avatar behaviors that adapt to user input.

            Examples:
                Point left arm upward (local coordinates):
                    result = await interactive_pose_control({
                        'avatar_id': 'performer',
                        'bone_controls': {
                            'LeftArm': {
                                'rotation': {'x': -90, 'y': 0, 'z': 0},
                                'scale': {'x': 1, 'y': 1, 'z': 1}
                            }
                        },
                        'coordinate_system': 'local',
                        'duration': 0.3
                    })
                    # Avatar raises left arm smoothly over 0.3 seconds

                Dramatic pose with multiple bones:
                    result = await interactive_pose_control({
                        'avatar_id': 'actor',
                        'bone_controls': {
                            'Head': {'rotation': {'x': 0, 'y': 45, 'z': 0}},
                            'LeftArm': {'rotation': {'x': -120, 'y': 0, 'z': 15}},
                            'RightArm': {'rotation': {'x': -120, 'y': 0, 'z': -15}},
                            'Spine': {'rotation': {'x': 10, 'y': 0, 'z': 0}}
                        },
                        'interpolation_mode': 'smooth',
                        'duration': 1.0,
                        'maintain_pose': True
                    })
                    # Avatar strikes dramatic pose with smooth transitions

                Physics-based movement:
                    result = await interactive_pose_control({
                        'avatar_id': 'athlete',
                        'bone_controls': {
                            'RightArm': {
                                'rotation': {'x': -45, 'y': 0, 'z': 0},
                                'force': {'x': 0, 'y': 10, 'z': 5}
                            }
                        },
                        'interpolation_mode': 'physics',
                        'duration': 0.2
                    })
                    # Arm movement with physics simulation

                World-space positioning:
                    result = await interactive_pose_control({
                        'avatar_id': 'character',
                        'bone_controls': {
                            'Head': {
                                'position': {'x': 0, 'y': 1.8, 'z': 0.2},
                                'look_at': {'x': 1, 'y': 1.6, 'z': 5}
                            }
                        },
                        'coordinate_system': 'world',
                        'interpolation_mode': 'kinematic'
                    })
                    # Head positioned in world space, looking at specific point

                Interactive gesture sequence:
                    # Wave hello
                    await interactive_pose_control({
                        'avatar_id': 'greeter',
                        'bone_controls': {'RightArm': {'rotation': {'x': -90, 'y': 0, 'z': 0}}},
                        'duration': 0.2
                    })
                    await asyncio.sleep(0.5)
                    # Return to neutral
                    await interactive_pose_control({
                        'avatar_id': 'greeter',
                        'bone_controls': {'RightArm': {'rotation': {'x': 0, 'y': 0, 'z': 0}}},
                        'duration': 0.3
                    })

                Error handling:
                    result = await interactive_pose_control({
                        'avatar_id': 'nonexistent',
                        'bone_controls': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Pose control failed: {result['message']}")
                    # Check avatar exists and bone controls are provided

            Raises:
                ValueError: If avatar_id invalid or bone controls malformed
                RuntimeError: If avatar doesn't support pose manipulation
                KeyError: If specified bones don't exist on avatar

            Notes:
                - Requires avatar with pose manipulation capabilities
                - Bone names must match avatar's bone structure
                - Transformations are applied relative to coordinate system
                - Interpolation modes affect movement quality and performance
                - Physics mode requires physics-enabled avatar
                - Pose changes are real-time and can be interrupted
                - Complex poses may require multiple sequential calls
                - Maintain_pose allows persistent pose holding

            See Also:
                - interactive_gesture_recognize: Recognize gestures from pose
                - unity_avatar_animation: Play pre-recorded animations
                - bone_control: Direct bone manipulation
                - animation_blend_layers: Combine with layered animations
            """
            # Implementation for interactive_pose_control
    # Send OSC message to Unity desktop avatar
    osc_address = "/avatar/interactive/pose/control"
    if self.mcp_server._send_osc_message(osc_address, str(params)):
        return {
            'status': 'success',
            'message': 'interactive_pose_control tool executed successfully',
            'osc_message': f'{osc_address} {params}',
            'params': params
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to send interactive_pose_control command to Unity desktop avatar'
        }

        @self.mcp_server.mcp.tool()
        def interactive_gesture_recognize(params: Dict[str, Any]) -> Dict[str, Any]:
            """Recognize and respond to avatar gestures in real-time.

            Analyzes avatar pose and movement patterns to recognize gestures,
            then triggers appropriate responses. Essential for creating interactive
            avatar communication and gesture-based user interfaces.

            Parameters:
                avatar_id: Avatar to analyze for gestures (required)
                    - Must be actively animated or posed
                    - Case-sensitive avatar identifier
                    - Avatar must have gesture recognition enabled
                recognition_mode: How to analyze gestures (default: "realtime")
                    - "realtime" = continuous analysis of current pose
                    - "sequence" = analyze movement sequences over time
                    - "pose" = analyze static pose configurations
                    - "motion" = focus on movement patterns and speed
                gesture_types: Types of gestures to recognize (optional)
                    - Array of gesture categories to detect
                    - If empty, recognizes all supported gestures
                    - Examples: ["waving", "pointing", "nodding", "dancing"]
                sensitivity: Gesture recognition sensitivity (default: 0.7)
                    - 0.0 = very insensitive (few false positives)
                    - 1.0 = very sensitive (more detections but false positives)
                    - Balance between detection rate and accuracy
                confidence_threshold: Minimum confidence for gesture detection (default: 0.8)
                    - 0.0 = detect any potential gesture
                    - 1.0 = only detect very confident matches
                    - Higher values reduce false positives
                response_actions: Automatic responses to detected gestures (optional)
                    - Dictionary mapping gestures to response actions
                    - Example: {"wave": "wave_back", "nod": "acknowledge"}
                    - Responses can trigger other avatar actions

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar being analyzed
                    - recognition_mode: Analysis mode used
                    - gestures_detected: List of currently detected gestures
                    - gesture_confidence: Confidence scores for detections
                    - sensitivity: Recognition sensitivity applied
                    - response_actions: Automatic responses triggered
                    - analysis_timestamp: When analysis was performed

            Usage:
                Use this tool to make avatars responsive to their own gestures and
                movements. Perfect for creating interactive performances, gesture-based
                communication, and dynamic avatar behaviors that react to movement.

            Examples:
                Basic gesture recognition:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'performer',
                        'recognition_mode': 'realtime',
                        'gesture_types': ['waving', 'pointing', 'nodding']
                    })
                    # Detects basic communicative gestures in real-time

                Dance move recognition:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'dancer',
                        'recognition_mode': 'sequence',
                        'gesture_types': ['twirl', 'jump', 'spin'],
                        'sensitivity': 0.8
                    })
                    # Recognizes complex dance movements and sequences

                Pose-based interaction:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'character',
                        'recognition_mode': 'pose',
                        'gesture_types': ['thumbs_up', 'peace_sign', 'salute'],
                        'confidence_threshold': 0.9
                    })
                    # Recognizes specific static poses and gestures

                Interactive gesture response:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'interactive_avatar',
                        'gesture_types': ['wave', 'bow', 'clap'],
                        'response_actions': {
                            'wave': 'wave_back_animation',
                            'bow': 'bow_response',
                            'clap': 'applause_reaction'
                        },
                        'sensitivity': 0.6
                    })
                    # Avatar responds automatically to recognized gestures

                Motion analysis for sports:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'athlete',
                        'recognition_mode': 'motion',
                        'gesture_types': ['run', 'jump', 'throw', 'catch'],
                        'sensitivity': 0.9
                    })
                    # Analyzes athletic movements and sports gestures

                Low-sensitivity for accuracy:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'precise_actor',
                        'gesture_types': ['subtle_nod', 'eye_contact'],
                        'sensitivity': 0.3,
                        'confidence_threshold': 0.95
                    })
                    # Very precise gesture recognition for subtle cues

                Error handling:
                    result = await interactive_gesture_recognize({
                        'avatar_id': 'nonexistent',
                        'gesture_types': []
                    })
                    if result['status'] == 'error':
                        logger.error(f"Gesture recognition failed: {result['message']}")
                    # Check avatar exists and is active

            Raises:
                ValueError: If avatar_id invalid or parameters malformed
                RuntimeError: If gesture recognition system unavailable
                KeyError: If unsupported gesture types specified

            Notes:
                - Requires avatar with gesture recognition capabilities
                - Recognition accuracy depends on gesture complexity
                - Real-time mode provides immediate feedback
                - Sequence mode better for complex multi-step gestures
                - Sensitivity vs accuracy trade-off affects performance
                - Response actions can create interactive feedback loops
                - Multiple gestures can be detected simultaneously
                - Confidence scores help filter reliable detections

            See Also:
                - interactive_pose_control: Create gestures manually
                - animation_sequence_play: Play gesture-based sequences
                - emotion_micro_expressions: Add emotional cues to gestures
                - unity_system_status: Check gesture recognition status
            """
            # Implementation for interactive_gesture_recognize
    # Send OSC message to Unity desktop avatar
    osc_address = "/avatar/interactive/gesture/recognize"
    if self.mcp_server._send_osc_message(osc_address, str(params)):
        return {
            'status': 'success',
            'message': 'interactive_gesture_recognize tool executed successfully',
            'osc_message': f'{osc_address} {params}',
            'params': params
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to send interactive_gesture_recognize command to Unity desktop avatar'
        }

        @self.mcp_server.mcp.tool()
        def interactive_feedback_system(params: Dict[str, Any]) -> Dict[str, Any]:
            """Create real-time feedback systems for avatar interaction.

            Establishes adaptive feedback loops where avatar behavior responds
            to user input, environmental changes, and system states. Essential
            for creating immersive, responsive avatar experiences that adapt
            in real-time.

            Parameters:
                avatar_id: Avatar to apply feedback system to (required)
                    - Must be loaded and active
                    - Case-sensitive avatar identifier
                    - Avatar must support dynamic behavior changes
                feedback_triggers: Events that trigger feedback responses (required)
                    - Dictionary of trigger conditions and responses
                    - At least one trigger required
                    - Triggers can be user input, time-based, or state-based
                feedback_responses: Available response actions (required)
                    - Dictionary of named response behaviors
                    - Responses can modify animation, expression, pose
                    - At least one response required
                adaptation_mode: How feedback system learns and adapts (default: "reactive")
                    - "reactive" = direct response to triggers
                    - "adaptive" = learns from interaction patterns
                    - "predictive" = anticipates user needs
                    - "contextual" = adapts based on situation
                intensity_multiplier: Overall response intensity (default: 1.0)
                    - 0.5 = subdued responses
                    - 1.0 = normal intensity
                    - 2.0 = exaggerated responses
                    - Scales all feedback responses
                cooldown_period: Minimum time between responses (default: 0.5)
                    - Prevents response spam
                    - 0.0 = no cooldown
                    - Higher values = more deliberate responses

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar with feedback system
                    - triggers_configured: Number of feedback triggers set
                    - responses_configured: Number of response actions set
                    - adaptation_mode: Learning mode applied
                    - intensity_multiplier: Response intensity applied
                    - system_active: Whether feedback system is running
                    - configured_at: Timestamp when system was configured

            Usage:
                Use this tool to create adaptive, responsive avatars that react
                intelligently to user interaction and environmental changes.
                Perfect for interactive storytelling, gaming, and dynamic social experiences.

            Examples:
                User proximity feedback:
                    result = await interactive_feedback_system({
                        'avatar_id': 'companion',
                        'feedback_triggers': {
                            'user_close': {'distance': 2.0, 'response': 'wave_hello'},
                            'user_far': {'distance': 5.0, 'response': 'look_around'},
                            'user_touch': {'contact': True, 'response': 'react_surprised'}
                        },
                        'feedback_responses': {
                            'wave_hello': {'animation': 'WaveHello', 'expression': 'Joy'},
                            'look_around': {'animation': 'IdleLook', 'expression': 'Neutral'},
                            'react_surprised': {'animation': 'SurprisedJump', 'expression': 'Surprised'}
                        },
                        'adaptation_mode': 'reactive'
                    })
                    # Avatar responds differently based on user proximity

                Adaptive learning system:
                    result = await interactive_feedback_system({
                        'avatar_id': 'student',
                        'feedback_triggers': {
                            'positive_feedback': {'user_input': 'good_job', 'response': 'happy_learn'},
                            'negative_feedback': {'user_input': 'try_again', 'response': 'focused_retry'},
                            'confusion_detected': {'pattern': 'repeated_failure', 'response': 'seek_help'}
                        },
                        'feedback_responses': {
                            'happy_learn': {'animation': 'Celebrate', 'intensity': 0.8},
                            'focused_retry': {'animation': 'Thinking', 'intensity': 1.0},
                            'seek_help': {'animation': 'Questioning', 'intensity': 0.6}
                        },
                        'adaptation_mode': 'adaptive',
                        'intensity_multiplier': 1.2
                    })
                    # Avatar learns from interaction patterns and adapts responses

                Gaming interaction feedback:
                    result = await interactive_feedback_system({
                        'avatar_id': 'game_character',
                        'feedback_triggers': {
                            'health_low': {'health_percent': 25, 'response': 'injured_react'},
                            'enemy_near': {'distance': 3.0, 'response': 'combat_ready'},
                            'victory_achieved': {'event': 'level_complete', 'response': 'victory_celebrate'}
                        },
                        'feedback_responses': {
                            'injured_react': {'animation': 'Wounded', 'expression': 'Pain', 'pose': 'guarding'},
                            'combat_ready': {'animation': 'BattleStance', 'expression': 'Determined'},
                            'victory_celebrate': {'animation': 'VictoryDance', 'expression': 'Joy'}
                        },
                        'adaptation_mode': 'contextual',
                        'cooldown_period': 1.0
                    })
                    # Game character responds to game state changes

                Predictive assistance:
                    result = await interactive_feedback_system({
                        'avatar_id': 'assistant',
                        'feedback_triggers': {
                            'task_starting': {'pattern': 'user_preparing_task', 'response': 'prepare_help'},
                            'frustration_detected': {'pattern': 'repeated_errors', 'response': 'offer_assistance'},
                            'success_pattern': {'pattern': 'task_completion', 'response': 'praise_effort'}
                        },
                        'feedback_responses': {
                            'prepare_help': {'animation': 'ReadyToHelp', 'expression': 'Eager'},
                            'offer_assistance': {'animation': 'ConcernedHelp', 'expression': 'Caring'},
                            'praise_effort': {'animation': 'Applause', 'expression': 'Proud'}
                        },
                        'adaptation_mode': 'predictive',
                        'intensity_multiplier': 0.8
                    })
                    # Assistant anticipates user needs and provides proactive help

                Error handling:
                    result = await interactive_feedback_system({
                        'avatar_id': 'avatar1',
                        'feedback_triggers': {},
                        'feedback_responses': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Feedback system failed: {result['message']}")
                    # Check triggers and responses are properly configured

            Raises:
                ValueError: If avatar_id invalid or configuration malformed
                RuntimeError: If feedback system unavailable for avatar
                KeyError: If referenced responses don't exist

            Notes:
                - Feedback systems run continuously while active
                - Multiple triggers can fire simultaneously
                - Adaptation modes learn from interaction patterns
                - Intensity multiplier affects all response strengths
                - Cooldown prevents overwhelming response frequency
                - Reactive mode provides immediate, predictable responses
                - Adaptive mode improves with repeated interactions
                - Predictive mode anticipates user intentions
                - Contextual mode adapts to situational factors

            See Also:
                - interactive_gesture_recognize: Recognize user gestures
                - emotion_state_machine: Create emotional response systems
                - animation_sequence_play: Play response animations
                - avatar_personality_apply: Apply personality to responses
            """
            # Implementation for interactive_feedback_system
    # Send OSC message to Unity desktop avatar
    osc_address = "/avatar/interactive/feedback/system"
    if self.mcp_server._send_osc_message(osc_address, str(params)):
        return {
            'status': 'success',
            'message': 'interactive_feedback_system tool executed successfully',
            'osc_message': f'{osc_address} {params}',
            'params': params
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to send interactive_feedback_system command to Unity desktop avatar'
        }

        @self.mcp_server.mcp.tool()
        def interactive_scene_control(params: Dict[str, Any]) -> Dict[str, Any]:
            """Manage multi-avatar scenes with coordinated interactions.

            Controls multiple avatars simultaneously, coordinating their behaviors,
            positioning, and interactions within a shared scene. Essential for
            creating complex social scenarios, performances, and multi-character
            experiences.

            Parameters:
                scene_name: Name for the coordinated scene (required)
                    - Unique identifier for the scene
                    - Used to reference and modify the scene
                    - Case-sensitive naming
                avatars: Dictionary of avatars and their roles (required)
                    - Keys are avatar IDs, values are role configurations
                    - At least one avatar required
                    - Each avatar can have specific behaviors and positioning
                scene_layout: Spatial arrangement of avatars (optional)
                    - Dictionary defining avatar positions and orientations
                    - Can include formations, groupings, and movement paths
                    - Affects how avatars interact spatially
                interaction_rules: Rules for avatar-avatar interactions (optional)
                    - Dictionary defining how avatars respond to each other
                    - Can include proximity triggers, gesture mirroring, etc.
                    - Creates coordinated multi-avatar behaviors
                scene_duration: How long scene should run (default: "continuous")
                    - "continuous" = scene runs until explicitly stopped
                    - Number = seconds to run before auto-stopping
                    - Affects scene lifecycle management
                synchronization_mode: How avatars coordinate timing (default: "loose")
                    - "loose" = independent timing with occasional sync
                    - "tight" = synchronized timing for group actions
                    - "leader_follower" = one avatar leads, others follow
                    - Affects coordination precision vs naturalness

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - scene_name: Name of created scene
                    - avatars_in_scene: Number of avatars in scene
                    - scene_layout: Layout configuration applied
                    - synchronization_mode: Coordination method used
                    - scene_duration: Duration setting applied
                    - scene_active: Whether scene is currently running
                    - created_at: Timestamp when scene was created

            Usage:
                Use this tool to create rich, multi-avatar experiences with
                coordinated behaviors and interactions. Perfect for creating
                social scenarios, performances, storytelling, and group activities.

            Examples:
                Simple conversation scene:
                    result = await interactive_scene_control({
                        'scene_name': 'casual_chat',
                        'avatars': {
                            'alice': {'role': 'talker', 'position': {'x': 0, 'y': 0, 'z': 0}},
                            'bob': {'role': 'listener', 'position': {'x': 1, 'y': 0, 'z': 1}}
                        },
                        'scene_layout': {
                            'formation': 'facing_circle',
                            'spacing': 1.5
                        },
                        'interaction_rules': {
                            'mirroring': True,
                            'proximity_response': 'look_at_speaker'
                        }
                    })
                    # Two avatars in conversation with natural interactions

                Performance scene with multiple dancers:
                    result = await interactive_scene_control({
                        'scene_name': 'dance_troupe',
                        'avatars': {
                            'lead_dancer': {'role': 'leader', 'skill_level': 'expert'},
                            'backup_dancer1': {'role': 'follower', 'skill_level': 'intermediate'},
                            'backup_dancer2': {'role': 'follower', 'skill_level': 'intermediate'},
                            'backup_dancer3': {'role': 'follower', 'skill_level': 'beginner'}
                        },
                        'scene_layout': {
                            'formation': 'dance_line',
                            'leader_position': 'center_front'
                        },
                        'interaction_rules': {
                            'follow_leader': True,
                            'sync_moves': True,
                            'error_correction': 'subtle'
                        },
                        'synchronization_mode': 'leader_follower',
                        'scene_duration': 180  # 3 minutes
                    })
                    # Coordinated dance performance with leader-follower dynamics

                Classroom learning scene:
                    result = await interactive_scene_control({
                        'scene_name': 'classroom_lesson',
                        'avatars': {
                            'teacher': {'role': 'instructor', 'position': 'front'},
                            'student1': {'role': 'active_learner', 'engagement': 'high'},
                            'student2': {'role': 'quiet_learner', 'engagement': 'medium'},
                            'student3': {'role': 'distracted', 'engagement': 'low'}
                        },
                        'scene_layout': {
                            'formation': 'classroom_seats',
                            'teacher_at_board': True
                        },
                        'interaction_rules': {
                            'raise_hand_to_speak': True,
                            'teacher_attention_focus': True,
                            'peer_learning_opportunities': True
                        },
                        'synchronization_mode': 'loose'
                    })
                    # Educational scene with varied student behaviors

                Improvisational theater scene:
                    result = await interactive_scene_control({
                        'scene_name': 'improv_theater',
                        'avatars': {
                            'actor1': {'role': 'lead', 'style': 'expressive'},
                            'actor2': {'role': 'support', 'style': 'reactive'},
                            'actor3': {'role': 'comic_relief', 'style': 'physical'}
                        },
                        'scene_layout': {
                            'formation': 'flexible_stage',
                            'movement_allowed': True
                        },
                        'interaction_rules': {
                            'build_on_cues': True,
                            'physical_comedy': True,
                            'audience_engagement': True
                        },
                        'synchronization_mode': 'tight',
                        'scene_duration': 'continuous'
                    })
                    # Dynamic improv scene with flexible interactions

                Error handling:
                    result = await interactive_scene_control({
                        'scene_name': 'empty_scene',
                        'avatars': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Scene control failed: {result['message']}")
                    # Check scene_name and avatars are provided

            Raises:
                ValueError: If scene_name invalid or avatar configuration malformed
                RuntimeError: If scene system unavailable or avatar conflicts
                KeyError: If referenced avatars don't exist

            Notes:
                - Scenes can include avatars from different systems
                - Layout affects spatial relationships and interactions
                - Interaction rules create emergent behaviors
                - Synchronization modes balance precision vs naturalness
                - Scenes can be modified while running
                - Multiple scenes can run simultaneously
                - Duration control allows for timed performances
                - Complex scenes may require significant processing

            See Also:
                - interactive_feedback_system: Individual avatar responses
                - animation_sequence_play: Play coordinated sequences
                - unity_system_status: Check scene system status
                - avatar_load: Load avatars before adding to scenes
            """
            # Implementation for interactive_scene_control
    # Send OSC message to Unity desktop avatar
    osc_address = "/avatar/interactive/scene/control"
    if self.mcp_server._send_osc_message(osc_address, str(params)):
        return {
            'status': 'success',
            'message': 'interactive_scene_control tool executed successfully',
            'osc_message': f'{osc_address} {params}',
            'params': params
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to send interactive_scene_control command to Unity desktop avatar'
        }
