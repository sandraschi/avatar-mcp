"""
Speech Processing Module

This module provides speech-to-text (STT) and text-to-speech (TTS) functionality
for the AI NPC system, with support for multiple backends and configurations.
"""

import asyncio
import logging
import json
import re
import wave
import io
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Union
from enum import Enum, auto

logger = logging.getLogger(__name__)

class SpeechBackend(Enum):
    """Available speech processing backends."""
    WHISPER = auto()
    VOSK = auto()
    GOOGLE = auto()
    AZURE = auto()
    COQUI = auto()
    ELEVENLABS = auto()
    PYTTSX3 = auto()
    GTTS = auto()

@dataclass
class SpeechConfig:
    """Configuration for speech processing."""
    stt_backend: SpeechBackend = SpeechBackend.WHISPER
    tts_backend: SpeechBackend = SpeechBackend.GTTS
    language: str = "en-US"
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    energy_threshold: int = 300
    pause_threshold: float = 0.8
    dynamic_energy_threshold: bool = True
    model_path: Optional[str] = None
    api_keys: Dict[str, str] = field(default_factory=dict)
    voice_id: Optional[str] = None
    voice_style: str = "neutral"

class SpeechProcessor:
    """Handles speech recognition and synthesis with multiple backends."""
    
    def __init__(self, config: Optional[SpeechConfig] = None):
        """Initialize the speech processor."""
        self.config = config or SpeechConfig()
        self.stt_engine = None
        self.tts_engine = None
        self.is_listening = False
        self._stop_listening = False
        self._audio_queue = asyncio.Queue()
        self._callbacks = []
        
        # Initialize backends
        self._init_stt_backend()
        self._init_tts_backend()
    
    def _init_stt_backend(self):
        """Initialize the speech-to-text backend."""
        try:
            if self.config.stt_backend == SpeechBackend.WHISPER:
                self._init_whisper()
            elif self.config.stt_backend == SpeechBackend.VOSK:
                self._init_vosk()
            elif self.config.stt_backend == SpeechBackend.GOOGLE:
                self._init_google()
            elif self.config.stt_backend == SpeechBackend.AZURE:
                self._init_azure()
            else:
                logger.warning(f"Unsupported STT backend: {self.config.stt_backend}")
        except ImportError as e:
            logger.error(f"Failed to initialize STT backend: {e}")
            raise
    
    def _init_tts_backend(self):
        """Initialize the text-to-speech backend."""
        try:
            if self.config.tts_backend == SpeechBackend.COQUI:
                self._init_coqui()
            elif self.config.tts_backend == SpeechBackend.ELEVENLABS:
                self._init_elevenlabs()
            elif self.config.tts_backend == SpeechBackend.PYTTSX3:
                self._init_pyttsx3()
            elif self.config.tts_backend == SpeechBackend.GTTS:
                self._init_gtts()
            else:
                logger.warning(f"Unsupported TTS backend: {self.config.tts_backend}")
        except ImportError as e:
            logger.error(f"Failed to initialize TTS backend: {e}")
            raise
    
    # === Speech-to-Text Methods ===
    
    def _init_whisper(self):
        """Initialize Whisper STT."""
        try:
            import whisper
            self.stt_engine = whisper.load_model(
                self.config.model_path or "base",
                download_root="./models/whisper"
            )
            logger.info("Initialized Whisper STT")
        except ImportError:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            raise
    
    def _init_vosk(self):
        """Initialize Vosk STT."""
        try:
            import vosk
            if not self.config.model_path:
                raise ValueError("Vosk requires a model path")
            self.stt_engine = vosk.Model(self.config.model_path)
            logger.info("Initialized Vosk STT")
        except ImportError:
            logger.warning("Vosk not available. Install with: pip install vosk")
            raise
    
    def _init_google(self):
        """Initialize Google STT."""
        try:
            import speech_recognition as sr
            self.stt_engine = sr.Recognizer()
            self.stt_engine.energy_threshold = self.config.energy_threshold
            self.stt_engine.pause_threshold = self.config.pause_threshold
            self.stt_engine.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            logger.info("Initialized Google STT")
        except ImportError:
            logger.warning("SpeechRecognition not available. Install with: pip install SpeechRecognition")
            raise
    
    def _init_azure(self):
        """Initialize Azure STT."""
        try:
            import azure.cognitiveservices.speech as speechsdk
            speech_key = self.config.api_keys.get("azure")
            if not speech_key:
                raise ValueError("Azure Speech key not provided")
                
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=self.config.api_keys.get("azure_region", "eastus")
            )
            self.stt_engine = speechsdk.SpeechRecognizer(speech_config=speech_config)
            logger.info("Initialized Azure STT")
        except ImportError:
            logger.warning("Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")
            raise
    
    # === Text-to-Speech Methods ===
    
    def _init_coqui(self):
        """Initialize Coqui TTS."""
        try:
            from TTS.api import TTS
            self.tts_engine = TTS(model_name=self.config.model_path or "tts_models/en/ljspeech/tacotron2-DDC")
            logger.info("Initialized Coqui TTS")
        except ImportError:
            logger.warning("Coqui TTS not available. Install with: pip install TTS")
            raise
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS."""
        try:
            from elevenlabs import voices, generate, set_api_key
            
            api_key = self.config.api_keys.get("elevenlabs")
            if not api_key:
                raise ValueError("ElevenLabs API key not provided")
                
            set_api_key(api_key)
            self.tts_engine = {
                "voices": voices(),
                "generate": generate
            }
            logger.info("Initialized ElevenLabs TTS")
        except ImportError:
            logger.warning("ElevenLabs not available. Install with: pip install elevenlabs")
            raise
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 TTS."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            if self.config.voice_id:
                for voice in voices:
                    if self.config.voice_id in voice.id:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Configure rate and volume
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            logger.info("Initialized pyttsx3 TTS")
        except ImportError:
            logger.warning("pyttsx3 not available. Install with: pip install pyttsx3")
            raise
    
    def _init_gtts(self):
        """Initialize gTTS (Google Text-to-Speech)."""
        try:
            from gtts import gTTS
            import pygame
            
            class GTTSWrapper:
                def __init__(self, config):
                    self.config = config
                    pygame.mixer.init()
                
                def text_to_speech(self, text, lang=None):
                    tts = gTTS(text=text, lang=lang or self.config.language[:2])
                    with io.BytesIO() as f:
                        tts.write_to_fp(f)
                        f.seek(0)
                        pygame.mixer.music.load(f)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
            
            self.tts_engine = GTTSWrapper(self.config)
            logger.info("Initialized gTTS")
        except ImportError:
            logger.warning("gTTS not available. Install with: pip install gtts pygame")
            raise
    
    # === Public API ===
    
    async def recognize_speech(self, audio_data: Optional[bytes] = None) -> Optional[str]:
        """Convert speech to text.
        
        Args:
            audio_data: Optional audio data to process. If None, uses the microphone.
            
        Returns:
            Recognized text, or None if recognition failed.
        """
        if not self.stt_engine:
            logger.error("STT engine not initialized")
            return None
        
        try:
            if self.config.stt_backend == SpeechBackend.WHISPER:
                return await self._recognize_whisper(audio_data)
            elif self.config.stt_backend == SpeechBackend.VOSK:
                return await self._recognize_vosk(audio_data)
            elif self.config.stt_backend == SpeechBackend.GOOGLE:
                return await self._recognize_google(audio_data)
            elif self.config.stt_backend == SpeechBackend.AZURE:
                return await self._recognize_azure(audio_data)
            else:
                logger.error(f"Unsupported STT backend: {self.config.stt_backend}")
                return None
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return None
    
    async def text_to_speech(self, text: str, **kwargs) -> Optional[bytes]:
        """Convert text to speech.
        
        Args:
            text: Text to convert to speech.
            **kwargs: Additional arguments for the TTS engine.
            
        Returns:
            Audio data as bytes, or None if synthesis failed.
        """
        if not self.tts_engine:
            logger.error("TTS engine not initialized")
            return None
        
        try:
            if self.config.tts_backend == SpeechBackend.COQUI:
                return await self._synthesize_coqui(text, **kwargs)
            elif self.config.tts_backend == SpeechBackend.ELEVENLABS:
                return await self._synthesize_elevenlabs(text, **kwargs)
            elif self.config.tts_backend == SpeechBackend.PYTTSX3:
                return await self._synthesize_pyttsx3(text, **kwargs)
            elif self.config.tts_backend == SpeechBackend.GTTS:
                return await self._synthesize_gtts(text, **kwargs)
            else:
                logger.error(f"Unsupported TTS backend: {self.config.tts_backend}")
                return None
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None
    
    async def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """Start continuously listening for speech.
        
        Args:
            callback: Function to call when speech is recognized.
        """
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        if callback:
            self._callbacks.append(callback)
        
        self.is_listening = True
        self._stop_listening = False
        
        # Start the listening loop in a background task
        asyncio.create_task(self._listening_loop())
    
    async def stop_listening(self):
        """Stop listening for speech."""
        self._stop_listening = True
        self.is_listening = False
    
    # === Private Implementation ===
    
    async def _listening_loop(self):
        """Background task that continuously listens for speech."""
        import sounddevice as sd
        import queue
        
        audio_queue = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            audio_queue.put(indata.copy())
        
        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            callback=audio_callback,
            blocksize=int(self.config.sample_rate * 0.1)  # 100ms chunks
        ) as stream:
            logger.info("Listening... (press Ctrl+C to stop)")
            
            while not self._stop_listening:
                try:
                    # Collect audio chunks until there's a pause
                    audio_chunks = []
                    while not self._stop_listening:
                        try:
                            chunk = audio_queue.get(timeout=1.0)
                            audio_chunks.append(chunk)
                            # If we have enough audio, process it
                            if len(audio_chunks) >= 10:  # ~1 second of audio
                                break
                        except queue.Empty:
                            if audio_chunks:  # End of speech
                                break
                except KeyboardInterrupt:
                    break
                
                if audio_chunks:
                    # Process the collected audio
                    audio_data = np.concatenate(audio_chunks)
                    text = await self.recognize_speech(audio_data.tobytes())
                    
                    if text and self._callbacks:
                        for callback in self._callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(text)
                                else:
                                    callback(text)
                            except Exception as e:
                                logger.error(f"Error in callback: {e}")
        
        self.is_listening = False
        logger.info("Stopped listening")
    
    # === STT Backend Implementations ===
    
    async def _recognize_whisper(self, audio_data: Optional[bytes]) -> Optional[str]:
        """Recognize speech using Whisper."""
        import whisper
        import torch
        import io
        import soundfile as sf
        
        try:
            # If no audio data provided, use the microphone
            if audio_data is None:
                import sounddevice as sd
                duration = 5  # seconds
                logger.info(f"Recording for {duration} seconds...")
                audio_data = sd.rec(
                    int(duration * self.config.sample_rate),
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    dtype='float32'
                )
                sd.wait()
                audio_data = (audio_data * 32767).astype('int16').tobytes()
            
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Save to a temporary WAV file
            with io.BytesIO() as wav_io:
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(self.config.channels)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.config.sample_rate)
                    wav_file.writeframes(audio_data)
                
                # Load audio with Whisper
                audio = whisper.load_audio(wav_io, sr=self.config.sample_rate)
                audio = whisper.pad_or_trim(audio)
                
                # Make log-Mel spectrogram and move to device
                mel = whisper.log_mel_spectrogram(audio).to(self.stt_engine.device)
                
                # Detect language if needed
                if self.config.language == "auto":
                    _, probs = self.stt_engine.detect_language(mel)
                    language = max(probs, key=probs.get)
                else:
                    language = self.config.language[:2]  # Convert en-US to en
                
                # Decode the audio
                options = whisper.DecodingOptions(language=language, fp16=torch.cuda.is_available())
                result = whisper.decode(self.stt_engine, mel, options)
                
                return result.text
                
        except Exception as e:
            logger.error(f"Whisper recognition failed: {e}")
            return None
    
    async def _recognize_vosk(self, audio_data: Optional[bytes]) -> Optional[str]:
        """Recognize speech using Vosk."""
        import vosk
        import json
        
        if audio_data is None:
            logger.error("Vosk requires pre-recorded audio")
            return None
        
        try:
            # Create a recognizer with the model
            rec = vosk.KaldiRecognizer(self.stt_engine, self.config.sample_rate)
            rec.SetWords(True)
            
            # Process the audio data
            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())
                return result.get("text")
            
            return None
        except Exception as e:
            logger.error(f"Vosk recognition failed: {e}")
            return None
    
    async def _recognize_google(self, audio_data: Optional[bytes]) -> Optional[str]:
        """Recognize speech using Google's speech recognition."""
        import speech_recognition as sr
        
        try:
            if audio_data is not None:
                # Convert bytes to AudioData
                import io
                with io.BytesIO(audio_data) as audio_file:
                    audio = sr.AudioFile(audio_file)
                    with audio as source:
                        audio_data = self.stt_engine.record(source)
            else:
                # Use microphone
                with sr.Microphone(sample_rate=self.config.sample_rate) as source:
                    logger.info("Listening...")
                    audio_data = self.stt_engine.listen(source)
            
            # Recognize speech
            text = self.stt_engine.recognize_google(
                audio_data,
                language=self.config.language
            )
            
            return text
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return None
    
    async def _recognize_azure(self, audio_data: Optional[bytes]) -> Optional[str]:
        """Recognize speech using Azure Cognitive Services."""
        import azure.cognitiveservices.speech as speechsdk
        
        try:
            if audio_data is not None:
                # Convert bytes to AudioData
                audio_config = speechsdk.audio.AudioConfig(stream=speechsdk.audio.PullAudioInputStream(
                    stream_format=speechsdk.audio.AudioStreamFormat(
                        samples_per_second=self.config.sample_rate,
                        bits_per_sample=16,
                        channels=1
                    ),
                    pull_stream=speechsdk.audio.PullAudioInputStreamCallback()
                ))
                
                # Push audio data to the stream
                # (This is a simplified example - in practice, you'd need to manage the stream properly)
                audio_config.set_property("speech.config-upload-data", audio_data)
            else:
                # Use default microphone
                audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            
            # Configure speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.stt_engine.speech_config,
                audio_config=audio_config
            )
            
            # Start recognition
            result = speech_recognizer.recognize_once_async().get()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails.from_result(result)
                logger.error(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation.error_details}")
                return None
                
        except Exception as e:
            logger.error(f"Azure speech recognition failed: {e}")
            return None
    
    # === TTS Backend Implementations ===
    
    async def _synthesize_coqui(self, text: str, **kwargs) -> Optional[bytes]:
        """Synthesize speech using Coqui TTS."""
        import io
        import soundfile as sf
        
        try:
            # Generate speech
            wav = self.tts_engine.tts(text, **kwargs)
            
            # Convert to bytes
            with io.BytesIO() as wav_io:
                sf.write(wav_io, wav, self.config.sample_rate, format='WAV')
                return wav_io.getvalue()
                
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            return None
    
    async def _synthesize_elevenlabs(self, text: str, **kwargs) -> Optional[bytes]:
        """Synthesize speech using ElevenLabs."""
        from elevenlabs import generate, set_api_key
        
        try:
            # Generate speech
            audio = generate(
                text=text,
                voice=kwargs.get("voice_id") or self.config.voice_id or "Adam",
                model=kwargs.get("model") or "eleven_monolingual_v1"
            )
            
            return audio
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS synthesis failed: {e}")
            return None
    
    async def _synthesize_pyttsx3(self, text: str, **kwargs) -> Optional[bytes]:
        """Synthesize speech using pyttsx3."""
        import pyttsx3
        import io
        import wave
        import pyaudio
        import numpy as np
        
        try:
            # Create an in-memory file
            with io.BytesIO() as wav_io:
                # Configure the engine
                engine = pyttsx3.init()
                
                # Set properties if provided
                if "rate" in kwargs:
                    engine.setProperty('rate', kwargs["rate"])
                if "volume" in kwargs:
                    engine.setProperty('volume', kwargs["volume"])
                if "voice" in kwargs:
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if kwargs["voice"] in voice.id:
                            engine.setProperty('voice', voice.id)
                            break
                
                # Save to WAV file
                engine.save_to_file(text, 'temp.wav')
                engine.runAndWait()
                
                # Read the WAV file
                with open('temp.wav', 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"pyttsx3 TTS synthesis failed: {e}")
            return None
        finally:
            # Clean up temporary file
            import os
            if os.path.exists('temp.wav'):
                os.remove('temp.wav')
    
    async def _synthesize_gtts(self, text: str, **kwargs) -> Optional[bytes]:
        """Synthesize speech using gTTS."""
        from gtts import gTTS
        import io
        
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=kwargs.get("lang") or self.config.language[:2],
                slow=kwargs.get("slow", False)
            )
            
            # Save to bytes
            with io.BytesIO() as f:
                tts.write_to_fp(f)
                return f.getvalue()
                
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            return None

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create a speech processor with default settings
        speech = SpeechProcessor()
        
        # Example: Text-to-speech
        logger.info("Testing text-to-speech...")
        text = "Hello, this is a test of the text-to-speech system."
        audio_data = await speech.text_to_speech(text)
        
        if audio_data:
            logger.info(f"Generated {len(audio_data)} bytes of audio")
            
            # Play the audio (requires pyaudio)
            try:
                import pyaudio
                import wave
                import io
                
                with io.BytesIO(audio_data) as wav_io:
                    with wave.open(wav_io, 'rb') as wav_file:
                        p = pyaudio.PyAudio()
                        stream = p.open(
                            format=p.get_format_from_width(wav_file.getsampwidth()),
                            channels=wav_file.getnchannels(),
                            rate=wav_file.getframerate(),
                            output=True
                        )
                        
                        data = wav_file.readframes(1024)
                        while data:
                            stream.write(data)
                            data = wav_file.readframes(1024)
                        
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
            except ImportError:
                logger.warning("pyaudio not available, cannot play audio")
        
        # Example: Speech-to-text
        logger.info("Testing speech-to-text (5 seconds of microphone input)...")
        text = await speech.recognize_speech()
        if text:
            logger.info(f"Recognized: {text}")
        else:
            logger.info("No speech recognized")
    
    asyncio.run(main())
