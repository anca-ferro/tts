#!/bin/bash
# Silero TTS Installation Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Silero TTS Installation Script${NC}\n"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "Python version: $python_version"

# Check if venv is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not detected${NC}"
    echo -e "It's recommended to activate venv first"
    read -p "Continue anyway? (y/n): " continue_install
    if [[ "$continue_install" != "y" ]]; then
        echo "Installation cancelled"
        exit 0
    fi
fi

# Get script directory (bin/) and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Models directory configuration
echo -e "\n${YELLOW}Models storage directory:${NC}"
echo "Where do you want to store Silero models?"
echo "1) Default: .silerotts/ (in project directory)"
echo "2) Standard: ~/.cache/torch/hub/ (default Silero location)"
echo "3) Custom directory (e.g., /data/tts-models, /mnt/ssd/models)"
read -p "Your choice (1, 2, or 3): " models_dir_choice

MODELS_DIR=""
case "$models_dir_choice" in
    1)
        # Default: use .silerotts in project directory
        MODELS_DIR="$PROJECT_ROOT/.silerotts"
        if [[ ! -d "$MODELS_DIR" ]]; then
            echo -e "${YELLOW}Creating directory: $MODELS_DIR${NC}"
            mkdir -p "$MODELS_DIR" || {
                echo -e "${RED}Failed to create directory${NC}"
                exit 1
            }
        fi
        echo -e "${GREEN}Using project directory: $MODELS_DIR${NC}"
        export SILEROTTS_MODELS="$MODELS_DIR"
        ;;
    2)
        # Standard Silero location
        MODELS_DIR="$HOME/.cache/torch/hub"
        if [[ ! -d "$MODELS_DIR" ]]; then
            echo -e "${YELLOW}Creating directory: $MODELS_DIR${NC}"
            mkdir -p "$MODELS_DIR" || {
                echo -e "${RED}Failed to create directory${NC}"
                exit 1
            }
        fi
        echo -e "${GREEN}Using standard Silero directory: $MODELS_DIR${NC}"
        # Don't set SILERO_MODELS_DIR - let it use default
        ;;
    3)
        # Custom directory
        read -p "Enter custom directory path: " custom_dir
        # Expand ~ to full path
        custom_dir="${custom_dir/#\~/$HOME}"
        
        # Create directory if it doesn't exist
        if [[ ! -d "$custom_dir" ]]; then
            echo -e "${YELLOW}Directory doesn't exist. Creating: $custom_dir${NC}"
            mkdir -p "$custom_dir" || {
                echo -e "${RED}Failed to create directory${NC}"
                exit 1
            }
        fi
        
        echo -e "${GREEN}Using custom directory: $custom_dir${NC}"
        MODELS_DIR="$custom_dir"
        export SILEROTTS_MODELS="$custom_dir"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Using default: .silerotts/${NC}"
        MODELS_DIR="$PROJECT_ROOT/.silerotts"
        mkdir -p "$MODELS_DIR"
        export SILEROTTS_MODELS="$MODELS_DIR"
        ;;
esac

# Installation type selection
echo -e "\n${YELLOW}Select installation type:${NC}"
echo "1) CPU only (recommended, works on all systems)"
echo "2) GPU with CUDA (faster, requires NVIDIA GPU)"
read -p "Your choice (1 or 2): " install_type

if [[ "$install_type" == "2" ]]; then
    echo -e "\n${BLUE}Installing PyTorch with CUDA support...${NC}"
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    # Verify CUDA
    echo -e "\n${YELLOW}Checking CUDA availability...${NC}"
    python3 << 'PYEOF'
import torch
if torch.cuda.is_available():
    print(f"CUDA available: YES")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA available: NO")
    print("Will use CPU mode")
PYEOF
else
    echo -e "\n${BLUE}Installing PyTorch (CPU version)...${NC}"
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install additional dependencies
echo -e "\n${BLUE}Installing additional dependencies...${NC}"
pip install omegaconf

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 << 'PYEOF'
try:
    import torch
    import torchaudio
    import omegaconf
    print(f"PyTorch version: {torch.__version__}")
    print(f"torchaudio version: {torchaudio.__version__}")
    print(f"omegaconf version: {omegaconf.__version__}")
    print("Silero TTS dependencies installed successfully!")
except ImportError as e:
    print(f"Installation failed: {e}")
    exit(1)
PYEOF

# Pre-download models
echo -e "\n${YELLOW}Pre-download voice models? (optional, recommended)${NC}"
echo "Models will be downloaded automatically on first use,"
echo "but you can download them now to save time later."
echo ""
echo "1) Download Russian model (~80MB)"
echo "2) Download English model (~80MB)"
echo "3) Download both Russian and English"
echo "4) Skip (download on first use)"
read -p "Your choice (1, 2, 3, or 4): " model_choice

download_russian() {
    echo -e "\n${BLUE}Downloading Russian model...${NC}"
    if [[ -n "$SILEROTTS_MODELS" ]]; then
        echo -e "Target directory: $SILEROTTS_MODELS"
    fi
    python3 << 'PYEOF'
import torch
import os

# Set custom directory if specified
models_dir = os.environ.get('SILEROTTS_MODELS')
if models_dir:
    torch.hub.set_dir(models_dir)
    print(f"Using custom directory: {models_dir}")

print("Loading Russian Silero model...")
model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v3_1_ru',
    verbose=True,
    trust_repo=True
)
print("Russian model downloaded and cached!")
PYEOF
}

download_english() {
    echo -e "\n${BLUE}Downloading English model...${NC}"
    if [[ -n "$SILEROTTS_MODELS" ]]; then
        echo -e "Target directory: $SILEROTTS_MODELS"
    fi
    python3 << 'PYEOF'
import torch
import os

# Set custom directory if specified
models_dir = os.environ.get('SILEROTTS_MODELS')
if models_dir:
    torch.hub.set_dir(models_dir)
    print(f"Using custom directory: {models_dir}")

print("Loading English Silero model...")
model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='en',
    speaker='v3_en',
    verbose=True,
    trust_repo=True
)
print("English model downloaded and cached!")
PYEOF
}

case "$model_choice" in
    1)
        download_russian
        ;;
    2)
        download_english
        ;;
    3)
        download_russian
        download_english
        ;;
    4)
        echo "Skipping model download"
        ;;
    *)
        echo "Invalid choice, skipping"
        ;;
esac

# Installation complete
echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "\n${BLUE}Usage examples:${NC}"
echo -e "   python cli.py \"Hello world\" --engine silerotts"
echo -e "   python cli.py \"Привет мир\" --engine silerotts --language ru"
echo -e "   python cli.py \"Hello\" --engine silerotts --file output.wav"

echo -e "\n${YELLOW}Notes:${NC}"
echo -e "- First run per language will download model automatically"
echo -e "- Models cached in: $MODELS_DIR"
echo -e "- Fast on CPU, no GPU required"
echo -e "- Particularly excellent for Russian language"

if [[ "$MODELS_DIR" == "$PROJECT_ROOT/.silerotts" ]]; then
    echo -e "\n${BLUE}Using default models directory:${NC}"
    echo -e "   $PROJECT_ROOT/.silerotts/"
    echo -e "   To use a different location, set SILEROTTS_MODELS in .env file"
else
    echo -e "\n${BLUE}Using custom models directory:${NC}"
    echo -e "   $MODELS_DIR"
fi

echo ""

