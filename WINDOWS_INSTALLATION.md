# Windows Installation Guide

This guide covers Windows-specific installation methods for HUD Notes, including Git Bash and WSL integration.

## 🪟 Windows Shell Integration

### For Git Bash Users

HUD Notes can be made globally accessible via a custom launcher and alias setup in Git Bash.

#### 🔧 Step-by-Step Integration (Git Bash)

**1. Create Directories**
Ensure user-level directories exist:
```bash
mkdir -p ~/bin ~/tools
```

**2. Copy the Python Script**
Copy `hud_notes.py` into your `~/tools` directory:
```bash
cp path/to/hud_notes.py ~/tools/hud-notes
```
💡 *Note: Rename if needed depending on usage (with or without .py extension)*

**3. Create the Launcher Stub**
Create a shell wrapper in `~/bin/hud-notes`:
```bash
echo '#!/bin/bash
exec python3 "$HOME/tools/hud-notes" "$@"' > ~/bin/hud-notes
chmod +x ~/bin/hud-notes
```

**4. Update .bashrc**
Add your alias and PATH update to `.bashrc`:
```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
source ~/.bashrc
```

**5. Confirm Installation**
Verify everything is set up:
```bash
which hud-notes
HUD --help
```

✅ After these steps, you'll be able to launch HUD Notes globally using `HUD` or `hud-notes` from any Git Bash window.

### For PowerShell Users

#### Using PowerShell Profile

**1. Create Tools Directory**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\tools"
```

**2. Copy HUD Notes**
```powershell
Copy-Item "path\to\hud_notes.py" "$env:USERPROFILE\tools\hud-notes.py"
```

**3. Create PowerShell Function**
Add to your PowerShell profile (`$PROFILE`):
```powershell
# Open profile for editing
notepad $PROFILE

# Add this function to the profile:
function HUD {
    python3 "$env:USERPROFILE\tools\hud-notes.py" $args
}

function hud-notes {
    python3 "$env:USERPROFILE\tools\hud-notes.py" $args
}
```

**4. Reload Profile**
```powershell
. $PROFILE
```

## 🐧 WSL Integration

### For WSL (Windows Subsystem for Linux)

#### Ubuntu/Debian WSL

**1. Install Dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
pip3 install pynput markdown2
```

**2. Clone and Setup**
```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
./setup.sh
./install_hud_notes.sh
```

**3. Configure X11 Forwarding**
For GUI support in WSL, install an X server like VcXsrv or Xming:

Add to your `~/.bashrc`:
```bash
export DISPLAY=:0.0
export LIBGL_ALWAYS_INDIRECT=1
```

#### Kali Linux WSL

**1. Install Dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
pip3 install pynput markdown2
```

**2. Setup HUD Notes**
```bash
git clone https://github.com/yourusername/hud-notes.git
cd hud-notes
chmod +x *.sh
./setup.sh
```

**3. Kali-Specific Alias Setup**
Add to `~/.zshrc` (Kali uses zsh by default):
```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
echo 'alias hud="hud-notes"' >> ~/.zshrc
echo 'alias notes="hud-notes"' >> ~/.zshrc
source ~/.zshrc
```

**4. Security Tools Integration**
For CTF and security work, you can create specialized templates:
```bash
# Copy CTF template to a quick-access location
cp templates/ctf_writeup.md ~/ctf-template.md

# Create quick CTF note alias
echo 'alias ctf-note="hud-notes ~/ctf-notes/$(date +%Y%m%d)-\$1.md"' >> ~/.zshrc
```

### WSL GUI Requirements

#### Option 1: VcXsrv (Recommended)
1. Download and install VcXsrv from: https://sourceforge.net/projects/vcxsrv/
2. Start XLaunch with these settings:
   - Multiple windows
   - Display number: 0
   - Disable access control: ✓

#### Option 2: Windows 11 WSLg
If you're on Windows 11, WSLg provides built-in GUI support:
```bash
# No additional setup needed for Windows 11 WSL
echo $DISPLAY  # Should show something like :0
```

## 🚀 Windows-Specific Features

### Desktop Integration

**Create Desktop Shortcut (Git Bash)**
```bash
cat > ~/Desktop/HUD\ Notes.lnk << 'EOF'
[InternetShortcut]
URL=file:///C:/Program%20Files/Git/git-bash.exe
IconFile=C:\Program Files\Git\mingw64\share\git\git-for-windows.ico
IconIndex=0
HotKey=0
IDList=
[{000214A0-0000-0000-C000-000000000046}]
Prop3=19,0
EOF
```

**Start Menu Integration (PowerShell)**
```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\HUD Notes.lnk")
$Shortcut.TargetPath = "python3"
$Shortcut.Arguments = "$env:USERPROFILE\tools\hud-notes.py"
$Shortcut.WorkingDirectory = "$env:USERPROFILE\tools"
$Shortcut.IconLocation = "python.exe,0"
$Shortcut.Save()
```

## 🛠️ Troubleshooting Windows Issues

### Common Problems

**Python not found in Git Bash:**
```bash
# Add Python to PATH in .bashrc
echo 'export PATH="/c/Python39:/c/Python39/Scripts:$PATH"' >> ~/.bashrc
# Adjust path based on your Python installation
```

**Permission errors:**
```bash
# Fix permissions for Git Bash
chmod +x ~/bin/hud-notes
chmod +x ~/tools/hud-notes
```

**Display issues in WSL:**
```bash
# Test X11 forwarding
xclock &
# If this doesn't work, check your X server setup
```

**Dependencies missing:**
```bash
# Install with pip user flag
pip3 install --user pynput markdown2

# Or use conda if you have it
conda install pynput markdown2
```

### Windows Firewall

If global hotkeys don't work, you may need to allow Python through Windows Firewall:
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Add Python (python.exe) to the exceptions

## 📝 Windows-Specific Templates

### PowerShell Script Template
Create `templates/powershell_script.md`:
```markdown
# {title}

**Author:** {author}
**Date:** {date}
**Script Type:** PowerShell
**Execution Policy:** 

---

## Purpose


## Parameters

```powershell
param(
    [string]$Parameter1,
    [switch]$Verbose
)
```

## Script

```powershell
# PowerShell script content

```

## Usage Examples

```powershell
.\script.ps1 -Parameter1 "value" -Verbose
```

## Notes


---
**Tags:** #powershell #windows #script
```

### Batch File Template
Create `templates/batch_script.md`:
```markdown
# {title}

**Author:** {author}
**Date:** {date}
**Script Type:** Batch File

---

## Purpose


## Script

```batch
@echo off
REM Batch script content

```

## Usage

```cmd
script.bat
```

## Notes


---
**Tags:** #batch #windows #cmd
```

## 🎯 Platform-Specific Tips

### Git Bash
- Use forward slashes in paths
- Python commands work best with `python3`
- Use `~/` for home directory references

### PowerShell
- Use backslashes in Windows paths
- PowerShell functions are preferred over aliases
- Use `$env:USERPROFILE` for user directory

### WSL
- GUI apps require X server or WSLg
- Use Linux paths within WSL
- Windows drives accessible via `/mnt/c/`

This integration allows Windows users to seamlessly use HUD Notes regardless of their preferred shell environment.
