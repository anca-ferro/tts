# TTS Library - Quick Start for Multiple TTS Engines

Simple library for quickly testing various Text-to-Speech (TTS) engines through a unified interface.

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

## License

MIT License
