"""
pyttsx3 TTS Engine Implementation

Offline text-to-speech engine using pyttsx3.
"""

import os
import tempfile
import time
import logging
from typing import Dict, Any

from .exceptions import EngineNotAvailableError, TTSException

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
Config = Dict[str, Any]

# Try to import pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available. Offline TTS will not work.")


def is_available() -> bool:
    """Check if pyttsx3 engine is available."""
    return PYTTSX3_AVAILABLE


def init_engine(config: Config):
    """Initialize pyttsx3 engine with configuration."""
    if not PYTTSX3_AVAILABLE:
        raise EngineNotAvailableError("pyttsx3 not available")

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', config['rate'])
        engine.setProperty('volume', config['volume'])
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize pyttsx3: {e}")
        raise EngineNotAvailableError(f"pyttsx3 initialization failed: {e}")


def to_file(text: str, filename: str, config: Config) -> str:
    """Generate TTS using pyttsx3 and save to file."""
    engine = init_engine(config)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        
        # Give the engine time to complete file writing (Linux espeak issue)
        time.sleep(0.5)
        
        # Stop the engine properly
        engine.stop()
        
        # Verify file was created with content
        if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
            raise TTSException("pyttsx3 failed to generate audio file - file is empty or missing")
        
        os.rename(temp_filename, filename)
        return filename
    except Exception as e:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
        raise TTSException(f"pyttsx3 file generation failed: {e}")


def to_bytes(text: str, config: Config) -> bytes:
    """Generate TTS using pyttsx3 and return as bytes."""
    engine = init_engine(config)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        
        # Give the engine time to complete file writing (Linux espeak issue)
        time.sleep(0.5)
        
        # Stop the engine properly
        engine.stop()
        
        # Verify file was created with content
        if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
            raise TTSException("pyttsx3 failed to generate audio file - file is empty or missing")

        with open(temp_filename, 'rb') as f:
            audio_bytes = f.read()

        return audio_bytes
    except Exception as e:
        raise TTSException(f"pyttsx3 bytes generation failed: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

