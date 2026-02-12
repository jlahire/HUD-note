#!/bin/bash

# HUD Notes v2.1.0 Update Script
# Updates existing global installation in ~/tools/hud-notes
# Creates automatic backups and logs everything

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Setup
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="update-${TIMESTAMP}.txt"
TOOLS_DIR="$HOME/tools"
TARGET_DIR="$TOOLS_DIR/hud-notes"

log_print() { echo -e "$1" | tee -a "$LOG_FILE"; }
log_status() { log_print "${BLUE}[INFO]${NC} $1"; }
log_success() { log_print "${GREEN}[OK]${NC} $1"; }
log_warning() { log_print "${YELLOW}[WARN]${NC} $1"; }
log_error() { log_print "${RED}[ERROR]${NC} $1"; }

echo "HUD Notes Update Log - $(date)" > "$LOG_FILE"
echo "===============================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

log_print "${CYAN}HUD Notes v2.1.0 Update${NC}"
log_print "========================"
log_print ""

# Check source directory
if [ ! -f "main.py" ]; then
    log_error "main.py not found in current directory!"
    log_error "Run this from the HUD-note source directory."
    exit 1
fi
log_success "Source directory OK"

# Check target installation
if [ ! -d "$TARGET_DIR" ]; then
    log_error "No existing installation at $TARGET_DIR"
    log_error "Run ./setup.sh first to install."
    exit 1
fi
log_success "Found installation: $TARGET_DIR"

# Create backup
BACKUP_DIR="${TARGET_DIR}.bak-${TIMESTAMP}"
log_status "Creating backup: $BACKUP_DIR"
if cp -r "$TARGET_DIR" "$BACKUP_DIR"; then
    log_success "Backup created"
else
    log_error "Backup failed"
    exit 1
fi

# List what will be updated
log_status "Files to update:"

# Collect source files
SOURCE_FILES=$(find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" -o -name "*.txt" -o -name "*.md" \) ! -name "$LOG_FILE" | sort)
SOURCE_DIRS=""
for dir in config core features ui utils; do
    if [ -d "$dir" ]; then
        SOURCE_DIRS="$SOURCE_DIRS $dir"
        log_print "  $dir/"
    fi
done
for f in $SOURCE_FILES; do
    log_print "  $f"
done

# Confirm
log_print ""
read -p "Proceed with update? (y/N): " -n 1 -r
echo
log_print "Response: $REPLY"

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warning "Cancelled by user"
    rm -rf "$BACKUP_DIR"
    log_status "Backup removed"
    exit 0
fi

# Copy files
log_print ""
log_status "Updating..."

ERRORS=0

for f in $SOURCE_FILES; do
    if cp "$f" "$TARGET_DIR/"; then
        log_success "  $f"
    else
        log_error "  $f"
        ERRORS=$((ERRORS + 1))
    fi
done

for dir in $SOURCE_DIRS; do
    if cp -r "$dir" "$TARGET_DIR/"; then
        log_success "  $dir/"
    else
        log_error "  $dir/"
        ERRORS=$((ERRORS + 1))
    fi
done

# Make scripts executable
for script in main.py setup.sh install_hud_notes.sh update.sh; do
    if [ -f "$TARGET_DIR/$script" ]; then
        chmod +x "$TARGET_DIR/$script"
    fi
done
log_success "Scripts marked executable"

# Verify global command
if command -v hud-notes &> /dev/null; then
    log_success "'hud-notes' command available"
else
    log_warning "'hud-notes' command not found - you may need to run ./install_hud_notes.sh"
fi

# Summary
FILE_COUNT=$(echo "$SOURCE_FILES" | wc -w)
DIR_COUNT=$(echo "$SOURCE_DIRS" | wc -w)

log_print ""
log_print "${GREEN}Update Summary${NC}"
log_print "=============="
log_print "  Files: $FILE_COUNT"
log_print "  Directories: $DIR_COUNT"
log_print "  Errors: $ERRORS"
log_print "  Backup: $BACKUP_DIR"
log_print "  Log: $LOG_FILE"

# Clean up old backups (keep last 5)
OLD_BACKUPS=$(find "$TOOLS_DIR" -maxdepth 1 -name "hud-notes.bak-*" -type d 2>/dev/null | sort -r | tail -n +6)
if [ -n "$OLD_BACKUPS" ]; then
    for backup in $OLD_BACKUPS; do
        rm -rf "$backup"
        log_status "Removed old backup: $(basename "$backup")"
    done
fi

log_print ""
if [ "$ERRORS" -eq 0 ]; then
    log_print "${GREEN}Update complete!${NC}"
else
    log_print "${YELLOW}Update finished with $ERRORS error(s). Check log: $LOG_FILE${NC}"
fi

log_print ""
log_print "Test: ${YELLOW}hud-notes${NC}  or  ${YELLOW}python3 $TARGET_DIR/main.py${NC}"
log_print "Rollback: ${YELLOW}cp -r $BACKUP_DIR $TARGET_DIR${NC}"

echo "$(date): Update completed" >> "$LOG_FILE"
