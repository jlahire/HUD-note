# Windows Installation Guide - HUD Notes v2.0.4

This guide covers Windows installation for HUD Notes v2.0.4. It works best on Windows - other platforms have issues.

## Quick Start

**1. Clone and Install**

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip install pynput markdown2
python main.py
```

That's it. First run will ask where to save notes.

## Known Limitations

- **Multi-monitor stuff is broken** - stick to single monitor
- **Linux/WSL is flaky** - expect issues with window positioning and transparency
- **Preview hotkey crashes tabs** - don't use Ctrl+Alt+P
- **Tab closing can get weird** - restart app if it acts up

## Git Bash Setup

If you use Git Bash and want global access:

```bash
# Create launcher
mkdir -p ~/bin
echo '#!/bin/bash
cd "'$(pwd)'"
python main.py "$@"' > ~/bin/hud-notes
chmod +x ~/bin/hud-notes

# Add to PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
source ~/.bashrc
```

Now you can run `HUD` from anywhere.

## PowerShell Setup

Add to your PowerShell profile:

```powershell
function HUD {
    Set-Location "C:\path\to\your\HUD-note"
    python main.py $args
}
```

Replace the path with wherever you put the files.

## WSL (Linux Subsystem)

Works but has issues. You'll need an X server for the GUI.

**Install X server (VcXsrv):**
1. Download VcXsrv from SourceForge
2. Run with "Disable access control" checked
3. Add to ~/.bashrc: `export DISPLAY=:0.0`

**Then install HUD Notes:**

```bash
sudo apt install python3 python3-pip python3-tk
pip3 install pynput markdown2
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
python3 main.py
```

**Expect problems with:**
- Window positioning
- Transparency not working
- Hotkeys being unreliable
- General flakiness

Windows 11 has WSLg built-in which might work better, but still expect issues.

## Troubleshooting

**Hotkeys not working:**
- Allow Python through Windows Firewall
- Try running as administrator once

**Can't see the overlay:**
- Check if transparency is set too high
- Press Ctrl+Alt+R to reset position

**Window acting weird:**
- Restart the app
- Don't close all tabs at once
- Avoid the preview hotkey

**Python not found:**
- Make sure Python is in your PATH
- Try `py main.py` instead of `python main.py`

## What Actually Works

- Single monitor use
- Tab system (mostly)
- Templates and themes
- Auto-save
- Basic hotkeys
- File operations

## What's Broken

- Multi-monitor cycling (Ctrl+Alt+M)
- Screen positioning (Ctrl+Alt+1-4)
- Center window (Ctrl+Alt+5)
- Preview hotkey (Ctrl+Alt+P)
- Reliable Linux support

## Templates

All templates are built into the app now:
- Basic note
- Meeting notes
- Daily log
- CTF writeup
- Code review
- And more

Just click "New" and pick one.

## Why Windows Works Best

This was built and tested mainly on Windows 10/11. The Python Tkinter GUI library works most reliably there. Linux window managers all do things differently, so window positioning and transparency get flaky.

If you're on Linux, it might work, but don't expect the same experience.

## Desktop Shortcut

Create a batch file:

```batch
@echo off
cd /d "C:\path\to\HUD-note"
python main.py
```

Save as `HUD Notes.bat` on your desktop.

## Quick Tips

- Use `Ctrl+Alt+H` to show/hide
- Open multiple notes in tabs
- Don't use preview mode yet
- Restart if tabs get weird
- Works best windowed, not fullscreen