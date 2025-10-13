"""
Audio Playback Module

Handles audio playback using pygame.
"""

import os
import tempfile
import logging
from typing import Union

from exceptions import EngineNotAvailableError, TTSException, ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
AudioSource = Union[str, bytes]

# Try to import pygame
try:
    import pygame
    from pygame import mixer
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available. Audio playback will not work.")


def is_available() -> bool:
    """Check if pygame is available for playback."""
    return PYGAME_AVAILABLE


def play_file(filename: str) -> None:
    """Play audio from file."""
    if not PYGAME_AVAILABLE:
        raise EngineNotAvailableError("pygame not available for audio playback")

    if not os.path.exists(filename):
        raise ValidationError(f"Audio file not found: {filename}")

    try:
        mixer.init()
        mixer.music.load(filename)
        mixer.music.play()

        while mixer.music.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        raise TTSException(f"Audio playback failed: {e}")


def play_bytes(audio_bytes: bytes) -> None:
    """Play audio from bytes."""
    if not PYGAME_AVAILABLE:
        raise EngineNotAvailableError("pygame not available for audio playback")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(audio_bytes)
        temp_file.flush()

    try:
        mixer.init()
        mixer.music.load(temp_filename)
        mixer.music.play()

        while mixer.music.get_busy():
            pygame.time.wait(100)
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def play(audio_source: AudioSource) -> None:
    """
    Play audio from file path or bytes.
    
    Args:
        audio_source: Either a file path (str) or audio bytes (bytes)
    """
    if isinstance(audio_source, str):
        play_file(audio_source)
    elif isinstance(audio_source, bytes):
        play_bytes(audio_source)
    else:
        raise ValidationError(f"Invalid audio source type: {type(audio_source)}")

