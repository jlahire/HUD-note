# Windows Installation Guide - HUD Notes v2.0.0

This guide covers Windows-specific installation methods for HUD Notes v2.0.0, including Git Bash, PowerShell, and WSL integration.

## 🪟 Windows Shell Integration

### Quick Installation (Recommended)

**1. Clone Repository**

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
```

**2. Install Dependencies**

```bash
pip install pynput markdown2
```

**3. Run HUD Notes**

```bash
python main.py
```

### For Git Bash Users

HUD Notes can be made globally accessible via a custom launcher and alias setup in Git Bash.

#### 🔧 Step-by-Step Integration (Git Bash)

**1. Create Directories**

```bash
mkdir -p ~/bin ~/tools
```

**2. Copy HUD Notes to Tools**

```bash
# From the HUD-note repository directory
cp -r . ~/tools/hud-notes
```

**3. Create Global Launcher**

```bash
cat > ~/bin/hud-notes << 'EOF'
#!/bin/bash
cd "$HOME/tools/hud-notes"
python main.py "$@"
EOF
chmod +x ~/bin/hud-notes
```

**4. Update .bashrc**

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
echo 'alias notes="hud-notes"' >> ~/.bashrc
source ~/.bashrc
```

**5. Test Installation**

```bash
which hud-notes
HUD  # Should launch HUD Notes
```

### For PowerShell Users

#### Using PowerShell Profile

**1. Create Tools Directory**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\tools"
```

**2. Copy HUD Notes**

```powershell
# From the HUD-note repository directory
Copy-Item -Recurse . "$env:USERPROFILE\tools\hud-notes"
```

**3. Create PowerShell Functions**

```powershell
# Open profile for editing
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
notepad $PROFILE

# Add these functions to the profile:
function HUD {
    Set-Location "$env:USERPROFILE\tools\hud-notes"
    python main.py $args
}

function hud-notes {
    Set-Location "$env:USERPROFILE\tools\hud-notes"
    python main.py $args
}
```

**4. Reload Profile**

```powershell
. $PROFILE
```

## 🐧 WSL Integration

### Ubuntu/Debian WSL

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
```

**3. Configure X11 Forwarding**
For GUI support in WSL, install an X server like VcXsrv:

Add to your `~/.bashrc`:

```bash
export DISPLAY=:0.0
export LIBGL_ALWAYS_INDIRECT=1
```

**4. Create WSL Alias**

```bash
echo 'alias hud="cd ~/HUD-note && python3 main.py"' >> ~/.bashrc
echo 'alias notes="hud"' >> ~/.bashrc
source ~/.bashrc
```

### Kali Linux WSL

**1. Install Dependencies**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
pip3 install pynput markdown2
```

**2. Setup HUD Notes**

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
```

**3. Kali-Specific Alias Setup**
Add to `~/.zshrc` (Kali uses zsh by default):

```bash
echo 'alias hud="cd ~/HUD-note && python3 main.py"' >> ~/.zshrc
echo 'alias notes="hud"' >> ~/.zshrc
echo 'alias ctf-notes="hud"' >> ~/.zshrc
source ~/.zshrc
```

**4. CTF-Specific Integration**

```bash
# Create CTF workspace
mkdir -p ~/ctf-notes

# Quick CTF note function
echo 'ctf-note() { cd ~/HUD-note && python3 main.py --dir ~/ctf-notes --title "CTF-$(date +%Y%m%d)-$1"; }' >> ~/.zshrc
```

### WSL GUI Requirements

#### Option 1: VcXsrv (Windows 10/11)

1. Download VcXsrv: https://sourceforge.net/projects/vcxsrv/
2. Start XLaunch with settings:
   - Multiple windows
   - Display number: 0
   - Disable access control: ✓
   - Additional parameters: `-ac -multiwindow`

#### Option 2: WSLg (Windows 11)

```bash
# Windows 11 has built-in GUI support
echo $DISPLAY  # Should show something like :0
# If empty, try: export DISPLAY=:0
```

## 🚀 Advanced Windows Integration

### Desktop Shortcut

**Create Desktop Shortcut (PowerShell):**

```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\HUD Notes.lnk")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = "main.py"
$Shortcut.WorkingDirectory = "$env:USERPROFILE\tools\hud-notes"
$Shortcut.IconLocation = "python.exe,0"
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Description = "HUD Notes v2.0.0 - Modular Note-Taking System"
$Shortcut.Save()
```

### Start Menu Integration

```powershell
$StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$StartMenu\HUD Notes.lnk")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = "$env:USERPROFILE\tools\hud-notes\main.py"
$Shortcut.WorkingDirectory = "$env:USERPROFILE\tools\hud-notes"
$Shortcut.Save()
```

