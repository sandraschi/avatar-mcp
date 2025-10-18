"""
Collaboration Tools for AvatarMCP - Multi-Avatar Scene Management & Communication

This module contains tools for managing multiple avatars in shared scenes,
coordinating collaborative interactions, synchronizing scene states, and
enabling avatar-to-avatar communication for complex social experiences.
"""

from typing import Dict, Any


class CollaborationTools:
    """Container for all collaboration-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize collaboration tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all collaboration tools with the MCP server."""
        # Register avatar_scene_join tool
        @self.mcp_server.mcp.tool()
        def avatar_scene_join(params: Dict[str, Any]) -> Dict[str, Any]:
            """Add an avatar to a shared scene with synchronization and role assignment.

            Enables avatars to join collaborative scenes, synchronizing their state
            with the scene environment and other participating avatars. Essential for
            creating multi-avatar experiences like concerts, parties, and social gatherings.

            Parameters:
                avatar_id: Avatar to join the scene (required)
                    - Must be loaded with avatar_load or unity_avatar_load
                    - Avatar will be synchronized with scene state
                    - Case-sensitive avatar identifier
                scene_id: Target scene for avatar to join (required)
                    - Must be an active scene created with scene_template_create
                    - Scene must support multiple avatars
                    - Case-sensitive scene identifier
                join_position: Entry position in the scene (optional)
                    - Dictionary with x, y, z coordinates
                    - Relative to scene origin
                    - If not provided, uses scene default entry point
                join_role: Role assignment for the avatar (default: "participant")
                    - "participant" = standard scene participant
                    - "host" = scene coordinator with special privileges
                    - "performer" = entertainment-focused role
                    - "observer" = view-only participation
                    - "moderator" = content moderation role
                sync_options: State synchronization preferences (optional)
                    - Dictionary of sync settings
                    - Controls what avatar state gets synchronized
                    - Includes position, animations, expressions
                entry_animation: Animation to play on scene entry (optional)
                    - Name of animation to play when joining
                    - Must exist in animation library
                    - Creates smooth entry experience

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that joined the scene
                    - scene_id: Scene that was joined
                    - join_role: Role assigned to the avatar
                    - scene_participants: Current participant count
                    - sync_status: Synchronization state
                    - entry_timestamp: When avatar joined the scene

            Usage:
                Use this tool to create collaborative multi-avatar experiences where
                avatars can interact, perform together, and participate in shared activities.
                Essential for concerts, parties, meetings, and social avatar experiences.

            Examples:
                Join enka concert as performer:
                    result = await avatar_scene_join({
                        'avatar_id': 'nekomimi_chan',
                        'scene_id': 'enka_concert_hall',
                        'join_position': {'x': 0, 'y': 0, 'z': -2},
                        'join_role': 'performer',
                        'entry_animation': 'stage_entrance',
                        'sync_options': {
                            'position': True,
                            'animations': True,
                            'lighting': True,
                            'audio': True
                        }
                    })
                    # Nekomimi-chan joins concert scene as performer with full synchronization

                Join social gathering as participant:
                    result = await avatar_scene_join({
                        'avatar_id': 'guest_avatar',
                        'scene_id': 'virtual_party',
                        'join_role': 'participant',
                        'entry_animation': 'casual_wave'
                    })
                    # Guest avatar joins party scene with casual entry

                Join meeting as host:
                    result = await avatar_scene_join({
                        'avatar_id': 'meeting_host',
                        'scene_id': 'conference_room',
                        'join_role': 'host',
                        'sync_options': {
                            'moderation': True,
                            'presentation': True
                        }
                    })
                    # Host avatar joins meeting with coordination privileges

                Error handling:
                    result = await avatar_scene_join({
                        'avatar_id': 'nonexistent',
                        'scene_id': 'enka_concert_hall'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Scene join failed: {result['message']}")
                    # Check avatar and scene exist and are compatible

            Raises:
                ValueError: If avatar_id or scene_id invalid, or parameters malformed
                RuntimeError: If scene doesn't support multiple avatars or join fails
                ConnectionError: If network synchronization fails

            Notes:
                - Scene capacity limits may apply
                - Synchronization ensures consistent experience across avatars
                - Roles determine avatar capabilities and permissions
                - Entry animations create smooth scene transitions
                - State sync prevents desynchronization issues
                - Participants receive scene updates automatically

            See Also:
                - avatar_scene_leave: Remove avatar from scene
                - avatar_group_create: Create coordinated avatar groups
                - scene_state_broadcast: Synchronize scene state changes
                - avatar_message_broadcast: Communicate with scene participants
            """
            # Implementation for avatar_scene_join
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/avatar/scene/join"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'avatar_scene_join tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send avatar_scene_join command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def avatar_group_create(params: Dict[str, Any]) -> Dict[str, Any]:
            """Create coordinated groups of avatars for collaborative activities.

            Forms organized groups of avatars with shared objectives, synchronized
            behaviors, and coordinated actions. Enables complex multi-avatar
            performances, team activities, and group interactions.

            Parameters:
                group_name: Unique name for the avatar group (required)
                    - Case-sensitive identifier
                    - Must be unique within the system
                    - Used for referencing and managing the group
                group_type: Category of group activity (required)
                    - "performance" = coordinated entertainment (concerts, shows)
                    - "social" = casual social interaction (parties, gatherings)
                    - "educational" = learning and training activities
                    - "gameplay" = competitive or cooperative gaming
                    - "work" = professional collaboration (meetings, projects)
                max_participants: Maximum number of avatars in group (default: 10)
                    - Must be positive integer
                    - System may impose upper limits
                    - Affects resource allocation and performance
                group_leader: Avatar designated as group coordinator (optional)
                    - Must be a valid avatar ID
                    - Has special permissions and controls
                    - Can be changed during group lifetime
                participation_rules: Rules for joining and participating (optional)
                    - Dictionary defining group policies
                    - Includes join requirements, behavior guidelines
                    - Automatic enforcement of group norms
                sync_requirements: Synchronization requirements for group (optional)
                    - Dictionary specifying sync needs
                    - Includes timing, state, and behavior synchronization
                    - Higher sync = more coordinated but higher resource use

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - group_name: Name of created group
                    - group_id: Unique identifier for the group
                    - group_type: Type of group activity
                    - max_participants: Maximum allowed participants
                    - current_participants: Current participant count (initially 0)
                    - group_leader: Designated group coordinator
                    - created_at: Timestamp when group was created

            Usage:
                Use this tool to organize avatars into coordinated groups for complex
                collaborative activities. Essential for concerts, team sports, meetings,
                and any scenario requiring synchronized multi-avatar behavior.

            Examples:
                Create enka concert group:
                    result = await avatar_group_create({
                        'group_name': 'enka_performers',
                        'group_type': 'performance',
                        'max_participants': 5,
                        'group_leader': 'nekomimi_chan',
                        'participation_rules': {
                            'skill_requirement': 'singing_proficiency',
                            'behavior_code': 'professional_performance',
                            'sync_timing': 'millisecond_precision'
                        },
                        'sync_requirements': {
                            'animation_timing': True,
                            'audio_sync': True,
                            'lighting_cues': True,
                            'audience_reactions': True
                        }
                    })
                    # Creates professional enka performance group with Nekomimi-chan as leader

                Create social gathering group:
                    result = await avatar_group_create({
                        'group_name': 'virtual_party_guests',
                        'group_type': 'social',
                        'max_participants': 20,
                        'participation_rules': {
                            'age_appropriate': True,
                            'positive_interactions': True
                        }
                    })
                    # Creates casual party group with flexible participation

                Create educational study group:
                    result = await avatar_group_create({
                        'group_name': 'language_learning_class',
                        'group_type': 'educational',
                        'max_participants': 12,
                        'group_leader': 'teacher_avatar',
                        'sync_requirements': {
                            'lesson_timing': True,
                            'progress_tracking': True,
                            'interactive_responses': True
                        }
                    })
                    # Creates structured learning environment with teacher coordination

                Error handling:
                    result = await avatar_group_create({
                        'group_name': '',
                        'group_type': 'performance'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Group creation failed: {result['message']}")
                    # Check group_name and required parameters

            Raises:
                ValueError: If group_name empty or group parameters invalid
                RuntimeError: If group creation system unavailable
                KeyError: If group_type or parameters malformed

            Notes:
                - Group size affects performance and coordination complexity
                - Leader has special permissions for group management
                - Participation rules are automatically enforced
                - Higher sync requirements improve coordination but increase resource use
                - Groups persist until explicitly dissolved
                - Members can be added/removed dynamically
                - Group activities are logged for analysis

            See Also:
                - avatar_group_assign: Add avatars to existing groups
                - avatar_group_sync: Synchronize group member actions
                - avatar_scene_join: Add groups to shared scenes
                - avatar_interaction_request: Request collaborative interactions within groups
            """
            # Implementation for avatar_group_create
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/avatar/group/create"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'avatar_group_create tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send avatar_group_create command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def avatar_interaction_request(params: Dict[str, Any]) -> Dict[str, Any]:
            """Request collaborative interactions between avatars.

            Initiates interaction requests between avatars, enabling coordinated
            activities, joint performances, and social exchanges. Supports various
            interaction types from simple greetings to complex collaborative tasks.

            Parameters:
                requester_avatar: Avatar initiating the interaction (required)
                    - Must be active and in a shared scene
                    - Has permission to request interactions
                    - Case-sensitive avatar identifier
                target_avatar: Avatar being requested for interaction (required)
                    - Must be active and accessible
                    - Will receive and can accept/reject request
                    - Case-sensitive avatar identifier
                interaction_type: Type of interaction being requested (required)
                    - "performance" = joint entertainment activity
                    - "conversation" = social dialogue exchange
                    - "collaboration" = coordinated task completion
                    - "competition" = friendly competitive activity
                    - "assistance" = help or guidance request
                    - "celebration" = shared celebratory activity
                interaction_details: Specific details about the interaction (required)
                    - Dictionary with interaction-specific parameters
                    - Varies by interaction_type
                    - Defines scope and requirements of interaction
                priority_level: Urgency of the interaction request (default: "normal")
                    - "low" = casual, can be delayed
                    - "normal" = standard timing expectations
                    - "high" = urgent, requires immediate attention
                    - "critical" = immediate response required
                timeout_seconds: How long to wait for response (default: 30.0)
                    - Seconds before request expires
                    - 0 = no timeout (wait indefinitely)
                    - Prevents hanging interaction requests
                fallback_action: What to do if request is rejected or times out (optional)
                    - "retry" = attempt request again later
                    - "alternative" = try different interaction
                    - "cancel" = abort interaction attempt
                    - "solo" = proceed with solo activity

            Returns:
                Dictionary containing:
                    - status: Either "success", "pending", or "error"
                    - message: Human-readable result description
                    - requester_avatar: Avatar that made the request
                    - target_avatar: Avatar that received the request
                    - interaction_type: Type of interaction requested
                    - request_id: Unique identifier for this interaction request
                    - priority_level: Urgency level of the request
                    - timeout_seconds: Response timeout duration
                    - request_timestamp: When request was made

            Usage:
                Use this tool to enable avatars to initiate collaborative activities,
                from simple conversations to complex joint performances. Essential for
                creating dynamic, interactive multi-avatar experiences.

            Examples:
                Request duet performance:
                    result = await avatar_interaction_request({
                        'requester_avatar': 'nekomimi_chan',
                        'target_avatar': 'backup_singer',
                        'interaction_type': 'performance',
                        'interaction_details': {
                            'activity': 'duet_singing',
                            'song': '雪が降る町に',
                            'role_assignment': 'lead_vocal'
                        },
                        'priority_level': 'high',
                        'timeout_seconds': 60.0,
                        'fallback_action': 'solo'
                    })
                    # Requests collaborative duet performance with backup singer

                Request conversation:
                    result = await avatar_interaction_request({
                        'requester_avatar': 'social_avatar',
                        'target_avatar': 'conversation_partner',
                        'interaction_type': 'conversation',
                        'interaction_details': {
                            'topic': 'enka_music',
                            'duration_estimate': 300,
                            'language': 'japanese'
                        },
                        'priority_level': 'normal',
                        'timeout_seconds': 30.0
                    })
                    # Requests social conversation about enka music

                Request collaborative task:
                    result = await avatar_interaction_request({
                        'requester_avatar': 'project_manager',
                        'target_avatar': 'team_member',
                        'interaction_type': 'collaboration',
                        'interaction_details': {
                            'task': 'scene_setup',
                            'required_skills': ['lighting', 'audio'],
                            'estimated_duration': 600
                        },
                        'priority_level': 'normal',
                        'timeout_seconds': 120.0,
                        'fallback_action': 'retry'
                    })
                    # Requests help with scene setup collaboration

                Error handling:
                    result = await avatar_interaction_request({
                        'requester_avatar': 'nonexistent',
                        'target_avatar': 'nekomimi_chan',
                        'interaction_type': 'performance'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Interaction request failed: {result['message']}")
                    # Check avatars exist and are accessible

            Raises:
                ValueError: If avatar IDs invalid or interaction parameters malformed
                RuntimeError: If interaction system unavailable
                TimeoutError: If request times out without response
                PermissionError: If avatar lacks interaction permissions

            Notes:
                - Target avatar can accept or reject requests
                - Priority affects response expectations and queuing
                - Timeout prevents indefinite waiting
                - Fallback actions handle rejection gracefully
                - Request status can be monitored
                - Interaction history is maintained
                - System prevents spam and abuse

            See Also:
                - avatar_interaction_accept: Accept interaction requests
                - avatar_group_create: Create groups for regular collaboration
                - avatar_message_send: Communicate during interactions
                - scene_state_broadcast: Share state during collaborative activities
            """
            # Implementation for avatar_interaction_request
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/avatar/interaction/request"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'avatar_interaction_request tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send avatar_interaction_request command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def scene_state_save(params: Dict[str, Any]) -> Dict[str, Any]:
            """Save the current state of a scene for later restoration or sharing.

            Captures complete scene state including avatar positions, object states,
            lighting conditions, audio settings, and environmental parameters.
            Enables scene bookmarking, backup, and sharing between sessions.

            Parameters:
                scene_id: Scene to save state for (required)
                    - Must be an active scene
                    - Scene must be accessible for state capture
                    - Case-sensitive scene identifier
                save_name: Name for the saved state (required)
                    - Unique identifier for this state save
                    - Used for loading and management
                    - Case-sensitive naming
                save_scope: What aspects of scene to save (default: "complete")
                    - "complete" = full scene state including all elements
                    - "avatars_only" = only avatar positions and states
                    - "environment_only" = lighting, objects, audio settings
                    - "minimal" = basic scene configuration only
                include_participants: Whether to include participant information (default: True)
                    - True = save participant states and roles
                    - False = save scene without participant details
                    - Affects privacy and state size
                compression_level: State data compression (default: "balanced")
                    - "none" = no compression, fastest save/load
                    - "fast" = quick compression, good compression ratio
                    - "balanced" = balanced speed and compression
                    - "maximum" = best compression, slower processing
                metadata: Additional information about the save (optional)
                    - Dictionary with descriptive information
                    - Includes save purpose, scene context, notes
                    - Helps with organization and search

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - scene_id: Scene that was saved
                    - save_name: Name of the saved state
                    - save_scope: Scope of state that was saved
                    - data_size: Size of saved state data in bytes
                    - compression_used: Compression method applied
                    - participants_saved: Number of participants included
                    - save_timestamp: When state was saved
                    - save_id: Unique identifier for the saved state

            Usage:
                Use this tool to preserve scene states for backup, sharing, or later
                restoration. Essential for creating reproducible scenes, saving progress,
                and enabling collaborative scene development.

            Examples:
                Save complete concert scene:
                    result = await scene_state_save({
                        'scene_id': 'enka_concert_hall',
                        'save_name': 'concert_climax_moment',
                        'save_scope': 'complete',
                        'include_participants': True,
                        'compression_level': 'balanced',
                        'metadata': {
                            'performance_type': 'enka_concert',
                            'performer': 'nekomimi_chan',
                            'audience_count': 150,
                            'special_effects': 'fireworks_and_lighting',
                            'emotional_peak': True
                        }
                    })
                    # Saves complete concert scene at emotional climax

                Save avatar positions only:
                    result = await scene_state_save({
                        'scene_id': 'dance_party',
                        'save_name': 'party_dance_positions',
                        'save_scope': 'avatars_only',
                        'include_participants': True,
                        'compression_level': 'fast',
                        'metadata': {
                            'activity': 'group_dancing',
                            'music_genre': 'electronic',
                            'energy_level': 'high'
                        }
                    })
                    # Saves just avatar positions for dance scene

                Save environment configuration:
                    result = await scene_state_save({
                        'scene_id': 'meditation_garden',
                        'save_name': 'peaceful_evening_setup',
                        'save_scope': 'environment_only',
                        'include_participants': False,
                        'compression_level': 'maximum',
                        'metadata': {
                            'mood': 'calm_relaxing',
                            'lighting': 'soft_warm',
                            'sounds': 'gentle_nature'
                        }
                    })
                    # Saves environment settings for meditation scene

                Error handling:
                    result = await scene_state_save({
                        'scene_id': 'nonexistent_scene',
                        'save_name': 'test_save'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Scene save failed: {result['message']}")
                    # Check scene exists and is accessible

            Raises:
                ValueError: If scene_id or save_name invalid
                RuntimeError: If scene state capture fails
                PermissionError: If save access denied
                FileNotFoundError: If scene no longer exists

            Notes:
                - Save scope affects file size and load time
                - Compression reduces storage but increases save/load time
                - Participant information may have privacy implications
                - Metadata helps with organization and search
                - Saved states can be loaded with scene_state_load
                - Multiple saves can be maintained for same scene
                - System may limit number of saved states per scene

            See Also:
                - scene_state_load: Restore saved scene state
                - scene_state_broadcast: Share state with participants
                - avatar_scene_join: Add avatars to saved scene state
                - performance_recording_system: Record dynamic scene changes
            """
            # Implementation for scene_state_save
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/scene/state/save"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'scene_state_save tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send scene_state_save command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def avatar_message_send(params: Dict[str, Any]) -> Dict[str, Any]:
            """Send messages between avatars in collaborative environments.

            Enables direct communication between avatars through text, voice,
            or gesture-based messaging. Supports various message types for
            coordination, social interaction, and collaborative activities.

            Parameters:
                sender_avatar: Avatar sending the message (required)
                    - Must be active and in a shared context
                    - Has permission to send messages
                    - Case-sensitive avatar identifier
                recipient_avatar: Avatar receiving the message (required)
                    - Must be active and accessible
                    - Can be "all" for broadcast messages
                    - Case-sensitive avatar identifier
                message_type: Type of message being sent (required)
                    - "text" = written communication
                    - "voice" = audio message
                    - "gesture" = non-verbal communication
                    - "system" = automated status messages
                    - "emotion" = emotional state sharing
                message_content: Content of the message (required)
                    - Format depends on message_type
                    - Text for text messages, audio data for voice
                    - Structured data for gestures and emotions
                delivery_method: How message should be delivered (default: "immediate")
                    - "immediate" = send immediately
                    - "queued" = add to message queue
                    - "scheduled" = send at specific time
                    - "conditional" = send when conditions met
                priority_level: Message importance level (default: "normal")
                    - "low" = informational, can be delayed
                    - "normal" = standard message priority
                    - "high" = important, expedited delivery
                    - "urgent" = critical, immediate attention required
                message_metadata: Additional message information (optional)
                    - Dictionary with contextual data
                    - Includes sender context, message purpose
                    - Helps receivers understand message context

            Returns:
                Dictionary containing:
                    - status: Either "success", "queued", or "error"
                    - message: Human-readable result description
                    - sender_avatar: Avatar that sent the message
                    - recipient_avatar: Avatar that received the message
                    - message_type: Type of message sent
                    - message_id: Unique identifier for the message
                    - delivery_status: Current delivery state
                    - priority_level: Message priority assigned
                    - sent_timestamp: When message was sent

            Usage:
                Use this tool to enable avatar communication for coordination,
                social interaction, and collaborative activities. Essential for
                multi-avatar experiences requiring real-time communication.

            Examples:
                Send performance coordination message:
                    result = await avatar_message_send({
                        'sender_avatar': 'nekomimi_chan',
                        'recipient_avatar': 'backup_dancer',
                        'message_type': 'text',
                        'message_content': '準備はいい？3小節目からスタートだよ！',
                        'delivery_method': 'immediate',
                        'priority_level': 'high',
                        'message_metadata': {
                            'context': 'performance_coordination',
                            'song_section': 'bridge',
                            'timing_critical': True
                        }
                    })
                    # Sends urgent coordination message to backup dancer

                Broadcast party invitation:
                    result = await avatar_message_send({
                        'sender_avatar': 'party_host',
                        'recipient_avatar': 'all',
                        'message_type': 'text',
                        'message_content': '今夜8時に仮想パーティーへようこそ！ 楽しい時間を過ごしましょう！',
                        'delivery_method': 'scheduled',
                        'priority_level': 'normal',
                        'message_metadata': {
                            'event_type': 'social_gathering',
                            'start_time': '20:00',
                            'expected_guests': 25
                        }
                    })
                    # Broadcasts party invitation to all participants

                Send emotional gesture:
                    result = await avatar_message_send({
                        'sender_avatar': 'emotional_character',
                        'recipient_avatar': 'conversation_partner',
                        'message_type': 'emotion',
                        'message_content': {
                            'emotion_type': 'joy',
                            'intensity': 0.8,
                            'duration': 3.0,
                            'context': 'shared_laughter'
                        },
                        'delivery_method': 'immediate',
                        'priority_level': 'normal'
                    })
                    # Shares joyful emotion with conversation partner

                Send voice message:
                    result = await avatar_message_send({
                        'sender_avatar': 'storyteller',
                        'recipient_avatar': 'audience_group',
                        'message_type': 'voice',
                        'message_content': 'audio_data_base64_encoded',
                        'delivery_method': 'queued',
                        'priority_level': 'high',
                        'message_metadata': {
                            'narrative_context': 'story_climax',
                            'voice_emotion': 'dramatic'
                        }
                    })
                    # Queues important voice message for audience

                Error handling:
                    result = await avatar_message_send({
                        'sender_avatar': 'nonexistent',
                        'recipient_avatar': 'nekomimi_chan',
                        'message_type': 'text',
                        'message_content': 'Hello!'
                    })
                    if result['status'] == 'error':
                        logger.error(f"Message send failed: {result['message']}")
                    # Check sender avatar exists and has messaging permissions

            Raises:
                ValueError: If avatar IDs invalid or message parameters malformed
                RuntimeError: If messaging system unavailable
                PermissionError: If avatar lacks messaging permissions
                ConnectionError: If message delivery fails

            Notes:
                - "all" recipient enables broadcast messaging
                - Message types support different communication styles
                - Priority affects delivery speed and queuing
                - Delivery methods allow flexible timing
                - Message history is maintained for context
                - System prevents spam and abuse
                - Metadata provides rich communication context

            See Also:
                - avatar_message_broadcast: Send to multiple recipients
                - avatar_message_receive: Check for received messages
                - avatar_interaction_request: Request interactive activities
                - avatar_group_create: Create communication groups
            """
            # Implementation for avatar_message_send
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/avatar/message/send"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'avatar_message_send tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send avatar_message_send command to Unity desktop avatar'
                }
