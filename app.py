#!/usr/bin/env python3
"""
TTS App - Interactive Text-to-Speech Application

Interactive application with infinite loop that automatically saves and plays audio files.
User can input text and the app will generate audio, save it, and play it automatically.

Features:
- Infinite loop for continuous operation
- Automatic audio generation and playback
- Timestamp-based file naming
- Professional error handling
- Clean user interface

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
logging.basicConfig(level=logging.WARNING)  # Suppress warnings for cleaner output
logger = logging.getLogger(__name__)

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

try:
    from tts_lib import (
        text_to_speech_file,
        play_audio,
        generate_timestamp_filename,
        ensure_audio_directory,
        TTSException,
        ValidationError,
        EngineNotAvailableError
    )
except ImportError as e:
    logger.error(f"Failed to import TTS library: {e}")
    sys.exit(1)


def print_header():
    """Print application header."""
    print("=" * 60)
    print("🎤 TTS Interactive Application")
    print("=" * 60)
    print("Enter text to convert to speech")
    print("Type 'quit', 'exit', or 'q' to stop")
    print("Type 'help' for more options")
    print("=" * 60)


def print_help():
    """Print help information."""
    print("\n📖 Help:")
    print("  • Enter any text to convert to speech")
    print("  • Audio will be automatically saved and played")
    print("  • Files are saved in 'audio/' directory with timestamp names")
    print("  • Commands:")
    print("    - 'quit', 'exit', 'q' - Stop the application")
    print("    - 'help' - Show this help")
    print("    - 'clear' - Clear screen")
    print("    - 'list' - List recent audio files")
    print()


def clear_screen():
    """Clear the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def list_recent_files():
    """List recent audio files."""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        print("No audio directory found.")
        return
    
    files = []
    for file in os.listdir(audio_dir):
        if file.endswith(('.mp3', '.wav')):
            file_path = os.path.join(audio_dir, file)
            file_time = os.path.getmtime(file_path)
            files.append((file, file_time))
    
    if not files:
        print("No audio files found.")
        return
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📁 Recent audio files ({len(files)} total):")
    for i, (filename, _) in enumerate(files[:10]):  # Show only last 10
        file_path = os.path.join(audio_dir, filename)
        file_size = os.path.getsize(file_path)
        print(f"  {i+1:2d}. {filename} ({file_size:,} bytes)")
    
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")


def process_text(text: str) -> Optional[str]:
    """
    Process text and generate audio.
    
    Args:
        text: Text to convert to speech.
        
    Returns:
        Filename of generated audio file, or None if failed.
    """
    try:
        # Create audio directory
        audio_dir = ensure_audio_directory("audio")
        
        # Generate timestamp filename
        filename = os.path.join(audio_dir, generate_timestamp_filename("", "mp3"))
        
        print(f"🎵 Generating audio...")
        
        # Generate audio file
        result_filename = text_to_speech_file(
            text=text,
            filename=filename,
            engine="gtts",
            language="en"
        )
        
        # Get file information
        file_size = os.path.getsize(result_filename)
        
        print(f"✅ Audio generated: {os.path.basename(result_filename)}")
        print(f"📊 File size: {file_size:,} bytes")
        
        return result_filename
        
    except ValidationError as e:
        print(f"❌ Input error: {e}")
        return None
    except EngineNotAvailableError as e:
        print(f"❌ Engine error: {e}")
        print("💡 Make sure to install dependencies: pip install -r requirements.txt")
        return None
    except TTSException as e:
        print(f"❌ TTS error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def play_audio_file(filename: str) -> bool:
    """
    Play audio file.
    
    Args:
        filename: Path to audio file.
        
    Returns:
        True if playback successful, False otherwise.
    """
    try:
        print(f"🔊 Playing audio...")
        play_audio(filename)
        print(f"✅ Playback completed")
        return True
    except Exception as e:
        print(f"❌ Playback error: {e}")
        return False


def main():
    """Main application loop."""
    print_header()
    
    # Create audio directory
    ensure_audio_directory("audio")
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Enter text: ").strip()
            
            # Handle empty input
            if not user_input:
                print("⚠️  Please enter some text.")
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                clear_screen()
                print_header()
                continue
            elif user_input.lower() == 'list':
                list_recent_files()
                continue
            
            # Process text
            filename = process_text(user_input)
            
            if filename:
                # Play audio automatically
                play_audio_file(filename)
                
                # Show file location
                print(f"📁 File saved to: {filename}")
            else:
                print("❌ Failed to generate audio. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Application interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Input ended. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("🔄 Continuing...")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
