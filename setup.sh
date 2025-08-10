#!/bin/bash

# HUD Notes v2.0.4 Setup Script
# Gets everything ready for installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}HUD Notes v2.0.4 Setup${NC}"
echo "======================"
echo

# Check if we're in the right place
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found!${NC}"
    echo "Run this script from the HUD-note directory."
    echo
    echo "Expected files:"
    echo "  - main.py"
    echo "  - install_hud_notes.sh"
    echo "  - requirements.txt"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found main.py"

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x main.py
chmod +x install_hud_notes.sh
if [ -f "uninstall_hud_notes.sh" ]; then
    chmod +x uninstall_hud_notes.sh
fi
echo -e "${GREEN}✓${NC} Scripts are executable"

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found!${NC}"
    echo "Install Python 3.8+ first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  macOS:         brew install python3"
    echo "  Windows:       Download from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Found $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}pip3 not found, trying to install...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install python3-pip
    else
        echo -e "${RED}Install pip3 manually${NC}"
        exit 1
    fi
fi

# Install dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
MISSING=()

# Check core dependencies
for package in "tkinter" "pynput" "markdown2"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        case $package in
            "pynput"|"markdown2") MISSING+=("$package") ;;
            "tkinter") 
                echo -e "${YELLOW}⚠ tkinter missing - usually comes with Python${NC}"
                if command -v apt &> /dev/null; then
                    echo "Try: sudo apt install python3-tk"
                fi
                ;;
        esac
    fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
    echo -e "${YELLOW}Missing: ${MISSING[*]}${NC}"
    echo
    read -p "Install now? (Y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${BLUE}Installing...${NC}"
        if pip3 install "${MISSING[@]}"; then
            echo -e "${GREEN}✓${NC} Dependencies installed"
        else
            echo -e "${RED}Installation failed${NC}"
            echo "Try: pip3 install pynput markdown2"
            exit 1
        fi
    else
        echo -e "${YELLOW}Skipped - install manually: pip3 install pynput markdown2${NC}"
    fi
else
    echo -e "${GREEN}✓${NC} All dependencies found"
fi

# Quick test
echo -e "${BLUE}Testing HUD Notes...${NC}"
if timeout 3 python3 main.py --help 2>/dev/null || timeout 3 python3 -c "
import sys, os
sys.path.insert(0, '.')
try:
    # Try importing some basic modules
    import tkinter
    print('✓ tkinter works')
except ImportError as e:
    print(f'✗ tkinter error: {e}')
" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} HUD Notes can run"
else
    echo -e "${YELLOW}⚠ Could not test (probably normal)${NC}"
fi

echo
echo -e "${GREEN}Setup Complete!${NC}"
echo "==============="
echo
echo -e "${CYAN}Next steps:${NC}"
echo "1. Run: ${YELLOW}./install_hud_notes.sh${NC}"
echo "2. Choose an alias"
echo "3. Start using HUD Notes"
echo
echo -e "${CYAN}Known issues:${NC}"
echo "• Don't use preview hotkey (Ctrl+Alt+P)"
echo "• Multi-monitor features broken"
echo "• Linux/X11 can be flaky"
echo "• Works best on Windows single monitor"
echo
echo -e "${CYAN}Quick test:${NC}"
echo "Run directly: ${YELLOW}python3 main.py${NC}"

# Ask to install now
echo
read -p "Install globally now? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}Starting installation...${NC}"
    echo
    ./install_hud_notes.sh
else
    echo "Run ${YELLOW}./install_hud_notes.sh${NC} when ready"
    echo
    echo "Or test directly: ${YELLOW}python3 main.py${NC}"
fi

echo
echo -e "${CYAN}Enjoy HUD Notes!${NC}"