#!/usr/bin/env python3
"""
TTS CLI Tool - Professional Command Line Interface

A professional command-line interface for the TTS library with comprehensive
error handling, validation, and user-friendly output.

Features:
- Multiple input methods (text, file)
- Flexible output options (file, bytesio)
- Multiple TTS engines (pyttsx3, gTTS)
- Environment configuration support
- Audio playback capabilities
- Comprehensive error handling

Usage:
    python cli.py "Hello world"                    # Play audio (default)
    python cli.py "Hello world" --file             # Save to auto-generated file
    python cli.py "Hello world" --file output.mp3  # Save to specific file
    python cli.py -i input.txt                     # Read text from file
    python cli.py "Hello" --file --play            # Save and play
    python cli.py "Hello" --engine pyttsx3         # Use offline engine
    python cli.py "Hello" --format bytesio         # Output as BytesIO (advanced)

Author: TTS Library Team
Version: 1.0.0
License: MIT
"""

import argparse
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
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
        text_to_speech_bytesio,
        play_audio,
        create_tts_pipeline,
        generate_timestamp_filename,
        ensure_audio_directory,
        TTSException,
        ValidationError,
        EngineNotAvailableError
    )
except ImportError as e:
    logger.error(f"Failed to import TTS library: {e}")
    sys.exit(1)


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from .env file if it exists.

    Returns:
        Configuration dictionary with default values.
    """
    config = {
        'engine': 'gtts',
        'language': 'en',
        'output_format': 'file',
        'audio_directory': 'audio',
        'filename_prefix': 'tts_output',
        'auto_play': False
    }

    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key == 'tts_engine':
                            config['engine'] = value
                        elif key == 'tts_language':
                            config['language'] = value
                        elif key == 'default_output_format':
                            config['output_format'] = value
                        elif key == 'audio_directory':
                            config['audio_directory'] = value
                        elif key == 'filename_prefix':
                            config['filename_prefix'] = value
                        elif key == 'auto_play':
                            config['auto_play'] = value.lower() == 'true'

        except Exception as e:
            logger.warning(f"Could not load .env file: {e}")

    return config


def read_text_from_file(file_path: str) -> str:
    """
    Read text content from a file.

    Args:
        file_path: Path to the text file.

    Returns:
        Text content from the file.

    Raises:
        ValidationError: If file cannot be read or is empty.
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            raise ValidationError(f"File is empty: {file_path}")

        return content

    except UnicodeDecodeError as e:
        raise ValidationError(f"File encoding error: {e}")
    except Exception as e:
        raise ValidationError(f"Could not read file {file_path}: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Professional TTS (Text-to-Speech) CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello world"                    # Play audio (default)
  %(prog)s "Hello world" --file             # Save with auto-generated name
  %(prog)s "Hello world" --file out.mp3     # Save to specific file
  %(prog)s "Hello world" --file audio/      # Save to directory with timestamp
  %(prog)s -i input.txt                     # Read text from file
  %(prog)s "Hello" --file --play            # Save and play
  %(prog)s "Hello" --engine pyttsx3         # Use offline engine
  %(prog)s "Hello" --language es            # Use Spanish language
  %(prog)s "Hello" --format bytesio         # Output as BytesIO (advanced)

Environment Configuration:
  Create a .env file to set default values:
  TTS_ENGINE=gtts
  TTS_LANGUAGE=en
  DEFAULT_OUTPUT_FORMAT=file
  AUDIO_DIRECTORY=audio
  AUTO_PLAY=false
        """
    )

    # Text input options
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument(
        'text',
        nargs='?',
        help='Text to convert to speech'
    )
    text_group.add_argument(
        '-i', '--input',
        metavar='FILE',
        dest='text_file',
        help='Path to text file to read'
    )

    # Output options
    parser.add_argument(
        '--file',
        nargs='?',
        const='',  # If --file is specified without value, use empty string
        metavar='PATH',
        help='Save to file. Can be: filename (e.g. output.mp3), directory (e.g. audio/), or just --file for auto-generated name'
    )
    parser.add_argument(
        '--format',
        choices=['file', 'bytesio'],
        help='Output format: file (default) or bytesio (for programmatic use)'
    )

    # TTS engine options
    parser.add_argument(
        '--engine',
        choices=['pyttsx3', 'gtts'],
        help='TTS engine to use (pyttsx3 for offline, gtts for online)'
    )
    parser.add_argument(
        '--language',
        default='en',
        help='Language code (default: en)'
    )

    # Audio options
    parser.add_argument(
        '--play',
        action='store_true',
        help='Play audio (use with --file to both save and play)'
    )

    # Audio directory option
    parser.add_argument(
        '--audio-dir',
        metavar='DIR',
        help='Directory to save audio files (default: audio/)'
    )

    # Verbosity options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress non-error output'
    )

    return parser


def setup_logging(verbose: bool, quiet: bool) -> None:
    """
    Setup logging based on verbosity options.

    Args:
        verbose: Enable verbose logging.
        quiet: Suppress non-error output.
    """
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command line arguments.

    Args:
        args: Parsed command line arguments.

    Raises:
        ValidationError: If arguments are invalid.
    """
    if args.verbose and args.quiet:
        raise ValidationError("Cannot specify both --verbose and --quiet")


def determine_text_input(args: argparse.Namespace) -> str:
    """
    Determine text input from arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Text to convert to speech.

    Raises:
        ValidationError: If no valid text input is provided.
    """
    if args.text_file:
        return read_text_from_file(args.text_file)
    elif args.text:
        return args.text
    else:
        raise ValidationError("No text provided")


def determine_output_filename(args: argparse.Namespace, config: Dict[str, Any], engine: str) -> Optional[str]:
    """
    Determine output filename from arguments and configuration.

    Args:
        args: Parsed command line arguments.
        config: Configuration dictionary.
        engine: TTS engine being used.

    Returns:
        Output filename or None if no file should be saved.
    """
    # If --file is not specified at all, return None (play only mode)
    if args.file is None:
        return None
    
    # Determine extension based on engine
    extension = "mp3" if engine == "gtts" else "wav"
    
    # If --file is specified without argument (empty string)
    if args.file == '':
        audio_dir = args.audio_dir or config['audio_directory']
        ensure_audio_directory(audio_dir)
        timestamp_filename = generate_timestamp_filename("", extension)
        return os.path.join(audio_dir, timestamp_filename)
    
    # If --file points to a directory (ends with / or is existing directory)
    file_path = Path(args.file)
    if args.file.endswith('/') or (file_path.exists() and file_path.is_dir()):
        ensure_audio_directory(args.file)
        timestamp_filename = generate_timestamp_filename("", extension)
        return os.path.join(args.file, timestamp_filename)
    
    # If --file is a specific filename
    # Ensure parent directory exists
    if file_path.parent != Path('.'):
        ensure_audio_directory(str(file_path.parent))
    
    return args.file


def determine_playback_setting(args: argparse.Namespace) -> bool:
    """
    Determine if audio should be played.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if audio should be played, False otherwise.
    
    Logic:
        - If --play is specified: play
        - If --file is NOT specified: play (default mode)
        - If --file is specified but --play is not: don't play (save only)
    """
    # If --play is explicitly specified, play
    if args.play:
        return True
    
    # If --file is not specified (play-only mode), play by default
    if args.file is None:
        return True
    
    # If --file is specified but --play is not, don't play (save only)
    return False


def print_success_message(filename: str, file_size: int, quiet: bool) -> None:
    """
    Print success message with file information.

    Args:
        filename: Generated filename.
        file_size: Size of the generated file.
        quiet: Whether to suppress output.
    """
    if not quiet:
        print(f"Audio file generated successfully!")
        print(f"Filename: {filename}")
        print(f"File size: {file_size:,} bytes")


def print_bytesio_message(size: int, quiet: bool) -> None:
    """
    Print BytesIO generation message.

    Args:
        size: Size of the generated bytes.
        quiet: Whether to suppress output.
    """
    if not quiet:
        print(f"BytesIO object generated successfully!")
        print(f"Size: {size:,} bytes")


def main() -> int:
    """
    Main CLI function.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Setup logging
        setup_logging(args.verbose, args.quiet)

        # Validate arguments
        validate_arguments(args)

        # Load configuration
        config = load_env_config()

        # Determine text input
        text = determine_text_input(args)

        # Determine engine and language
        engine = args.engine or config['engine']
        language = args.language or config['language']

        # Determine output format
        output_format = args.format or config['output_format']

        # Determine output filename (can be None for play-only mode)
        output_filename = determine_output_filename(args, config, engine)

        # Determine if we should play audio
        should_play = determine_playback_setting(args)

        # Print operation summary
        if not args.quiet:
            print("TTS CLI Tool")
            print("=" * 40)
            print(f"Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"Engine: {engine}")
            print(f"Language: {language}")
            if output_filename:
                print(f"Output file: {output_filename}")
            if should_play:
                print(f"Playback: enabled")
            print()

        # Generate TTS
        if output_format == "file" or output_filename or should_play:
            # If we need to save to file
            if output_filename:
                filename = text_to_speech_file(
                    text=text,
                    filename=output_filename,
                    engine=engine,
                    language=language
                )

                file_size = os.path.getsize(filename)
                print_success_message(filename, file_size, args.quiet)

                # Play audio if requested
                if should_play:
                    if not args.quiet:
                        print("Playing audio...")
                    play_audio(filename)
                    if not args.quiet:
                        print("Playback completed")

                return 0
            
            # Play-only mode: create temporary file
            elif should_play:
                extension = "mp3" if engine == "gtts" else "wav"
                
                with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as temp_file:
                    temp_filename = temp_file.name
                
                try:
                    text_to_speech_file(
                        text=text,
                        filename=temp_filename,
                        engine=engine,
                        language=language
                    )
                    
                    if not args.quiet:
                        print("Playing audio...")
                    play_audio(temp_filename)
                    if not args.quiet:
                        print("Playback completed")
                    
                    return 0
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_filename):
                        os.unlink(temp_filename)

        elif output_format == "bytesio":
            audio_bytesio = text_to_speech_bytesio(
                text=text,
                engine=engine,
                language=language
            )

            size = len(audio_bytesio.getvalue())
            print_bytesio_message(size, args.quiet)

            # Save to file if output filename specified
            if args.output:
                with open(output_filename, 'wb') as f:
                    f.write(audio_bytesio.getvalue())
                if not args.quiet:
                    print(f"Saved to: {output_filename}")

            # Play audio if requested
            if should_play:
                if not args.quiet:
                    print("Playing audio...")
                play_audio(audio_bytesio.getvalue())
                if not args.quiet:
                    print("Playback completed")

            return 0

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except EngineNotAvailableError as e:
        logger.error(f"Engine not available: {e}")
        return 1
    except TTSException as e:
        logger.error(f"TTS error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
