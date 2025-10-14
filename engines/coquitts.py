"""
Coqui TTS Engine

High-quality text-to-speech using Coqui TTS (formerly Mozilla TTS).
Supports voice cloning, multi-speaker models, and emotion control.

IMPORTANT: Requires Python 3.9-3.11 (NOT compatible with Python 3.12+)

Note: Works best with GPU. CPU mode is very slow.
"""

import tempfile
import os
import logging
import torch

from libs.exceptions import EngineNotAvailableError, TTSException

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Get project root and load .env
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _env_file = os.path.join(_project_root, '.env')
    if os.path.exists(_env_file):
        load_dotenv(_env_file)
except ImportError:
    pass  # dotenv not installed, skip

logger = logging.getLogger(__name__)

# Try to import Coqui TTS
try:
    from TTS.api import TTS
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
    logger.warning("Coqui TTS not available. Install with: pip install TTS")


def is_available() -> bool:
    """Check if Coqui TTS is available."""
    return AVAILABLE


def get_models_directory() -> str:
    """
    Get the directory for storing Coqui TTS models.

    Priority:
    1. Environment variable COQUITTS_MODELS (from .env or export)
    2. .coquitts directory in project root (if exists)
    3. Default: ~/.local/share/tts/

    Returns:
        Path to models directory
    """
    # Get project root (parent of engines/ directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Priority 1: Check environment variable (from .env or export)
    env_var = os.environ.get('COQUITTS_MODELS')
    if env_var:
        models_path = env_var.strip()
        # If relative path, resolve from project root
        if not os.path.isabs(models_path):
            models_path = os.path.join(project_root, models_path)
        return os.path.expanduser(models_path)

    # Priority 2: Check .coquitts directory in project root
    coquitts_dir = os.path.join(project_root, '.coquitts')
    if os.path.exists(coquitts_dir) and os.path.isdir(coquitts_dir):
        return coquitts_dir

    # Priority 3: Default - use Coqui TTS default
    return os.path.expanduser('~/.local/share/tts')


def get_model_name(language: str = 'en') -> str:
    """
    Get appropriate model name for language.
    
    Args:
        language: Language code
    
    Returns:
        Model name for Coqui TTS
    """
    # Multilingual model supports many languages
    multilingual_model = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    # Language-specific models (higher quality for specific language)
    language_models = {
        'en': "tts_models/en/ljspeech/tacotron2-DDC",  # English
        'es': "tts_models/es/mai/tacotron2-DDC",       # Spanish
        'fr': "tts_models/fr/mai/tacotron2-DDC",       # French
        'de': "tts_models/de/thorsten/tacotron2-DDC",  # German
    }
    
    # Use multilingual for most languages (includes ru, zh, etc.)
    if language in ['ru', 'uk', 'zh', 'ja', 'ko', 'ar', 'hi']:
        return multilingual_model
    
    # Use language-specific if available, otherwise multilingual
    return language_models.get(language, multilingual_model)


def generate(text: str, config: dict) -> bytes:
    """
    Generate TTS and return audio as bytes.
    
    Args:
        text: Text to synthesize
        config: Configuration dict with language
    
    Returns:
        Audio bytes in WAV format (22050 Hz by default)
    
    Note:
        First run will download the model (can be slow).
        Generation is slow on CPU, fast on GPU.
    """
    if not AVAILABLE:
        raise EngineNotAvailableError(
            "Coqui TTS not available. Install with: pip install TTS\n"
            "See docs/COQUITTS.md for setup instructions."
        )
    
    try:
        language = config.get('language', 'en')
        model_name = get_model_name(language)
        
        # Set custom models directory if configured
        models_dir = get_models_directory()
        if models_dir != os.path.expanduser('~/.local/share/tts'):
            # Coqui TTS uses TORCH_HOME for model cache
            os.environ['TORCH_HOME'] = models_dir
            logger.info(f"Coqui TTS models directory: {models_dir}")

        model_dir = os.path.join(models_dir, model_name.replace('/', '--'))
        if not os.path.exists(model_dir) or not os.path.isdir(model_dir):
            logger.error(f"Coqui TTS models directory {model_dir} does not exist")
            return bytes()
        # find file.pth in model_dir
        models_paths = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
        if not models_paths:
            logger.error(f"Coqui TTS model file (.pth) not found in {model_dir}")
            return bytes()
        models_path = os.path.join(model_dir, models_paths[0])
        logger.info(f"Using Coqui TTS model: {models_path}")
        # Initialize TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # This will download model on first use
        tts = TTS(model_name=model_name, progress_bar=False).to(device)

        # Generate to temporary file (Coqui TTS requires file output)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Generate audio
            # For multilingual models, specify language
            if "multilingual" in model_name:
                tts.tts_to_file(text=text, file_path=temp_filename, language=language)
            else:
                tts.tts_to_file(text=text, file_path=temp_filename)
            
            # Read and return bytes
            if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
                raise TTSException("Coqui TTS failed to generate audio")
            
            with open(temp_filename, 'rb') as f:
                return f.read()
                
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
        
    except Exception as e:
        if "model" in str(e).lower() and "not found" in str(e).lower():
            raise TTSException(
                f"Coqui TTS model not found.\n"
                f"Error: {e}"
            )
        raise TTSException(f"Coqui TTS generation failed: {e}")

