# Bachelor's Thesis: Universal Text-to-Speech System with Online and Offline Capabilities

By Anca Kovach

A software engineering thesis project implementing a text-to-speech library that supports multiple TTS engines and can operate in both online (Google TTS) and offline (espeak, Piper) modes.

Author: Anca Kovach
Project Advisor: Aleksandr Pimenov
Department of Computer Science
2025

## Project Overview

This library provides a unified interface for various text-to-speech synthesis systems, enabling seamless switching between online and offline engines based on requirements and internet connectivity.

Key Features:
- Online synthesis through Google TTS
- Offline synthesis using espeak and Piper
- Unified interface for all engines
- Multi-language support
- Multiple audio output formats
- CLI and Python API

## Installation

```bash
# System dependencies (Linux)
sudo apt install espeak espeak-data libespeak1 python3-pip
# Python dependencies
pip install -r requirements.txt
```

## Usage

### Basic examples

```bash
# Google TTS (online)
python cli.py "Hello world"
# espeak (offline)
python cli.py "Hello world" --engine pyttsx3
# Another languages
python cli.py "Hola amigo!" --language es
# Save with automatic name
python cli.py "Hello world" --file
# Save to specific file
python cli.py "Hello world" --file output.mp3
# Google TTS (best quality)
python cli.py "Hello world" --engine gtts
# espeak (fast, offline)
python cli.py "Hello world" --engine pyttsx3
# Piper (high-quality offline)
python cli.py "Hello world" --engine pipertts
# Read from file
python cli.py -i input.txt
python cli.py -i input.txt --file output.mp3
# BytesIO
python cli.py "Hello world" --stdout | python3 play.py
# Multiple outputs
python cli.py "Hello world" --output play,file 
```

### Python API

```python
from libs.api import text_to_speech_file, text_to_speech_bytes

# Save to file
filename = text_to_speech_file("Hello world!", engine="gtts")
print(f"File created: {filename}")

# Get as bytes (for web apps)
audio_bytes = text_to_speech_bytes("Hello world!", engine="gtts")
```

## Project structure

```
text-to-speech/
├── engines/
│   ├── gtts.py
│   ├── pyttsx3.py
│   └── piper.py
├── libs/
│   ├── api.py
│   ├── tools.py
│   ├── playback.py
│   └── exceptions.py
├── bin/
│   └── install_piper.sh
├── cli.py
└── requirements.txt
```

### Installing dependencies

Install runtime (user) dependencies:

```bash
pip install -r requirements.txt
```

Install developer tools (linters, type checkers, test tools):

```bash
pip install -r requirements-dev.txt
```

## License

MIT License
