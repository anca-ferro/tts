#!/bin/bash
# Coqui TTS Installation Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Coqui TTS Installation Script${NC}\n"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

echo -e "Python version: $python_version"

# Check Python version compatibility
if [[ "$python_major" -eq 3 ]] && [[ "$python_minor" -ge 12 ]]; then
    echo -e "${RED}ERROR: Coqui TTS requires Python 3.9-3.11${NC}"
    echo -e "${RED}Your Python version: $python_version (not supported)${NC}\n"
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  1. Use other engines: piper, silerotts, gtts, pyttsx3"
    echo -e "  2. Install Python 3.11 in separate venv:"
    echo -e "     python3.11 -m venv venv311"
    echo -e "     source venv311/bin/activate"
    echo -e "     pip install TTS\n"
    exit 1
elif [[ "$python_major" -ne 3 ]] || [[ "$python_minor" -lt 9 ]]; then
    echo -e "${RED}ERROR: Coqui TTS requires Python 3.9-3.11${NC}"
    echo -e "${RED}Your Python version: $python_version (too old)${NC}\n"
    exit 1
fi

echo -e "${GREEN}Python version compatible: OK${NC}\n"

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
echo "Where do you want to store Coqui TTS models?"
echo "1) Default: .coquitts/ (in project directory)"
echo "2) Standard: ~/.local/share/tts/ (default Coqui location)"
echo "3) Custom directory (e.g., /data/tts-models, /mnt/ssd/models)"
read -p "Your choice (1, 2, or 3): " models_dir_choice

MODELS_DIR=""
case "$models_dir_choice" in
    1)
        # Default: use .coquitts in project directory
        MODELS_DIR="$PROJECT_ROOT/.coquitts"
        if [[ ! -d "$MODELS_DIR" ]]; then
            echo -e "${YELLOW}Creating directory: $MODELS_DIR${NC}"
            mkdir -p "$MODELS_DIR" || {
                echo -e "${RED}Failed to create directory${NC}"
                exit 1
            }
        fi
        echo -e "${GREEN}Using project directory: $MODELS_DIR${NC}"
        export COQUITTS_MODELS="$MODELS_DIR"
        export TORCH_HOME="$MODELS_DIR"
        ;;
    2)
        # Standard Coqui location
        MODELS_DIR="$HOME/.local/share/tts"
        if [[ ! -d "$MODELS_DIR" ]]; then
            echo -e "${YELLOW}Creating directory: $MODELS_DIR${NC}"
            mkdir -p "$MODELS_DIR" || {
                echo -e "${RED}Failed to create directory${NC}"
                exit 1
            }
        fi
        echo -e "${GREEN}Using standard Coqui directory: $MODELS_DIR${NC}"
        # Don't set env variables - let it use default
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
        export COQUITTS_MODELS="$custom_dir"
        export TORCH_HOME="$custom_dir"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Using default: .coquitts/${NC}"
        MODELS_DIR="$PROJECT_ROOT/.coquitts"
        mkdir -p "$MODELS_DIR"
        export COQUITTS_MODELS="$MODELS_DIR"
        export TORCH_HOME="$MODELS_DIR"
        ;;
esac

# GPU or CPU installation
echo -e "\n${YELLOW}Select installation type:${NC}"
echo "1) CPU only (slower, works everywhere)"
echo "2) GPU with CUDA (faster, requires NVIDIA GPU)"
read -p "Your choice (1 or 2): " install_type

if [[ "$install_type" == "2" ]]; then
    echo -e "\n${BLUE}Installing PyTorch with CUDA support...${NC}"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
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
    print("Will use CPU mode (slower)")
PYEOF
fi

# Install Coqui TTS
echo -e "\n${BLUE}Installing Coqui TTS...${NC}"
# Install with compatible transformers version
pip install TTS transformers==4.33.0

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 << 'PYEOF'
try:
    from TTS.api import TTS
    import transformers
    print(f"Coqui TTS installed successfully!")
    print(f"transformers version: {transformers.__version__}")
    
    # Warn if transformers version is not 4.33.x
    version = transformers.__version__.split('.')
    if version[0] != '4' or int(version[1]) > 33:
        print("\nWARNING: transformers version may be incompatible!")
        print(f"Recommended: 4.33.0, Installed: {transformers.__version__}")
        print("You may encounter ImportError with xtts_v2 models.")
        
except ImportError as e:
    print(f"Installation failed: {e}")
    exit(1)
PYEOF

# Model selection
echo -e "\n${YELLOW}Pre-download models? (optional, recommended)${NC}"
echo "Models will be downloaded automatically on first use,"
echo "but you can download them now to save time later."
echo ""
echo "1) Download multilingual model (xtts_v2, ~1.8GB)"
echo "2) Download English model (tacotron2, ~200MB)"
echo "3) Skip (download on first use)"
read -p "Your choice (1, 2, or 3): " model_choice

if [[ "$model_choice" == "1" ]]; then
    echo -e "\n${YELLOW}IMPORTANT: License Agreement${NC}"
    echo "The xtts_v2 model requires accepting a license:"
    echo "  - Non-commercial use: CPML license (https://coqui.ai/cpml)"
    echo "  - Commercial use: Requires commercial license from Coqui"
    echo ""
    read -p "Do you accept the non-commercial CPML license? (y/n): " accept_license
    
    if [[ "$accept_license" != "y" ]]; then
        echo "License not accepted. Skipping model download."
    else
        echo -e "\n${BLUE}Downloading multilingual model (this may take 10-30 minutes)...${NC}"
        echo "When prompted for license, type: y"
        echo ""
        # Run Python directly (not through heredoc) so stdin works
        python3 -c "from TTS.api import TTS; print('Downloading tts_models/multilingual/multi-dataset/xtts_v2...'); tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=True, gpu=False); print('Download complete!')"
    fi

elif [[ "$model_choice" == "2" ]]; then
    echo -e "\n${BLUE}Downloading English model...${NC}"
    python3 << 'PYEOF'
from TTS.api import TTS
print("Downloading tts_models/en/ljspeech/tacotron2-DDC...")
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)
print("Download complete!")
PYEOF
fi

# Installation complete
echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "\n${BLUE}Usage examples:${NC}"
echo -e "   python cli.py \"Hello world\" --engine coquitts"
echo -e "   python cli.py \"Привет мир\" --engine coquitts --language ru"
echo -e "   python cli.py \"Hello\" --engine coquitts --file output.wav"

echo -e "\n${YELLOW}Notes:${NC}"
echo -e "- First run will download models if not pre-downloaded"
echo -e "- CPU mode is slow. GPU mode is much faster"
echo -e "- Models cached in: $MODELS_DIR"

if [[ "$MODELS_DIR" == "$PROJECT_ROOT/.coquitts" ]]; then
    echo -e "\n${BLUE}Using default models directory:${NC}"
    echo -e "   $PROJECT_ROOT/.coquitts/"
    echo -e "   To use a different location, set COQUITTS_MODELS in .env file"
else
    echo -e "\n${BLUE}Using custom models directory:${NC}"
    echo -e "   $MODELS_DIR"
fi

echo ""

