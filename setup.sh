#!/bin/bash

# HUD Notes v2.1.0 Setup Script
# Checks prerequisites, installs dependencies, optionally installs globally
# Works on Linux and macOS

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}HUD Notes v2.1.0 Setup${NC}"
echo "======================"
echo

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found!${NC}"
    echo "Run this script from the HUD-note directory."
    exit 1
fi
echo -e "${GREEN}+${NC} Found project files"

# Make scripts executable
chmod +x main.py
chmod +x install_hud_notes.sh 2>/dev/null || true
chmod +x update.sh 2>/dev/null || true
echo -e "${GREEN}+${NC} Scripts are executable"

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)  PLATFORM="linux" ;;
    Darwin*) PLATFORM="macos" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)       PLATFORM="unknown" ;;
esac
echo -e "${GREEN}+${NC} Platform: $PLATFORM ($OS)"

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}Python not found!${NC}"
    echo
    echo "Install Python 3.8+ first:"
    case "$PLATFORM" in
        linux)
            echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
            echo "  Fedora:        sudo dnf install python3 python3-pip python3-tkinter"
            echo "  Arch:          sudo pacman -S python python-pip tk"
            ;;
        macos)
            echo "  brew install python3 python-tk"
            ;;
        *)
            echo "  Download from https://python.org"
            ;;
    esac
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}+${NC} $PYTHON_VERSION ($PYTHON_CMD)"

# Check pip
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_CMD="$PYTHON_CMD -m pip"
fi

if [ -z "$PIP_CMD" ]; then
    echo -e "${YELLOW}pip not found, attempting install...${NC}"
    case "$PLATFORM" in
        linux)
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y python3-pip
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3-pip
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm python-pip
            fi
            ;;
        macos)
            echo "pip should come with Homebrew Python. Try: brew reinstall python3"
            exit 1
            ;;
    esac
    # Re-check
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        echo -e "${RED}Could not install pip. Install it manually.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}+${NC} pip available"

# Check tkinter
echo -e "${BLUE}Checking tkinter...${NC}"
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}tkinter not found${NC}"
    case "$PLATFORM" in
        linux)
            echo "Install it with:"
            echo "  Ubuntu/Debian: sudo apt install python3-tk"
            echo "  Fedora:        sudo dnf install python3-tkinter"
            echo "  Arch:          sudo pacman -S tk"
            echo
            read -p "Try installing now (apt)? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                sudo apt install -y python3-tk || {
                    echo -e "${RED}Install python3-tk manually${NC}"
                    exit 1
                }
            else
                echo -e "${RED}tkinter is required${NC}"
                exit 1
            fi
            ;;
        macos)
            echo "Install with: brew install python-tk"
            exit 1
            ;;
    esac
fi
echo -e "${GREEN}+${NC} tkinter available"

# Install pip dependencies
echo -e "${BLUE}Checking pip dependencies...${NC}"
MISSING=()

for package in pynput markdown2; do
    if ! $PYTHON_CMD -c "import $package" 2>/dev/null; then
        MISSING+=("$package")
    fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
    echo -e "${YELLOW}Missing: ${MISSING[*]}${NC}"
    read -p "Install now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        $PIP_CMD install "${MISSING[@]}" || {
            echo -e "${RED}Installation failed. Try: $PIP_CMD install pynput markdown2${NC}"
            exit 1
        }
        echo -e "${GREEN}+${NC} Dependencies installed"
    else
        echo -e "${RED}Dependencies are required. Install with: $PIP_CMD install pynput markdown2${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}+${NC} All dependencies found"
fi

# Quick import test
echo -e "${BLUE}Testing imports...${NC}"
if $PYTHON_CMD -c "
import tkinter
import pynput
import markdown2
print('All imports OK')
" 2>/dev/null; then
    echo -e "${GREEN}+${NC} All modules import successfully"
else
    echo -e "${YELLOW}!${NC} Some imports failed (may still work)"
fi

echo
echo -e "${GREEN}Setup Complete!${NC}"
echo "==============="
echo
echo "Run directly:"
echo "  ${YELLOW}$PYTHON_CMD main.py${NC}"
echo

# Offer global install (Linux/macOS only)
if [ "$PLATFORM" = "linux" ] || [ "$PLATFORM" = "macos" ]; then
    read -p "Install globally (creates 'hud-notes' command)? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        ./install_hud_notes.sh
    else
        echo "Run ${YELLOW}./install_hud_notes.sh${NC} later to install globally."
    fi
else
    echo "On Windows, see INSTALL.md for shortcut and alias options."
fi
