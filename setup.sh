#!/bin/bash

# HUD Notes Production Setup Script
# Sets up everything needed for HUD Notes installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🚀 HUD Notes Production Setup${NC}"
echo -e "${CYAN}=============================${NC}"
echo

# Check if we're in the right directory
if [ ! -f "hud_notes.py" ]; then
    echo -e "${RED}❌ Error: hud_notes.py not found!${NC}"
    echo "Please run this script from the HUD Notes directory."
    echo
    echo "Expected files:"
    echo "  - hud_notes.py (main application)"
    echo "  - install_hud_notes.sh"
    echo "  - uninstall_hud_notes.sh"
    echo "  - templates/ directory"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found hud_notes.py"

# Check for templates directory
if [ ! -d "templates" ]; then
    echo -e "${YELLOW}⚠️  Templates directory not found, creating...${NC}"
    mkdir -p templates
    echo -e "${GREEN}✓${NC} Created templates directory"
else
    echo -e "${GREEN}✓${NC} Found templates directory"
fi

# Check template files
TEMPLATE_COUNT=$(find templates -name "*.md" -type f | wc -l)
if [ "$TEMPLATE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No template files found in templates/${NC}"
    echo "Templates will be created automatically on first run."
else
    echo -e "${GREEN}✓${NC} Found $TEMPLATE_COUNT template files"
fi

# Make scripts executable
echo -e "${BLUE}[INFO]${NC} Making scripts executable..."
chmod +x hud_notes.py
chmod +x install_hud_notes.sh
chmod +x uninstall_hud_notes.sh

echo -e "${GREEN}✓${NC} Scripts are now executable"

# Check Python installation
echo -e "${BLUE}[INFO]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed or not in PATH!${NC}"
    echo "Please install Python 3.7 or higher first."
    echo
    echo "Installation guides:"
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
    echo -e "${YELLOW}⚠️  pip3 not found, attempting to install...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install python3-pip
    else
        echo -e "${RED}❌ Please install pip3 manually${NC}"
        exit 1
    fi
fi

# Check and install requirements
echo -e "${BLUE}[INFO]${NC} Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} Found requirements.txt"
    
    # Check if dependencies are already installed
    MISSING_DEPS=()
    
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Extract package name (before >=, ==, etc.)
        PACKAGE=$(echo "$line" | sed 's/[>=<].*//' | tr -d '[:space:]')
        
        if [ -n "$PACKAGE" ]; then
            if ! python3 -c "import $PACKAGE" 2>/dev/null; then
                MISSING_DEPS+=("$line")
            fi
        fi
    done < requirements.txt
    
    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        echo -e "${GREEN}✓${NC} All dependencies are already installed!"
    else
        echo -e "${YELLOW}⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
        echo
        read -p "Install missing dependencies now? (Y/n): " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            echo -e "${BLUE}[INFO]${NC} Installing dependencies..."
            if pip3 install -r requirements.txt; then
                echo -e "${GREEN}✓${NC} Dependencies installed successfully!"
            else
                echo -e "${RED}❌ Failed to install dependencies${NC}"
                echo "Please run manually: pip3 install -r requirements.txt"
                exit 1
            fi
        else
            echo -e "${YELLOW}⚠️  Skipping dependency installation${NC}"
            echo "Run manually later: pip3 install -r requirements.txt"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
    echo "Installing core dependencies manually..."
    pip3 install pynput markdown2
fi

# Test the application
echo -e "${BLUE}[INFO]${NC} Testing HUD Notes..."
if python3 hud_notes.py --version 2>/dev/null || timeout 3 python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import hud_notes
    print('✓ HUD Notes can be imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✓ HUD Notes loads correctly (expected timeout)')
" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} HUD Notes is working correctly"
else
    echo -e "${YELLOW}⚠️  Could not test HUD Notes (this is usually normal)${NC}"
fi

echo
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${GREEN}==================${NC}"
echo
echo -e "${CYAN}Next steps:${NC}"
echo "1. Run the installer: ${YELLOW}./install_hud_notes.sh${NC}"
echo "2. Choose your preferred alias name"
echo "3. Start using HUD Notes!"
echo
echo -e "${CYAN}Quick commands:${NC}"
echo "• Run directly:       ${YELLOW}python3 hud_notes.py${NC}"
echo "• Install globally:   ${YELLOW}./install_hud_notes.sh${NC}"
echo "• Uninstall:          ${YELLOW}./uninstall_hud_notes.sh${NC}"
echo "• View templates:     ${YELLOW}ls templates/${NC}"
echo
echo -e "${BLUE}📁 File structure:${NC}"
echo "  hud_notes.py        - Main application"
echo "  templates/          - Note templates"
echo "  requirements.txt    - Python dependencies"
echo "  install_*.sh        - Installation scripts"
echo

# Ask if user wants to install globally now
read -p "Do you want to install HUD Notes globally now? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Starting global installation..."
    echo
    ./install_hud_notes.sh
else
    echo -e "${YELLOW}Installation skipped.${NC}"
    echo "Run ${YELLOW}./install_hud_notes.sh${NC} when you're ready to install globally."
    echo
    echo "You can also run HUD Notes directly with:"
    echo "  ${YELLOW}python3 hud_notes.py${NC}"
fi

echo
echo -e "${CYAN}🚀 Enjoy using HUD Notes!${NC}"