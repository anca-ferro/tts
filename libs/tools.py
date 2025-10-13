"""
TTS Tools and Utilities

Validation, configuration, functional programming helpers, and utilities.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Any, Optional, Union
import io

from .exceptions import TTSException, EngineNotAvailableError, ValidationError
from . import pyttsx3, gtts

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
Config = Dict[str, Any]


def get_default_config() -> Config:
    """Get default configuration for TTS operations."""
    return {
        'engine': 'gtts',
        'language': 'en',
        'rate': 150,
        'volume': 0.9,
        'slow': False
    }


def validate_text(text: str) -> str:
    """Validate and clean input text."""
    if not isinstance(text, str):
        raise ValidationError("Text must be a string")

    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValidationError("Text cannot be empty")

    if len(cleaned_text) > 5000:
        raise ValidationError("Text too long (max 5000 characters)")

    return cleaned_text


def validate_engine(engine: str) -> str:
    """Validate TTS engine type."""
    if engine not in ['pyttsx3', 'gtts']:
        raise ValidationError("Engine must be 'pyttsx3' or 'gtts'")

    if engine == 'pyttsx3' and not pyttsx3.is_available():
        raise EngineNotAvailableError("pyttsx3 engine not available")

    if engine == 'gtts' and not gtts.is_available():
        raise EngineNotAvailableError("gTTS engine not available")

    return engine


def validate_language(language: str) -> str:
    """Validate language code."""
    if not isinstance(language, str) or len(language) != 2:
        raise ValidationError("Language must be a 2-character code")

    return language.lower()


def get_engine_function(engine_type: str) -> Dict[str, Callable]:
    """Get the appropriate engine functions based on engine type."""
    engine_functions = {
        'pyttsx3': {
            'file': pyttsx3.to_file,
            'bytes': pyttsx3.to_bytes
        },
        'gtts': {
            'file': gtts.to_file,
            'bytes': gtts.to_bytes
        }
    }

    if engine_type not in engine_functions:
        raise ValidationError(f"Unsupported engine type: {engine_type}")

    return engine_functions[engine_type]


def compose(*functions: Callable) -> Callable:
    """Compose multiple functions into a single function."""
    def composed(x: Any) -> Any:
        for f in reversed(functions):
            x = f(x)
        return x
    return composed


def with_engine(engine: str) -> Callable:
    """Create a function that uses the given engine."""
    def engine_wrapper(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            kwargs['engine'] = engine
            return func(*args, **kwargs)
        return wrapper
    return engine_wrapper


def with_language(language: str) -> Callable:
    """Create a function that uses the given language."""
    def language_wrapper(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            kwargs['language'] = language
            return func(*args, **kwargs)
        return wrapper
    return language_wrapper


def create_tts_pipeline(engine: str = "gtts", language: str = "en") -> Callable:
    """Create a TTS pipeline with predefined settings."""
    # Import here to avoid circular import
    from .api import text_to_speech_file, text_to_speech_bytes, text_to_speech_bytesio
    
    def pipeline(
        text: str,
        output_format: str = "file",
        filename: Optional[str] = None
    ) -> Union[str, bytes, io.BytesIO]:
        if output_format == "file":
            return text_to_speech_file(text, filename, engine, language)
        elif output_format == "bytes":
            return text_to_speech_bytes(text, engine, language)
        elif output_format == "bytesio":
            return text_to_speech_bytesio(text, engine, language)
        else:
            raise ValidationError("output_format must be 'file', 'bytes', or 'bytesio'")

    return pipeline


def batch_tts(
    texts: List[str],
    engine: str = "gtts",
    language: str = "en",
    output_dir: str = "audio"
) -> List[str]:
    """Process multiple texts in batch."""
    if not isinstance(texts, list) or not texts:
        raise ValidationError("texts must be a non-empty list")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    pipeline = create_tts_pipeline(engine, language)
    generated_files = []

    for i, text in enumerate(texts):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"{timestamp}.mp3")

            result_filename = pipeline(text, "file", filename)
            generated_files.append(result_filename)
        except Exception as e:
            logger.error(f"Failed to process text {i}: {e}")
            raise TTSException(f"Batch processing failed at item {i}: {e}")

    return generated_files


def generate_timestamp_filename(prefix: str = "", extension: str = "mp3") -> str:
    """Generate filename with timestamp only."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}.{extension}"
    else:
        return f"{timestamp}.{extension}"


def ensure_audio_directory(directory: str = "audio") -> str:
    """Ensure audio directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory

