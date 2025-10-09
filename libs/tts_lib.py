"""
TTS (Text-to-Speech) Library - Functional Programming Style

A professional-grade text-to-speech library built with functional programming principles.
Provides pure functions, function composition, and pipelines for flexible TTS operations.

Features:
- Pure functions with no side effects
- Function composition and higher-order functions
- Multiple TTS engines (pyttsx3, gTTS)
- Flexible output formats (file, bytes, BytesIO)
- Batch processing capabilities
- Audio playback functionality
- Comprehensive error handling

Author: TTS Library Team
Version: 1.0.0
License: MIT
"""

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Callable, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Third-party imports with error handling
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available. Offline TTS will not work.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available. Online TTS will not work.")

try:
    import pygame
    from pygame import mixer
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available. Audio playback will not work.")


# Type definitions
Config = Dict[str, Any]
AudioSource = Union[str, bytes]


class TTSException(Exception):
    """Base exception for TTS operations."""
    pass


class EngineNotAvailableError(TTSException):
    """Raised when a TTS engine is not available."""
    pass


class ValidationError(TTSException):
    """Raised when input validation fails."""
    pass


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
    
    if engine == 'pyttsx3' and not PYTTSX3_AVAILABLE:
        raise EngineNotAvailableError("pyttsx3 engine not available")
    
    if engine == 'gtts' and not GTTS_AVAILABLE:
        raise EngineNotAvailableError("gTTS engine not available")
    
    return engine


def validate_language(language: str) -> str:
    """Validate language code."""
    if not isinstance(language, str) or len(language) != 2:
        raise ValidationError("Language must be a 2-character code")
    
    return language.lower()


def init_pyttsx3_engine(config: Config):
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


def pyttsx3_to_file(text: str, filename: str, config: Config) -> str:
    """Generate TTS using pyttsx3 and save to file."""
    engine = init_pyttsx3_engine(config)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        os.rename(temp_filename, filename)
        return filename
    except Exception as e:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
        raise TTSException(f"pyttsx3 file generation failed: {e}")


def pyttsx3_to_bytes(text: str, config: Config) -> bytes:
    """Generate TTS using pyttsx3 and return as bytes."""
    engine = init_pyttsx3_engine(config)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        
        with open(temp_filename, 'rb') as f:
            audio_bytes = f.read()
        
        return audio_bytes
    except Exception as e:
        raise TTSException(f"pyttsx3 bytes generation failed: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def gtts_to_file(text: str, filename: str, config: Config) -> str:
    """Generate TTS using gTTS and save to file."""
    if not GTTS_AVAILABLE:
        raise EngineNotAvailableError("gTTS not available")
    
    try:
        tts = gTTS(text=text, lang=config['language'], slow=config['slow'])
        tts.save(filename)
        return filename
    except Exception as e:
        raise TTSException(f"gTTS file generation failed: {e}")


def gtts_to_bytes(text: str, config: Config) -> bytes:
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


def get_engine_function(engine_type: str) -> Dict[str, Callable]:
    """Get the appropriate engine functions based on engine type."""
    engine_functions = {
        'pyttsx3': {
            'file': pyttsx3_to_file,
            'bytes': pyttsx3_to_bytes
        },
        'gtts': {
            'file': gtts_to_file,
            'bytes': gtts_to_bytes
        }
    }
    
    if engine_type not in engine_functions:
        raise ValidationError(f"Unsupported engine type: {engine_type}")
    
    return engine_functions[engine_type]


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


def play_audio_bytes(audio_bytes: bytes) -> None:
    """Play audio from bytes."""
    if not PYGAME_AVAILABLE:
        raise EngineNotAvailableError("pygame not available for audio playback")
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        temp_file.write(audio_bytes)
        temp_file.flush()
        
        mixer.init()
        mixer.music.load(temp_filename)
        mixer.music.play()
        
        while mixer.music.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        raise TTSException(f"Audio playback failed: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def play_audio(audio_source: AudioSource) -> None:
    """Play audio from file or bytes."""
    if isinstance(audio_source, str):
        play_audio_file(audio_source)
    elif isinstance(audio_source, bytes):
        play_audio_bytes(audio_source)
    else:
        raise ValidationError("Audio source must be a file path (str) or bytes")


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