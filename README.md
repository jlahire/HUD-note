# HUD Notes v2.0.4 - Overlay Note-Taking

> This project was built with AI help. It's designed for my personal use when I'm out with just my laptop and need quick notes during CTF competitions, coding sessions, and research. Feel free to use it, but test it yourself first.

A floating note-taking overlay that stays on top of everything else. Built with Python and Tkinter because it works everywhere.

## What's New

### Tab System

- Open multiple notes at once in tabs
- Each tab saves automatically
- Click to switch between notes
- Close tabs with the X button

### Simplified Interface

- Just the buttons you actually need
- Text size controls (T-/T+)
- Transparency controls (O-/O+)
- New note, Open file, Settings
- That's it

### Built-in Templates

- No more external template files that can break
- 11 templates built into the code
- Just works

## Known Issues

**Don't use the preview hotkey** (`Ctrl+Alt+P`) - it breaks with the tab system. Everything else works fine.

**Tab closing quirk** - When you close the last tab, it automatically creates a new "Untitled" tab. Sometimes this can cause weird window behavior. Just roll with it or restart the app if things get wonky.

**Multi-monitor issues** - The multi-window/display cycling features don't work properly yet. Stick to single monitor for now.

**Linux/X11 problems** - Some features are flaky on Linux, especially window positioning and transparency. Works best on Windows. If you're on Linux, expect some rough edges.

## Quick Start

```bash
pip install pynput markdown2
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
python main.py
```

First run will ask where to save notes and your name. Then press `Ctrl+Alt+H` to show/hide the overlay.

## Installation Options

**Run directly:**

```bash
python main.py
```

**Install globally:**

```bash
./setup.sh          # One-time setup
./install_hud_notes.sh   # Global installation
```

**Update existing installation:**

```bash
./update.sh         # Updates ~/tools/hud-notes from current directory
```

The update script creates automatic backups and logs everything to `update-YYYYMMDD.txt`.

## How to Use

- **New note**: Click "New" or `Ctrl+Alt+N` - opens in new tab
- **Open file**: Click "Open" or `Ctrl+Alt+O` - opens in new tab
- **Save**: `Ctrl+Alt+S` saves current tab
- **Switch tabs**: Click on tab names
- **Close tabs**: Click the X on each tab
- **Font size**: T- and T+ buttons
- **Transparency**: O- and O+ buttons
- **Hide overlay**: Press `Esc`

## Templates

Built-in templates for different use cases:

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

10+ built-in color themes:

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

Change themes in Settings.

## File Structure

```text
hud-notes/
├── config/          # Settings
├── core/            # Main app logic
├── features/        # Hotkeys, window management
├── ui/              # Interface and tabs
├── utils/           # Helper functions
└── main.py          # Run this
```

## Hotkeys

| Key | Action |
|-----|--------|
| `Ctrl+Alt+H` | Show/hide overlay |
| `Ctrl+Alt+N` | New note (new tab) |
| `Ctrl+Alt+O` | Open file (new tab) |
| `Ctrl+Alt+S` | Save current tab |
| `Ctrl+Alt+G` | Settings |
| `Ctrl+Alt+±` | Font size |
| `Alt+±` | Transparency |
| `Esc` | Hide |

## Common Problems

- **Preview hotkey broken** - Don't use `Ctrl+Alt+P` with tabs
- **Tab auto-creation** - Closing the last tab makes a new "Untitled" tab that can act weird
- **Multi-monitor not working** - Display cycling and multi-window features are broken
- **Linux/X11 issues** - Window positioning, transparency, and other features can be flaky
- **Hotkeys not working** - Allow Python through Windows Firewall
- **Wrong size/position** - Press `Ctrl+Alt+R` to reset
- **Can't see overlay** - Check if transparency is too high
- **Window acting strange** - Restart the app (`python main.py`)

## Configuration

Settings are saved in `.note_config.json` in your notes folder. Delete this file to reset everything.

## Why This Exists

I needed something that:

- Stays on top during CTF competitions
- Takes up 1/4 of my screen (right side)
- Saves automatically so I don't lose notes
- Works on any screen size (single monitor)
- Has templates for different note types
- Doesn't require external dependencies
- Actually works reliably on Windows

Most note apps either take over your whole screen or disappear behind other windows. This stays put and gets out of your way.

## License

AGPL-3.0 - see LICENSE file

## Issues

If something breaks, check the console output when you run `python main.py`. The debug version shows what's going wrong.

Known issues: Preview feature doesn't play nice with tabs yet. Also, closing all tabs creates a new "Untitled" tab that sometimes behaves oddly. Multi-monitor support is broken. Linux/X11 has various issues with window management. Built and tested mainly on Windows. Will fix these eventually.

---

**Quick tip**: Use `Ctrl+Alt+H` to quickly show/hide during any activity. Open different topics in separate tabs.