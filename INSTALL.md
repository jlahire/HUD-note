# HUD Notes - Installation Guide

Installation instructions for Windows, Linux, and macOS.

## Requirements

- Python 3.8 or newer
- pip (Python package manager)
- tkinter (usually included with Python)

## All Platforms - Quick Install

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip install -r requirements.txt
python main.py
```

---

## Windows

### Option 1: Run directly

1. Install Python from [python.org](https://www.python.org/downloads/) (check "Add to PATH" during install)
2. Open Command Prompt or PowerShell:

```cmd
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip install -r requirements.txt
python main.py
```

### Option 2: Desktop shortcut

Create a file called `HUD Notes.bat` on your desktop:

```batch
@echo off
cd /d "C:\path\to\HUD-note"
python main.py
```

Replace `C:\path\to\HUD-note` with the actual path.

### Option 3: Git Bash global command

```bash
mkdir -p ~/bin
echo '#!/bin/bash
cd "'"$(pwd)"'"
python main.py "$@"' > ~/bin/hud-notes
chmod +x ~/bin/hud-notes

echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
source ~/.bashrc
```

Now run `HUD` from anywhere in Git Bash.

### Option 4: PowerShell alias

Add to your PowerShell profile (`notepad $PROFILE`):

```powershell
function HUD {
    Set-Location "C:\path\to\HUD-note"
    python main.py $args
}
```

### Windows troubleshooting

- **`python` not found** - Try `py main.py` instead, or re-install Python with "Add to PATH" checked
- **Hotkeys not working** - Allow Python through Windows Firewall, or try running as administrator once
- **tkinter missing** - Reinstall Python and make sure "tcl/tk" is checked in the installer

---

## Linux

### Prerequisites

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-tk

# Fedora
sudo dnf install python3 python3-pip python3-tkinter

# Arch
sudo pacman -S python python-pip tk
```

### Option 1: Run directly

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip3 install -r requirements.txt
python3 main.py
```

### Option 2: Global install with setup script

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
./setup.sh
```

The setup script checks dependencies, installs them if needed, and optionally runs the global installer (`install_hud_notes.sh`) which:
- Creates a `hud-notes` wrapper in `/usr/local/bin`
- Optionally adds a shell alias of your choice

After installation, run `hud-notes` from anywhere.

### Option 3: Manual global install

```bash
# Install to ~/tools
mkdir -p ~/tools
cp -r HUD-note ~/tools/hud-notes

# Create launcher
sudo tee /usr/local/bin/hud-notes << 'EOF'
#!/bin/bash
exec python3 ~/tools/hud-notes/main.py "$@"
EOF
sudo chmod +x /usr/local/bin/hud-notes
```

### Update an existing global install

```bash
cd HUD-note    # the source directory with latest code
./update.sh
```

This backs up your current installation, copies the new files, and logs everything to `update-YYYYMMDD.txt`.

### Linux notes

- Requires an X11 or Wayland display server (won't work in a headless terminal)
- Transparency and window positioning work on most desktop environments but may vary
- If hotkeys conflict with your DE, change them in Settings (`Ctrl+Alt+G`)

### WSL (Windows Subsystem for Linux)

WSL requires a display server to run GUI apps:

- **Windows 11 with WSLg**: Should work out of the box
- **Windows 10 or older WSL**: Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/), run it with "Disable access control" checked, then add to `~/.bashrc`:

```bash
export DISPLAY=:0.0
```

Then install normally:

```bash
sudo apt install python3 python3-pip python3-tk
pip3 install -r requirements.txt
python3 main.py
```

---

## macOS

### Prerequisites

Install Python 3 via Homebrew (recommended) or from python.org:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python (includes tkinter and pip)
brew install python3 python-tk
```

### Option 1: Run directly

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
pip3 install -r requirements.txt
python3 main.py
```

### Option 2: Global install

```bash
cd HUD-note
./setup.sh
```

Works the same as the Linux global install.

### macOS notes

- You may need to grant Accessibility permissions for global hotkeys: System Settings > Privacy & Security > Accessibility > allow Terminal (or your terminal app)
- If `python3` isn't found after Homebrew install, add it to your PATH: `export PATH="/opt/homebrew/bin:$PATH"` in `~/.zshrc`
- macOS may prompt for permissions when the app tries to monitor keyboard input (pynput). Allow it.

---

## Updating

### If you ran `setup.sh` / `install_hud_notes.sh`

```bash
cd HUD-note        # your source directory
git pull            # get latest code
./update.sh         # update the global installation
```

### If you run directly from the cloned directory

```bash
cd HUD-note
git pull
pip install -r requirements.txt    # in case dependencies changed
```

---

## Uninstalling

### Global install (Linux/macOS)

```bash
sudo rm /usr/local/bin/hud-notes
rm -rf ~/tools/hud-notes          # if you used the installer
```

Remove any aliases from your `~/.bashrc` or `~/.zshrc`.

### Direct install (all platforms)

Delete the `HUD-note` directory.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` / `python3` not found | Install Python 3.8+ and add to PATH |
| `No module named tkinter` | Linux: `sudo apt install python3-tk`. macOS: `brew install python-tk`. Windows: reinstall Python with tcl/tk checked. |
| `No module named pynput` | Run `pip install -r requirements.txt` |
| Hotkeys not working | Windows: check Firewall. macOS: grant Accessibility permissions. Linux: check for DE hotkey conflicts. |
| Can't see the overlay | Transparency may be too high - press `Ctrl+Alt+R` to reset position |
| Window stuck or invisible | Restart the app with `python main.py` |
| Overlay behind other windows | Press `Ctrl+Alt+H` twice to re-raise it |
