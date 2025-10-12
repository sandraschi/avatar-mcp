"""
Audio Tools for AvatarMCP - Singing and Voice Synthesis

This module contains tools for audio processing, voice synthesis,
and vocal performance capabilities for VRM avatars.
"""

import os
import time
from typing import Dict, Any


class AudioTools:
    """Container for all audio-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize audio tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all audio tools with the MCP server."""
        # Register audio_singing_synthesize tool
        @self.mcp_server.mcp.tool()
        def audio_singing_synthesize(params: Dict[str, Any]) -> Dict[str, Any]:
            '''Generate synthesized singing voice from lyrics and melody.

            Creates realistic singing audio by combining lyrics with musical notes,
            allowing avatars to perform songs with synthesized vocals. Perfect for
            making Nekomimi-chan sing enka songs or any other musical performance.

            Parameters:
                lyrics: Text lyrics to sing (required)
                    - Plain text or with timing annotations
                    - Supports multiple languages (Japanese for enka!)
                    - Can include pronunciation guides
                melody: Musical melody specification (required)
                    - Array of notes with pitch and duration
                    - MIDI note numbers (60 = C4, 62 = D4, etc.)
                    - Can be generated from MIDI files or specified manually
                voice_style: Singing style and voice characteristics (default: "enka_female")
                    - "enka_female" = Traditional Japanese enka female voice
                    - "enka_male" = Traditional Japanese enka male voice
                    - "pop_female" = Modern pop female voice
                    - "pop_male" = Modern pop male voice
                    - "opera" = Classical operatic voice
                emotion: Emotional delivery style (default: "passionate")
                    - "passionate" = Deep emotional delivery (perfect for enka)
                    - "joyful" = Happy, upbeat delivery
                    - "melancholic" = Sad, reflective delivery
                    - "neutral" = Straightforward delivery
                output_file: Path to save generated audio (default: auto-generated)
                    - WAV format recommended for best quality
                    - MP3 for smaller files
                    - Directory must be writable
                tempo: Song tempo in BPM (default: 120)
                    - 60-200 BPM range
                    - Affects timing and feel of the performance
                key: Musical key for the song (default: "C")
                    - Standard musical keys (C, D, E, F, G, A, B)
                    - Affects the pitch range and tonality

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - audio_file: Path to generated audio file
                    - duration: Length of generated audio in seconds
                    - sample_rate: Audio quality (44100 or 48000 Hz)
                    - voice_used: Which voice model was selected
                    - lyrics_processed: Number of lyrics processed
                    - notes_generated: Number of musical notes synthesized

            Usage:
                Use this tool to create singing performances for your avatars. Perfect for
                enka songs, musical numbers, or any vocal performance. The tool handles
                Japanese lyrics beautifully for authentic enka performances.

            Examples:
                Basic enka singing (Japanese lyrics):
                    result = await audio_singing_synthesize({
                        'lyrics': '雪が降る町に 別れの歌を 歌わせてあげて',
                        'melody': [
                            {'note': 64, 'duration': 1.0},  # E4
                            {'note': 62, 'duration': 0.5},  # D4
                            {'note': 60, 'duration': 1.5},  # C4
                            # ... more notes for the melody
                        ],
                        'voice_style': 'enka_female',
                        'emotion': 'passionate'
                    })
                    # Creates authentic Japanese enka singing

                Pop song with English lyrics:
                    result = await audio_singing_synthesize({
                        'lyrics': 'You are my sunshine, my only sunshine',
                        'melody': [
                            {'note': 67, 'duration': 1.0},  # G4
                            {'note': 69, 'duration': 1.0},  # A4
                            {'note': 71, 'duration': 1.0},  # B4
                            {'note': 72, 'duration': 2.0},  # C5
                        ],
                        'voice_style': 'pop_female',
                        'emotion': 'joyful',
                        'tempo': 140
                    })
                    # Creates cheerful pop singing

                Classical operatic performance:
                    result = await audio_singing_synthesize({
                        'lyrics': 'O mio babbino caro',
                        'melody': [
                            {'note': 69, 'duration': 1.5},  # A4
                            {'note': 71, 'duration': 0.5},  # B4
                            {'note': 72, 'duration': 2.0},  # C5
                            # ... opera melody notes
                        ],
                        'voice_style': 'opera',
                        'emotion': 'passionate',
                        'key': 'G'
                    })
                    # Creates dramatic operatic singing

                Custom tempo and key:
                    result = await audio_singing_synthesize({
                        'lyrics': 'Amazing grace, how sweet the sound',
                        'melody': [...],  # Hymn melody notes
                        'voice_style': 'enka_male',
                        'tempo': 80,  # Slow, reflective tempo
                        'key': 'F',   # Lower key for male voice
                        'emotion': 'melancholic'
                    })
                    # Creates slow, emotional performance

                Error handling:
                    result = await audio_singing_synthesize({
                        'lyrics': '',
                        'melody': []
                    })
                    if result['status'] == 'error':
                        logger.error(f"Synthesis failed: {result['message']}")
                    # Check lyrics and melody are provided

            Raises:
                ValueError: If lyrics or melody are empty/invalid
                RuntimeError: If voice synthesis engine unavailable
                FileNotFoundError: If output directory doesn't exist
                PermissionError: If output file cannot be written

            Notes:
                - Requires voice synthesis engine (may need additional installation)
                - Japanese lyrics are handled with proper pronunciation
                - Melody can be generated from MIDI files using external tools
                - Audio quality depends on voice model and system performance
                - Long lyrics may take time to synthesize
                - Output files are standard audio formats playable anywhere
                - Emotion affects vocal expression and timing

            See Also:
                - audio_lip_sync_analyze: Analyze audio for lip sync
                - audio_singing_karaoke: Create karaoke with lyrics
                - animation_play: Combine with avatar animations
                - unity_avatar_animation: Sync with Unity avatar movements
            '''
            return self.mcp_server._execute_audio_singing_synthesize(params)
