#!/bin/bash
# Script to download Piper TTS voice models

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Voice directory - use .pipertts in project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VOICE_DIR="$PROJECT_DIR/.pipertts/"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

# Install Piper
pip install piper-tts

echo -e "${BLUE}Piper TTS Voice Model Installer${NC}\n"

# Create directory
echo -e "${YELLOW}Creating directory: $VOICE_DIR${NC}"
mkdir -p "$VOICE_DIR"

# Function to download model
download_model() {
    local lang=$1
    local model_name=$2
    local model_path=$3
    
    echo -e "\n${GREEN}Processing: $lang ($model_name)${NC}"
    
    # Check if files already exist
    if [ -f "$VOICE_DIR/$model_name.onnx" ] && [ -f "$VOICE_DIR/$model_name.onnx.json" ]; then
        echo "  Files already exist. Skipping download."
        return 0
    fi
    
    # Download .onnx file
    if command -v wget &> /dev/null; then
        if [ ! -f "$VOICE_DIR/$model_name.onnx" ]; then
            wget -q --show-progress -O "$VOICE_DIR/$model_name.onnx" "$BASE_URL/$model_path/$model_name.onnx"
        fi
        if [ ! -f "$VOICE_DIR/$model_name.onnx.json" ]; then
            wget -q --show-progress -O "$VOICE_DIR/$model_name.onnx.json" "$BASE_URL/$model_path/$model_name.onnx.json"
        fi
    elif command -v curl &> /dev/null; then
        if [ ! -f "$VOICE_DIR/$model_name.onnx" ]; then
            curl -L -o "$VOICE_DIR/$model_name.onnx" "$BASE_URL/$model_path/$model_name.onnx"
        fi
        if [ ! -f "$VOICE_DIR/$model_name.onnx.json" ]; then
            curl -L -o "$VOICE_DIR/$model_name.onnx.json" "$BASE_URL/$model_path/$model_name.onnx.json"
        fi
    else
        echo "Error: wget or curl not found!"
        exit 1
    fi
    
    echo -e "${GREEN}Done: $model_name${NC}"
}

# Language selection menu
echo -e "\nSelect languages to download (space separated, e.g., 1 2):"
echo "1) English (en_US-lessac-medium) - female voice"
echo "2) Russian (ru_RU-ruslan-medium) - male voice"
echo "3) Spanish (es_ES-davefx-medium)"
echo "4) German (de_DE-thorsten-medium)"
echo "5) French (fr_FR-siwis-medium)"
echo "6) All languages"
echo ""
read -p "Your choice: " choices

# Download selected models
for choice in $choices; do
    case $choice in
        1)
            download_model "English" "en_US-lessac-medium" "en/en_US/lessac/medium"
            ;;
        2)
            download_model "Russian" "ru_RU-ruslan-medium" "ru/ru_RU/ruslan/medium"
            ;;
        3)
            download_model "Spanish" "es_ES-davefx-medium" "es/es_ES/davefx/medium"
            ;;
        4)
            download_model "German" "de_DE-thorsten-medium" "de/de_DE/thorsten/medium"
            ;;
        5)
            download_model "French" "fr_FR-siwis-medium" "fr/fr_FR/siwis/medium"
            ;;
        6)
            download_model "English" "en_US-lessac-medium" "en/en_US/lessac/medium"
            download_model "Russian" "ru_RU-ruslan-medium" "ru/ru_RU/ruslan/medium"
            download_model "Spanish" "es_ES-davefx-medium" "es/es_ES/davefx/medium"
            download_model "German" "de_DE-thorsten-medium" "de/de_DE/thorsten/medium"
            download_model "French" "fr_FR-siwis-medium" "fr/fr_FR/siwis/medium"
            ;;
        *)
            echo "Invalid choice: $choice"
            ;;
    esac
done

echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "\nModels installed in: $VOICE_DIR"
echo -e "Files:"
ls -lh "$VOICE_DIR"

echo -e "\n${BLUE}You can now use Piper:${NC}"
echo -e "   python cli.py \"Hello world\" --engine pipertts"
echo -e "   python cli.py \"Привет мир\" --engine pipertts --language ru\n"
