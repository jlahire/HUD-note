"""
Template management system for HUD Notes
"""

from typing import Dict, List


class TemplateManager:
    """Manages note templates from hardcoded definitions"""
    
    def __init__(self, templates_dir: str = None):
        # Keep templates_dir for compatibility but don't use it
        self.templates_dir = templates_dir
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load hardcoded templates"""
        print("DEBUG: Loading hardcoded templates...")
        
        self.templates = {
            "Basic": "# {title}\n\n**Author:** {author}\n**Date:** {date}\n\n---\n\n",
            
            "Meeting": """# {title}

**Date:** {date}
**Attendees:** 
**Agenda:**

---

## Notes

## Action Items
- [ ] 

""",
            
            "Daily Log": """# {title}

**Date:** {date}

---

## Today's Goals
- [ ] 

## Completed

## Notes

## Tomorrow
- [ ] 

""",
            
            "Code Review": """# {title}

**Author:** {author}
**Date:** {date}
**Repository:** 
**Branch:** 

---

## Changes

## Issues Found

## Recommendations

""",
            
            "Ctf Writeup": """# {title}

**Author:** {author}
**Date:** {date}
**Challenge:** 
**Category:** 
**Points:** 

---

## Challenge Description

## Solution

### Reconnaissance

### Exploitation

### Flag

```
[FLAG_HERE]
```

## Lessons Learned

""",
            
            "Class Notes": """# {title}

**Date:** {date}
**Course:** 
**Professor:** 
**Topic:** 

---

## Key Concepts

## Notes

## Important Formulas/Code

## Questions/Clarifications

## Action Items
- [ ] 

""",
            
            "Study Session": """# {title}

**Date:** {date}
**Subject:** 
**Duration:** 
**Goal:** 

---

## Topics Covered

## What I Learned

## Still Need to Review

## Next Session Plan

""",
            
            "Project Planning": """# {title}

**Author:** {author}
**Date:** {date}
**Project:** 
**Deadline:** 

---

## Objectives

## Requirements

## Timeline

## Resources Needed

## Risks/Concerns

## Next Steps
- [ ] 

""",
            
            "Bug Report": """# {title}

**Author:** {author}
**Date:** {date}
**Severity:** 
**Priority:** 

---

## Description

## Steps to Reproduce

1. 
2. 
3. 

## Expected Behavior

## Actual Behavior

## Environment

## Additional Notes

""",
            
            "Powershell Script": """# {title}

**Author:** {author}
**Date:** {date}
**Purpose:** 
**Requirements:** 

---

## Script Overview

## Parameters

## Usage Examples

```powershell
# Example usage
.\\{title}.ps1 -Parameter "value"
```

## Script Code

```powershell
# PowerShell script content here
```

## Notes

""",
            
            "Batch Script": """# {title}

**Author:** {author}
**Date:** {date}
**Purpose:** 
**Requirements:** 

---

## Script Overview

## Usage

```batch
REM Usage example
{title}.bat [parameters]
```

## Script Code

```batch
@echo off
REM Batch script content here
```

## Notes

