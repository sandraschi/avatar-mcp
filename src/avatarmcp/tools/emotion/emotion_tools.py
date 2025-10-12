"""
Emotion Tools for AvatarMCP - Advanced Expression & Personality Systems

This module contains tools for emotional expression, state machines,
and personality-driven avatar behavior for lifelike interactions.
"""

import os
import time
import random
from typing import Dict, Any, List


class EmotionTools:
    """Container for all emotion-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize emotion tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all emotion tools with the MCP server."""
        # Register emotion_state_machine tool
        @self.mcp_server.mcp.tool()
        def emotion_state_machine(params: Dict[str, Any]) -> Dict[str, Any]:
            """Create emotional state machines for realistic avatar behavior.

            Defines complex emotional states and transition rules that govern
            how avatars express and change emotions over time. Essential for
            creating believable, responsive characters that react naturally to
            interactions and events.

            Parameters:
                avatar_id: Avatar to apply emotion state machine to (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                    - State machine persists until explicitly changed
                states: Array of emotional states to define (required)
                    - Each state defines an emotion with expression parameters
                    - Must contain at least one state
                    - States can reference VRM blend shapes or animation sequences
                transitions: Rules for moving between emotional states (required)
                    - Defines how and when emotions change
                    - Can be triggered by events, time, or other conditions
                    - Supports smooth transitions between states
                triggers: Events that can trigger state changes (optional)
                    - External events (user input, system events, etc.)
                    - Internal triggers (time-based, random, etc.)
                    - Conditional triggers based on avatar state
                blend_time: Default time for smooth emotion transitions (default: 0.5)
                    - Seconds to blend between emotional states
                    - 0.0 = instant changes, > 0.0 = smooth transitions
                    - Prevents jarring emotion switches
                auto_transitions: Whether states can transition automatically (default: True)
                    - True = states evolve naturally over time
                    - False = states only change via explicit triggers
                    - Affects avatar's baseline emotional behavior

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar the state machine was applied to
                    - states_defined: Number of emotional states created
                    - transitions_created: Number of transition rules defined
                    - machine_id: Unique identifier for this emotion state machine
                    - current_state: Initial emotional state set
                    - applied_at: Timestamp when state machine was applied

            Usage:
                Use this tool to create rich, dynamic emotional personalities for your
                avatars. Essential for interactive storytelling, character development,
                and creating emotionally responsive AI companions.

            Examples:
                Create a happy character that gets sad when ignored:
                    result = await emotion_state_machine({
                        'avatar_id': 'companion_cat',
                        'states': [
                            {
                                'name': 'happy',
                                'expressions': ['Joy', 'Relaxed'],
                                'intensity': 0.8,
                                'duration_range': [10, 30]  # 10-30 seconds
                            },
                            {
                                'name': 'sad',
                                'expressions': ['Sad', 'Tearful'],
                                'intensity': 0.6,
                                'duration_range': [15, 45]
                            }
                        ],
                        'transitions': [
                            {
                                'from': 'happy',
                                'to': 'sad',
                                'trigger': 'no_interaction',
                                'delay_seconds': 60
                            },
                            {
                                'from': 'sad',
                                'to': 'happy',
                                'trigger': 'user_interaction'
                            }
                        ],
                        'triggers': [
                            {'type': 'user_speech', 'action': 'to_happy'},
                            {'type': 'silence', 'duration': 60, 'action': 'to_sad'}
                        ],
                        'blend_time': 1.0
                    })
                    # Creates emotionally responsive companion avatar

                Complex emotional character with multiple states:
                    result = await emotion_state_machine({
                        'avatar_id': 'drama_queen',
                        'states': [
                            {'name': 'excited', 'expressions': ['Joy', 'Surprised'], 'intensity': 1.0},
                            {'name': 'angry', 'expressions': ['Angry', 'Frown'], 'intensity': 0.9},
                            {'name': 'calm', 'expressions': ['Neutral', 'Relaxed'], 'intensity': 0.3},
                            {'name': 'mysterious', 'expressions': ['Thinking', 'SubtleSmile'], 'intensity': 0.5}
                        ],
                        'transitions': [
                            {'from': '*', 'to': 'excited', 'trigger': 'good_news'},
                            {'from': '*', 'to': 'angry', 'trigger': 'bad_news'},
                            {'from': 'excited', 'to': 'calm', 'trigger': 'time', 'delay_seconds': 30},
                            {'from': 'angry', 'to': 'mysterious', 'trigger': 'time', 'delay_seconds': 20}
                        ],
                        'triggers': [
                            {'type': 'text_contains', 'words': ['great', 'awesome', 'wonderful'], 'action': 'to_excited'},
                            {'type': 'text_contains', 'words': ['terrible', 'awful', 'hate'], 'action': 'to_angry'},
                            {'type': 'random', 'probability': 0.1, 'action': 'to_mysterious'}
                        ],
                        'auto_transitions': True
                    })
                    # Creates dramatically expressive character

                Simple mood-based avatar:
                    result = await emotion_state_machine({
                        'avatar_id': 'mood_ring',
                        'states': [
                            {'name': 'content', 'expressions': ['Smile'], 'intensity': 0.5},
                            {'name': 'ecstatic', 'expressions': ['Joy', 'Laugh'], 'intensity': 1.0},
                            {'name': 'grumpy', 'expressions': ['Frown', 'Angry'], 'intensity': 0.7}
                        ],
                        'transitions': [
                            {'from': 'content', 'to': 'ecstatic', 'trigger': 'positive_feedback'},
                            {'from': 'content', 'to': 'grumpy', 'trigger': 'negative_feedback'},
                            {'from': '*', 'to': 'content', 'trigger': 'time', 'delay_seconds': 60}
                        ],
                        'blend_time': 0.3
                    })
                    # Creates simple reactive emotional avatar

                Error handling:
                    result = await emotion_state_machine({
                        'avatar_id': 'avatar1',
                        'states': [],
                        'transitions': []
                    })
                    if result['status'] == 'error':
                        logger.error(f"State machine failed: {result['message']}")
                    # Check states and transitions are properly defined

            Raises:
                ValueError: If avatar_id invalid or state machine definition malformed
                RuntimeError: If avatar not loaded or emotion system unavailable
                KeyError: If referenced expressions don't exist in avatar

            Notes:
                - State machines run continuously while avatar is active
                - Multiple triggers can fire simultaneously
                - Transitions can be interrupted by higher priority triggers
                - Expression intensity affects how strongly emotions are shown
                - State machines can be modified while running
                - Performance depends on number of states and transitions
                - States persist across animation changes
                - Auto-transitions create natural emotional evolution

            See Also:
                - emotion_micro_expressions: Add subtle emotional cues
                - avatar_personality_create: Create personality profiles
                - morph_control: Direct expression control
                - animation_blend_layers: Combine with emotional animations
            """
            # Implementation for emotion_state_machine
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/emotion/state/machine"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    'status': 'success',
                    'message': 'emotion_state_machine tool executed successfully',
                    'osc_message': f'{osc_address} {params}',
                    'params': params
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to send emotion_state_machine command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def emotion_micro_expressions(params: Dict[str, Any]) -> Dict[str, Any]:
            """Add subtle micro-expressions for enhanced emotional realism.

            Generates brief, subtle emotional expressions that add depth and
            humanity to avatar interactions. Micro-expressions are quick,
            involuntary emotional cues that make avatars feel more alive and
            emotionally complex.

            Parameters:
                avatar_id: Avatar to add micro-expressions to (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                    - Micro-expressions overlay on current emotions
                emotion: Base emotion for micro-expression context (required)
                    - Current emotional state (happy, sad, angry, etc.)
                    - Affects which micro-expressions are appropriate
                    - Can be overridden by specific micro_type
                micro_type: Specific type of micro-expression to show (optional)
                    - "doubt" = Brief hesitation or uncertainty
                    - "realization" = Sudden understanding
                    - "concern" = Momentary worry
                    - "amusement" = Quick, subtle smile
                    - "discomfort" = Brief unease
                    - "relief" = Moment of relaxation
                    - "random" = Auto-select based on emotion context
                duration: How long micro-expression lasts (default: 0.5)
                    - Seconds for the brief expression
                    - Range: 0.1 to 2.0 seconds
                    - Too long loses the "micro" quality
                intensity: How subtle vs obvious the expression is (default: 0.3)
                    - 0.0 = barely perceptible, 1.0 = clearly visible
                    - Range: 0.1 to 1.0
                    - Micro-expressions should be subtle
                frequency: How often micro-expressions occur (default: "occasional")
                    - "rare" = Every 30-60 seconds
                    - "occasional" = Every 15-30 seconds
                    - "frequent" = Every 5-15 seconds
                    - "constant" = Every 1-5 seconds
                blend_with_current: Whether to blend with current expressions (default: True)
                    - True = overlays on current emotional state
                    - False = temporarily replaces current expressions
                    - True preserves emotional context

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar receiving micro-expressions
                    - micro_type_applied: Which micro-expression was triggered
                    - emotion_context: Base emotion used for context
                    - duration: Expression duration in seconds
                    - intensity: Expression intensity applied
                    - frequency: Occurrence frequency set
                    - expression_id: Unique identifier for this micro-expression instance

            Usage:
                Use micro-expressions to add emotional depth and realism to your
                avatars. They make characters feel more human and emotionally
                complex, even during simple interactions.

            Examples:
                Add doubt during conversation:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'skeptical_character',
                        'emotion': 'neutral',
                        'micro_type': 'doubt',
                        'duration': 0.3,
                        'intensity': 0.4
                    })
                    # Avatar briefly shows doubt during discussion

                Random micro-expressions for natural behavior:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'lifelike_companion',
                        'emotion': 'happy',
                        'micro_type': 'random',
                        'frequency': 'occasional',
                        'intensity': 0.2
                    })
                    # Avatar occasionally shows subtle emotional cues

                Subtle amusement during storytelling:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'storyteller',
                        'emotion': 'excited',
                        'micro_type': 'amusement',
                        'duration': 0.4,
                        'intensity': 0.3,
                        'blend_with_current': True
                    })
                    # Brief amused expression during funny story

                Concern during serious discussion:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'empathetic_listener',
                        'emotion': 'focused',
                        'micro_type': 'concern',
                        'duration': 0.6,
                        'intensity': 0.5
                    })
                    # Shows momentary concern during serious topic

                Frequent emotional cues for lively character:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'expressive_actor',
                        'emotion': 'dramatic',
                        'micro_type': 'random',
                        'frequency': 'frequent',
                        'intensity': 0.4,
                        'duration': 0.3
                    })
                    # Constant subtle emotional reactions

                Error handling:
                    result = await emotion_micro_expressions({
                        'avatar_id': 'nonexistent',
                        'emotion': 'happy'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Micro-expression failed: {result['message']}")
                    # Check avatar exists and emotion is valid

            Raises:
                ValueError: If avatar_id invalid or parameters out of range
                RuntimeError: If avatar not loaded or emotion system unavailable
                KeyError: If micro_type doesn't exist for given emotion

            Notes:
                - Micro-expressions are brief and subtle by design
                - They overlay on current emotional states
                - Random mode selects contextually appropriate expressions
                - Frequency affects how "alive" avatar appears
                - Too frequent can be distracting, too rare feels robotic
                - Intensity should remain low (0.1-0.5) for realism
                - Duration should be short (0.1-1.0 seconds)
                - Blend mode preserves emotional context
                - Can run simultaneously with state machines

            See Also:
                - emotion_state_machine: Create full emotional state systems
                - morph_control: Direct facial expression control
                - avatar_personality_apply: Apply personality to expressions
                - animation_sequence_play: Combine with emotional sequences
            """
            # Implementation for emotion_micro_expressions
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/emotion/micro/expressions"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    'status': 'success',
                    'message': 'emotion_micro_expressions tool executed successfully',
                    'osc_message': f'{osc_address} {params}',
                    'params': params
                }
            else:
                return {
            'status': 'error',
            'message': 'Failed to send emotion_micro_expressions command to Unity desktop avatar'
        }

        @self.mcp_server.mcp.tool()
        def avatar_personality_create(params: Dict[str, Any]) -> Dict[str, Any]:
            """Create personality profiles that influence avatar behavior.

            Defines personality traits and behavioral patterns that affect how
            avatars express emotions, react to events, and interact with users.
            Creates consistent, recognizable character personalities.

            Parameters:
                personality_name: Unique name for the personality profile (required)
                    - Case-sensitive identifier
                    - Must be unique within the system
                    - Used to reference personality in applications
                traits: Dictionary of personality dimensions (required)
                    - "extroversion": How outgoing/social (0.0-1.0)
                    - "agreeableness": How friendly/considerate (0.0-1.0)
                    - "conscientiousness": How organized/reliable (0.0-1.0)
                    - "neuroticism": How anxious/emotional (0.0-1.0)
                    - "openness": How curious/creative (0.0-1.0)
                    - At least one trait must be specified
                expression_bias: How personality affects emotional expressions (optional)
                    - Dictionary mapping traits to expression modifications
                    - Example: {"extroversion": {"intensity_multiplier": 1.2}}
                    - Affects how strongly emotions are expressed
                gesture_style: How personality influences movement and gestures (optional)
                    - Dictionary defining gesture preferences
                    - Example: {"speed": "energetic", "amplitude": "expressive"}
                    - Affects animation selection and timing
                response_patterns: How personality affects interaction responses (optional)
                    - Dictionary of behavioral tendencies
                    - Example: {"enthusiasm": 0.8, "formality": 0.3}
                    - Affects reaction timing and style
                base_emotions: Default emotional tendencies (optional)
                    - Array of preferred emotional states
                    - Example: ["joy", "curiosity", "excitement"]
                    - Affects baseline emotional state

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - personality_name: Name of created personality profile
                    - traits_defined: Number of personality traits set
                    - profile_id: Unique identifier for the personality profile
                    - created_at: Timestamp when profile was created
                    - compatibility_score: How well traits work together (0.0-1.0)

            Usage:
                Use this tool to create distinct, consistent character personalities
                for your avatars. Essential for creating memorable, relatable AI
                companions and characters with unique behavioral patterns.

            Examples:
                Create an enthusiastic, outgoing personality:
                    result = await avatar_personality_create({
                        'personality_name': 'bubbly_friend',
                        'traits': {
                            'extroversion': 0.9,
                            'agreeableness': 0.8,
                            'neuroticism': 0.2,
                            'openness': 0.7
                        },
                        'expression_bias': {
                            'extroversion': {'intensity_multiplier': 1.3},
                            'agreeableness': {'smile_frequency': 1.5}
                        },
                        'gesture_style': {
                            'speed': 'energetic',
                            'amplitude': 'expressive',
                            'fluidity': 0.8
                        },
                        'base_emotions': ['joy', 'excitement', 'curiosity']
                    })
                    # Creates enthusiastic, expressive personality

                Create a calm, analytical personality:
                    result = await avatar_personality_create({
                        'personality_name': 'thoughtful_mentor',
                        'traits': {
                            'extroversion': 0.4,
                            'agreeableness': 0.7,
                            'conscientiousness': 0.9,
                            'neuroticism': 0.3,
                            'openness': 0.8
                        },
                        'expression_bias': {
                            'conscientiousness': {'thinking_expressions': 1.4},
                            'openness': {'curious_expressions': 1.2}
                        },
                        'response_patterns': {
                            'enthusiasm': 0.5,
                            'formality': 0.7,
                            'response_delay': 1.2
                        },
                        'base_emotions': ['calm', 'thoughtful', 'interested']
                    })
                    # Creates analytical, mentoring personality

                Create a dramatic, artistic personality:
                    result = await avatar_personality_create({
                        'personality_name': 'melodramatic_artist',
                        'traits': {
                            'extroversion': 0.8,
                            'neuroticism': 0.7,
                            'openness': 0.9
                        },
                        'expression_bias': {
                            'neuroticism': {'intensity_multiplier': 1.4},
                            'openness': {'dramatic_expressions': 1.6}
                        },
                        'gesture_style': {
                            'speed': 'dramatic',
                            'amplitude': 'exaggerated',
                            'fluidity': 0.6
                        },
                        'response_patterns': {
                            'enthusiasm': 0.9,
                            'formality': 0.2,
                            'dramatic_pause': 1.8
                        }
                    })
                    # Creates theatrical, expressive personality

                Simple personality with minimal traits:
                    result = await avatar_personality_create({
                        'personality_name': 'shy_helper',
                        'traits': {
                            'extroversion': 0.2,
                            'agreeableness': 0.8
                        },
                        'base_emotions': ['nervous', 'helpful']
                    })
                    # Creates simple, shy personality

                Error handling:
                    result = await avatar_personality_create({
                        'personality_name': '',
                        'traits': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Personality creation failed: {result['message']}")
                    # Check personality_name and traits are provided

            Raises:
                ValueError: If personality_name empty or traits malformed
                RuntimeError: If personality system unavailable
                KeyError: If invalid trait names are specified

            Notes:
                - Personality profiles are stored persistently
                - Traits use Big Five personality model as foundation
                - Expression bias affects how emotions are displayed
                - Gesture style influences animation selection
                - Response patterns affect interaction timing
                - Base emotions set default emotional tendencies
                - Profiles can be modified after creation
                - Multiple avatars can share the same personality
                - Personality affects all emotional and behavioral systems

            See Also:
                - avatar_personality_apply: Apply personality to avatar
                - emotion_state_machine: Create emotion systems
                - animation_blend_layers: Personality affects animation selection
                - morph_control: Personality influences expression intensity
            """
            # Implementation for avatar_personality_create
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/avatar/personality/create"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    'status': 'success',
                    'message': 'avatar_personality_create tool executed successfully',
                    'osc_message': f'{osc_address} {params}',
                    'params': params
                }
            else:
        return {
            'status': 'error',
            'message': 'Failed to send avatar_personality_create command to Unity desktop avatar'
        }

        @self.mcp_server.mcp.tool()
        def avatar_personality_apply(params: Dict[str, Any]) -> Dict[str, Any]:
            """Apply personality profile to avatar behavior in real-time.

            Applies a previously created personality profile to an avatar,
            causing it to exhibit consistent behavioral patterns, emotional
            responses, and interaction styles based on its personality traits.

            Parameters:
                avatar_id: Avatar to apply personality to (required)
                    - Must be loaded with avatar_load
                    - Case-sensitive avatar identifier
                    - Personality replaces any existing personality
                personality_name: Name of personality profile to apply (required)
                    - Must exist in the personality system
                    - Case-sensitive profile identifier
                    - Created with avatar_personality_create
                intensity: How strongly to apply personality traits (default: 1.0)
                    - 1.0 = full personality expression
                    - 0.5 = moderate personality influence
                    - 0.0 = no personality influence (neutral)
                    - Range: 0.0 to 1.0
                context: Current situational context (optional)
                    - "conversation" = Social interaction mode
                    - "work" = Professional/task-focused mode
                    - "play" = Recreational/entertainment mode
                    - "stress" = High-pressure situation
                    - "relaxed" = Low-pressure situation
                    - Affects how personality is expressed
                transition_time: Time to blend to new personality (default: 2.0)
                    - Seconds for smooth personality transition
                    - 0.0 = instant change
                    - Helps maintain continuity during personality switches

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar receiving personality
                    - personality_name: Applied personality profile
                    - intensity: Personality intensity applied
                    - context: Situational context set
                    - traits_applied: List of personality traits now active
                    - applied_at: Timestamp when personality was applied

            Usage:
                Use this tool to give avatars distinct, consistent personalities
                that make them feel like real characters. Essential for creating
                engaging, relatable AI companions with unique behavioral patterns.

            Examples:
                Apply bubbly personality to avatar:
                    result = await avatar_personality_apply({
                        'avatar_id': 'companion_bot',
                        'personality_name': 'bubbly_friend',
                        'intensity': 0.9,
                        'context': 'conversation'
                    })
                    # Avatar becomes outgoing and enthusiastic

                Switch to professional mode:
                    result = await avatar_personality_apply({
                        'avatar_id': 'assistant',
                        'personality_name': 'thoughtful_mentor',
                        'intensity': 1.0,
                        'context': 'work'
                    })
                    # Avatar adopts professional, analytical behavior

                Temporary personality for role-play:
                    result = await avatar_personality_apply({
                        'avatar_id': 'actor',
                        'personality_name': 'melodramatic_artist',
                        'intensity': 0.8,
                        'context': 'play',
                        'transition_time': 1.0
                    })
                    # Avatar takes on theatrical role with smooth transition

                Reduce personality intensity:
                    result = await avatar_personality_apply({
                        'avatar_id': 'character',
                        'personality_name': 'shy_helper',
                        'intensity': 0.3,
                        'context': 'stress'
                    })
                    # Avatar shows subdued personality under stress

                Context switching:
                    # Morning - relaxed
                    await avatar_personality_apply({
                        'avatar_id': 'daily_companion',
                        'personality_name': 'bubbly_friend',
                        'context': 'relaxed'
                    })

                    # Work meeting - professional
                    await avatar_personality_apply({
                        'avatar_id': 'daily_companion',
                        'personality_name': 'thoughtful_mentor',
                        'context': 'work'
                    })

                    # Evening - playful
                    await avatar_personality_apply({
                        'avatar_id': 'daily_companion',
                        'personality_name': 'melodramatic_artist',
                        'context': 'play'
                    })

                Error handling:
                    result = await avatar_personality_apply({
                        'avatar_id': 'avatar1',
                        'personality_name': 'nonexistent'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Personality application failed: {result['message']}")
                    # Check personality_name exists and avatar is loaded

            Raises:
                ValueError: If avatar_id or personality_name invalid
                RuntimeError: If avatar not loaded or personality system unavailable
                FileNotFoundError: If personality profile doesn't exist

            Notes:
                - Personality affects emotional expression intensity
                - Context modifies how personality is expressed
                - Intensity allows fine-tuned personality control
                - Transitions prevent jarring personality changes
                - Multiple contexts allow situational adaptation
                - Personality persists until explicitly changed
                - Works with emotion state machines and micro-expressions
                - Affects animation selection and timing
                - Influences interaction response patterns

            See Also:
                - avatar_personality_create: Create personality profiles
                - emotion_state_machine: Create emotion systems
                - emotion_micro_expressions: Add emotional depth
                - animation_sequence_play: Personality affects animation choice
            """
            # Implementation for avatar_personality_apply
    # Send OSC message to Unity desktop avatar
    osc_address = "/avatar/avatar/personality/apply"
    if self.mcp_server._send_osc_message(osc_address, str(params)):
        return {
            'status': 'success',
            'message': 'avatar_personality_apply tool executed successfully',
            'osc_message': f'{osc_address} {params}',
            'params': params
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to send avatar_personality_apply command to Unity desktop avatar'
        }
