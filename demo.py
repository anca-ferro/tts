#!/usr/bin/env python3
"""
TTS Simple Example - Professional Demo

A clean, professional example demonstrating basic TTS functionality
with proper error handling and user feedback.

This example shows:
- Basic text-to-speech conversion
- Automatic audio directory creation
- Timestamp-based file naming
- Comprehensive error handling
- Professional output formatting

Author: TTS Library Team
Version: 1.0.0
License: MIT
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stderr)],
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s.%(funcName)s) - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

try:
    from tts_lib import (
        text_to_speech_file,
        generate_timestamp_filename,
        ensure_audio_directory,
        TTSException,
        ValidationError,
        EngineNotAvailableError
    )
except ImportError as e:
    logger.error(f"Failed to import TTS library: {e}")
    sys.exit(1)


def demo_function() -> Optional[str]:
    """
    Demo function that generates TTS audio from a sample string.

    This function demonstrates:
    - Professional error handling
    - Automatic directory creation
    - Timestamp-based file naming
    - Clean output formatting

    Returns:
        Filename of the generated audio file, or None if failed.
    """
    # Sample text for demonstration
    sample_text = (
        "Hello! This is a professional text-to-speech demonstration. "
        "The library is working correctly and generating high-quality audio."
    )

    print("TTS Professional Demo")
    print("=" * 50)
    print(f"Sample text: {sample_text}")
    print()

    try:
        # Create audio directory if it doesn't exist
        audio_dir = ensure_audio_directory("audio")

        # Generate timestamp filename
        filename = os.path.join(audio_dir, generate_timestamp_filename("", "mp3"))

        print("Generating audio...")

        # Generate audio file
        result_filename = text_to_speech_file(
            text=sample_text,
            filename=filename,
            engine="gtts",
            language="en"
        )

        # Get file information
        file_size = os.path.getsize(result_filename)

        print("Audio file generated successfully!")
        print(f"  Filename: {result_filename}")
        print(f"  File size: {file_size:,} bytes")
        print(f"  Engine: gTTS (Google Text-to-Speech)")
        print(f"  Language: English")

        return result_filename

    except ValidationError as e:
        logger.error(f"Input validation error: {e}")
        return None
    except EngineNotAvailableError as e:
        logger.error(f"TTS engine not available: {e}")
        return None
    except TTSException as e:
        logger.error(f"TTS generation error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def main() -> int:
    """
    Main function for the demo.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        result = demo_function()

        if result:
            print()
            print("Demo completed successfully!")
            print(f"Audio file saved to: {result}")
            return 0
        else:
            print()
            print("Demo failed. Please check the error messages above.")
            return 1

    except KeyboardInterrupt:
        print("\nDemo cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
