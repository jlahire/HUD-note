# Changelog

All notable changes to HUD Notes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Automated testing framework
- Plugin system for extensions
- Cloud sync capabilities
- Export to various formats (PDF, HTML)
- Theme customization system
- Multi-language support

## [1.1.0] - 2025-01-XX

### Added - Windows Integration & Enhanced Templates
- **Windows Installation Guide**: Comprehensive `WINDOWS_INSTALLATION.md` with multiple setup methods
- **Git Bash Integration**: Step-by-step global command setup for Git Bash users
- **PowerShell Support**: Profile-based integration with custom functions and aliases
- **WSL/WSLg Integration**: Full Linux subsystem support with GUI compatibility
- **Kali Linux Integration**: Security-focused setup with CTF workflow integration
- **Desktop Integration**: Start Menu shortcuts and desktop launcher creation
- **New Templates**:
  - PowerShell Script documentation template
  - Windows Batch Script documentation template
- **Enhanced Documentation**: 
  - Windows-specific troubleshooting guide
  - Platform-specific installation methods
  - Cross-platform compatibility notes

### Improved
- **Template System**: Better organization and hot-reloading
- **Multi-Shell Support**: Git Bash, PowerShell, WSL, Command Prompt compatibility
- **Error Handling**: Windows-specific error resolution
- **Documentation Structure**: Clearer separation of platform-specific guides
- **Project Organization**: Enhanced file structure for better maintainability

### Fixed
- **Windows Firewall**: Added troubleshooting for hotkey blocking issues
- **Path Handling**: Better cross-platform path resolution
- **Dependencies**: Clearer Windows dependency installation instructions

### Security
- **Windows Integration**: Secure launcher creation and PATH management
- **Permission Handling**: Proper file permissions for cross-platform compatibility

## [1.0.0] - 2025-01-XX

### Added - Initial Production Release
- **Core HUD Interface**:
  - HUD-style overlay interface with transparency controls
  - Multi-display support with automatic detection and positioning
  - DPI-aware scaling for high-resolution displays
  - Always-visible screen borders with hotkey display bar
  
- **Note-Taking Features**:
  - Rich text editor with syntax highlighting
  - Auto-save functionality with configurable intervals
  - Markdown preview pane with live updates
  - Right-click context menu with undo/redo support
  - Font size controls and window positioning shortcuts

- **Template System**:
  - Customizable note templates with variable substitution
  - Template hot-reloading without restart
  - Template directory organization (`templates/` folder)
  - Built-in templates (9 initial templates):
    - Basic note template
    - Meeting notes with agenda and action items
    - Daily log for planning and reflection
    - Code review checklist and workflow
    - CTF writeup for security challenges
    - Class notes for academic use
    - Study session planning and tracking
    - Project planning with timelines
    - Bug report tracking and resolution

- **Global Hotkey System**:
  - `Ctrl+Alt+T` to toggle HUD overlay
  - Complete hotkey set for all major functions
  - Code input window with 25+ programming languages
  - Window positioning shortcuts (corners, center)
  - Multi-display navigation hotkeys

- **Cross-Platform Installation**:
  - Automated setup scripts for Linux/Unix systems
  - Global installation with custom alias support
  - One-click dependency checking and installation
  - Clean uninstall with configuration backup
  - Desktop launcher creation

- **Advanced Features**:
  - Drag-and-drop window positioning
  - Multi-display awareness and positioning
  - Configuration management with JSON storage
  - Template variable system (`{title}`, `{author}`, `{date}`)
  - Enhanced syntax highlighting for code, markdown, and file paths

### Technical Implementation
- **Pure Python**: Single-file application using tkinter
- **Minimal Dependencies**: Only `pynput` and `markdown2` required
- **Memory Efficient**: Lightweight overlay with optimized rendering
- **Error Resilient**: Graceful degradation and comprehensive error handling
- **Configuration System**: JSON-based settings with auto-migration

### Documentation & Development
- **Comprehensive Documentation**:
  - Detailed README with setup instructions
  - Contributing guidelines for developers
  - Template development guide
  - Troubleshooting and FAQ sections
  
- **Development Infrastructure**:
  - GitHub Actions CI/CD pipeline
  - Automated testing and validation
  - Code formatting and linting standards
  - Issue templates for bugs and features
  - Makefile for development automation

- **Project Organization**:
  - Professional file structure
  - Template directory separation
  - Clear documentation hierarchy
  - Version control best practices

### Platform Support
- **Linux**: Full support with automated installation
- **Windows**: Multi-shell support (Git Bash, PowerShell, WSL)
- **macOS**: Basic support with manual installation

## Development History

### v0.4.0 - Windows Integration
- Added comprehensive Windows support
- Multi-shell installation methods
- WSL and desktop integration
- Platform-specific templates

### v0.3.0 - Enhanced Features
- Template system implementation
- Improved syntax highlighting
- Multi-display support enhancement
- Better error handling and user experience

### v0.2.0 - Core Functionality  
- HUD overlay implementation
- Basic note-taking features
- Global hotkey system
- Auto-save functionality

### v0.1.0 - Initial Concept
- Basic tkinter interface
- Simple note editing capabilities
- File operations (open, save, new)
- Foundation architecture

---

## Version Numbering

- **Major version** (X.0.0): Breaking changes, major architectural updates, or significant feature overhauls
- **Minor version** (0.X.0): New features, platform support, template additions, backwards compatible
- **Patch version** (0.0.X): Bug fixes, minor improvements, documentation updates

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this changelog and the project.

## Release Notes

### What's New in v1.1.0
Windows users can now enjoy full HUD Notes integration across all major Windows environments. Whether you're using Git Bash, PowerShell, WSL, or Kali Linux, HUD Notes adapts to your workflow with native installation methods and desktop integration.

### What's New in v1.0.0
The first production release brings a complete HUD-style note-taking experience with professional-grade features including multi-display support, customizable templates, global hotkeys, and cross-platform installation scripts. Perfect for developers, students, and security professionals.