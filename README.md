# HUD Notes

A lightweight, HUD-style overlay note-taking application with multi-display support, syntax highlighting, and customizable templates.

![HUD Notes Demo](screenshots/hud_notes_demo.gif)

## Features

- 🎯 **HUD-Style Overlay**: Always-on-top transparent interface
- 🖥️ **Multi-Display Support**: Automatically adapts to your display setup
- 📝 **Template System**: Customizable note templates for different use cases
- 🎨 **Syntax Highlighting**: Enhanced code and markdown syntax highlighting
- ⌨️ **Global Hotkeys**: Quick access with Ctrl+Alt+T
- 💾 **Auto-Save**: Automatic saving with configurable intervals
- 🎛️ **Customizable**: Adjustable transparency, font size, and positioning
- 📱 **DPI Aware**: Automatically scales for high-DPI displays

## Quick Start

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)
- Required packages (auto-installed during setup)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/hud-notes.git
   cd hud-notes
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Follow the installer prompts:**
   ```bash
   ./install_hud_notes.sh
   ```

4. **Start using HUD Notes:**
   ```bash
   hud-notes
   # or use your custom alias
   ```

### Windows Installation

For Windows users with Git Bash, PowerShell, or WSL:

#### Quick Setup (Git Bash)
```bash
# Create directories
mkdir -p ~/bin ~/tools

# Copy HUD Notes
cp hud_notes.py ~/tools/hud-notes

# Create launcher
echo '#!/bin/bash
exec python3 "$HOME/tools/hud-notes" "$@"' > ~/bin/hud-notes
chmod +x ~/bin/hud-notes

# Add to PATH and create alias
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
source ~/.bashrc
```

#### WSL/Kali Integration
```bash
# Install dependencies
sudo apt install python3 python3-pip python3-tk
pip3 install pynput markdown2

# Clone and setup
git clone https://github.com/yourusername/hud-notes.git
cd hud-notes
./setup.sh
```

**For comprehensive Windows setup including PowerShell, WSL, and desktop integration, see [WINDOWS_INSTALLATION.md](WINDOWS_INSTALLATION.md)**

### Manual Installation

If you prefer to install manually:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Make the script executable
chmod +x hud_notes.py

# Run directly
python3 hud_notes.py
```

## Usage

### First Run

On first run, you'll see a setup dialog where you can configure:

- **Notes Directory**: Where your notes will be stored
- **Author Name**: Your name for note templates
- **Initial Note Title**: Title for your first note
- **Template**: Choose from available templates

### Global Hotkeys

| Hotkey | Action |
|--------|--------|
| `Ctrl+Alt+T` | Toggle HUD overlay |
| `Ctrl+Alt+N` | New note |
| `Ctrl+Alt+O` | Open note |
| `Ctrl+Alt+S` | Save note |
| `Ctrl+Alt+C` | Code input window |
| `Ctrl+Alt+P` | Toggle preview |
| `Ctrl+Alt+M` | Move to next display |
| `Ctrl+Alt+R` | Reset to quarter screen |
| `Ctrl+Alt+1-4` | Move to corners |
| `Ctrl+Alt+5` | Center window |
| `Ctrl+Alt+Q` | Quit application |
| `Esc` | Hide overlay |

### Interface Controls

- **A-/A+**: Font size adjustment
- **</>**: Code input window
- **●**: New note
- **▲**: Open note
- **■**: Save note
- **◊**: Toggle preview
- **↻**: Reset window
- **✕**: Hide overlay
- **α: -/+**: Transparency controls

## Templates

HUD Notes supports customizable templates stored in the `templates/` directory. Templates use Python string formatting with these variables:

- `{title}`: Note title
- `{author}`: Author name
- `{date}`: Current date and time

### Built-in Templates

- **Basic**: Simple note template
- **Meeting**: Meeting notes with agenda and action items
- **Daily Log**: Daily planning and reflection
- **Code Review**: Code review checklist and comments
- **CTF Writeup**: Capture The Flag challenge documentation
- **Class Notes**: Academic note-taking with structured sections
- **Study Session**: Study planning and progress tracking
- **Project Planning**: Project management with timelines and resources
- **Bug Report**: Bug tracking and resolution workflow
- **PowerShell Script**: Windows PowerShell script documentation
- **Batch Script**: Windows batch file documentation

### Creating Custom Templates

1. Create a new `.md` file in the `templates/` directory
2. Use the formatting variables (`{title}`, `{author}`, `{date}`)
3. Restart HUD Notes to see your new template

Example template (`templates/my_template.md`):
```markdown
# {title}

