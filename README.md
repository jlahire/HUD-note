# HUD Notes v2.0.0 - Modular HUD Overlay System

> **🚀 Complete Architectural Overhaul** - Now with microarchitecture design and plugin-based modularity

A powerful, customizable HUD overlay note-taking system built with Python and Tkinter. Designed for real-time note-taking during activities like CTF competitions, coding sessions, research, and learning.

## ✨ What's New in v2.0.0

### 🏗️ Modular Architecture

- **Microarchitecture Design** - Every component split into single-responsibility files (50-100 lines max)
- **Plugin System** - Hot-swappable overlay modules
- **Easy Maintenance** - Debug and modify any component independently
- **LEGO-block Philosophy** - Small, independent pieces that snap together cleanly

### 🎨 Enhanced User Interface

- **Smart Tooltips** - Hover descriptions with hotkey information (toggleable)
- **Larger Buttons** - Improved usability with better sizing and spacing
- **Transparency Controls** - Dedicated α+/α- buttons with live percentage display
- **Better Cursor Management** - Fixed resize cursor sticking issues
- **DPI Awareness** - Proper scaling on high-resolution displays

### 🎭 Advanced Theme System

- **10+ Built-in Themes** - Matrix Green, Cyber Blue, Neon Purple, Hacker Orange, and more
- **Full Customization** - Create custom color schemes
- **Live Theme Switching** - Change themes without restart
- **Component Integration** - Themes apply to all UI elements

### 🪟 Improved Dialog System

- **Smart Sizing** - Dialogs adapt to content and DPI scaling
- **Better UX** - Fixed cancel loops and window management
- **Enhanced Template Selection** - Better preview and organization

## 🎯 Core Features

### 📝 Advanced Note-Taking

- **Template System** - 11 built-in templates (Meeting, CTF Writeup, Class Notes, etc.)
- **Syntax Highlighting** - Code blocks, markdown, file paths, URLs
- **Auto-Save** - Continuous saving every 2 seconds
- **Live Preview** - Markdown rendering with theme integration

### ⌨️ Powerful Hotkeys

- **Global Hotkeys** - Work system-wide (default: `Ctrl+Alt+H` to toggle)
- **Window Positioning** - `Ctrl+Alt+1-4` for corners, `Ctrl+Alt+5` for center
- **Quick Actions** - Instant access to new note, save, open, settings
- **Customizable** - Change any hotkey combination in settings

### 🖥️ Multi-Monitor Support

- **Display Detection** - Automatic multi-monitor setup
- **Smart Positioning** - Quarter-screen layouts with proper bounds
- **Display Cycling** - Move between monitors with hotkeys
- **DPI Scaling** - Consistent appearance across different displays

### 🎮 HUD Features

- **Always-on-Top** - Stays visible during any activity
- **Screen Borders** - Visual indicators for active areas
- **Hotkey Bar** - Persistent bottom display of all shortcuts
- **Auto Show/Hide** - Mouse hover and click-outside options

## 🏗️ Microarchitecture Structure

```text
hud-notes/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── core/
│   ├── __init__.py
│   ├── application.py       # Main application controller
│   └── template_manager.py  # Template system
├── features/
│   ├── __init__.py
│   ├── auto_features.py     # Auto show/hide functionality
│   ├── hotkeys.py           # Global hotkey management
│   ├── syntax_highlighting.py # Text highlighting system
│   └── window_manager.py    # Window positioning & resizing
├── ui/
│   ├── __init__.py
│   ├── components.py        # Reusable UI components
│   ├── dialogs.py          # Dialog windows
│   ├── overlay.py          # Main overlay window
│   └── themes.py           # Theme management system
├── utils/
│   ├── __init__.py
│   ├── display_utils.py    # DPI scaling & multi-monitor
│   └── file_operations.py  # File I/O operations
└── main.py                 # Application entry point
```

### Design Principles

- **Single Responsibility** - Each file handles exactly one concept
- **Minimal Coupling** - Files work independently when possible
- **Easy Testing** - Each component is unit-testable in isolation
- **Self-Documenting** - File and function names explain purpose

## 🚀 Quick Start

### Installation

**Requirements:**

- Python 3.8+
- Tkinter (usually included with Python)

**Install Dependencies:**

```bash
pip install pynput markdown2
```

**Clone and Run:**

```bash
git clone https://github.com/jlahire/HUD-note.git
cd HUD-note
python main.py
```

### First Launch

1. **Setup Dialog** - Choose notes directory, author name, and initial note title
2. **Press `Ctrl+Alt+H`** - Toggle HUD overlay visibility
3. **Create Notes** - Click ● (New Note) to select templates
4. **Customize** - Click ⚙ (Settings) to change themes and preferences

## 🎨 Built-in Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| **Matrix Green** | Classic Matrix-style green on black | General use, coding |
| **Cyber Blue** | Cyberpunk blue with electric accents | Futuristic aesthetic |
| **Neon Purple** | Vibrant purple with yellow highlights | Creative work |
| **Hacker Orange** | Orange and green hacker style | Security/CTF work |
| **Terminal White** | High contrast white on black | Readability |
| **Blood Red** | Dark red with blood-like accents | Dark themes |
| **Stealth Gray** | Professional gray theme | Work environments |
| **Retro Amber** | Classic amber terminal style | Retro computing |
| **Electric Pink** | Vibrant pink with cyan accents | Bold aesthetic |
| **Deep Ocean** | Blue ocean depths theme | Calming, focused work |

## ⌨️ Default Hotkeys

