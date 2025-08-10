#!/bin/bash

# HUD Notes v2.0.4 Installation Script
# Simple global installation - works best on single monitor Windows/Linux

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_NAME="hud-notes"
PYTHON_SCRIPT="main.py"
INSTALL_DIR="/usr/local/bin"

echo -e "${CYAN}HUD Notes v2.0.4 Installation${NC}"
echo "=============================="
echo

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if we're in the right place
if [ ! -f "$PYTHON_SCRIPT" ]; then
    print_error "main.py not found!"
    echo "Run this script from the HUD-note directory."
    exit 1
fi
print_success "Found main.py"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found!"
    echo "Install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Found $PYTHON_VERSION"

# Check dependencies
print_status "Checking dependencies..."
MISSING=()

for package in "tkinter" "pynput" "markdown2"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING+=("$package")
    fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
    print_warning "Missing: ${MISSING[*]}"
    echo "Install with: pip3 install pynput markdown2"
    read -p "Install now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install pynput markdown2 || {
            print_error "Installation failed"
            exit 1
        }
        print_success "Dependencies installed"
    else
        print_error "Can't continue without dependencies"
        exit 1
    fi
else
    print_success "All dependencies found"
fi

# Create wrapper script
print_status "Creating wrapper script..."
SCRIPT_DIR="$(pwd)"
WRAPPER_CONTENT="#!/bin/bash
# HUD Notes v2.0.4 Wrapper
SCRIPT_DIR=\"$SCRIPT_DIR\"
PYTHON_SCRIPT=\"\$SCRIPT_DIR/main.py\"

if [ ! -f \"\$PYTHON_SCRIPT\" ]; then
    echo \"Error: HUD Notes not found at: \$PYTHON_SCRIPT\"
    exit 1
fi

exec python3 \"\$PYTHON_SCRIPT\" \"\$@\"
"

TEMP_WRAPPER="/tmp/$SCRIPT_NAME"
echo "$WRAPPER_CONTENT" > "$TEMP_WRAPPER"
chmod +x "$TEMP_WRAPPER"

# Install globally
print_status "Installing to $INSTALL_DIR..."
if [ -w "$INSTALL_DIR" ]; then
    cp "$TEMP_WRAPPER" "$INSTALL_DIR/$SCRIPT_NAME"
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
else
    sudo cp "$TEMP_WRAPPER" "$INSTALL_DIR/$SCRIPT_NAME"
    sudo chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
fi

rm "$TEMP_WRAPPER"
print_success "Installed as '$SCRIPT_NAME'"

# Create alias
SHELL_NAME=$(basename "$SHELL")
case $SHELL_NAME in
    bash) SHELL_CONFIG="$HOME/.bashrc" ;;
    zsh) SHELL_CONFIG="$HOME/.zshrc" ;;
    *) SHELL_CONFIG="$HOME/.profile" ;;
esac

echo
read -p "Create alias? (enter name or press Enter to skip): " CUSTOM_ALIAS

if [ -n "$CUSTOM_ALIAS" ]; then
    if [[ "$CUSTOM_ALIAS" =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
        ALIAS_LINE="alias $CUSTOM_ALIAS='$SCRIPT_NAME'"
        
        if [ -f "$SHELL_CONFIG" ]; then
            cp "$SHELL_CONFIG" "$SHELL_CONFIG.backup"
        fi
        
        if ! grep -q "alias $CUSTOM_ALIAS=" "$SHELL_CONFIG" 2>/dev/null; then
            echo "" >> "$SHELL_CONFIG"
            echo "# HUD Notes alias" >> "$SHELL_CONFIG"
            echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
            print_success "Alias '$CUSTOM_ALIAS' added to $SHELL_CONFIG"
        else
            print_warning "Alias '$CUSTOM_ALIAS' already exists"
        fi
    else
        print_error "Invalid alias name"
    fi
fi

# Test installation
if command -v "$SCRIPT_NAME" &> /dev/null; then
    print_success "Installation successful!"
else
    print_error "Installation failed - command not found"
    exit 1
fi

echo
echo -e "${GREEN}Installation Complete!${NC}"
echo "======================"
echo
echo "Usage:"
echo "  $SCRIPT_NAME              # Run HUD Notes"
if [ -n "$CUSTOM_ALIAS" ]; then
    echo "  $CUSTOM_ALIAS                   # Your alias"
fi
echo "  Ctrl+Alt+H             # Toggle overlay (global hotkey)"
echo
echo "Known issues:"
echo "  - Don't use Ctrl+Alt+P (preview breaks tabs)"
echo "  - Multi-monitor features don't work"
echo "  - Linux/X11 can be flaky"
echo
echo "Uninstall:"
echo "  sudo rm $INSTALL_DIR/$SCRIPT_NAME"
echo
echo -e "${CYAN}Ready to use HUD Notes!${NC}"

if [ -n "$CUSTOM_ALIAS" ]; then
    echo
    echo "Restart your terminal or run: source $SHELL_CONFIG"
fi