"""
gTTS Engine Implementation

Online text-to-speech engine using Google Text-to-Speech (gTTS).
"""

import io
import logging
from typing import Dict, Any

from exceptions import EngineNotAvailableError, TTSException

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
Config = Dict[str, Any]

# Try to import gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available. Online TTS will not work.")


def is_available() -> bool:
    """Check if gTTS engine is available."""
    return GTTS_AVAILABLE


def to_file(text: str, filename: str, config: Config) -> str:
    """Generate TTS using gTTS and save to file."""
    if not GTTS_AVAILABLE:
        raise EngineNotAvailableError("gTTS not available")

    try:
        tts = gTTS(text=text, lang=config['language'], slow=config['slow'])
        tts.save(filename)
        return filename
    except Exception as e:
        raise TTSException(f"gTTS file generation failed: {e}")


def to_bytes(text: str, config: Config) -> bytes:
    """Generate TTS using gTTS and return as bytes."""
    if not GTTS_AVAILABLE:
        raise EngineNotAvailableError("gTTS not available")

    try:
        tts = gTTS(text=text, lang=config['language'], slow=config['slow'])
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        raise TTSException(f"gTTS bytes generation failed: {e}")

