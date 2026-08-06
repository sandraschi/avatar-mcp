"""
Speech handler for the Avatar MCP server.

This module provides speech-to-text (STT) and text-to-speech (TTS) capabilities
for voice interaction with the avatar system.
"""

import asyncio
import logging
import os
import time
import wave
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
import sounddevice as sd
from pydantic import BaseModel, Field

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

# Type aliases
AudioData = np.ndarray  # 1D numpy array of float32 samples in [-1, 1]
SpeechResult = dict[str, Any]


class SpeechState(StrEnum):
    """Speech recognition states."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class TTSVoice(BaseModel):
    """TTS voice configuration."""

    id: str = Field(..., description="Unique voice ID")
    name: str = Field(..., description="Display name")
    language: str = Field(..., description="Language code (e.g., 'en-US')")
    gender: str | None = Field(None, description="Voice gender ('male', 'female', 'neutral')")
    provider: str = Field(..., description="TTS provider (e.g., 'system', 'google', 'azure')")
    engine: str | None = Field(None, description="Engine name (provider-specific)")
    sample_rate: int = Field(24000, description="Sample rate in Hz")
    is_default: bool = Field(False, description="Whether this is the default voice")


class STTConfig(BaseModel):
    """Speech-to-Text configuration."""

    enabled: bool = Field(True, description="Whether STT is enabled")
    language: str = Field("en-US", description="Language code for speech recognition")
    energy_threshold: int = Field(300, description="Energy level for mic to detect")
    pause_threshold: float = Field(0.8, description="Seconds of silence to end listening")
    phrase_time_limit: float = Field(10.0, description="Maximum seconds before stopping")
    dynamic_energy: bool = Field(True, description="Adjust energy threshold based on ambient noise")
    save_audio: bool = Field(False, description="Save recorded audio for debugging")
    audio_dir: str = Field("data/audio", description="Directory to save audio files")


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""

    enabled: bool = Field(True, description="Whether TTS is enabled")
    default_voice: str = Field("default", description="Default voice ID to use")
    rate: int = Field(175, description="Speech rate (words per minute)")
    volume: float = Field(1.0, description="Volume (0.0 to 1.0)")
    play_audio: bool = Field(True, description="Play audio through speakers")
    save_audio: bool = Field(False, description="Save generated audio files")
    audio_dir: str = Field("data/audio", description="Directory to save audio files")


@dataclass
class SpeechRecognitionResult:
    """Result of a speech recognition operation."""

    text: str = ""
    is_final: bool = False
    confidence: float = 0.0
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    audio_data: bytes | None = None
    audio_path: str | None = None


class SpeechHandler(BaseHandler):
    """Handler for speech recognition and synthesis."""

    def __init__(self, server: Any = None):
        """Initialize the speech handler."""
        super().__init__(server)
        self.state: SpeechState = SpeechState.IDLE
        self._stt_config = STTConfig()
        self._tts_config = TTSConfig()
        self._voices: dict[str, TTSVoice] = {}
        self._audio_device_info: dict[str, Any] = {}
        self._current_utterance: asyncio.Future | None = None
        self._audio_stream = None
        self._stop_listening = asyncio.Event()
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._sample_rate = 16000  # Default sample rate for audio processing
        self._channels = 1  # Mono audio
        self._audio_processing_task: asyncio.Task | None = None
        self._audio_playback_task: asyncio.Task | None = None
        self._audio_callback = None

    async def _initialize(self) -> None:
        """Initialize the speech handler."""
        # Create audio directories if they don't exist
        os.makedirs(self._stt_config.audio_dir, exist_ok=True)
        os.makedirs(self._tts_config.audio_dir, exist_ok=True)

        # Initialize audio devices
        await self._initialize_audio_devices()

        # Load available TTS voices
        await self._load_voices()

        # Start background tasks
        self._audio_processing_task = asyncio.create_task(self._process_audio_queue())

        logger.info("Speech handler initialized")

    async def _initialize_audio_devices(self) -> None:
        """Initialize audio input/output devices."""
        try:
            # Get default input/output devices
            default_input = sd.query_devices(kind="input")
            default_output = sd.query_devices(kind="output")

            self._audio_device_info = {
                "input_device": default_input["name"],
                "input_channels": default_input["max_input_channels"],
                "output_device": default_output["name"],
                "output_channels": default_output["max_output_channels"],
                "sample_rate": default_input["default_samplerate"],
            }

            # Update sample rate from device if available
            if self._audio_device_info["sample_rate"] > 0:
                self._sample_rate = int(self._audio_device_info["sample_rate"])

            logger.info(
                f"Audio devices initialized. Input: {default_input['name']}, "
                f"Output: {default_output['name']}, Sample rate: {self._sample_rate}Hz"
            )

        except Exception as e:
            logger.error(f"Error initializing audio devices: {e!s}")
            self.state = SpeechState.ERROR

    async def _load_voices(self) -> None:
        """Load available TTS voices."""
        try:
            # Add system voices (if available)
            self._add_system_voices()

            # Add a default voice if none found
            if not self._voices:
                default_voice = TTSVoice(
                    id="default",
                    name="Default Voice",
                    language="en-US",
                    gender="female",
                    provider="system",
                    is_default=True,
                )
                self._voices[default_voice.id] = default_voice

            logger.info(f"Loaded {len(self._voices)} TTS voices")

        except Exception as e:
            logger.error(f"Error loading TTS voices: {e!s}")

    def _add_system_voices(self) -> None:
        """Add system-provided TTS voices."""
        try:
            # This is a placeholder - in a real implementation, you would query the system TTS
            # For example, on Windows, you might use pyttsx3 or win32com to get voices
            # Here we'll add some example voices

            # Example English voices
            self._voices["en-us-1"] = TTSVoice(
                id="en-us-1",
                name="English (US) - Female",
                language="en-US",
                gender="female",
                provider="system",
                is_default=True,
            )

            self._voices["en-gb-1"] = TTSVoice(
                id="en-gb-1",
                name="English (UK) - Male",
                language="en-GB",
                gender="male",
                provider="system",
            )

        except Exception as e:
            logger.warning(f"Could not load system voices: {e!s}")

    async def start_listening(self) -> bool:
        """Start listening for speech input.

        Returns:
            bool: True if listening started successfully, False otherwise
        """
        if self.state != SpeechState.IDLE:
            logger.warning(f"Cannot start listening in state: {self.state}")
            return False

        if not self._stt_config.enabled:
            logger.warning("Speech-to-text is disabled in configuration")
            return False

        try:
            self.state = SpeechState.LISTENING
            self._stop_listening.clear()

            # Start audio capture in a separate thread
            self._audio_stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                callback=self._audio_callback,
                dtype="float32",
            )

            self._audio_stream.start()
            logger.info("Started listening for speech input")
            return True

        except Exception as e:
            self.state = SpeechState.ERROR
            logger.error(f"Error starting speech recognition: {e!s}")
            return False

    async def stop_listening(self) -> None:
        """Stop listening for speech input."""
        if self.state == SpeechState.LISTENING:
            self._stop_listening.set()

            if self._audio_stream is not None:
                self._audio_stream.stop()
                self._audio_stream.close()
                self._audio_stream = None

            self.state = SpeechState.IDLE
            logger.info("Stopped listening for speech input")

    async def recognize_speech(self, audio_data: bytes | None = None) -> SpeechRecognitionResult:
        """Recognize speech from audio data or microphone input.

        Args:
            audio_data: Optional pre-recorded audio data to recognize

        Returns:
            SpeechRecognitionResult with the recognition results
        """
        result = SpeechRecognitionResult()

        try:
            self.state = SpeechState.PROCESSING

            if audio_data is not None:
                # Process provided audio data
                result = await self._process_audio(audio_data)
            else:
                # Record from microphone
                if not await self.start_listening():
                    result.error = "Failed to start listening"
                    return result

                # Wait for speech to start
                await asyncio.sleep(0.5)  # Small delay to avoid clipping

                # Record until silence or timeout
                audio_frames = []
                start_time = time.time()

                while (time.time() - start_time) < self._stt_config.phrase_time_limit:
                    if self._stop_listening.is_set():
                        break

                    try:
                        # Get audio data from queue (non-blocking)
                        try:
                            chunk = self._audio_queue.get_nowait()
                            audio_frames.append(chunk)
                        except asyncio.QueueEmpty:
                            await asyncio.sleep(0.1)
                            continue

                        # Check for silence (implement silence detection here)
                        # For now, just process after a fixed duration
                        if (time.time() - start_time) >= 2.0:  # Process after 2 seconds
                            break

                    except Exception as e:
                        logger.error(f"Error during speech recording: {e!s}")
                        break

                # Stop listening
                await self.stop_listening()

                if audio_frames:
                    # Process recorded audio
                    combined_audio = b"".join(audio_frames)
                    result = await self._process_audio(combined_audio)
                else:
                    result.error = "No audio data recorded"

            return result

        except Exception as e:
            self.state = SpeechState.ERROR
            result.error = str(e)
            logger.error(f"Speech recognition error: {e!s}", exc_info=True)
            return result

        finally:
            self.state = SpeechState.IDLE

    async def _process_audio(self, audio_data: bytes) -> SpeechRecognitionResult:
        """Process audio data for speech recognition.

        Args:
            audio_data: Raw audio data to process

        Returns:
            SpeechRecognitionResult with the recognition results
        """
        result = SpeechRecognitionResult()

        try:
            # Save audio for debugging if enabled
            audio_path = None
            if self._stt_config.save_audio:
                timestamp = int(time.time())
                audio_path = os.path.join(self._stt_config.audio_dir, f"recording_{timestamp}.wav")
                self._save_audio(audio_data, audio_path)
                result.audio_path = audio_path

            # In a real implementation, you would send the audio to a speech recognition service
            # For now, we'll just return a placeholder result
            result.text = (
                "This is a placeholder for recognized speech. "
                "In a real implementation, this would contain the actual recognized text."
            )
            result.is_final = True
            result.confidence = 0.9
            result.alternatives = [
                {"text": result.text, "confidence": 0.9},
                {"text": "This is a placeholder for recognized speech.", "confidence": 0.8},
                {"text": "This is a placeholder.", "confidence": 0.7},
            ]
            result.audio_data = audio_data

            return result

        except Exception as e:
            result.error = f"Error processing audio: {e!s}"
            logger.error(result.error, exc_info=True)
            return result

    def _save_audio(self, audio_data: bytes, filepath: str) -> None:
        """Save audio data to a WAV file."""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Save as WAV file
            with wave.open(filepath, "wb") as wf:
                wf.setnchannels(self._channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self._sample_rate)
                wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())

            logger.debug(f"Saved audio to {filepath}")

        except Exception as e:
            logger.error(f"Error saving audio to {filepath}: {e!s}")

    async def speak(self, text: str, voice_id: str | None = None, **kwargs) -> dict[str, Any]:
        """Convert text to speech and optionally play it.

        Args:
            text: Text to speak
            voice_id: Optional voice ID to use (defaults to configured voice)
            **kwargs: Additional options (rate, volume, etc.)

        Returns:
            Dictionary with results including audio data and path if saved
        """
        if not self._tts_config.enabled:
            return {"success": False, "error": "Text-to-speech is disabled"}

        self.state = SpeechState.SPEAKING

        try:
            # Get voice to use
            voice = self._get_voice(voice_id)
            if not voice:
                return {"success": False, "error": f"Voice not found: {voice_id}"}

            # Generate speech (in a real implementation, this would call a TTS service)
            logger.info(f"Speaking text with voice {voice_id}: {text[:100]}...")

            # Simulate speech generation time
            await asyncio.sleep(0.5)

            # In a real implementation, this would generate actual audio data
            audio_data = self._generate_silence(1.0)  # 1 second of silence as placeholder

            # Save audio if enabled
            audio_path = None
            if self._tts_config.save_audio:
                timestamp = int(time.time())
                os.makedirs(self._tts_config.audio_dir, exist_ok=True)
                audio_path = os.path.join(self._tts_config.audio_dir, f"tts_{timestamp}.wav")
                self._save_audio(audio_data, audio_path)

            # Play audio if enabled
            if self._tts_config.play_audio:
                await self._play_audio(audio_data)

            return {
                "success": True,
                "text": text,
                "voice_id": voice_id,
                "audio_data": audio_data if self._tts_config.save_audio else None,
                "audio_path": audio_path,
            }

        except Exception as e:
            self.state = SpeechState.ERROR
            error_msg = f"Error generating speech: {e!s}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

        finally:
            self.state = SpeechState.IDLE

    def _get_voice(self, voice_id: str | None = None) -> TTSVoice | None:
        """Get a voice by ID or return the default voice."""
        if voice_id and voice_id in self._voices:
            return self._voices[voice_id]

        # Try to find a default voice
        for voice in self._voices.values():
            if voice.is_default:
                return voice

        # Return the first available voice if no default is set
        if self._voices:
            return next(iter(self._voices.values()))

        return None

    def _generate_silence(self, duration: float) -> bytes:
        """Generate silent audio data (placeholder for TTS output)."""
        samples = int(duration * self._sample_rate)
        return np.zeros(samples, dtype=np.float32).tobytes()

    async def _play_audio(self, audio_data: bytes) -> None:
        """Play audio data through the default audio output device."""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Play audio in a separate thread
            def play():
                try:
                    sd.play(audio_array, samplerate=self._sample_rate)
                    sd.wait()
                except Exception as e:
                    logger.error(f"Error playing audio: {e!s}")

            # Run in a thread to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, play)

        except Exception as e:
            logger.error(f"Error in audio playback: {e!s}", exc_info=True)

    async def _process_audio_queue(self) -> None:
        """Process audio data from the queue (for streaming recognition)."""
        while True:
            try:
                # Get audio data from queue
                audio_data = await self._audio_queue.get()

                # Process the audio data
                if audio_data is None:  # Sentinel value to stop
                    break

                # In a real implementation, you would process the audio data here
                # For now, we'll just log that we received it
                logger.debug(f"Processed {len(audio_data)} bytes of audio data")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audio processing: {e!s}", exc_info=True)
                await asyncio.sleep(0.1)  # Prevent tight loop on errors

    async def get_voices(self) -> list[dict[str, Any]]:
        """Get a list of available TTS voices.

        Returns:
            List of voice dictionaries with id, name, language, etc.
        """
        return [voice.dict() for voice in self._voices.values()]

    async def get_config(self) -> dict[str, Any]:
        """Get the current speech configuration.

        Returns:
            Dictionary with STT and TTS configuration
        """
        return {
            "stt": self._stt_config.dict(),
            "tts": self._tts_config.dict(),
            "state": self.state.value,
            "audio_devices": self._audio_device_info,
        }

    async def update_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Update the speech configuration.

        Args:
            config: Dictionary with configuration updates

        Returns:
            Updated configuration
        """
        if "stt" in config:
            self._stt_config = STTConfig(**{**self._stt_config.dict(), **config["stt"]})

        if "tts" in config:
            self._tts_config = TTSConfig(**{**self._tts_config.dict(), **config["tts"]})

        return await self.get_config()

    async def shutdown(self) -> None:
        """Clean up resources used by the speech handler."""
        # Stop any active listening or playback
        await self.stop_listening()

        # Cancel background tasks
        if self._audio_processing_task:
            self._audio_processing_task.cancel()
            try:
                await self._audio_processing_task
            except asyncio.CancelledError:
                pass
            self._audio_processing_task = None

        # Close audio stream if still open
        if self._audio_stream is not None:
            try:
                self._audio_stream.stop()
                self._audio_stream.close()
            except Exception as e:
                logger.error(f"Error closing audio stream: {e!s}")
            self._audio_stream = None

        logger.info("Speech handler shutdown complete")


# Helper functions for audio processing
def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio data to a different sample rate."""
    if orig_sr == target_sr:
        return audio_data

    # Simple linear resampling (in a real implementation, use a proper resampling library)
    duration = len(audio_data) / orig_sr
    target_length = int(duration * target_sr)
    return np.interp(np.linspace(0, len(audio_data) - 1, target_length), np.arange(len(audio_data)), audio_data)


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """Normalize audio data to the range [-1, 1]."""
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        return audio_data / max_val
    return audio_data


def trim_silence(audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    """Trim silence from the beginning and end of audio data."""
    # Find the first sample above the threshold
    start = 0
    for i, sample in enumerate(audio_data):
        if abs(sample) > threshold:
            start = i
            break

    # Find the last sample above the threshold
    end = len(audio_data) - 1
    for i in range(len(audio_data) - 1, -1, -1):
        if abs(audio_data[i]) > threshold:
            end = i
            break

    return audio_data[start : end + 1]
