#!/bin/bash

# HUD Notes v2.0.4 Update Script
# Updates existing installation in ~/tools/hud-notes

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Setup logging
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="update-${TIMESTAMP}.txt"
TOOLS_DIR="$HOME/tools"
TARGET_DIR="$TOOLS_DIR/hud-notes"

# Function to log and print
log_print() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function for status messages (log and print)
log_status() { log_print "${BLUE}[INFO]${NC} $1"; }
log_success() { log_print "${GREEN}[OK]${NC} $1"; }
log_warning() { log_print "${YELLOW}[WARNING]${NC} $1"; }
log_error() { log_print "${RED}[ERROR]${NC} $1"; }

# Start logging
echo "HUD Notes Update Log - $(date)" > "$LOG_FILE"
echo "===============================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

log_print "${CYAN}HUD Notes v2.0.4 Update Script${NC}"
log_print "==============================="
log_print ""

# Check if we're in source directory
if [ ! -f "main.py" ]; then
    log_error "main.py not found in current directory!"
    log_error "Run this script from the HUD-note source directory."
    exit 1
fi
log_success "Found main.py in current directory"

# Check if tools directory exists
if [ ! -d "$TOOLS_DIR" ]; then
    log_error "Tools directory not found: $TOOLS_DIR"
    log_error "Create it first: mkdir -p $TOOLS_DIR"
    exit 1
fi
log_success "Found tools directory: $TOOLS_DIR"

# Check if target installation exists
if [ ! -d "$TARGET_DIR" ]; then
    log_error "HUD Notes installation not found: $TARGET_DIR"
    log_error "Install first with: ./install_hud_notes.sh"
    exit 1
fi
log_success "Found existing installation: $TARGET_DIR"

# Create backup
BACKUP_DIR="${TARGET_DIR}.bak-${TIMESTAMP}"
log_status "Creating backup: $BACKUP_DIR"

if cp -r "$TARGET_DIR" "$BACKUP_DIR"; then
    log_success "Backup created successfully"
else
    log_error "Failed to create backup"
    exit 1
fi

# Check what we're about to copy
log_status "Files to be updated:"
FILES_TO_COPY=$(find . -maxdepth 1 -type f -name "*.py" -o -name "*.sh" -o -name "*.txt" -o -name "*.md" | grep -v "$LOG_FILE" | sort)

if [ -z "$FILES_TO_COPY" ]; then
    log_warning "No files found to copy"
else
    for file in $FILES_TO_COPY; do
        log_print "  - $file"
    done
fi

# Check for directories to copy
DIRS_TO_COPY=""
for dir in ui config core features utils templates; do
    if [ -d "$dir" ]; then
        DIRS_TO_COPY="$DIRS_TO_COPY $dir"
        log_print "  - $dir/ (directory)"
    fi
done

# Ask for confirmation
log_print ""
read -p "Continue with update? (y/N): " -n 1 -r
echo
log_print "User response: $REPLY"

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warning "Update cancelled by user"
    log_status "Removing backup: $BACKUP_DIR"
    rm -rf "$BACKUP_DIR"
    exit 0
fi

# Start update process
log_print ""
log_status "Starting update process..."

# Copy files
if [ -n "$FILES_TO_COPY" ]; then
    log_status "Copying files..."
    for file in $FILES_TO_COPY; do
        if cp "$file" "$TARGET_DIR/"; then
            log_success "Copied: $file"
        else
            log_error "Failed to copy: $file"
        fi
    done
fi

# Copy directories
if [ -n "$DIRS_TO_COPY" ]; then
    log_status "Copying directories..."
    for dir in $DIRS_TO_COPY; do
        if cp -r "$dir" "$TARGET_DIR/"; then
            log_success "Copied: $dir/"
        else
            log_error "Failed to copy: $dir/"
        fi
    done
fi

# Make main script executable
if chmod +x "$TARGET_DIR/main.py"; then
    log_success "Made main.py executable"
else
    log_warning "Could not make main.py executable"
fi

# Make other scripts executable
for script in install_hud_notes.sh setup.sh uninstall_hud_notes.sh; do
    if [ -f "$TARGET_DIR/$script" ]; then
        if chmod +x "$TARGET_DIR/$script"; then
            log_success "Made $script executable"
        else
            log_warning "Could not make $script executable"
        fi
    fi
done

# Check if global command still works
log_status "Testing global command..."
if command -v hud-notes &> /dev/null; then
    log_success "Global 'hud-notes' command is available"
    
    # Quick test
    if timeout 3 hud-notes --help 2>/dev/null || timeout 3 hud-notes --version 2>/dev/null; then
        log_success "HUD Notes can execute successfully"
    else
        log_warning "Could not test execution (probably normal)"
    fi
else
    log_warning "Global 'hud-notes' command not found"
    log_warning "You may need to reinstall: ./install_hud_notes.sh"
fi

# Show update summary
log_print ""
log_print "${GREEN}Update Summary${NC}"
log_print "=============="

# Count what was updated
FILE_COUNT=$(echo "$FILES_TO_COPY" | wc -w)
DIR_COUNT=$(echo "$DIRS_TO_COPY" | wc -w)

log_print "Files updated: $FILE_COUNT"
log_print "Directories updated: $DIR_COUNT"
log_print "Backup created: $BACKUP_DIR"
log_print "Installation: $TARGET_DIR"

# Check version (if available)
if [ -f "$TARGET_DIR/main.py" ]; then
    VERSION_INFO=$(grep -i "version\|v[0-9]" "$TARGET_DIR/main.py" | head -1 | cut -c1-50 || echo "Unknown")
    log_print "Version info: $VERSION_INFO"
fi

log_print ""
log_print "${GREEN}Update Complete!${NC}"
log_print "================"
log_print ""
log_print "What was updated:"
log_print "• Source files copied to: $TARGET_DIR"
log_print "• Backup saved as: $BACKUP_DIR"
log_print "• Log saved as: $LOG_FILE"
log_print ""
log_print "Test the update:"
log_print "• Run: ${YELLOW}hud-notes${NC}"
log_print "• Or: ${YELLOW}python3 $TARGET_DIR/main.py${NC}"
log_print ""
log_print "If something breaks:"
log_print "• Restore backup: ${YELLOW}cp -r $BACKUP_DIR $TARGET_DIR${NC}"
log_print "• Check log: ${YELLOW}cat $LOG_FILE${NC}"
log_print ""

# Clean up old backups (keep last 5)
log_status "Cleaning up old backups..."
OLD_BACKUPS=$(find "$TOOLS_DIR" -maxdepth 1 -name "hud-notes.bak-*" -type d | sort -r | tail -n +6)

if [ -n "$OLD_BACKUPS" ]; then
    for backup in $OLD_BACKUPS; do
        log_status "Removing old backup: $(basename "$backup")"
        rm -rf "$backup"
    done
    log_success "Old backups cleaned up"
else
    log_status "No old backups to clean up"
fi

# Final status
log_print ""
log_print "${CYAN}Update completed successfully!${NC}"
log_print "Log saved to: $LOG_FILE"
log_print ""

# Show any warnings
if grep -q "WARNING\|ERROR" "$LOG_FILE"; then
    log_print "${YELLOW}Note: Check log file for any warnings or errors${NC}"
fi

echo "$(date): Update process completed" >> "$LOG_FILE"