"""
        }
        
        print(f"DEBUG: Loaded {len(self.templates)} hardcoded templates")
        print(f"DEBUG: Template names: {list(self.templates.keys())}")
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names"""
        return list(self.templates.keys())
    
    def get_template_content(self, template_name: str) -> str:
        """Get content of specified template"""
        return self.templates.get(template_name, self.templates.get("Basic", ""))
    
    def get_template_description(self, template_name: str) -> str:
        """Get a description for each template type"""
        descriptions = {
            'Basic': 'Simple note template with title, author, and date',
            'Meeting': 'Meeting notes with attendees, agenda, and action items',
            'Daily Log': 'Daily planning with goals, completed tasks, and reflections',
            'Code Review': 'Code review checklist with repository and branch info',
            'Ctf Writeup': 'Capture The Flag challenge documentation',
            'Class Notes': 'Academic note-taking with structured sections',
            'Study Session': 'Study planning and progress tracking',
            'Project Planning': 'Project management with timelines and resources',
            'Bug Report': 'Bug tracking and resolution workflow',
            'Powershell Script': 'Windows PowerShell script documentation',
            'Batch Script': 'Windows batch file documentation'
        }
        
        return descriptions.get(template_name, 'Custom template for specialized note-taking')
    
    def format_template(self, template_name: str, **kwargs) -> str:
        """Format template with provided variables"""
        template_content = self.get_template_content(template_name)
        try:
            return template_content.format(**kwargs)
        except (KeyError, IndexError, ValueError) as e:
            print(f"Warning: Template formatting error for {template_name}: {e}")
            # Try to format with safe replacement
            try:
                import re
                # Replace any numbered placeholders with named ones or remove them
                safe_content = re.sub(r'\{(\d+)\}', r'{placeholder_\1}', template_content)
                # Replace any malformed placeholders
                safe_content = re.sub(r'\{[^}]*\}', '', safe_content)
                return safe_content
            except:
                # Last resort - return template as-is
                return template_content
    
    def reload_templates(self):
        """Reload templates (no-op for hardcoded templates)"""
        self.load_templates()
    
    def create_template_overview(self, author: str) -> str:
        """Create a comprehensive template overview"""
        from datetime import datetime
        
        template_names = self.get_template_names()
        
        overview_content = f"# HUD Notes - Available Templates\n\n"
        overview_content += f"**Author:** {author}\n"
        overview_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        overview_content += f"**Templates Available:** {len(template_names)}\n\n"
        overview_content += "---\n\n"
        overview_content += "## Quick Start Guide\n\n"
        overview_content += "• Press **Ctrl+Alt+N** or click **New** for new note with template selection\n"
        overview_content += "• Press **Ctrl+Alt+S** to save current note\n"
        overview_content += "• Use **T-/T+** buttons for text size adjustment\n"
        overview_content += "• Use **O-/O+** buttons for transparency adjustment\n"
        overview_content += "• Click **⚙** for settings and theme customization\n\n"
        overview_content += "---\n\n"
        overview_content += "## Available Templates\n\n"
        
        # Add each template with preview
        for i, template_name in enumerate(sorted(template_names), 1):
            template_content = self.get_template_content(template_name)
            
            # Format the template to show structure
            try:
                formatted_template = self.format_template(
                    template_name,
                    title=f"Example {template_name}",
                    author=author or "Your Name",
                    date=datetime.now().strftime('%Y-%m-%d %H:%M')
                )
            except Exception as e:
                print(f"Warning: Could not format template {template_name}: {e}")
                formatted_template = self.get_template_content(template_name)
            
            overview_content += f"### {i}. {template_name}\n\n"
            overview_content += f"**Description:** {self.get_template_description(template_name)}\n\n"
            overview_content += "**Preview:**\n"
            overview_content += "```markdown\n"
            # Show first few lines of template
            lines = formatted_template.split('\n')
            preview_lines = lines[:8] if len(lines) > 8 else lines
            overview_content += '\n'.join(preview_lines)
            if len(lines) > 8:
                overview_content += "\n[... rest of template ...]"
            overview_content += "\n```\n\n"
            overview_content += "---\n\n"
        
        # Add footer
        overview_content += "## Getting Started\n\n"
        overview_content += "1. **Choose a template** by pressing **Ctrl+Alt+N** or clicking **New**\n"
        overview_content += "2. **Select from the list** of available templates\n"
        overview_content += "3. **Start writing** - your content will auto-save\n"
        overview_content += "4. **Adjust appearance** using the control buttons:\n"
        overview_content += "   - **T-/T+** - Decrease/increase text size\n"
        overview_content += "   - **O-/O+** - Decrease/increase transparency\n"
        overview_content += "   - **⚙** - Open settings for themes and preferences\n\n"
        overview_content += "**Tip:** Templates are now built into the application for reliability!\n\n"
        overview_content += "---\n\n"
        overview_content += "*Welcome to HUD Notes! This overview will be replaced when you create your first note.*"
        
        return overview_content