| Action | Hotkey | Description |
|--------|---------|-------------|
| **Toggle HUD** | `Ctrl+Alt+H` | Show/hide overlay |
| **New Note** | `Ctrl+Alt+N` | Create note with template |
| **Open Note** | `Ctrl+Alt+O` | Open existing note |
| **Save Note** | `Ctrl+Alt+S` | Save current note |
| **Save As** | `Ctrl+Alt+Shift+S` | Save with new name |
| **Code Input** | `Ctrl+Alt+C` | Insert code block |
| **Preview** | `Ctrl+Alt+P` | Toggle markdown preview |
| **Settings** | `Ctrl+Alt+G` | Open settings dialog |
| **Font Size** | `Ctrl+Alt+±` | Increase/decrease font |
| **Transparency** | `Alt+±` | Adjust window opacity |
| **Corners** | `Ctrl+Alt+1-4` | Move to screen corners |
| **Center** | `Ctrl+Alt+5` | Center window |
| **Reset Position** | `Ctrl+Alt+R` | Reset to quarter screen |
| **Hide** | `Esc` | Hide overlay |
| **Quit** | `Ctrl+Alt+Q` | Exit application |

## 📋 Template System

### Built-in Templates

- **Basic** - Simple note with title, author, date
- **Meeting** - Meeting notes with attendees and action items
- **Daily Log** - Daily planning and reflection
- **Code Review** - Code review checklist
- **CTF Writeup** - Capture The Flag documentation
- **Class Notes** - Academic note-taking
- **Study Session** - Study planning and progress
- **Project Planning** - Project management
- **Bug Report** - Bug tracking workflow
- **PowerShell Script** - Windows PowerShell documentation
- **Batch Script** - Windows batch file documentation

### Custom Templates

Add `.md` files to your `templates/` directory with placeholders:
- `{title}` - Note title
- `{author}` - Author name  
- `{date}` - Current date/time

## ⚙️ Configuration Options

### General Settings

- **Notes Directory** - Where to store your notes
- **Author Name** - Default author for templates
- **Font Size** - Text editor font size (8-24)
- **Auto-Save Interval** - How often to save (1-10 seconds)

### Appearance

- **Color Schemes** - Choose from 10+ built-in themes or create custom
- **Transparency** - Window opacity (30-100%)
- **Screen Borders** - Visual HUD indicators
- **Hotkey Display** - Bottom screen hotkey reference

### Advanced Features

- **Mouse Hover Show** - Show overlay when hovering top-left corner
- **Click Outside Hide** - Hide overlay when clicking outside
- **Show Tooltips** - Toggle button hover descriptions
- **Syntax Highlighting** - Code and markdown highlighting

### Hotkey Customization

- **Custom Combinations** - Set any key combination
- **Conflict Detection** - Avoid system hotkey conflicts
- **Reset Options** - Restore defaults for any hotkey

## 🪟 Windows Integration

### Git Bash Setup

```bash
# Create launcher
mkdir -p ~/bin
cp main.py ~/bin/hud-notes
chmod +x ~/bin/hud-notes
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
echo 'alias HUD="hud-notes"' >> ~/.bashrc
```

### PowerShell Setup

```powershell
function HUD { python main.py $args }
```

### WSL Support
- **X11 Forwarding** - Use with VcXsrv or WSLg
- **Kali Integration** - Special aliases for CTF work
- **Template Integration** - Security-focused templates

## 🛠️ Development & Customization

### Adding New Themes

```python
# In ui/themes.py, add to ThemeManager._initialize_built_in_themes()
self.themes['Your Theme'] = Theme(
    name='Your Theme',
    colors={
        'bg_color': '#your_bg',
        'fg_color': '#your_fg',
        'accent_color': '#your_accent',
        # ... more colors
    },
    description='Your theme description'
)
```

### Creating Plugin Modules

Follow the microarchitecture principles:
- **One class per file** - Maximum 50-100 lines
- **Single responsibility** - Each file handles one concept
- **Minimal imports** - Reduce dependencies
- **Clear naming** - File names indicate exact purpose

### Custom Hotkey Actions

```python
# In features/hotkeys.py, add to hotkey_actions dictionary
'your_action': your_function,
```

## 🐛 Troubleshooting

### Common Issues

- **Hotkeys not working** - Check Windows Firewall, allow Python
- **Display scaling issues** - Application auto-detects DPI, try reset position
- **Template errors** - Ensure proper `{placeholder}` format
- **Performance** - Disable syntax highlighting for large files

### Debug Mode

```bash
python main.py  # Includes debug output and error tracking
```

### Reset Configuration

Delete `.note_config.json` in your notes directory to restore defaults.

## 📈 Version History

### v2.0.0 (Current)

- Complete modular architecture redesign
- Enhanced UI with tooltips and themes
- Improved dialog system and DPI scaling
- Plugin-based overlay system

### v1.0.3 (Legacy)

- Initial monolithic implementation
- Basic note-taking functionality
- Simple theme support

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow microarchitecture principles
4. Add comprehensive tooltips to new UI elements
5. Test with multiple themes and DPI settings
6. Submit pull request

### Code Style

- **Microarchitecture** - Keep files small and focused
- **Type hints** - Use Python type annotations
- **Docstrings** - Document all classes and methods
- **Error handling** - Graceful degradation for all features

## 📄 License

AGPL-3.0 License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and Tkinter for cross-platform compatibility
- Inspired by gaming HUD overlays and developer productivity tools
- Designed for CTF competitors, developers, students, and researchers

---

**🎯 Perfect for:** CTF competitions, coding sessions, research notes, meeting minutes, study guides, project planning, and any scenario requiring persistent, always-accessible note-taking.

**💡 Pro Tip:** Use `Ctrl+Alt+H` to quickly toggle the overlay during any activity. Create custom templates for your specific workflows and use the theme system to match your environment.