**Author:** {author}
**Date:** {date}
**Project:** 

---

## Objective

## Notes

## Next Steps
- [ ] 
```

## Configuration

Configuration is stored in `.note_config.json` in your notes directory:

```json
{
  "window_width": 400,
  "window_height": 600,
  "window_x": 1520,
  "window_y": 0,
  "font_size": 10,
  "hud_transparency": 0.85,
  "auto_scale": true,
  "syntax_highlighting": true,
  "auto_save_interval": 2000
}
```

## File Structure

```
hud-notes/
├── README.md
├── requirements.txt
├── hud_notes.py              # Main application
├── setup.sh                  # One-click setup
├── install_hud_notes.sh      # Global installer
├── uninstall_hud_notes.sh    # Uninstaller
├── templates/                # Note templates
│   ├── basic.md
│   ├── meeting.md
│   ├── daily_log.md
│   ├── code_review.md
│   └── ctf_writeup.md
└── screenshots/              # Documentation images
```

## Development

### Requirements

See `requirements.txt` for all dependencies:

- `pynput`: Global hotkey support
- `markdown2`: Markdown processing
- `tkinter`: GUI framework (usually bundled with Python)

### Building from Source

```bash
git clone https://github.com/yourusername/hud-notes.git
cd hud-notes
pip3 install -r requirements.txt
python3 hud_notes.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Platform Support

- **Linux**: Full support with automated installation scripts
- **Windows**: Full support via multiple methods:
  - Git Bash integration with global commands
  - PowerShell profile integration
  - WSL/WSLg support with GUI
  - Desktop and Start Menu shortcuts
- **macOS**: Basic support (manual installation recommended)

## Troubleshooting

### Common Issues

**HUD Notes won't start:**
- Check Python 3.7+ is installed
- Install missing dependencies: `pip3 install -r requirements.txt`
- Check file permissions: `chmod +x hud_notes.py`

**Global hotkey not working:**
- Ensure `pynput` is installed
- Check for conflicting hotkey assignments
- Try running as administrator (Windows) or with proper permissions (Linux)
- On Windows: Allow Python through Windows Firewall

**Window positioning issues:**
- Use `Ctrl+Alt+R` to reset window position
- Check display scaling settings
- Verify multi-monitor setup

**Templates not loading:**
- Check templates directory exists and contains `.md` files
- Verify file permissions
- Restart HUD Notes after adding new templates

**Windows-specific issues:**
- See [WINDOWS_INSTALLATION.md](WINDOWS_INSTALLATION.md) for detailed troubleshooting
- WSL users: Ensure X server is running for GUI support
- Git Bash: Check Python is in PATH

### Debug Mode

Run with debug output:
```bash
python3 hud_notes.py --debug
```

## Uninstalling

To completely remove HUD Notes:

```bash
./uninstall_hud_notes.sh
```

This will:
- Remove the global executable
- Clean up shell aliases
- Optionally remove configuration files
- Preserve your notes directory

## License

AGPL-3.0 License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and tkinter
- Inspired by HUD interfaces and overlay applications
- Thanks to the open-source community for the dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have feature requests, please open an issue on GitHub.

---

**Made with ❤️ for efficient note-taking**
