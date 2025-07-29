# Contributing to HUD Notes

Thank you for your interest in contributing to HUD Notes! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Template Development](#template-development)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions on-topic

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/hud-notes.git
   cd hud-notes
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a branch** for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Bug Reports

When reporting bugs, please include:

- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots or error logs if applicable

Use the bug report template in `templates/bug_report.md` for consistency.

### Feature Requests

For new features:

- Describe the problem you're trying to solve
- Explain how you envision the solution working
- Consider backwards compatibility
- Discuss potential implementation approaches

### Code Contributions

We welcome:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- New templates
- Platform-specific enhancements

## Development Setup

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)
- Git

### Setup Instructions

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python3 hud_notes.py
   ```

3. **Test the installation scripts (optional):**
   ```bash
   ./setup.sh
   ```

### Development Dependencies

For development work, you may want to install additional tools:

```bash
# Code formatting
pip3 install black

# Linting
pip3 install flake8

# Testing
pip3 install pytest
```

## Coding Standards

### Python Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions focused and relatively small
- Use type hints where appropriate

### Code Formatting

We recommend using `black` for code formatting:

```bash
black hud_notes.py
```

### Documentation

- Update docstrings when modifying functions
- Update README.md for significant changes
- Comment complex logic clearly
- Keep comments up-to-date with code changes

## Template Development

### Creating New Templates

Templates are stored in the `templates/` directory and use Markdown format with Python string formatting.

#### Template Variables

Available variables:
- `{title}` - Note title
- `{author}` - Author name  
- `{date}` - Current date and time

#### Template Guidelines

1. **File naming:** Use snake_case with `.md` extension
2. **Content structure:** Include clear sections and helpful prompts
3. **Formatting:** Use consistent Markdown formatting
4. **Variables:** Always include `{title}`, `{author}`, and `{date}`
5. **Documentation:** Add comments explaining the template's purpose

#### Example Template

```markdown
# {title}

**Author:** {author}
**Date:** {date}
**Category:** Your Category Here

---

## Section 1

Content and prompts here...

## Section 2

More content...

---
**Tags:** #tag1 #tag2 #{category}
```

### Template Testing

Test your templates by:

1. Adding the template file to `templates/`
2. Restarting HUD Notes
3. Creating a new note with your template
4. Verifying all variables are properly substituted
5. Checking the formatting and usability

## Testing

### Manual Testing

Before submitting changes:

1. Test basic functionality (create, open, save notes)
2. Test new features thoroughly
3. Verify hotkeys work correctly
4. Test on different screen resolutions if possible
5. Test the installation scripts

### Automated Testing

We're working on automated tests. Future contributions should include tests for new features.

## Pull Request Process

1. **Update documentation** for any new features
2. **Test your changes** thoroughly
3. **Follow the coding standards** outlined above
4. **Create a clear commit message:**
   ```
   Add feature: Brief description
   
   - Detailed change 1
   - Detailed change 2
   - Fixes #issue_number (if applicable)
   ```

5. **Open a pull request** with:
   - Clear title describing the change
   - Description of what was changed and why
   - Any special testing instructions
   - Screenshots for UI changes

### Pull Request Review

All pull requests require review. The process includes:

- Code review for quality and standards
- Testing of new functionality
- Documentation review
- Compatibility checking

### Merge Requirements

Before merging, ensure:

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Feature works as expected
- [ ] No breaking changes (or properly documented)

## Development Roadmap

Current priorities:

1. **Cross-platform compatibility** improvements
2. **Automated testing** framework
3. **Plugin system** for extensions
4. **Enhanced syntax highlighting**
5. **Cloud sync** capabilities

## Getting Help

- **Issues:** Open an issue on GitHub
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check the README.md and code comments

## Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes for significant contributions
- README.md acknowledgments section

Thank you for contributing to HUD Notes! 🚀