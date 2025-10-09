# TTS Library - Professional Text-to-Speech Solution

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional-grade text-to-speech library built with functional programming principles. Provides pure functions, function composition, and pipelines for flexible TTS operations with comprehensive error handling and validation.

## Features

- **Functional Programming**: Pure functions with no side effects
- **Multiple TTS Engines**: Support for both offline (`pyttsx3`) and online (`gTTS`) engines
- **Flexible Output**: Generate audio as BytesIO objects or save to files
- **Function Composition**: Compose multiple functions for complex operations
- **Higher-Order Functions**: Create specialized functions with `with_engine()` and `with_language()`
- **Batch Processing**: Process multiple texts efficiently
- **Audio Playback**: Built-in audio playback functionality
- **Comprehensive Error Handling**: Professional error handling with custom exceptions
- **Type Safety**: Full type hints and validation
- **Professional CLI**: Command-line interface with comprehensive options
- **Test Coverage**: Comprehensive test suite with mocking
- **Cross-platform**: Works on Windows, macOS, and Linux

## Project Structure

```
tts/
├── libs/
│   ├── __init__.py              # Package initialization
│   └── tts_lib.py              # Core TTS library (functional)
├── audio/                      # Auto-generated audio files directory
├── .gitignore                  # Professional gitignore
├── env.example                 # Environment configuration template
├── requirements.txt            # Dependencies with exact versions
├── demo.py                     # Simple demo
├── app.py                      # Interactive app with infinite loop
├── cli.py                      # Professional CLI interface
├── test_tts.py                # Comprehensive test suite
└── README.md                   # This documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Internet connection (for gTTS engine)
- Audio system (for playback)

### Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# For Linux users, install additional system packages
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev

# For macOS users
brew install espeak

# For Windows users
# Download espeak from: http://espeak.sourceforge.net/download.html
```

### Environment Configuration (Optional)

```bash
# Copy the example configuration
cp env.example .env

# Edit .env file to customize settings
nano .env
```

## Quick Start

### Basic Usage

```python
from tts_lib import text_to_speech_file, text_to_speech_bytesio

# Convert text to speech and save to file
filename = text_to_speech_file("Hello, world!", filename="hello.mp3")
print(f"Audio saved to: {filename}")

# Convert text to speech and get BytesIO object
audio_bytesio = text_to_speech_bytesio("Hello, world!")
print(f"Audio size: {len(audio_bytesio.getvalue())} bytes")
```

### Functional Programming Examples

```python
from tts_lib import (
    create_tts_pipeline, 
    compose, 
    with_engine, 
    with_language,
    batch_tts
)

# Create a TTS pipeline
pipeline = create_tts_pipeline(engine="gtts", language="en")
filename = pipeline("Hello world!", "file", "output.mp3")

# Function composition
process_text = compose(
    lambda t: t.strip().upper(),
    lambda t: f"TTS: {t}"
)
processed = process_text("  hello world  ")

# Higher-order functions
english_tts = with_language("en")(text_to_speech_file)
offline_tts = with_engine("pyttsx3")(text_to_speech_file)

# Batch processing
texts = ["Hello", "World", "Functional"]
filenames = batch_tts(texts, engine="gtts", language="en")
```

## API Reference

### Core Functions

#### `text_to_speech_file(text, filename=None, engine="gtts", language="en")`

Converts text to speech and saves to file.

**Parameters:**
- `text` (str): Text to convert
- `filename` (str, optional): Output filename (auto-generated if None)
- `engine` (str): "pyttsx3" or "gtts"
- `language` (str): Language code

**Returns:** Filename of the generated audio file

**Example:**
```python
filename = text_to_speech_file("Hello world!", "output.mp3")
```

#### `text_to_speech_bytes(text, engine="gtts", language="en")`

Converts text to speech and returns as bytes.

**Parameters:**
- `text` (str): Text to convert
- `engine` (str): "pyttsx3" or "gtts"
- `language` (str): Language code

**Returns:** Bytes of the audio data

#### `text_to_speech_bytesio(text, engine="gtts", language="en")`

Converts text to speech and returns as BytesIO object.

**Parameters:**
- `text` (str): Text to convert
- `engine` (str): "pyttsx3" or "gtts"
- `language` (str): Language code

**Returns:** BytesIO object containing the audio data

#### `play_audio(audio_source)`

Plays audio from file or bytes.

**Parameters:**
- `audio_source`: Path to audio file or bytes data

### Functional Programming Functions

#### `create_tts_pipeline(engine="gtts", language="en")`

Creates a TTS pipeline with predefined settings.

**Returns:** Pipeline function that accepts text and output format

#### `compose(*functions)`

Composes multiple functions into a single function.

