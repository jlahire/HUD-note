# Project Tree

```
HUD-note/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies (pynput, markdown2)
├── setup.sh                         # Setup + optional global install (Linux/macOS)
├── install_hud_notes.sh             # Global install script (Linux/macOS)
├── update.sh                        # Update existing global installation
├── LICENSE                          # AGPL-3.0
├── README.md                        # Project overview
├── INSTALL.md                       # Installation guide (Windows/Linux/macOS)
├── tree.md                          # This file
├── .gitignore
│
├── config/
│   ├── __init__.py
│   └── settings.py                  # Settings manager, color schemes, hotkey defaults
│
├── core/
│   ├── __init__.py
│   ├── application.py               # Main app orchestrator (HUDNotesApp)
│   └── template_manager.py          # Built-in note templates
│
├── features/
│   ├── __init__.py
│   ├── auto_features.py             # Mouse hover show, click-outside hide
│   ├── hotkeys.py                   # Global hotkey registration (pynput)
│   ├── syntax_highlighting.py       # Markdown syntax highlighting
│   └── window_manager.py            # Window positioning, corner snapping, resizing
│
├── ui/
│   ├── __init__.py
│   ├── components.py                # StatusBar, ScreenBorder, tooltips, context menu
│   ├── dialogs.py                   # Startup, template selection, settings, code input
│   ├── overlay.py                   # Main overlay window
│   ├── tab_manager.py               # Tab bar and tab switching
│   └── themes.py                    # ThemeManager with 10 color themes
│
└── utils/
    ├── __init__.py
    ├── display_utils.py             # DisplayManager (DPI, screen detection), PlatformManager
    └── file_operations.py           # NotesManager (save, load, auto-save)
```
