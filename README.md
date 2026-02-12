# HUD Notes v2.1.0 - Overlay Note-Taking

> Built with AI help. Designed for quick notes during CTF competitions, coding sessions, and research. Feel free to use it, but test it yourself first.

A floating note-taking overlay that stays on top of everything else. Built with Python and Tkinter.

## Quick Start

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip install -r requirements.txt
python main.py
```

First run opens a setup dialog for your notes directory and author name. Then press `Ctrl+Alt+H` to toggle the overlay.

## Features

- **Tab system** - Open multiple notes at once, click to switch, close with X
- **11 built-in templates** - CTF writeup, meeting notes, code review, and more
- **10 color themes** - Matrix Green, Cyber Blue, Neon Purple, etc.
- **Global hotkeys** - Show/hide, new note, save, all without leaving your current app
- **Auto-save** - Notes save automatically so you don't lose work
- **Syntax highlighting** - Basic markdown highlighting in the editor
- **Transparency controls** - Adjust overlay opacity to see through it

## Installation

See [INSTALL.md](INSTALL.md) for detailed instructions for Windows, Linux, and macOS.

**Short version (all platforms):**

```bash
# 1. Install Python 3.8+
# 2. Clone and install dependencies
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip install -r requirements.txt

# 3. Run
python main.py
```

**Linux/macOS global install:**

```bash
./setup.sh
```

**Update existing installation:**

```bash
./update.sh
```

## How to Use

| Action | Button / Hotkey |
|--------|----------------|
| Show/hide overlay | `Ctrl+Alt+H` |
| New note (new tab) | Click "New" or `Ctrl+Alt+N` |
| Open file (new tab) | Click "Open" or `Ctrl+Alt+O` |
| Save current tab | `Ctrl+Alt+S` |
| Settings | `Ctrl+Alt+G` |
| Font size up/down | T+ / T- buttons |
| Transparency up/down | O+ / O- buttons |
| Hide overlay | `Esc` |
| Reset window position | `Ctrl+Alt+R` |

## Templates

Built-in templates available when creating a new note:

- Basic note
- Meeting notes
- Daily log
- Code review
- CTF writeup
- Class notes
- Study session
- Project planning
- Bug report
- PowerShell script
- Batch script

## Themes

Change in Settings (`Ctrl+Alt+G`):

- Matrix Green (default)
- Cyber Blue
- Neon Purple
- Hacker Orange
- Terminal White
- Blood Red
- Stealth Gray
- Retro Amber
- Electric Pink
- Deep Ocean

## File Structure

See [tree.md](tree.md) for the full project tree.

```
HUD-note/
├── main.py              # Entry point
├── core/                # App logic and templates
├── ui/                  # Interface, dialogs, tabs, themes
├── features/            # Hotkeys, window management, syntax highlighting
├── config/              # Settings manager
└── utils/               # Display and file utilities
```

## Known Issues

- **Wayland not supported** - Global hotkeys require X11. On Ubuntu 22.04+, log out, click the gear icon on the login screen, select "Ubuntu on Xorg", and log back in

- **Preview hotkey** (`Ctrl+Alt+P`) - broken with the tab system, don't use it
- **Multi-monitor** - display cycling features don't work properly, stick to single monitor
- **Tab closing** - closing the last tab auto-creates an "Untitled" tab that can act odd

## Configuration

Settings are saved in `.note_config.json` inside your notes directory. Delete this file to reset everything to defaults.

## License

AGPL-3.0 - see [LICENSE](LICENSE)

## Issues

If something breaks, check the terminal output when running `python main.py`. File issues at [github.com/jlahire/HUD-note/issues](https://github.com/jlahire/HUD-note/issues).