### Windows Terminal Integration

Add to Windows Terminal settings.json:

```json
{
    "name": "HUD Notes",
    "commandline": "python \"%USERPROFILE%\\tools\\hud-notes\\main.py\"",
    "startingDirectory": "%USERPROFILE%\\tools\\hud-notes",
    "icon": "🗒️"
}
```

## 🛠️ Troubleshooting Windows Issues

### Python Path Issues

**Git Bash:**

```bash
# Add Python to PATH in .bashrc
echo 'export PATH="/c/Python311:/c/Python311/Scripts:$PATH"' >> ~/.bashrc
# Adjust Python311 to your Python version
source ~/.bashrc
```

**PowerShell:**

```powershell
# Check Python installation
python --version
Get-Command python
```

### Permission Issues

```bash
# Fix permissions for Git Bash
chmod +x ~/bin/hud-notes
find ~/tools/hud-notes -name "*.py" -exec chmod +x {} \;
```

### Global Hotkeys Not Working

**Windows Firewall:**

1. Open Windows Defender Firewall
2. Click "Allow an app or feature"
3. Add Python (python.exe) to exceptions
4. Allow both Private and Public networks

**Alternative Hotkey:**

If `Ctrl+Alt+H` conflicts with other software:

1. Open HUD Notes Settings (⚙)
2. Go to Hotkeys tab
3. Change "Toggle HUD Overlay" to different combination
4. Apply & Close

### Display Issues in WSL

**Test X11 Setup:**

```bash
# Test basic X11
xclock &

# If that works, test Tkinter
python3 -c "import tkinter; tkinter.Tk().mainloop()"
```

**Fix Display Variable:**

```bash
# In WSL, add to ~/.bashrc
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

### Dependencies Missing

**Windows Native:**

```bash
pip install --user pynput markdown2
```

**Conda Environment:**

```bash
conda create -n hudnotes python=3.11
conda activate hudnotes
conda install pip
pip install pynput markdown2
```

## 📝 Windows-Specific Templates

The v2.0.0 template system includes Windows-specific templates:

### PowerShell Script Template

- Parameter documentation
- Usage examples
- Error handling patterns
- Windows-specific comments

### Batch File Template  

- Classic batch syntax
- Environment variable usage
- Error checking
- DOS-style documentation

### Windows Development Template

- Visual Studio integration
- .NET project structure
- Windows API references
- Registry modification notes

## 🎯 Platform-Specific Tips

### Git Bash Best Practices

- Use forward slashes in paths: `~/tools/hud-notes`
- Python commands work best with `python` or `python3`
- Use `~/` for home directory references
- MINGW64 environment provides best compatibility

### PowerShell Best Practices

- Use backslashes in Windows paths: `$env:USERPROFILE\tools`
- PowerShell functions preferred over aliases
- Use `$env:USERPROFILE` for user directory
- Execution policy may need adjustment: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### WSL Best Practices

- GUI apps require X server or WSLg (Windows 11)
- Use Linux paths within WSL: `/home/user/`
- Windows drives accessible via `/mnt/c/`
- Test X11 forwarding before running GUI apps

## 🎮 Gaming & CTF Integration

### For Gaming Sessions

```bash
# Quick gaming notes setup
alias game-notes='hud-notes --title "Gaming-$(date +%Y%m%d)" --theme "Matrix Green"'
```

### For CTF Competitions

```bash
# CTF-specific setup with security themes
alias ctf='hud-notes --title "CTF-$(date +%Y%m%d)" --theme "Hacker Orange" --template "ctf_writeup"'
```

### For Development Work

```bash
# Development environment
alias dev-notes='hud-notes --title "Dev-$(date +%Y%m%d)" --theme "Cyber Blue" --template "code_review"'
```

## 🔧 Advanced Configuration

### Custom Theme Creation

1. Open Settings (⚙) → Colors & Theme
2. Select "Custom" color scheme
3. Use color picker or hex values
4. Apply and save

### Hotkey Optimization

- **Gaming**: Use `F12` or `Insert` for easy access
- **Development**: Keep `Ctrl+Alt+H` for muscle memory
- **CTF**: Consider `Ctrl+Shift+N` for quick notes

### Multi-Monitor Setup

- HUD Notes auto-detects all displays
- Use `Ctrl+Alt+M` to cycle between monitors
- Each display remembers its layout preferences

This Windows integration makes HUD Notes seamlessly blend into any Windows workflow, whether you're using native PowerShell, Git Bash, or WSL environments.