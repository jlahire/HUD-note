#!/usr/bin/env python3
"""HUD Notes - Floating overlay note-taking app."""

from core.application import HUDNotesApp


def main():
    app = HUDNotesApp()
    if app.setup_complete:
        app.run()
    else:
        print("Setup cancelled. Exiting.")


if __name__ == "__main__":
    main()
