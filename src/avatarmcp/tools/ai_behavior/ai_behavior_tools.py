"""
AI Behavior Tools for AvatarMCP - Intelligent Avatar Behavior & Response Systems

This module contains AI-powered tools for creating intelligent, adaptive avatar behaviors
that learn from interactions, adapt to contexts, and provide natural, personality-driven
responses for immersive avatar experiences.
"""

from typing import Dict, Any


class AIBehaviorTools:
    """Container for all AI behavior-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize AI behavior tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all AI behavior tools with the MCP server."""
        # Register ai_conversation_respond tool
        @self.mcp_server.mcp.tool()
        def ai_conversation_respond(params: Dict[str, Any]) -> Dict[str, Any]:
            """Generate AI-powered intelligent responses for avatar conversations.

            Uses advanced natural language processing and personality modeling to create
            contextually appropriate, emotionally intelligent responses that maintain
            consistent character personalities and adapt to conversation flow.

            Parameters:
                avatar_id: Avatar to generate response for (required)
                    - Must have established personality and conversation history
                    - Avatar must be active and responsive
                    - Case-sensitive avatar identifier
                user_input: User's message or input to respond to (required)
                    - Text input from user interaction
                    - Can include context and emotional cues
                    - Supports multiple languages
                conversation_context: Current conversation state and history (optional)
                    - Previous messages and responses
                    - Emotional state of conversation
                    - Topic and context information
                response_style: Desired response characteristics (default: "natural")
                    - "natural" = conversational and authentic
                    - "formal" = polite and professional
                    - "playful" = fun and lighthearted
                    - "empathetic" = understanding and supportive
                    - "concise" = brief and direct
                emotional_tone: Target emotional tone for response (optional)
                    - "positive" = upbeat and encouraging
                    - "neutral" = balanced and objective
                    - "negative" = concerned or serious
                    - "auto" = adapt to conversation context
                personality_influence: How strongly to apply avatar personality (default: 0.8)
                    - 0.0 = generic responses only
                    - 1.0 = strongly personality-driven
                    - Affects response style and word choice
                creativity_level: Response creativity and variety (default: 0.6)
                    - 0.0 = predictable, standard responses
                    - 1.0 = highly creative and varied
                    - Higher values increase response diversity

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that generated the response
                    - response_text: Generated conversational response
                    - emotional_tone: Detected emotional tone of response
                    - confidence_score: AI confidence in response appropriateness
                    - personality_factors: Personality traits that influenced response
                    - response_timestamp: When response was generated

            Usage:
                Use this tool to create intelligent, personality-consistent responses
                that make avatars feel alive and engaging in conversations. Essential
                for creating immersive social experiences and natural interactions.

            Examples:
                Generate natural conversation response:
                    result = await ai_conversation_respond({
                        'avatar_id': 'nekomimi_chan',
                        'user_input': 'How are you feeling today?',
                        'conversation_context': {
                            'previous_messages': ['Hello!', 'Nice to meet you!'],
                            'current_topic': 'feelings'
                        },
                        'response_style': 'natural',
                        'emotional_tone': 'positive',
                        'personality_influence': 0.9
                    })
                    # Generates warm, personality-driven response about feelings

                Create empathetic support response:
                    result = await ai_conversation_respond({
                        'avatar_id': 'counselor_avatar',
                        'user_input': 'I had a really tough day at work',
                        'conversation_context': {
                            'emotional_state': 'distressed',
                            'support_needed': True
                        },
                        'response_style': 'empathetic',
                        'emotional_tone': 'supportive',
                        'creativity_level': 0.7
                    })
                    # Generates understanding, supportive response for difficult day

                Professional formal response:
                    result = await ai_conversation_respond({
                        'avatar_id': 'business_executive',
                        'user_input': 'Can we schedule a meeting?',
                        'response_style': 'formal',
                        'personality_influence': 0.6,
                        'creativity_level': 0.3
                    })
                    # Generates professional, business-appropriate response

                Playful creative interaction:
                    result = await ai_conversation_respond({
                        'avatar_id': 'fun_character',
                        'user_input': 'What should we do today?',
                        'response_style': 'playful',
                        'emotional_tone': 'excited',
                        'creativity_level': 0.9
                    })
                    # Generates fun, creative suggestions with high energy

                Error handling:
                    result = await ai_conversation_respond({
                        'avatar_id': 'nonexistent',
                        'user_input': 'Hello'
                    })
                    if result['status'] == 'error':
                        logger.error(f"AI conversation failed: {result['message']}")
                    # Check avatar exists and has AI capabilities enabled

            Raises:
                ValueError: If avatar_id invalid or conversation parameters malformed
                RuntimeError: If AI conversation system unavailable
                ConnectionError: If AI service cannot be reached

            Notes:
                - Responses adapt to conversation history and context
                - Personality consistency maintained across interactions
                - Emotional intelligence improves response appropriateness
                - Creativity level affects response variety and engagement
                - System learns from successful interactions over time
                - Multi-language support for international conversations
                - Response generation considers cultural context

            See Also:
                - avatar_personality_apply: Apply personality traits to avatars
                - emotion_state_machine: Manage emotional states in conversations
                - ai_behavior_adapt: Learn and adapt behavior patterns
                - ai_context_analyze: Understand conversation context
            """
            # Implementation for ai_conversation_respond
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/ai/conversation/respond"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'ai_conversation_respond tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send ai_conversation_respond command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def ai_behavior_adapt(params: Dict[str, Any]) -> Dict[str, Any]:
            """Enable avatars to learn and adapt their behavior based on interactions.

            Implements machine learning algorithms that allow avatars to learn from
            user interactions, adapt their responses, and develop personalized
            behavioral patterns over time for more natural and engaging experiences.

            Parameters:
                avatar_id: Avatar to adapt behavior for (required)
                    - Must have learning capabilities enabled
                    - Avatar must have interaction history
                    - Case-sensitive avatar identifier
                learning_mode: Type of behavioral learning to perform (required)
                    - "interaction_patterns" = learn from user interaction styles
                    - "preference_learning" = adapt to user preferences
                    - "emotional_response" = learn emotional response patterns
                    - "conversation_style" = adapt conversational approaches
                    - "activity_adaptation" = learn from activity participation
                adaptation_data: Data to learn and adapt from (required)
                    - Interaction history and outcomes
                    - User feedback and preferences
                    - Successful vs unsuccessful interactions
                adaptation_strength: How strongly to apply learned adaptations (default: 0.5)
                    - 0.0 = minimal adaptation (maintain original behavior)
                    - 1.0 = strong adaptation (heavily influenced by learning)
                    - Balance between consistency and adaptability
                learning_rate: Speed of behavioral adaptation (default: 0.1)
                    - 0.01 = very slow, gradual learning
                    - 0.5 = moderate learning speed
                    - 1.0 = rapid adaptation (may be unstable)
                reset_learning: Whether to reset learned behaviors (default: False)
                    - True = clear all learned adaptations
                    - False = continue building on existing learning
                    - Useful for behavior resets or fresh starts
                adaptation_scope: Which behaviors to adapt (default: "all")
                    - "all" = adapt all behavioral aspects
                    - "conversation" = only conversational behaviors
                    - "emotional" = only emotional responses
                    - "social" = only social interaction patterns

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that adapted behavior
                    - learning_mode: Type of learning performed
                    - adaptations_applied: Number of behavioral adaptations made
                    - adaptation_strength: Final adaptation strength applied
                    - learning_progress: Current learning progress (0.0-1.0)
                    - behavior_changes: Summary of behavioral modifications

            Usage:
                Use this tool to create avatars that grow and adapt through interactions,
                becoming more personalized and responsive over time. Essential for
                long-term avatar relationships and evolving character development.

            Examples:
                Learn from conversation patterns:
                    result = await ai_behavior_adapt({
                        'avatar_id': 'nekomimi_chan',
                        'learning_mode': 'conversation_style',
                        'adaptation_data': {
                            'successful_responses': ['warm_greetings', 'empathetic_listening'],
                            'user_feedback': 'positive',
                            'conversation_topics': ['enka_music', 'feelings', 'friendship']
                        },
                        'adaptation_strength': 0.7,
                        'learning_rate': 0.2
                    })
                    # Avatar learns to respond more warmly to music and emotional topics

                Adapt to user preferences:
                    result = await ai_behavior_adapt({
                        'avatar_id': 'personal_assistant',
                        'learning_mode': 'preference_learning',
                        'adaptation_data': {
                            'preferred_activities': ['reading', 'music', 'outdoor_activities'],
                            'communication_style': 'direct_and_concise',
                            'feedback_patterns': ['appreciates_efficiency', 'dislikes_small_talk']
                        },
                        'adaptation_strength': 0.8,
                        'adaptation_scope': 'conversation'
                    })
                    # Assistant adapts to user's preference for direct, efficient communication

                Learn emotional response patterns:
                    result = await ai_behavior_adapt({
                        'avatar_id': 'emotional_support',
                        'learning_mode': 'emotional_response',
                        'adaptation_data': {
                            'effective_emotions': ['empathy', 'encouragement', 'active_listening'],
                            'user_responses': ['feels_helped', 'opens_up_more'],
                            'stress_indicators': ['rushed_speech', 'negative_words']
                        },
                        'adaptation_strength': 0.6,
                        'learning_rate': 0.15
                    })
                    # Support avatar learns which emotional responses work best

                Reset and start fresh learning:
                    result = await ai_behavior_adapt({
                        'avatar_id': 'experiment_avatar',
                        'learning_mode': 'interaction_patterns',
                        'adaptation_data': {},
                        'reset_learning': True,
                        'adaptation_strength': 0.3
                    })
                    # Clears all learned behaviors and starts fresh adaptation

                Error handling:
                    result = await ai_behavior_adapt({
                        'avatar_id': 'nonexistent',
                        'learning_mode': 'conversation_style',
                        'adaptation_data': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"AI behavior adaptation failed: {result['message']}")
                    # Check avatar exists and has learning capabilities

            Raises:
                ValueError: If avatar_id invalid or adaptation parameters malformed
                RuntimeError: If AI learning system unavailable
                KeyError: If learning mode or adaptation data invalid

            Notes:
                - Learning improves avatar personalization over time
                - Adaptation strength balances consistency vs flexibility
                - Learning rate affects adaptation speed vs stability
                - Reset option allows fresh starts when needed
                - Scope control allows targeted behavioral changes
                - Progress tracking shows learning advancement
                - System maintains adaptation history for analysis

            See Also:
                - ai_conversation_respond: Use adapted behaviors in conversations
                - avatar_personality_apply: Apply learned traits to personality
                - ai_context_analyze: Understand context for better adaptation
                - ai_personality_predict: Predict user preferences for adaptation
            """
            # Implementation for ai_behavior_adapt
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/ai/behavior/adapt"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'ai_behavior_adapt tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send ai_behavior_adapt command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def ai_personality_predict(params: Dict[str, Any]) -> Dict[str, Any]:
            """Predict user preferences and behaviors for personalized avatar interactions.

            Uses machine learning to analyze user interaction patterns, predict preferences,
            and anticipate needs, enabling avatars to provide proactive, personalized
            experiences that feel intuitive and attentive.

            Parameters:
                avatar_id: Avatar to make predictions for (required)
                    - Must have interaction history with user
                    - Avatar needs prediction capabilities enabled
                    - Case-sensitive avatar identifier
                prediction_type: Type of prediction to generate (required)
                    - "preference" = predict user likes and dislikes
                    - "behavior" = predict likely user actions
                    - "emotional" = predict emotional responses
                    - "timing" = predict optimal interaction timing
                    - "content" = predict preferred content types
                prediction_context: Current context for predictions (required)
                    - Situation and environmental factors
                    - Recent interaction history
                    - User state and mood indicators
                confidence_threshold: Minimum confidence level for predictions (default: 0.6)
                    - 0.0 = accept all predictions (may include low confidence)
                    - 1.0 = only high-confidence predictions
                    - Higher thresholds reduce false predictions
                prediction_horizon: How far ahead to predict (default: "short_term")
                    - "immediate" = next few seconds/minutes
                    - "short_term" = next hour/day
                    - "long_term" = next week/month
                    - Affects prediction accuracy and usefulness
                adaptation_enabled: Whether to automatically adapt based on predictions (default: False)
                    - True = apply predictions to avatar behavior
                    - False = provide predictions for manual use
                    - Automatic adaptation increases responsiveness

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that made predictions
                    - prediction_type: Type of predictions generated
                    - predictions: Array of generated predictions with confidence scores
                    - average_confidence: Overall confidence in prediction set
                    - prediction_count: Number of predictions made
                    - adaptation_applied: Whether predictions were auto-applied

            Usage:
                Use this tool to create anticipatory, personalized avatar experiences
                that understand user preferences and proactively provide relevant
                interactions and content.

            Examples:
                Predict user preferences for activities:
                    result = await ai_personality_predict({
                        'avatar_id': 'activity_planner',
                        'prediction_type': 'preference',
                        'prediction_context': {
                            'time_of_day': 'evening',
                            'recent_activities': ['reading', 'music_listening'],
                            'user_mood': 'relaxed',
                            'weather': 'rainy'
                        },
                        'confidence_threshold': 0.7,
                        'prediction_horizon': 'short_term'
                    })
                    # Predicts user might prefer cozy indoor activities on rainy evening

                Anticipate emotional responses:
                    result = await ai_personality_predict({
                        'avatar_id': 'emotional_companion',
                        'prediction_type': 'emotional',
                        'prediction_context': {
                            'conversation_topic': 'career_challenges',
                            'user_stress_indicators': ['fast_typing', 'short_responses'],
                            'relationship_context': 'close_friend'
                        },
                        'confidence_threshold': 0.8,
                        'adaptation_enabled': True
                    })
                    # Predicts user needs emotional support and adapts responses accordingly

                Predict optimal interaction timing:
                    result = await ai_personality_predict({
                        'avatar_id': 'timing_expert',
                        'prediction_type': 'timing',
                        'prediction_context': {
                            'user_schedule': 'busy_workday',
                            'attention_patterns': ['focused_mornings', 'distracted_evenings'],
                            'current_time': '14:30'
                        },
                        'prediction_horizon': 'immediate'
                    })
                    # Predicts best time to initiate conversations during workday

                Content preference prediction:
                    result = await ai_personality_predict({
                        'avatar_id': 'content_curator',
                        'prediction_type': 'content',
                        'prediction_context': {
                            'previous_content': ['enka_music', 'japanese_culture', 'emotional_stories'],
                            'engagement_metrics': ['high_time_spent', 'frequent_returns'],
                            'cultural_background': 'mixed_heritage'
                        },
                        'confidence_threshold': 0.75
                    })
                    # Predicts user would enjoy cultural music and storytelling content

                Error handling:
                    result = await ai_personality_predict({
                        'avatar_id': 'new_avatar',
                        'prediction_type': 'preference',
                        'prediction_context': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"AI prediction failed: {result['message']}")
                    # Check avatar has sufficient interaction history for predictions

            Raises:
                ValueError: If avatar_id invalid or prediction parameters malformed
                RuntimeError: If AI prediction system unavailable
                KeyError: If prediction type or context data invalid

            Notes:
                - Prediction accuracy improves with interaction history
                - Confidence thresholds balance prediction volume vs accuracy
                - Different horizons serve different use cases
                - Automatic adaptation increases avatar responsiveness
                - Predictions can be overridden by explicit user preferences
                - System learns from prediction accuracy over time
                - Context awareness improves prediction relevance

            See Also:
                - ai_behavior_adapt: Adapt avatar behavior based on predictions
                - ai_context_analyze: Analyze context for better predictions
                - avatar_personality_apply: Apply predicted preferences to personality
                - ai_conversation_respond: Use predictions in conversation responses
            """
            # Implementation for ai_personality_predict
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/ai/personality/predict"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'ai_personality_predict tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send ai_personality_predict command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def ai_context_analyze(params: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze interaction context for intelligent avatar decision-making.

            Performs deep analysis of environmental, social, and situational context
            to provide avatars with rich understanding of their surroundings and
            enable more intelligent, contextually appropriate behaviors and responses.

            Parameters:
                avatar_id: Avatar to analyze context for (required)
                    - Must be active in a scene or interaction
                    - Avatar needs context analysis capabilities
                    - Case-sensitive avatar identifier
                analysis_scope: What aspects of context to analyze (required)
                    - "environmental" = physical surroundings and atmosphere
                    - "social" = relationships and social dynamics
                    - "emotional" = emotional states and mood indicators
                    - "situational" = current activity and circumstances
                    - "comprehensive" = all context aspects combined
                context_data: Current context information to analyze (required)
                    - Environmental factors, social relationships
                    - Current activities, emotional indicators
                    - Recent events and interaction history
                analysis_depth: How deeply to analyze context (default: "standard")
                    - "surface" = basic context recognition
                    - "standard" = moderate analysis with patterns
                    - "deep" = comprehensive analysis with insights
                    - "comprehensive" = full contextual understanding
                real_time_analysis: Whether to provide ongoing analysis (default: False)
                    - True = continuous context monitoring and updates
                    - False = single analysis of current context
                    - Real-time mode requires more processing resources
                insight_types: Types of insights to generate (optional)
                    - Array of specific analysis types to focus on
                    - ["opportunities", "risks", "preferences", "dynamics"]
                    - If empty, generates all available insights

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that performed analysis
                    - analysis_scope: Scope of context analyzed
                    - context_insights: Key insights and findings from analysis
                    - confidence_levels: Confidence scores for different insights
                    - actionable_recommendations: Suggested avatar actions based on context
                    - analysis_timestamp: When analysis was performed

            Usage:
                Use this tool to give avatars deep situational awareness and understanding,
                enabling them to make intelligent decisions and provide contextually
                appropriate responses in complex social and environmental situations.

            Examples:
                Analyze social dynamics in group setting:
                    result = await ai_context_analyze({
                        'avatar_id': 'social_analyzer',
                        'analysis_scope': 'social',
                        'context_data': {
                            'group_members': ['alice', 'bob', 'charlie'],
                            'relationship_status': {'alice': 'close_friend', 'bob': 'acquaintance'},
                            'current_activity': 'group_conversation',
                            'emotional_tones': {'alice': 'excited', 'bob': 'reserved'}
                        },
                        'analysis_depth': 'deep',
                        'insight_types': ['dynamics', 'opportunities']
                    })
                    # Analyzes social relationships and suggests interaction strategies

                Environmental context for scene adaptation:
                    result = await ai_context_analyze({
                        'avatar_id': 'scene_adaptor',
                        'analysis_scope': 'environmental',
                        'context_data': {
                            'lighting_conditions': 'dim_intimate',
                            'background_music': 'jazz_piano',
                            'participant_count': 8,
                            'atmospheric_mood': 'romantic_formal'
                        },
                        'analysis_depth': 'comprehensive'
                    })
                    # Analyzes scene atmosphere and suggests behavioral adaptations

                Emotional context awareness:
                    result = await ai_context_analyze({
                        'avatar_id': 'emotional_intelligence',
                        'analysis_scope': 'emotional',
                        'context_data': {
                            'user_emotion': 'anxious',
                            'conversation_tone': 'urgent',
                            'body_language': 'tense_posture',
                            'verbal_cues': ['fast_speech', 'repeated_phrases']
                        },
                        'real_time_analysis': True
                    })
                    # Provides ongoing emotional context analysis for supportive responses

                Situational awareness for activity planning:
                    result = await ai_context_analyze({
                        'avatar_id': 'activity_planner',
                        'analysis_scope': 'situational',
                        'context_data': {
                            'current_activity': 'waiting_in_lobby',
                            'time_constraints': 'limited_time',
                            'user_goals': 'networking_event',
                            'environmental_factors': 'crowded_noisy'
                        },
                        'insight_types': ['opportunities', 'risks']
                    })
                    # Analyzes situation and provides strategic recommendations

                Comprehensive context integration:
                    result = await ai_context_analyze({
                        'avatar_id': 'holistic_analyzer',
                        'analysis_scope': 'comprehensive',
                        'context_data': {
                            'environmental': {'setting': 'intimate_restaurant', 'mood': 'romantic'},
                            'social': {'relationship': 'first_date', 'comfort_level': 'nervous'},
                            'emotional': {'primary_emotion': 'excitement', 'secondary': 'anxiety'},
                            'situational': {'time_pressure': 'moderate', 'goals': 'good_impression'}
                        },
                        'analysis_depth': 'comprehensive'
                    })
                    # Provides integrated analysis across all context dimensions

                Error handling:
                    result = await ai_context_analyze({
                        'avatar_id': 'nonexistent',
                        'analysis_scope': 'environmental',
                        'context_data': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"AI context analysis failed: {result['message']}")
                    # Check avatar exists and context data is provided

            Raises:
                ValueError: If avatar_id invalid or analysis parameters malformed
                RuntimeError: If AI analysis system unavailable
                KeyError: If analysis scope or context data invalid

            Notes:
                - Analysis depth affects processing time and insight quality
                - Real-time analysis provides ongoing situational awareness
                - Context insights improve with analysis history
                - Actionable recommendations guide avatar behavior
                - Confidence levels help prioritize insights
                - Multi-dimensional analysis provides comprehensive understanding
                - System learns from successful context interpretations

            See Also:
                - ai_personality_predict: Use context analysis for predictions
                - ai_behavior_adapt: Adapt behavior based on context insights
                - ai_conversation_respond: Use context for conversation responses
                - scene_state_broadcast: Share context awareness with scene
            """
            # Implementation for ai_context_analyze
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/ai/context/analyze"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'ai_context_analyze tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send ai_context_analyze command to Unity desktop avatar'
                }

        @self.mcp_server.mcp.tool()
        def ai_interaction_learn(params: Dict[str, Any]) -> Dict[str, Any]:
            """Enable avatars to learn from interaction patterns and improve over time.

            Implements advanced learning algorithms that analyze interaction success,
            user satisfaction, and behavioral outcomes to continuously improve avatar
            responses, timing, and engagement strategies for better user experiences.

            Parameters:
                avatar_id: Avatar to perform interaction learning for (required)
                    - Must have interaction history and learning enabled
                    - Avatar needs sufficient interaction data
                    - Case-sensitive avatar identifier
                learning_objective: What aspect of interactions to learn from (required)
                    - "success_patterns" = learn what makes interactions successful
                    - "user_satisfaction" = learn user preferences and satisfaction
                    - "timing_optimization" = learn optimal response timing
                    - "engagement_strategies" = learn effective engagement techniques
                    - "error_prevention" = learn to avoid problematic interactions
                interaction_data: Historical interaction data to learn from (required)
                    - Past interactions with outcomes and feedback
                    - User responses and engagement metrics
                    - Success rates and improvement opportunities
                learning_algorithm: Learning approach to use (default: "reinforcement")
                    - "reinforcement" = learn from positive/negative outcomes
                    - "supervised" = learn from labeled good/bad examples
                    - "unsupervised" = discover patterns in interaction data
                    - "transfer" = apply learning from similar contexts
                learning_intensity: How aggressively to apply learning (default: 0.4)
                    - 0.0 = minimal learning changes
                    - 1.0 = maximum learning application (may be unstable)
                    - Balance between improvement and consistency
                validation_method: How to validate learned improvements (default: "cross_validation")
                    - "cross_validation" = test on held-out interaction data
                    - "user_feedback" = validate with explicit user feedback
                    - "performance_metrics" = measure engagement improvements
                    - "none" = apply learning without validation
                reset_baseline: Whether to reset learning baseline (default: False)
                    - True = start learning from scratch
                    - False = build on existing learned patterns
                    - Useful for major behavior changes or fresh starts

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar that performed learning
                    - learning_objective: What was learned from interactions
                    - improvements_identified: Number of improvement opportunities found
                    - learning_accuracy: Accuracy of learned patterns
                    - behavioral_changes: Summary of applied behavioral modifications
                    - validation_results: Results of learning validation if performed

            Usage:
                Use this tool to create avatars that continuously improve their interaction
                skills, becoming more effective and satisfying conversational partners
                through experience and feedback.

            Examples:
                Learn successful conversation patterns:
                    result = await ai_interaction_learn({
                        'avatar_id': 'conversation_expert',
                        'learning_objective': 'success_patterns',
                        'interaction_data': {
                            'successful_interactions': [
                                {'topic': 'shared_interests', 'outcome': 'engaged'},
                                {'approach': 'empathetic_listening', 'outcome': 'trusted'}
                            ],
                            'unsuccessful_interactions': [
                                {'topic': 'controversial_politics', 'outcome': 'disengaged'},
                                {'approach': 'interrupting_speaker', 'outcome': 'frustrated'}
                            ]
                        },
                        'learning_algorithm': 'reinforcement',
                        'learning_intensity': 0.6
                    })
                    # Learns to focus on shared interests and empathetic listening

                Optimize response timing:
                    result = await ai_interaction_learn({
                        'avatar_id': 'timing_optimizer',
                        'learning_objective': 'timing_optimization',
                        'interaction_data': {
                            'timing_success': [
                                {'delay': 1.5, 'context': 'thoughtful_response', 'outcome': 'appreciated'},
                                {'delay': 0.8, 'context': 'quick_acknowledgment', 'outcome': 'responsive'}
                            ],
                            'timing_failures': [
                                {'delay': 8.0, 'context': 'long_pause', 'outcome': 'awkward_silence'},
                                {'delay': 0.1, 'context': 'instant_response', 'outcome': 'rushed_feeling'}
                            ]
                        },
                        'validation_method': 'performance_metrics'
                    })
                    # Learns optimal response timing for different conversation contexts

                Improve user satisfaction:
                    result = await ai_interaction_learn({
                        'avatar_id': 'satisfaction_optimizer',
                        'learning_objective': 'user_satisfaction',
                        'interaction_data': {
                            'high_satisfaction': [
                                {'behavior': 'personalized_responses', 'rating': 9},
                                {'behavior': 'active_listening', 'rating': 8}
                            ],
                            'low_satisfaction': [
                                {'behavior': 'generic_responses', 'rating': 4},
                                {'behavior': 'monologue_style', 'rating': 3}
                            ]
                        },
                        'learning_algorithm': 'supervised',
                        'learning_intensity': 0.5
                    })
                    # Learns to prioritize personalized, listening-focused interactions

                Prevent interaction errors:
                    result = await ai_interaction_learn({
                        'avatar_id': 'error_preventer',
                        'learning_objective': 'error_prevention',
                        'interaction_data': {
                            'problematic_patterns': [
                                {'pattern': 'topic_domination', 'frequency': 'high', 'impact': 'negative'},
                                {'pattern': 'insensitive_comments', 'frequency': 'occasional', 'impact': 'severe'}
                            ],
                            'successful_avoidance': [
                                {'pattern': 'balanced_conversation', 'outcome': 'positive'},
                                {'pattern': 'empathy_focused', 'outcome': 'trusted'}
                            ]
                        },
                        'learning_intensity': 0.7,
                        'validation_method': 'user_feedback'
                    })
                    # Learns to avoid problematic interaction patterns

                Reset and start fresh learning:
                    result = await ai_interaction_learn({
                        'avatar_id': 'fresh_start_avatar',
                        'learning_objective': 'success_patterns',
                        'interaction_data': {},
                        'reset_baseline': True,
                        'learning_intensity': 0.3
                    })
                    # Clears all learned patterns and starts fresh interaction learning

                Error handling:
                    result = await ai_interaction_learn({
                        'avatar_id': 'new_avatar',
                        'learning_objective': 'success_patterns',
                        'interaction_data': {}
                    })
                    if result['status'] == 'error':
                        logger.error(f"AI interaction learning failed: {result['message']}")
                    # Check avatar has sufficient interaction history for learning

            Raises:
                ValueError: If avatar_id invalid or learning parameters malformed
                RuntimeError: If AI learning system unavailable
                KeyError: If learning objective or interaction data invalid

            Notes:
                - Learning effectiveness improves with more interaction data
                - Different algorithms suit different learning objectives
                - Learning intensity balances improvement vs stability
                - Validation ensures learning actually improves interactions
                - Reset option allows fresh starts when needed
                - System tracks learning progress and effectiveness
                - Continuous learning enables ongoing improvement

            See Also:
                - ai_behavior_adapt: Apply learned patterns to behavior
                - ai_conversation_respond: Use learned patterns in responses
                - ai_context_analyze: Analyze context for learning insights
                - ai_personality_predict: Use learning for better predictions
            """
            # Implementation for ai_interaction_learn
            # Send OSC message to Unity desktop avatar
            osc_address = "/avatar/ai/interaction/learn"
            if self.mcp_server._send_osc_message(osc_address, str(params)):
                return {
                'status': 'success',
                'message': 'ai_interaction_learn tool executed successfully',
                'osc_message': f'{osc_address} {params}',
                'params': params
                }
            else:
                return {
                'status': 'error',
                'message': 'Failed to send ai_interaction_learn command to Unity desktop avatar'
                }
