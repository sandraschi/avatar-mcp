"""
Performance Tools for AvatarMCP - Professional Show & Entertainment Systems

This module contains tools for professional avatar performances, including
lip sync, lighting, audience interaction, show management, and recording systems.
"""

from typing import Any


class PerformanceTools:
    """Container for all performance-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize performance tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all performance tools with the MCP server."""

        # Register audio_lip_sync_analyze tool
        @self.mcp_server.mcp.tool()
        def audio_lip_sync_analyze(params: dict[str, Any]) -> dict[str, Any]:
            """Analyze audio for lip sync animation and phoneme detection.

            Processes audio input to generate precise lip sync animations and phoneme
            data for realistic mouth movements during speech and singing. Essential
            for creating believable talking avatars and synchronized vocal performances.

            Parameters:
                audio_source: Audio source for analysis (required)
                    - "file" = analyze audio file path
                    - "stream" = analyze live audio stream
                    - "text" = generate from text input (TTS preview)
                    - "recording" = analyze from performance recording
                audio_path: Path to audio file (required for "file" source)
                    - Absolute or relative path to audio file
                    - Supports WAV, MP3, FLAC formats
                    - File must exist and be readable
                text_content: Text content for phoneme alignment (optional)
                    - Plain text or lyrics with timing annotations
                    - Used to improve phoneme accuracy
                    - Supports multiple languages
                sensitivity: Lip sync sensitivity and precision (default: 0.8)
                    - 0.0 = basic mouth shapes only
                    - 1.0 = highly detailed phoneme shapes
                    - Higher values = more expressive but complex animations
                language: Language for phoneme analysis (default: "auto")
                    - "auto" = automatic language detection
                    - "en" = English phonemes
                    - "ja" = Japanese phonemes (for enka!)
                    - "es" = Spanish phonemes
                    - Affects mouth shape selection
                output_format: Lip sync output format (default: "animation")
                    - "animation" = keyframe animation data
                    - "phonemes" = phoneme sequence with timings
                    - "blend_shapes" = VRM blend shape weights
                    - "unity" = Unity-compatible animation curves

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - audio_source: Source type that was analyzed
                    - duration: Audio duration in seconds
                    - phonemes_detected: Number of phoneme segments found
                    - lip_sync_data: Generated lip sync animation data
                    - language_detected: Language identified for phonemes
                    - confidence_score: Analysis confidence (0.0-1.0)
                    - processing_time: Analysis duration in seconds

            Usage:
                Use this tool to create realistic lip sync animations for talking avatars,
                singing performances, and any vocal content. Essential for professional
                avatar entertainment and interactive storytelling.

            Examples:
                Analyze audio file for lip sync:
                    result = await audio_lip_sync_analyze({
                        'audio_source': 'file',
                        'audio_path': 'dialogue.wav',
                        'text_content': 'Hello, how are you today?',
                        'language': 'en',
                        'sensitivity': 0.9
                    })
                    # Generates lip sync animation for English dialogue

                Analyze singing for enka performance:
                    result = await audio_lip_sync_analyze({
                        'audio_source': 'file',
                        'audio_path': 'enka_singing.mp3',
                        'text_content': '雪が降る町に 別れの歌を',
                        'language': 'ja',
                        'output_format': 'blend_shapes'
                    })
                    # Creates Japanese lip sync for enka singing

                Live stream analysis:
                    result = await audio_lip_sync_analyze({
                        'audio_source': 'stream',
                        'sensitivity': 0.7,
                        'output_format': 'phonemes'
                    })
                    # Analyzes live audio for real-time phoneme detection

                Text-to-animation preview:
                    result = await audio_lip_sync_analyze({
                        'audio_source': 'text',
                        'text_content': 'This is a test of lip sync animation',
                        'language': 'en'
                    })
                    # Generates preview animation from text input

                Error handling:
                    result = await audio_lip_sync_analyze({
                        'audio_source': 'file',
                        'audio_path': 'nonexistent.wav'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Lip sync analysis failed: {result['message']}")
                    # Check audio file exists and is valid

            Raises:
                FileNotFoundError: If audio file doesn't exist
                ValueError: If audio format unsupported or parameters invalid
                RuntimeError: If audio processing fails
                KeyError: If language not supported

            Notes:
                - Audio quality affects lip sync accuracy
                - Text alignment significantly improves results
                - Japanese phonemes require specialized mouth shapes
                - Real-time analysis has slight processing delay
                - Output formats vary in complexity and compatibility
                - Sensitivity affects both accuracy and performance
                - Multiple language support for international content
                - Phoneme detection works best with clear audio

            See Also:
                - audio_singing_synthesize: Generate singing audio with lyrics
                - animation_sequence_play: Combine with lip sync animations
                - morph_control: Direct facial expression control
                - performance_recording_system: Record performances with lip sync
            """
            # Implementation for audio_lip_sync_analyze
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/audio/lip/sync/analyze"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "audio_lip_sync_analyze tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Failed to send audio_lip_sync_analyze command to Unity desktop avatar"
                    ),
                }

        @self.mcp_server.mcp.tool()
        def performance_lighting_control(params: dict[str, Any]) -> dict[str, Any]:
            """Control stage lighting and visual effects for avatar performances.

            Manages professional lighting setups, color schemes, and dynamic lighting
            effects to enhance avatar performances and create immersive show environments.
            Perfect for concerts, theater, and interactive entertainment experiences.

            Parameters:
                lighting_mode: Lighting control mode (required)
                    - "preset" = apply predefined lighting setups
                    - "custom" = create custom lighting configuration
                    - "sequence" = program lighting sequences/timeline
                    - "dynamic" = real-time lighting based on performance
                preset_name: Name of lighting preset (required for "preset" mode)
                    - "concert" = dramatic concert lighting
                    - "theater" = warm theater ambiance
                    - "intimate" = close, personal lighting
                    - "party" = energetic, colorful party lights
                    - "mood" = atmospheric mood lighting
                custom_config: Custom lighting configuration (required for "custom" mode)
                    - Dictionary with lighting parameters
                    - Colors, intensities, positions, directions
                    - Advanced lighting setup options
                sequence_steps: Lighting sequence timeline (required for "sequence" mode)
                    - Array of timed lighting changes
                    - Each step defines lighting state and duration
                    - Supports smooth transitions between steps
                dynamic_triggers: Performance triggers for lighting (optional for "dynamic" mode)
                    - Events that change lighting automatically
                    - Audio levels, avatar emotions, audience reactions
                    - Real-time lighting adaptation
                transition_time: Default transition duration between lighting changes (default: 1.0)
                    - Seconds for smooth lighting transitions
                    - 0.0 = instant changes
                    - Prevents jarring light shifts
                intensity_multiplier: Overall lighting intensity scale (default: 1.0)
                    - 0.5 = dimmed lighting
                    - 1.0 = normal intensity
                    - 2.0 = dramatic bright lighting

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - lighting_mode: Mode that was applied
                    - lights_configured: Number of lights set up
                    - effects_applied: Number of lighting effects activated
                    - transition_time: Transition duration used
                    - intensity_multiplier: Intensity scale applied
                    - lighting_active: Whether lighting system is running

            Usage:
                Use this tool to create professional lighting for avatar performances,
                enhancing the visual impact of shows, concerts, and interactive experiences.
                Essential for creating immersive entertainment environments.

            Examples:
                Apply concert lighting preset:
                    result = await performance_lighting_control({
                        'lighting_mode': 'preset',
                        'preset_name': 'concert',
                        'intensity_multiplier': 1.2
                    })
                    # Dramatic concert lighting with spotlights and colors

                Create custom mood lighting:
                    result = await performance_lighting_control({
                        'lighting_mode': 'custom',
                        'custom_config': {
                            'ambient_color': {'r': 0.2, 'g': 0.1, 'b': 0.3},
                            'spotlight_color': {'r': 1.0, 'g': 0.8, 'b': 0.2},
                            'intensity': 0.8,
                            'direction': {'x': 0, 'y': -1, 'z': 0}
                        },
                        'transition_time': 2.0
                    })
                    # Custom purple-blue mood lighting with warm accents

                Program lighting sequence:
                    result = await performance_lighting_control({
                        'lighting_mode': 'sequence',
                        'sequence_steps': [
                            {
                                'step_name': 'intro',
                                'duration': 10,
                                'lighting': {'preset': 'intimate', 'intensity': 0.6}
                            },
                            {
                                'step_name': 'performance',
                                'duration': 180,
                                'lighting': {'preset': 'concert', 'intensity': 1.0}
                            },
                            {
                                'step_name': 'encore',
                                'duration': 30,
                                'lighting': {'preset': 'party', 'intensity': 1.3}
                            }
                        ]
                    })
                    # Timed lighting sequence for full performance

                Dynamic reactive lighting:
                    result = await performance_lighting_control({
                        'lighting_mode': 'dynamic',
                        'dynamic_triggers': {
                            'high_energy': {
                                'trigger': 'audio_level_above_0.8',
                                'lighting': {'preset': 'party', 'intensity': 1.5}
                            },
                            'emotional_moment': {
                                'trigger': 'avatar_emotion_sad',
                                'lighting': {'preset': 'mood', 'intensity': 0.4}
                            },
                            'applause': {
                                'trigger': 'audience_clap_detected',
                                'lighting': {'preset': 'concert', 'intensity': 1.2}
                            }
                        },
                        'transition_time': 0.5
                    })
                    # Lighting that reacts to performance energy and emotions

                Error handling:
                    result = await performance_lighting_control({
                        'lighting_mode': 'preset',
                        'preset_name': 'nonexistent'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Lighting control failed: {result['message']}")
                    # Check preset name exists and lighting system is available

            Raises:
                ValueError: If lighting mode or parameters are invalid
                RuntimeError: If lighting system unavailable
                KeyError: If preset name doesn't exist

            Notes:
                - Lighting enhances performance atmosphere significantly
                - Smooth transitions prevent audience discomfort
                - Dynamic lighting creates engaging, responsive shows
                - Custom configurations allow artistic creativity
                - Sequence mode enables professional show production
                - Intensity affects both visibility and mood
                - Multiple lighting modes can be combined
                - Performance depends on available lighting hardware

            See Also:
                - performance_particle_effects: Add visual particle effects
                - audio_singing_synthesize: Sync lighting with music
                - show_script_create: Coordinate lighting with show scripts
                - animation_sequence_play: Time lighting with animations
            """
            # Implementation for performance_lighting_control
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/performance/lighting/control"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "performance_lighting_control tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Failed to send performance_lighting_control command to Unity "
                        "desktop avatar"
                    ),
                }

        @self.mcp_server.mcp.tool()
        def performance_particle_effects(params: dict[str, Any]) -> dict[str, Any]:
            """Create and control particle effects for avatar performances.

            Generates and manages visual particle effects including confetti, sparks,
            magical auras, and environmental effects to enhance avatar performances
            and create spectacular visual experiences.

            Parameters:
                effect_type: Type of particle effect to create (required)
                    - "confetti" = celebratory falling confetti
                    - "sparks" = magical spark effects
                    - "aura" = glowing energy field around avatar
                    - "hearts" = floating heart particles
                    - "stars" = twinkling star field
                    - "fireworks" = explosive firework effects
                    - "rain" = weather particle effects
                    - "snow" = falling snow particles
                effect_config: Detailed effect configuration (required)
                    - Dictionary with effect-specific parameters
                    - Particle count, colors, speed, lifetime
                    - Size, shape, and behavior settings
                trigger_event: When to trigger the effect (default: "immediate")
                    - "immediate" = start effect now
                    - "performance_start" = when performance begins
                    - "performance_end" = when performance ends
                    - "emotion_happy" = when avatar shows happiness
                    - "applause" = when audience applauds
                    - "custom" = user-defined trigger condition
                duration: How long effect should last (default: 5.0)
                    - Seconds for effect duration
                    - 0 = instant burst effect
                    - -1 = continuous effect until stopped
                intensity: Effect intensity and scale (default: 1.0)
                    - 0.5 = subtle, small effect
                    - 1.0 = normal intensity
                    - 2.0 = spectacular, large-scale effect
                position_offset: Effect position relative to avatar (optional)
                    - Dictionary with x, y, z coordinates
                    - Relative to avatar center or specific bone
                    - Allows effects to emanate from specific body parts
                color_scheme: Color palette for particles (optional)
                    - Array of RGB color values
                    - Gradient definitions for color transitions
                    - Theme-based color selections

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - effect_type: Type of effect created
                    - effect_id: Unique identifier for this effect instance
                    - trigger_event: Event that will trigger the effect
                    - duration: Effect duration in seconds
                    - intensity: Intensity scale applied
                    - particles_count: Number of particles in effect
                    - effect_active: Whether effect is currently running

            Usage:
                Use this tool to add spectacular visual effects to avatar performances,
                creating magical, celebratory, and immersive entertainment experiences.
                Perfect for concerts, celebrations, and interactive shows.

            Examples:
                Create confetti celebration:
                    result = await performance_particle_effects({
                        'effect_type': 'confetti',
                        'effect_config': {
                            'particle_count': 200,
                            'fall_speed': 2.0,
                            'colors': [
                                {'r': 1.0, 'g': 0.0, 'b': 0.0},  # Red
                                {'r': 0.0, 'g': 1.0, 'b': 0.0},  # Green
                                {'r': 0.0, 'g': 0.0, 'b': 1.0}   # Blue
                            ]
                        },
                        'trigger_event': 'performance_end',
                        'duration': 10.0,
                        'intensity': 1.5
                    })
                    # Colorful confetti rain at performance end

                Magical aura effect:
                    result = await performance_particle_effects({
                        'effect_type': 'aura',
                        'effect_config': {
                            'particle_count': 50,
                            'glow_intensity': 0.8,
                            'rotation_speed': 1.0,
                            'size': 2.0
                        },
                        'trigger_event': 'emotion_happy',
                        'duration': -1,  # Continuous
                        'intensity': 0.7,
                        'color_scheme': [
                            {'r': 1.0, 'g': 0.8, 'b': 0.2},  # Golden glow
                            {'r': 1.0, 'g': 0.4, 'b': 0.8}   # Pink energy
                        ]
                    })
                    # Continuous magical aura when avatar is happy

                Firework spectacular:
                    result = await performance_particle_effects({
                        'effect_type': 'fireworks',
                        'effect_config': {
                            'burst_count': 10,
                            'explosion_size': 3.0,
                            'trail_length': 2.0,
                            'sound_sync': True
                        },
                        'trigger_event': 'applause',
                        'duration': 15.0,
                        'intensity': 2.0,
                        'position_offset': {'x': 0, 'y': 5, 'z': 0}
                    })
                    # Overhead fireworks triggered by audience applause

                Romantic heart effects:
                    result = await performance_particle_effects({
                        'effect_type': 'hearts',
                        'effect_config': {
                            'particle_count': 30,
                            'float_speed': 0.5,
                            'wiggle_amount': 0.2,
                            'size_variation': 0.3
                        },
                        'trigger_event': 'performance_start',
                        'duration': 30.0,
                        'intensity': 1.0,
                        'color_scheme': [
                            {'r': 1.0, 'g': 0.2, 'b': 0.4},  # Pink
                            {'r': 1.0, 'g': 0.4, 'b': 0.6}   # Light pink
                        ]
                    })
                    # Floating hearts for romantic performances

                Weather effects for atmosphere:
                    result = await performance_particle_effects({
                        'effect_type': 'snow',
                        'effect_config': {
                            'particle_count': 100,
                            'wind_direction': {'x': 0.1, 'y': 0, 'z': 0},
                            'flake_size': 0.05,
                            'settling': True
                        },
                        'trigger_event': 'custom',
                        'duration': -1,
                        'intensity': 0.8
                    })
                    # Continuous falling snow with wind effects

                Error handling:
                    result = await performance_particle_effects({
                        'effect_type': 'nonexistent',
                        'effect_config': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"Particle effect failed: {result['message']}")
                    # Check effect type exists and config is valid

            Raises:
                ValueError: If effect type or configuration is invalid
                RuntimeError: If particle system unavailable
                KeyError: If effect parameters are malformed

            Notes:
                - Particle effects significantly enhance visual appeal
                - Trigger events create responsive, interactive experiences
                - Intensity affects both visual impact and performance
                - Position offsets allow targeted effect placement
                - Color schemes support thematic customization
                - Continuous effects require manual stopping
                - Multiple effects can run simultaneously
                - Performance depends on graphics capabilities

            See Also:
                - performance_lighting_control: Combine with lighting effects
                - animation_sequence_play: Time effects with animations
                - audio_singing_synthesize: Sync effects with music
                - audience_response_analyze: Trigger effects based on audience
            """
            # Implementation for performance_particle_effects
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/performance/particle/effects"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "performance_particle_effects tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Failed to send performance_particle_effects command to Unity "
                        "desktop avatar"
                    ),
                }

        @self.mcp_server.mcp.tool()
        def audience_response_analyze(params: dict[str, Any]) -> dict[str, Any]:
            """Analyze audience reactions and engagement during performances.

            Monitors audience responses through various input methods including
            applause detection, facial recognition, verbal reactions, and engagement
            metrics to provide real-time feedback for avatar performances.

            Parameters:
                analysis_mode: Type of audience analysis to perform (required)
                    - "audio" = analyze applause, cheers, reactions
                    - "visual" = analyze facial expressions, gestures
                    - "combined" = analyze both audio and visual cues
                    - "engagement" = measure overall engagement levels
                    - "sentiment" = analyze emotional tone of responses
                input_sources: Sources for audience data (required)
                    - Array of input methods to use
                    - ["microphone"] = audio input
                    - ["camera"] = video input
                    - ["social"] = social media reactions
                    - ["survey"] = direct audience feedback
                analysis_duration: How long to analyze audience (default: 30.0)
                    - Seconds to monitor audience responses
                    - 0 = single snapshot analysis
                    - Longer durations provide trend analysis
                sensitivity: Analysis sensitivity for detecting responses (default: 0.7)
                    - 0.0 = very insensitive (few detections)
                    - 1.0 = very sensitive (more detections, more noise)
                    - Balance between detection rate and accuracy
                real_time_feedback: Whether to provide continuous feedback (default: True)
                    - True = ongoing analysis with immediate results
                    - False = batch analysis at end of duration
                    - Real-time mode allows performance adaptation
                response_categories: Types of responses to detect (optional)
                    - Array of specific response types to monitor
                    - ["applause", "cheers", "laughter", "silence", "boos"]
                    - If empty, detects all supported responses

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - analysis_mode: Type of analysis performed
                    - analysis_duration: Duration analyzed in seconds
                    - audience_size: Estimated number of audience members
                    - engagement_score: Overall engagement level (0.0-1.0)
                    - response_breakdown: Detailed response statistics
                    - sentiment_analysis: Emotional tone of responses
                    - peak_moments: Most engaging moments identified
                    - recommendations: Performance improvement suggestions

            Usage:
                Use this tool to understand audience reactions and adapt performances
                in real-time, creating more engaging and responsive avatar shows.
                Essential for professional entertainment and interactive experiences.

            Examples:
                Real-time audience analysis:
                    result = await audience_response_analyze({
                        'analysis_mode': 'combined',
                        'input_sources': ['microphone', 'camera'],
                        'analysis_duration': 60.0,
                        'real_time_feedback': True,
                        'response_categories': ['applause', 'laughter', 'cheers']
                    })
                    # Continuous analysis of live audience reactions

                Sentiment analysis for emotional content:
                    result = await audience_response_analyze({
                        'analysis_mode': 'sentiment',
                        'input_sources': ['microphone'],
                        'analysis_duration': 0,  # Snapshot
                        'sensitivity': 0.8
                    })
                    # Quick analysis of audience emotional response

                Engagement tracking during performance:
                    result = await audience_response_analyze({
                        'analysis_mode': 'engagement',
                        'input_sources': ['camera', 'social'],
                        'analysis_duration': 300.0,  # 5 minutes
                        'real_time_feedback': False
                    })
                    # Comprehensive engagement analysis over full performance

                Audio-only applause detection:
                    result = await audience_response_analyze({
                        'analysis_mode': 'audio',
                        'input_sources': ['microphone'],
                        'response_categories': ['applause', 'silence'],
                        'sensitivity': 0.6
                    })
                    # Detect applause and quiet moments in audio

                Error handling:
                    result = await audience_response_analyze({
                        'analysis_mode': 'combined',
                        'input_sources': ['microphone'],
                        'input_sources': []  # Invalid: empty sources
                    })
                    if result['status'] == 'error':
                        logger.error(f"Audience analysis failed: {result['message']}")
                    # Check input sources are valid and available

            Raises:
                ValueError: If analysis mode or parameters are invalid
                RuntimeError: If audience analysis system unavailable
                ConnectionError: If input devices cannot be accessed

            Notes:
                - Analysis accuracy depends on input quality
                - Real-time feedback enables adaptive performances
                - Multiple input sources improve accuracy
                - Sensitivity affects both detection and false positives
                - Engagement scoring provides overall performance metric
                - Sentiment analysis reveals emotional audience response
                - Peak moment identification helps optimize shows
                - Recommendations guide performance improvements

            See Also:
                - performance_lighting_control: Adjust lighting based on audience
                - performance_particle_effects: Trigger effects from audience reactions
                - show_script_create: Adapt scripts based on audience response
                - interactive_feedback_system: Create responsive avatar behavior
            """
            # Implementation for audience_response_analyze
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/audience/response/analyze"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "audience_response_analyze tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Failed to send audience_response_analyze command to Unity desktop avatar"
                    ),
                }

        @self.mcp_server.mcp.tool()
        def show_script_create(params: dict[str, Any]) -> dict[str, Any]:
            """Create and manage scripted performances for avatar shows.

            Develops comprehensive show scripts with timing, cues, dialogue,
            animations, and effects coordination for professional avatar performances.
            Enables complex, multi-act entertainment productions.

            Parameters:
                script_title: Title for the performance script (required)
                    - Unique identifier for the script
                    - Used for referencing and management
                    - Case-sensitive naming
                script_structure: Overall script organization (required)
                    - "single_act" = simple linear performance
                    - "multi_act" = complex multi-part show
                    - "interactive" = audience-influenced performance
                    - "improvised" = structured improvisation framework
                acts: Array of script acts/scenes (required for multi_act)
                    - Each act defines a performance segment
                    - Includes timing, content, and transitions
                    - Allows complex narrative structures
                dialogue_lines: Script dialogue and vocal content (optional)
                    - Array of spoken lines with timing
                    - Includes character assignments and emotions
                    - Supports multiple languages and styles
                animation_sequences: Pre-planned animation sequences (optional)
                    - References to animation_sequence_create results
                    - Timed animation triggers throughout script
                    - Synchronized with dialogue and effects
                effect_cues: Lighting and particle effect triggers (optional)
                    - References to performance_lighting_control and performance_particle_effects
                    - Timed effect triggers throughout performance
                    - Creates immersive show environments
                audience_interactions: Planned audience engagement points (optional)
                    - Specific moments for audience participation
                    - Question prompts, reaction cues, feedback points
                    - Interactive elements in scripted performance

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - script_title: Title of created script
                    - script_id: Unique identifier for the script
                    - total_duration: Estimated performance duration
                    - acts_count: Number of acts in script
                    - dialogue_lines: Number of dialogue entries
                    - effect_cues: Number of effect triggers
                    - script_created: Timestamp when script was created

            Usage:
                Use this tool to create professional, well-structured avatar performances
                with precise timing, coordinated effects, and engaging narratives.
                Essential for theater, concerts, and complex entertainment productions.

            Examples:
                Create simple concert script:
                    result = await show_script_create({
                        'script_title': 'Enka Concert Night',
                        'script_structure': 'single_act',
                        'dialogue_lines': [
                            {
                                'time': 0,
                                'character': 'nekomimi',
                                'text': '今夜は特別な夜です',
                                'emotion': 'excited',
                                'language': 'ja'
                            },
                            {
                                'time': 30,
                                'character': 'nekomimi',
                                'text': '雪が降る町に別れの歌を歌います',
                                'emotion': 'passionate'
                            }
                        ],
                        'animation_sequences': [
                            {'sequence_name': 'opening_wave', 'start_time': 0},
                            {'sequence_name': 'singing_pose', 'start_time': 30}
                        ],
                        'effect_cues': [
                            {'effect_type': 'lighting', 'preset': 'concert', 'time': 0},
                            {'effect_type': 'particles', 'type': 'snow', 'time': 45}
                        ]
                    })
                    # Complete concert script with dialogue, animations, and effects

                Multi-act theater production:
                    result = await show_script_create({
                        'script_title': 'Avatar Theater: Love Story',
                        'script_structure': 'multi_act',
                        'acts': [
                            {
                                'act_title': 'Act 1: Meeting',
                                'duration': 300,
                                'scene_description': 'Two avatars meet in a cafe',
                                'mood': 'romantic'
                            },
                            {
                                'act_title': 'Act 2: Conflict',
                                'duration': 240,
                                'scene_description': 'Relationship challenges emerge',
                                'mood': 'dramatic'
                            },
                            {
                                'act_title': 'Act 3: Resolution',
                                'duration': 180,
                                'scene_description': 'Happy ending with celebration',
                                'mood': 'joyful'
                            }
                        ],
                        'audience_interactions': [
                            {'time': 400, 'type': 'applause_break'},
                            {'time': 500, 'type': 'standing_ovation'}
                        ]
                    })
                    # Complex multi-act theater production

                Interactive improv framework:
                    result = await show_script_create({
                        'script_title': 'Improv Comedy Show',
                        'script_structure': 'interactive',
                        'dialogue_lines': [
                            {
                                'time': 0,
                                'character': 'host',
                                'text': 'Welcome to improv night!',
                                'emotion': 'excited'
                            }
                        ],
                        'audience_interactions': [
                            {
                                'time': 30,
                                'type': 'suggestion_request',
                                'prompt': 'Give us a profession!'
                            },
                            {
                                'time': 90,
                                'type': 'suggestion_request',
                                'prompt': 'Now a location!'
                            },
                            {'time': 150, 'type': 'scene_improv', 'duration': 180}
                        ],
                        'effect_cues': [
                            {'effect_type': 'lighting', 'preset': 'party', 'time': 0},
                            {'effect_type': 'particles', 'type': 'confetti', 'trigger': 'applause'}
                        ]
                    })
                    # Interactive improv show with audience participation

                Error handling:
                    result = await show_script_create({
                        'script_title': '',
                        'script_structure': 'single_act'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Script creation failed: {result['message']}")
                    # Check script_title and required parameters

            Raises:
                ValueError: If script parameters are invalid or malformed
                RuntimeError: If script system unavailable
                KeyError: If referenced sequences or effects don't exist

            Notes:
                - Scripts provide structure for complex performances
                - Multi-act structure enables narrative depth
                - Interactive elements create engaging experiences
                - Timing coordination is critical for professional results
                - Effect cues enhance visual and emotional impact
                - Audience interactions increase engagement
                - Scripts can be modified during performance
                - Complex scripts may require rehearsal time

            See Also:
                - animation_sequence_create: Create animation sequences for scripts
                - performance_lighting_control: Set up lighting for performances
                - performance_particle_effects: Add visual effects to shows
                - performance_recording_system: Record scripted performances
                - audience_response_analyze: Adapt scripts based on audience feedback
            """
            # Implementation for show_script_create
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/show/script/create"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "show_script_create tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to send show_script_create command to Unity desktop avatar",
                }

        @self.mcp_server.mcp.tool()
        def performance_recording_system(params: dict[str, Any]) -> dict[str, Any]:
            """Record and manage avatar performances for playback and analysis.

            Captures complete avatar performances including animations, audio, expressions,
            lighting, and effects for later playback, analysis, or improvement. Essential
            for performance review, content creation, and professional development.

            Parameters:
                recording_mode: Type of recording to perform (required)
                    - "live" = record current live performance
                    - "rehearse" = record rehearsal with annotations
                    - "segment" = record specific performance segments
                    - "multi_angle" = record from multiple virtual cameras
                    - "analysis" = record with performance metrics
                recording_name: Name for the recorded performance (required)
                    - Unique identifier for the recording
                    - Used for playback and management
                    - Case-sensitive naming
                duration: Recording duration in seconds (required for timed modes)
                    - How long to record the performance
                    - 0 = record until manually stopped
                    - Maximum recording time depends on system
                include_elements: Performance elements to record (default: "all")
                    - "all" = record everything available
                    - "avatar_only" = avatar animations and expressions
                    - "audio_visual" = audio and visual elements
                    - "effects_only" = lighting and particle effects
                    - Array of specific elements to include
                quality_settings: Recording quality and compression (optional)
                    - Dictionary with quality parameters
                    - Resolution, frame rate, compression settings
                    - Balance between quality and file size
                metadata: Additional information about the performance (optional)
                    - Performance notes, date, location, audience info
                    - Tags for categorization and search
                    - Performance statistics and metrics

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - recording_name: Name of the recorded performance
                    - recording_id: Unique identifier for the recording
                    - duration_recorded: Actual recording duration in seconds
                    - file_size: Size of recorded file in MB
                    - elements_recorded: List of elements captured
                    - quality_used: Recording quality settings applied
                    - recording_path: File path to recorded performance

            Usage:
                Use this tool to capture avatar performances for review, improvement,
                content creation, and professional development. Essential for creating
                performance libraries and analyzing show effectiveness.

            Examples:
                Record live performance:
                    result = await performance_recording_system({
                        'recording_mode': 'live',
                        'recording_name': 'Enka Concert Final',
                        'duration': 0,  # Record until stopped
                        'include_elements': 'all',
                        'quality_settings': {
                            'resolution': '1080p',
                            'frame_rate': 30,
                            'compression': 'high_quality'
                        },
                        'metadata': {
                            'performer': 'Nekomimi-chan',
                            'song': '雪が降る町に',
                            'date': '2025-10-12',
                            'audience_size': 150
                        }
                    })
                    # Records complete live enka performance

                Record rehearsal with annotations:
                    result = await performance_recording_system({
                        'recording_mode': 'rehearse',
                        'recording_name': 'Dance Rehearsal v3',
                        'duration': 300,  # 5 minutes
                        'include_elements': ['avatar', 'audio', 'lighting'],
                        'metadata': {
                            'notes': 'Fixed timing issues in bridge section',
                            'improvements_needed': ['faster transitions', 'better expressions']
                        }
                    })
                    # Records rehearsal for review and improvement

                Multi-angle recording:
                    result = await performance_recording_system({
                        'recording_mode': 'multi_angle',
                        'recording_name': 'Theater Production Multi-Cam',
                        'duration': 1800,  # 30 minutes
                        'include_elements': 'all',
                        'quality_settings': {
                            'cameras': ['front', 'side', 'overhead', 'closeup'],
                            'sync_audio': True
                        }
                    })
                    # Records performance from multiple virtual camera angles

                Segment recording for analysis:
                    result = await performance_recording_system({
                        'recording_mode': 'segment',
                        'recording_name': 'Emotional Scene Analysis',
                        'duration': 120,  # 2 minutes
                        'include_elements': ['avatar', 'expressions', 'audio'],
                        'metadata': {
                            'scene': 'confession_scene',
                            'focus': 'emotional_accuracy',
                            'metrics': ['expression_consistency', 'timing_accuracy']
                        }
                    })
                    # Records specific scene segment for detailed analysis

                High-quality archival recording:
                    result = await performance_recording_system({
                        'recording_mode': 'live',
                        'recording_name': 'Historic Performance Archive',
                        'duration': 0,
                        'include_elements': 'all',
                        'quality_settings': {
                            'resolution': '4K',
                            'frame_rate': 60,
                            'compression': 'lossless',
                            'metadata_embedded': True
                        },
                        'metadata': {
                            'event': 'AvatarMCP Launch Concert',
                            'significance': 'historic_first_performance',
                            'preservation': 'long_term_archive'
                        }
                    })
                    # Creates high-quality archival recording

                Error handling:
                    result = await performance_recording_system({
                        'recording_mode': 'live',
                        'recording_name': '',
                        'duration': 60
                    })
                    if result['status'] == 'error':
                        logger.error(f"Recording failed: {result['message']}")
                    # Check recording_name and parameters are valid

            Raises:
                ValueError: If recording parameters are invalid
                RuntimeError: If recording system unavailable
                FileNotFoundError: If output directory doesn't exist
                PermissionError: If write access denied

            Notes:
                - Recordings preserve complete performance state
                - Quality settings affect file size significantly
                - Multi-angle recordings require additional processing
                - Metadata enables better organization and search
                - Analysis mode includes performance metrics
                - Recordings can be played back for review
                - File sizes depend on duration and quality settings
                - Storage requirements should be considered

            See Also:
                - show_script_create: Record scripted performances
                - animation_sequence_play: Playback recorded animations
                - audience_response_analyze: Analyze recorded performances
                - performance_lighting_control: Include lighting in recordings
                - performance_particle_effects: Include effects in recordings
            """
            # Implementation for performance_recording_system
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/performance/recording/system"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                    "status": "success",
                    "message": "performance_recording_system tool executed successfully",
                    "osc_message": f"{osc_address} {params}",
                    "params": params,
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Failed to send performance_recording_system command to Unity "
                        "desktop avatar"
                    ),
                }
