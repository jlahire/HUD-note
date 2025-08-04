#!/usr/bin/env python3
"""
HUD Notes - Production Version
A HUD-style overlay note-taking application with multi-display support,
syntax highlighting, and template system.

Author: jLaHire
License: AGPL-3.0
"""

import sys
import os
from core.application import HUDNotesApp


def show_version():
    """Show version information"""
    print("HUD Notes v1.0.3")
    print("A HUD-style overlay note-taking application")
    print("Author: jLaHire")
    print("License: MIT")


def show_help():
    """Show help information"""
    print("HUD Notes - Overlay Note-Taking Application")
    print("")
    print("Usage:")
    print("  hud_notes.py [options]")
    print("")
    print("Options:")
    print("  -h, --help     Show this help message")
    print("  -v, --version  Show version information")
    print("")
    print("First Run:")
    print("  On first run, a setup dialog will appear to configure:")
    print("  - Notes directory location")
    print("  - Author name for templates")
    print("  - Initial note title")
    print("  - Default template selection")
    print("")
    print("Hotkeys:")
    print("  Ctrl+Alt+t     Toggle HUD overlay")
    print("  Ctrl+Alt+g     Settings")
    print("  Ctrl+Alt+n     New note")
    print("  Ctrl+Alt+o     Open note")
    print("  Ctrl+Alt+s     Save note")
    print("  Ctrl+Alt+c     Code input window")
    print("  Ctrl+Alt+p     Toggle preview")
    print("  Ctrl+Alt+m     Move to next display")
    print("  Ctrl+Alt+r     Reset window position")
    print("  Ctrl+Alt+1-4   Move to corners")
    print("  Ctrl+Alt+5     Center window")
    print("  Esc           Hide overlay")
    print("")
    print("For more information, see README.md")


def main():
    """Main entry point with argument handling"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--version', '-v']:
            show_version()
            return
        elif arg in ['--help', '-h']:
            show_help()
            return
    
    try:
        app = HUDNotesApp()
        if hasattr(app, 'setup_complete') and app.setup_complete:
            app.run()
        else:
            print("Setup was cancelled. Exiting...")
    except KeyboardInterrupt:
        print("\nShutting down HUD Notes...")
    except Exception as e:
        print(f"Error starting HUD Notes: {e}")
        print("Please check that all dependencies are installed:")
        print("  pip3 install -r requirements.txt")
        print("\nFor help, see README.md or run with --help")
        
        # Only pause on Windows or if we're in an interactive session
        if os.name == 'nt' or (hasattr(sys, 'ps1') or sys.stdin.isatty()):
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()