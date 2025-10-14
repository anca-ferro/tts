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
import logging
from typing import Optional, Dict, Any, cast
from dotenv import load_dotenv

# Import exceptions
from libs.exceptions import ValidationError, EngineNotAvailableError, TTSException

# Configure logging
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stderr)
    ],
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s.%(funcName)s) - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    from libs.api import (
        play_audio,
        TTSException,
        ValidationError,
        EngineNotAvailableError
    )
    from libs.tools import (
        generate_timestamp_filename,
        ensure_audio_directory
    )
except ImportError as e:
    logger.error(f"Failed to import TTS library: {e}")
    sys.exit(1)


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from .env file if it exists.

    Returns:
        Configuration dictionary with values from environment or defaults.
    """
    # Load environment variables from .env file
    load_dotenv('.env')
    # Build configuration from environment variables with defaults
    engine = os.getenv('TTS_ENGINE', 'gtts')
    language = os.getenv('TTS_LANGUAGE', 'en')
    audio_directory = os.getenv('AUDIO_DIRECTORY', 'audio')
    filename_prefix = os.getenv('FILENAME_PREFIX', '')
    # Parse output formats (comma-separated)
    default_output_format = os.getenv('DEFAULT_OUTPUT_FORMAT', 'play')
    output_formats = [f.strip() for f in default_output_format.split(',') if f.strip()]
    # Parse numeric values with error handling
    audio_rate = int(os.getenv('AUDIO_RATE', '150'))
    audio_volume = float(os.getenv('AUDIO_VOLUME', '0.9'))
    # Build and return config dictionary
    config = {
        'engine': engine,
        'language': language,
        'output_formats': output_formats,
        'audio_directory': audio_directory,
        'filename_prefix': filename_prefix,
        'audio_rate': audio_rate,
        'audio_volume': audio_volume
    }

    return config


def read_file(file_path: str) -> str:
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
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            raise ValidationError(f"File not found: {file_path}")
        if not os.path.isfile(file_path):
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


def parse_arguments() -> argparse.ArgumentParser:
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
  %(prog)s "Hello" --stdout                 # Output audio bytes to stdout
  %(prog)s "Hello" -o play,file             # Play and save (via --output)
  %(prog)s "Hello" -o file,stdout           # Save and output to stdout
  %(prog)s "Hello" --engine pyttsx3         # Use offline engine (espeak)
  %(prog)s "Hello" --language es            # Use Spanish language

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
        '-f', '--file',
        nargs='?',
        const='',  # If --file is specified without value, use empty string
        metavar='PATH',
        help='Save to file. Can be: filename (e.g. output.mp3), directory (e.g. audio/), or just --file for auto-generated name. Returns filename to stdout.'
    )
    parser.add_argument(
        '-p', '--play',
        action='store_true',
        help='Play audio (default if no other output specified)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Output audio bytes to stdout (disables --file)'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='FORMATS',
        help='Comma-separated output formats: play, file, stdout (e.g. "play,file" or "file,stdout")'
    )

    # TTS engine options
    parser.add_argument(
        '-e', '--engine',
        help='TTS engine to use (gtts, pyttsx3, or any custom engine in engines/)'
    )
    parser.add_argument(
        '-l', '--language',
        default='en',
        help='Language code (default: en)'
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

def get_text(args: argparse.Namespace) -> str:
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
        return read_file(args.text_file)
    elif args.text:
        return cast(str, args.text)
    else:
        raise ValidationError("No text provided")


def to_file(args: argparse.Namespace, config: Dict[str, Any], engine: str) -> Optional[str]:
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
    if args.file.endswith('/') or (os.path.exists(args.file) and os.path.isdir(args.file)):
        ensure_audio_directory(args.file)
        timestamp_filename = generate_timestamp_filename("", extension)
        return os.path.join(args.file, timestamp_filename)
    # If --file is a specific filename
    # Ensure parent directory exists
    parent_dir = os.path.dirname(args.file)
    if parent_dir and parent_dir != '.':
        ensure_audio_directory(parent_dir)
    filename: str = args.file
    return filename


def main() -> int:
    """
    Main CLI function.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = parse_arguments()
    args = parser.parse_args()

    try:
        # Setup logging
        setup_logging(args.verbose, args.quiet)
        # Load configuration
        config = load_env_config()
        # Determine text input
        text = get_text(args)
        # Determine engine and language
        engine = args.engine or config['engine']
        language = args.language or config['language']

        # Determine output formats
        output_formats = []

        # Parse -o/--output if provided
        if args.output:
            output_list = [f.strip() for f in args.output.split(',')]
            for fmt in output_list:
                if fmt not in ['play', 'file', 'stdout']:
                    raise ValidationError(f"Invalid output format: {fmt}. Valid: play, file, stdout")
                if fmt not in output_formats:
                    output_formats.append(fmt)

        # Add individual flags (if not already in list from --output)
        if args.file is not None and 'file' not in output_formats:
            output_formats.append('file')
        if args.play and 'play' not in output_formats:
            output_formats.append('play')
        if args.stdout and 'stdout' not in output_formats:
            output_formats.append('stdout')

        # If --stdout is set, ignore --file (unless explicitly in --output)
        if args.stdout and args.file is not None and not args.output:
            output_formats = [f for f in output_formats if f != 'file']

        # Default: play only
        if not output_formats:
            output_formats = ['play']

        # Determine output filename if saving to file
        output_filename = None
        if 'file' in output_formats:
            # If --file flag was used, use that
            # Otherwise, auto-generate filename for 'file' format from config
            if args.file is not None:
                output_filename = to_file(args, config, engine)
            else:
                # Auto-generate filename from config
                audio_dir = config['audio_directory']
                ensure_audio_directory(audio_dir)
                prefix = config.get('filename_prefix', '')
                extension = "wav" if engine in ["pyttsx3", "pipertts"] else "mp3"
                timestamp_filename = generate_timestamp_filename(prefix, extension)
                output_filename = os.path.join(audio_dir, timestamp_filename)

        # Print operation summary (only if not stdout or quiet)
        if not args.quiet and 'stdout' not in output_formats:
            print("TTS CLI Tool", file=sys.stderr)
            print("=" * 40, file=sys.stderr)
            print(f"Text: {text[:50]}{'...' if len(text) > 50 else ''}", file=sys.stderr)
            print(f"Engine: {engine}", file=sys.stderr)
            print(f"Language: {language}", file=sys.stderr)
            print(f"Formats: {', '.join(output_formats)}", file=sys.stderr)
            if output_filename:
                print(f"Output file: {output_filename}", file=sys.stderr)
            print(file=sys.stderr)

        # Generate TTS audio (engines return bytes)
        from libs.api import text_to_speech_bytes
        audio_bytes = text_to_speech_bytes(
            text=text,
            engine=engine,
            language=language
        )

        # Process based on output formats (file first, then play, then stdout)
        format_order = ['file', 'play', 'stdout']
        ordered_formats = [f for f in format_order if f in output_formats]

        for output_format in ordered_formats:
            if output_format == 'file' and output_filename:
                # Save to file
                with open(output_filename, 'wb') as f:
                    f.write(audio_bytes)

                # Return filename to stdout (main output)
                if 'stdout' not in output_formats:
                    print(output_filename, file=sys.stdout)
                else:
                    # If stdout is also requested, print filename to stderr
                    print(output_filename, file=sys.stderr)

            elif output_format == 'play':
                # Play audio
                if not args.quiet and 'stdout' not in output_formats:
                    logger.info("Playing audio...")
                play_audio(audio_bytes)
                if not args.quiet and 'stdout' not in output_formats:
                    logger.info("Playback completed")

            elif output_format == 'stdout':
                # Output audio bytes to stdout
                sys.stdout.buffer.write(audio_bytes)
                sys.stdout.buffer.flush()

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
