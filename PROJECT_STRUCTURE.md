# HUD Notes - Project Structure

This document outlines the complete file structure and organization of the HUD Notes project.

## 📁 Root Directory

```
hud-notes/
├── 📄 hud_notes.py              # Main application file
├── 📄 requirements.txt          # Python dependencies
├── 📄 setup.sh                  # One-click setup script
├── 📄 install_hud_notes.sh      # Global installation script
├── 📄 uninstall_hud_notes.sh    # Uninstallation script
├── 📄 Makefile                  # Development automation
├── 📄 .gitignore                # Git ignore rules
├── 📄 LICENSE                   # MIT License
├── 📄 README.md                 # Main documentation
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 CHANGELOG.md              # Version history
├── 📄 PROJECT_STRUCTURE.md      # This file
├── 📄 WINDOWS_INSTALLATION.md   # Windows-specific setup guide
├── 📁 templates/                # Note templates directory
├── 📁 .github/                  # GitHub configuration
└── 📁 screenshots/              # Documentation images (optional)
```

## 📁 Templates Directory

```
templates/
├── 📄 basic.md                  # Simple note template
├── 📄 meeting.md                # Meeting notes template
├── 📄 daily_log.md              # Daily planning template
├── 📄 code_review.md            # Code review template
├── 📄 ctf_writeup.md            # CTF challenge template
├── 📄 class_notes.md            # Academic notes template
├── 📄 study_session.md          # Study planning template
├── 📄 project_planning.md       # Project management template
├── 📄 bug_report.md             # Bug tracking template
├── 📄 powershell_script.md      # PowerShell script template
└── 📄 batch_script.md           # Windows batch script template
```

## 📁 GitHub Configuration

```
.github/
├── 📁 workflows/
│   └── 📄 ci.yml                # Continuous Integration
└── 📁 ISSUE_TEMPLATE/
    ├── 📄 bug_report.md         # Bug report template
    └── 📄 feature_request.md    # Feature request template
```

## 🔧 File Purposes

### Core Application

| File | Purpose | Language |
|------|---------|----------|
| `hud_notes.py` | Main application with all functionality | Python |
| `requirements.txt` | Python package dependencies | Text |

### Installation & Setup

| File | Purpose | Language |
|------|---------|----------|
| `setup.sh` | One-click setup and dependency check | Bash |
| `install_hud_notes.sh` | Global installation with alias creation | Bash |
| `uninstall_hud_notes.sh` | Clean removal of installation | Bash |

### Development

| File | Purpose | Language |
|------|---------|----------|
| `Makefile` | Development task automation | Make |
| `.gitignore` | Git ignore patterns | Text |
| `.github/workflows/ci.yml` | GitHub Actions CI/CD | YAML |

### Documentation

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Main project documentation | Markdown |
| `CONTRIBUTING.md` | Contribution guidelines | Markdown |
| `CHANGELOG.md` | Version history and changes | Markdown |
| `PROJECT_STRUCTURE.md` | This file - project organization | Markdown |
| `WINDOWS_INSTALLATION.md` | Windows-specific setup guide | Markdown |
| `LICENSE` | MIT License text | Text |

### Templates

| File | Purpose | Variables |
|------|---------|-----------|
| `basic.md` | Simple notes | title, author, date |
| `meeting.md` | Meeting documentation | title, author, date |
| `daily_log.md` | Daily planning and reflection | title, author, date |
| `code_review.md` | Code review checklist | title, author, date |
| `ctf_writeup.md` | Capture The Flag documentation | title, author, date |
| `class_notes.md` | Academic note-taking | title, author, date |
| `study_session.md` | Study planning and tracking | title, author, date |
| `project_planning.md` | Project management | title, author, date |
| `bug_report.md` | Bug tracking and resolution | title, author, date |
| `powershell_script.md` | PowerShell script documentation | title, author, date |
| `batch_script.md` | Windows batch script documentation | title, author, date |

## 🚀 Usage Flow

### Initial Setup
1. User runs `setup.sh`
2. Dependencies are checked and installed
3. User runs `install_hud_notes.sh`
4. Global command and alias are created

### Runtime Flow
1. User runs `hud-notes` (or custom alias)
2. First run shows setup dialog
3. Templates are loaded from `templates/`
4. Configuration saved to user's notes directory
5. HUD overlay becomes available via hotkeys

### Development Flow
1. Developer clones repository
2. Runs `make dev-install` for development setup
3. Uses `make` commands for testing and formatting
4. Creates pull requests via GitHub templates

## 📦 Packaging Structure

For distribution, the project maintains:

- **Minimal dependencies**: Only essential Python packages
- **Self-contained**: All functionality in single Python file
- **Template system**: Easily extensible template directory
- **Cross-platform**: Bash scripts for Unix-like systems
- **GitHub ready**: Complete CI/CD and issue templates

## 🔧 Configuration

### Runtime Configuration
- Stored in: `{notes_directory}/.note_config.json`
- Contains: Window position, font size, transparency, etc.
- Auto-created on first run

### Template Configuration
- Location: `{notes_directory}/templates/`
- Format: Markdown files with variable substitution
- Hot-reloadable: Restart app to see new templates

## 🎯 Design Principles

1. **Simplicity**: Single Python file for core functionality
2. **Modularity**: Separate templates and configuration
3. **Portability**: Minimal dependencies, cross-platform
4. **Extensibility**: Easy to add new templates and features
5. **Documentation**: Comprehensive guides and examples
6. **Automation**: Scripts for common tasks and setup

## 📈 Future Structure

Planned additions:

```
hud-notes/
├── 📁 plugins/                  # Plugin system (planned)
├── 📁 themes/                   # UI themes (planned)
├── 📁 exports/                  # Export formats (planned)
├── 📁 tests/                    # Automated tests (planned)
└── 📁 docs/                     # Extended documentation (planned)
```

This structure ensures the project remains organized, maintainable, and easy to contribute to while providing a professional foundation for future development.