**Parameters:**
- `*functions`: Functions to compose (applied right to left)

**Returns:** Composed function

#### `with_engine(engine)`

Creates a function that uses the given engine.

**Parameters:**
- `engine` (str): Engine type ("pyttsx3" or "gtts")

**Returns:** Function wrapper

#### `with_language(language)`

Creates a function that uses the given language.

**Parameters:**
- `language` (str): Language code

**Returns:** Function wrapper

#### `batch_tts(texts, engine="gtts", language="en", output_dir="audio")`

Processes multiple texts in batch.

**Parameters:**
- `texts` (list): List of texts to convert
- `engine` (str): TTS engine to use
- `language` (str): Language code
- `output_dir` (str): Directory to save files

**Returns:** List of generated filenames

## Command Line Interface

The `cli.py` script provides a professional command-line interface:

```bash
# Basic usage - convert text to speech
python cli.py "Hello world"

# Save to specific file
python cli.py "Hello world" -o output.mp3

# Read text from file
python cli.py -f input.txt

# Use offline engine
python cli.py "Hello world" --engine pyttsx3

# Output as BytesIO format
python cli.py "Hello world" --format bytesio

# Play audio after generation
python cli.py "Hello world" --play

# Use different language
python cli.py "Hola mundo" --language es

# Verbose output
python cli.py "Hello world" --verbose

# Quiet mode
python cli.py "Hello world" --quiet
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test_tts.py

# Run with pytest (if installed)
pytest test_tts.py -v

# Run with coverage
pytest test_tts.py --cov=libs --cov-report=html
```

## 📚 Examples

### Example 1: Simple File Output
```python
from tts_lib import text_to_speech_file

# Generate audio file
filename = text_to_speech_file("Welcome to our application!", filename="welcome.mp3")
print(f"Audio file created: {filename}")
```

### Example 2: BytesIO for Web Applications
```python
from tts_lib import text_to_speech_bytesio
from flask import Flask, Response

app = Flask(__name__)

@app.route('/tts/<text>')
def tts_endpoint(text):
    audio_bytesio = text_to_speech_bytesio(text, engine="gtts")
    return Response(audio_bytesio.getvalue(), mimetype='audio/mpeg')
```

### Example 3: Batch Processing
```python
from tts_lib import batch_tts

texts = [
    "First message",
    "Second message", 
    "Third message"
]

filenames = batch_tts(texts, engine="gtts", language="en")
for i, filename in enumerate(filenames):
    print(f"Generated: {filename}")
```

### Example 4: Audio Playback
```python
from tts_lib import text_to_speech_file, play_audio

# Generate and play audio
filename = text_to_speech_file("This will be played automatically!", filename="output.mp3")
play_audio(filename)
```

## Usage Examples

### Simple Demo

Run the simple demo:

```bash
python demo.py
```

### Interactive App

Run the interactive app with infinite loop (automatically saves and plays audio):

```bash
python app.py
```

The interactive app features:
- Infinite loop for continuous operation
- Automatic audio generation and playback
- Commands: `help`, `clear`, `list`, `quit`
- Timestamp-based file naming
- Professional error handling

## Engine Comparison

### pyttsx3 (Offline)
- **Pros**: No internet connection required, fast, works offline
- **Cons**: Limited voice quality, fewer language options
- **Output Format**: WAV files
- **Best for**: Offline applications, quick prototyping

### gTTS (Online)
- **Pros**: High-quality voices, many languages, natural-sounding
- **Cons**: Requires internet connection, slower
- **Output Format**: MP3 files
- **Best for**: Production applications, high-quality output

## 🌍 Supported Languages (gTTS)

The gTTS engine supports many languages. Some common language codes:

- `en`: English
- `es`: Spanish
- `fr`: French
- `de`: German
- `it`: Italian
- `pt`: Portuguese
- `ru`: Russian
- `ja`: Japanese
- `ko`: Korean
- `zh`: Chinese

For a complete list, see the [gTTS documentation](https://gtts.readthedocs.io/en/latest/).

## Error Handling

The library includes comprehensive error handling:

```python
from tts_lib import TTSException, ValidationError, EngineNotAvailableError

try:
    filename = text_to_speech_file("Hello world!")
    print(f"Success: {filename}")
except ValidationError as e:
    print(f"Input error: {e}")
except EngineNotAvailableError as e:
    print(f"Engine error: {e}")
except TTSException as e:
    print(f"TTS error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Development

### Code Style

The project follows professional Python standards:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

### Running Development Tools

```bash
# Format code
black libs/ *.py

# Lint code
flake8 libs/ *.py

# Type check
mypy libs/tts_lib.py

# Run tests
pytest test_tts.py -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with functional programming principles**