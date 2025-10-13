"""
TTS API Module

Main public API for the TTS library.
Provides high-level functions for text-to-speech conversion and audio playback.

Functions:
- text_to_speech_file() - Convert text to speech and save to file
- text_to_speech_bytes() - Convert text to speech and return bytes
- text_to_speech_bytesio() - Convert text to speech and return BytesIO
- play_audio_file() - Play audio from file
- play_audio_bytes() - Play audio from bytes
- play_audio() - Play audio from file or bytes

Re-exports:
- TTSException, EngineNotAvailableError, ValidationError from exceptions
- All tools and utilities from tools module

Author: TTS Library Team
Version: 1.0.0
License: MIT
"""

import io
from datetime import datetime
from typing import Union, Optional
import logging

# Import exceptions
from .exceptions import TTSException, EngineNotAvailableError, ValidationError

# Import tools and utilities
from .tools import (
    get_default_config,
    validate_text,
    validate_engine,
    validate_language,
    get_engine_function,
    compose,
    with_engine,
    with_language,
    create_tts_pipeline,
    batch_tts,
    generate_timestamp_filename,
    ensure_audio_directory
)

# Import playback
from . import playback

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Type definitions
AudioSource = Union[str, bytes]


def text_to_speech_file(
    text: str,
    filename: Optional[str] = None,
    engine: str = "gtts",
    language: str = "en"
) -> str:
    """Convert text to speech and save to file."""
    validated_text = validate_text(text)
    validated_engine = validate_engine(engine)
    validated_language = validate_language(language)

    config = get_default_config()
    config.update({
        'engine': validated_engine,
        'language': validated_language
    })

    engine_funcs = get_engine_function(validated_engine)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "wav" if validated_engine == "pyttsx3" else "mp3"
        filename = f"{timestamp}.{extension}"

    if validated_engine == "pyttsx3" and not filename.endswith('.wav'):
        filename = filename.rsplit('.', 1)[0] + '.wav'
    elif validated_engine == "gtts" and not filename.endswith('.mp3'):
        filename = filename.rsplit('.', 1)[0] + '.mp3'

    return engine_funcs['file'](validated_text, filename, config)


def text_to_speech_bytes(
    text: str,
    engine: str = "gtts",
    language: str = "en"
) -> bytes:
    """Convert text to speech and return as bytes."""
    validated_text = validate_text(text)
    validated_engine = validate_engine(engine)
    validated_language = validate_language(language)

    config = get_default_config()
    config.update({
        'engine': validated_engine,
        'language': validated_language
    })

    engine_funcs = get_engine_function(validated_engine)
    return engine_funcs['bytes'](validated_text, config)


def text_to_speech_bytesio(
    text: str,
    engine: str = "gtts",
    language: str = "en"
) -> io.BytesIO:
    """Convert text to speech and return as BytesIO object."""
    audio_bytes = text_to_speech_bytes(text, engine, language)
    return io.BytesIO(audio_bytes)


def play_audio_file(filename: str) -> None:
    """Play audio from file."""
    playback.play_file(filename)


def play_audio_bytes(audio_bytes: bytes) -> None:
    """Play audio from bytes."""
    playback.play_bytes(audio_bytes)


def play_audio(audio_source: AudioSource) -> None:
    """Play audio from file or bytes."""
    playback.play(audio_source)
