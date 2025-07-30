#!/usr/bin/env python3
"""
HUD Notes - Production Version
A HUD-style overlay note-taking application with multi-display support,
syntax highlighting, and template system.

Author: Lahire
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import json
import glob
from datetime import datetime
from pynput import keyboard
import threading
import markdown2
from tkinter import font

class TemplateManager:
    """Manages note templates from the templates directory"""
    
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all template files from templates directory"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            self.create_default_templates()
        
        # Load all .md files from templates directory
        template_files = glob.glob(os.path.join(self.templates_dir, "*.md"))
        
        for template_file in template_files:
            template_name = os.path.splitext(os.path.basename(template_file))[0]
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.templates[template_name.replace('_', ' ').title()] = content
            except Exception as e:
                print(f"Warning: Could not load template {template_file}: {e}")
        
        # Fallback to basic template if no templates loaded
        if not self.templates:
            self.templates["Basic"] = "# {title}\n\n**Author:** {author}\n**Date:** {date}\n\n---\n\n"
    
    def create_default_templates(self):
        """Create default template files if templates directory is empty"""
        default_templates = {
            "basic.md": "# {title}\n\n**Author:** {author}\n**Date:** {date}\n\n---\n\n",
            "meeting.md": """# {title}

**Date:** {date}
**Attendees:** 
**Agenda:**

---

## Notes

## Action Items
- [ ] 

""",
            "daily_log.md": """# {title}

**Date:** {date}

---

## Today's Goals
- [ ] 

## Completed

## Notes

## Tomorrow
- [ ] 

""",
            "code_review.md": """# {title}

**Author:** {author}
**Date:** {date}
**Repository:** 
**Branch:** 

---

## Changes

## Issues Found

## Recommendations

"""
        }
        
        for filename, content in default_templates.items():
            template_path = os.path.join(self.templates_dir, filename)
            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"Warning: Could not create template {filename}: {e}")
    
    def get_template_names(self):
        """Get list of available template names"""
        return list(self.templates.keys())
    
    def get_template_content(self, template_name):
        """Get content of specified template"""
        return self.templates.get(template_name, self.templates.get("Basic", ""))

class NoteOverlay:
    def __init__(self):
        self.overlay_visible = False
        self.current_file = None
        self.notes_dir = None
        self.author_name = None
        self.note_title = None
        self.templates_dir = None
        
        # Initialize template manager (will be set after config)
        self.template_manager = None
        
        # Get display settings first
        self.get_display_settings()
        
        # Initialize current display
        self.current_display = 0
        
        # Show startup configuration dialog
        if not self.show_startup_config():
            return
        
        # Initialize template manager now that we have templates_dir
        self.template_manager = TemplateManager(self.templates_dir)
        
        # Set config file path based on selected notes directory
        self.config_file = os.path.join(self.notes_dir, ".note_config.json")
        
        # Ensure directories exist
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Initialize advanced features
        self.hover_monitor_active = False
        
        # Setup advanced features if enabled
        if self.config.get('mouse_hover_show', False):
            self.setup_mouse_hover_monitor()
        
        if self.config.get('click_outside_hide', False):
            self.setup_click_outside_monitor()
        
        # Create screen border (always visible)
        self.create_screen_border()
        
        # Create persistent hotkey display
        self.create_hotkey_display()
        
        # Create overlay window
        self.create_overlay()
        
        # Setup global hotkey
        self.setup_hotkey()
        
        # Display all available templates at startup
        self.display_all_templates_at_startup()

    def show_startup_config(self):
        """Show startup configuration dialog with proper sizing"""
        # Create hidden root window first to prevent it from showing
        self.temp_root = tk.Tk()
        self.temp_root.withdraw()  # Hide immediately
        self.temp_root.attributes('-alpha', 0)  # Make transparent
        self.temp_root.geometry("1x1+0+0")  # Minimize size
        
        # Create the actual config window
        config_root = tk.Toplevel(self.temp_root)
        config_root.title("HUD Notes - Initial Setup")
        
        # Calculate proper window size and center it
        window_width = 600
        window_height = 500
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        config_root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        config_root.configure(bg='#1a1a1a')
        config_root.attributes('-topmost', True)
        config_root.resizable(True, True)  # Allow resizing
        
        # Ensure window is shown properly
        config_root.deiconify()
        config_root.lift()
        config_root.focus_force()
        
        # Variables to store config
        self.setup_complete = False
        
        # Create main frame with scrollable content
        main_frame = tk.Frame(config_root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 HUD Notes Setup", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notes directory selection
        dir_frame = tk.Frame(main_frame, bg='#1a1a1a')
        dir_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(dir_frame, text="📁 Notes Directory:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        default_notes_dir = os.path.expanduser("~/Documents/HUD_Notes")
        dir_var = tk.StringVar(value=default_notes_dir)
        
        dir_entry_frame = tk.Frame(dir_frame, bg='#1a1a1a')
        dir_entry_frame.pack(fill=tk.X, pady=5)
        
        dir_entry = tk.Entry(dir_entry_frame, textvariable=dir_var, 
                            bg='#333333', fg='#ffffff', font=('Consolas', 10),
                            insertbackground='#00ff41', relief=tk.FLAT)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_directory():
            directory = filedialog.askdirectory(initialdir=dir_var.get(), title="Select Notes Directory")
            if directory:
                dir_var.set(directory)
        
        tk.Button(dir_entry_frame, text="Browse...", command=browse_directory,
                 bg='#0066cc', fg='white', font=('Consolas', 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.RIGHT)
        
        # Author name
        author_frame = tk.Frame(main_frame, bg='#1a1a1a')
        author_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(author_frame, text="👤 Author Name:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        author_var = tk.StringVar(value=os.getenv('USERNAME', os.getenv('USER', 'User')))
        tk.Entry(author_frame, textvariable=author_var,
                bg='#333333', fg='#ffffff', font=('Consolas', 10),
                insertbackground='#00ff41', relief=tk.FLAT).pack(fill=tk.X, pady=5)
        
        # Note title
        title_frame = tk.Frame(main_frame, bg='#1a1a1a')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(title_frame, text="📝 Initial Note Title:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        title_var = tk.StringVar(value=f"Notes - {datetime.now().strftime('%Y-%m-%d')}")
        tk.Entry(title_frame, textvariable=title_var,
                bg='#333333', fg='#ffffff', font=('Consolas', 10),
                insertbackground='#00ff41', relief=tk.FLAT).pack(fill=tk.X, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        def save_config():
            self.notes_dir = dir_var.get()
            self.templates_dir = os.path.join(self.notes_dir, "templates")
            self.author_name = author_var.get()
            self.note_title = title_var.get()
            
            self.setup_complete = True
            config_root.destroy()
            self.temp_root.destroy()
        
        def cancel_setup():
            self.setup_complete = False
            config_root.destroy()
            self.temp_root.destroy()
        
        # Button styling
        button_style = {
            'font': ('Consolas', 12, 'bold'),
            'relief': tk.FLAT,
            'padx': 25,
            'pady': 8
        }
        
        tk.Button(button_frame, text="✓ Start HUD Notes", command=save_config,
                 bg='#006600', fg='white', **button_style).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="✗ Cancel", command=cancel_setup,
                 bg='#660000', fg='white', **button_style).pack(side=tk.RIGHT, padx=10)
        
        # Info text
        info_frame = tk.Frame(main_frame, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = ("💡 This setup creates your notes directory and templates folder.\n"
                    "You can add custom templates to the templates/ directory later.\n"
                    "Configuration will be saved to .note_config.json in your notes directory.")
        
        tk.Label(info_frame, 
                text=info_text,
                bg='#1a1a1a', fg='#888888', font=('Consolas', 10),
                wraplength=window_width-60, justify=tk.LEFT).pack()
        
        # Keyboard shortcuts
        config_root.bind('<Return>', lambda e: save_config())
        config_root.bind('<Escape>', lambda e: cancel_setup())
        
        # Handle window close button
        config_root.protocol("WM_DELETE_WINDOW", cancel_setup)
        
        # Run the config dialog
        config_root.mainloop()
        
        return self.setup_complete

    def show_template_selection(self):
        """Show template selection dialog when starting HUD Notes"""
        template_window = tk.Toplevel(self.root)
        template_window.title("Select Template")
        template_window.geometry("500x400")
        template_window.configure(bg='#1a1a1a')
        template_window.attributes('-topmost', True)
        template_window.resizable(True, True)
        
        # Center the window
        current_display = self.displays[self.current_display]
        x = current_display['x'] + (current_display['width'] - 500) // 2
        y = current_display['y'] + (current_display['height'] - 400) // 2
        template_window.geometry(f"500x400+{x}+{y}")
        
        # Ensure it shows properly
        template_window.deiconify()
        template_window.lift()
        template_window.focus_force()
        
        # Main frame
        main_frame = tk.Frame(template_window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="📋 Choose Note Template", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Template list frame
        list_frame = tk.Frame(main_frame, bg='#1a1a1a')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Listbox with templates
        listbox_frame = tk.Frame(list_frame, bg='#333333', relief=tk.SOLID, bd=1)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        template_listbox = tk.Listbox(
            listbox_frame,
            bg='#333333',
            fg='#ffffff',
            selectbackground='#0066cc',
            selectforeground='#ffffff',
            font=('Consolas', 11),
            relief=tk.FLAT,
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            height=15
        )
        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=template_listbox.yview)
        
        # Populate listbox with templates
        template_names = self.template_manager.get_template_names()
        for i, template_name in enumerate(sorted(template_names)):
            template_listbox.insert(tk.END, f"📝 {template_name}")
            if template_name == "Basic":
                template_listbox.selection_set(i)
        
        # Preview frame
        preview_frame = tk.Frame(main_frame, bg='#1a1a1a')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        tk.Label(preview_frame, text="Preview:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        preview_text = ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            bg='#2a2a2a',
            fg='#cccccc',
            font=('Consolas', 9),
            relief=tk.FLAT,
            borderwidth=1,
            height=8,
            state=tk.DISABLED
        )
        preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def update_preview(event=None):
            """Update preview when selection changes"""
            selection = template_listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                template_content = self.template_manager.get_template_content(template_name)
                
                # Format template with current values
                formatted_content = template_content.format(
                    title=self.note_title,
                    author=self.author_name,
                    date=datetime.now().strftime('%Y-%m-%d %H:%M')
                )
                
                preview_text.config(state=tk.NORMAL)
                preview_text.delete(1.0, tk.END)
                preview_text.insert(1.0, formatted_content)
                preview_text.config(state=tk.DISABLED)
        
        template_listbox.bind('<<ListboxSelect>>', update_preview)
        
        # Initial preview
        if template_listbox.curselection():
            update_preview()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X)
        
        def create_note():
            """Create note with selected template"""
            selection = template_listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                template_content = self.template_manager.get_template_content(template_name)
                
                # Format template with current values
                formatted_content = template_content.format(
                    title=self.note_title,
                    author=self.author_name,
                    date=datetime.now().strftime('%Y-%m-%d %H:%M')
                )
                
                # Insert into text area
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, formatted_content)
                
                # Auto-save with title as filename
                safe_filename = "".join(c for c in self.note_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                self.current_file = os.path.join(self.notes_dir, f"{safe_filename}.md")
                self.save_note()
                self.update_file_label()
                self.apply_syntax_highlighting()
                
                template_window.destroy()
                self.update_status(f"Created note with {template_name} template")
            else:
                messagebox.showwarning("No Selection", "Please select a template first.")
        
        def create_blank():
            """Create blank note"""
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.update_file_label()
            template_window.destroy()
            self.update_status("Created blank note")
        
        # Button styling
        button_style = {
            'font': ('Consolas', 11, 'bold'),
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8
        }
        
        tk.Button(button_frame, text="✓ Create with Template", command=create_note,
                 bg='#006600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📄 Create Blank", command=create_blank,
                 bg='#333333', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✗ Cancel", command=template_window.destroy,
                 bg='#660000', fg='white', **button_style).pack(side=tk.RIGHT, padx=5)
        
        # Keyboard shortcuts
        template_window.bind('<Return>', lambda e: create_note())
        template_window.bind('<Escape>', lambda e: template_window.destroy())
        template_window.bind('<Double-Button-1>', lambda e: create_note())
        
        # Handle window close button
        template_window.protocol("WM_DELETE_WINDOW", template_window.destroy)

    def display_all_templates_at_startup(self):
        """Display all available templates in the text area at startup"""
        self.text_area.delete(1.0, tk.END)
        
        # Get all template names
        template_names = self.template_manager.get_template_names()
        
        # Create a comprehensive template overview
        overview_content = f"# HUD Notes - Available Templates\n\n"
        overview_content += f"**Author:** {self.author_name}\n"
        overview_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        overview_content += f"**Templates Available:** {len(template_names)}\n\n"
        overview_content += "---\n\n"
        overview_content += "## Quick Start Guide\n\n"
        overview_content += "• Press **Ctrl+Alt+N** or click **●** for new note with template selection\n"
        overview_content += "• Press **Ctrl+Alt+O** or click **▲** to open existing note\n"
        overview_content += "• Press **Ctrl+Alt+S** or click **■** to save current note\n"
        overview_content += "• Press **Ctrl+Alt+C** or click **</>** for code input window\n"
        overview_content += "• Press **Ctrl+Alt+G** or click **⚙** for settings\n\n"
        overview_content += "---\n\n"
        overview_content += "## Available Templates\n\n"
        
        # Add each template with preview
        for i, template_name in enumerate(sorted(template_names), 1):
            template_content = self.template_manager.get_template_content(template_name)
            
            # Format the template to show structure
            formatted_template = template_content.format(
                title=f"Example {template_name}",
                author=self.author_name,
                date=datetime.now().strftime('%Y-%m-%d %H:%M')
            )
            
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
        overview_content += "1. **Choose a template** by pressing **Ctrl+Alt+N** (New Note)\n"
        overview_content += "2. **Select from the list** of available templates\n"
        overview_content += "3. **Start writing** - your content will auto-save\n"
        overview_content += "4. **Customize appearance** in Settings (⚙)\n\n"
        overview_content += "**Tip:** You can create custom templates by adding `.md` files to the `templates/` directory!\n\n"
        overview_content += f"**Templates Directory:** `{self.templates_dir}`\n\n"
        overview_content += "---\n\n"
        overview_content += "*Welcome to HUD Notes! This overview will be replaced when you create your first note.*"
        
        # Insert the overview content
        self.text_area.insert(1.0, overview_content)
        
        # Apply syntax highlighting
        self.apply_syntax_highlighting()
        
        # Update status and file label
        self.current_file = None
        self.update_file_label()
        self.update_status(f"Template overview loaded - {len(template_names)} templates available")

    def get_template_description(self, template_name):
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

    def get_display_settings(self):
        """Get current display settings and DPI scaling"""
        # Create temporary hidden window to get display info
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.attributes('-alpha', 0)
        temp_root.geometry("1x1+0+0")
        
        # Get screen dimensions
        self.screen_width = temp_root.winfo_screenwidth()
        self.screen_height = temp_root.winfo_screenheight()
        
        # Detect multiple displays
        self.detect_displays(temp_root)
        
        # Get DPI scaling factor
        try:
            dpi_x = temp_root.winfo_fpixels('1i')
            self.dpi_scale = dpi_x / 96.0
        except:
            self.dpi_scale = 1.0
        
        # Get system font size
        try:
            default_font = font.nametofont("TkDefaultFont")
            self.system_font_size = default_font['size']
            if self.system_font_size < 0:
                self.system_font_size = int(abs(self.system_font_size) * 72 / dpi_x)
        except:
            self.system_font_size = 9
        
        # Calculate scaled dimensions for right 1/4 of current display
        self.calculate_display_layout()
        
        # Scale font size based on DPI and system settings
        self.scaled_font_size = max(8, int(self.system_font_size * self.dpi_scale))
        
        temp_root.destroy()

    def detect_displays(self, temp_root):
        """Detect available displays/monitors"""
        self.displays = []
        self.current_display = 0
        
        try:
            # Simple approach - assume single display for now
            # In production, you might want to use platform-specific libraries
            self.displays = [
                {
                    'x': 0, 
                    'y': 0, 
                    'width': self.screen_width, 
                    'height': self.screen_height,
                    'name': 'Primary Display'
                }
            ]
        except:
            # Fallback
            self.displays = [
                {
                    'x': 0, 
                    'y': 0, 
                    'width': self.screen_width, 
                    'height': self.screen_height,
                    'name': 'Primary Display'
                }
            ]

    def calculate_display_layout(self):
        """Calculate window layout for current display"""
        current_display = self.displays[self.current_display]
        
        taskbar_height = 40
        hotkey_bar_height = 32
        
        display_width = current_display['width']
        display_height = current_display['height']
        display_x = current_display['x']
        display_y = current_display['y']
        
        self.calculated_width = int(display_width // 4)
        self.calculated_height = int(display_height - taskbar_height - hotkey_bar_height)
        self.calculated_x = int(display_x + display_width - self.calculated_width)
        self.calculated_y = display_y

    def load_config(self):
        """Load configuration from file with display-aware defaults"""
        default_config = {
            "window_width": self.calculated_width,
            "window_height": self.calculated_height,
            "window_x": self.calculated_x,
            "window_y": self.calculated_y,
            "last_file": None,
            "font_size": self.scaled_font_size,
            "theme": "dark",
            "hud_transparency": 0.85,
            "auto_scale": True,
            "notes_directory": self.notes_dir,
            "templates_directory": self.templates_dir,
            "author_name": self.author_name,
            "syntax_highlighting": True,
            "auto_save_interval": 2000
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    
                if saved_config.get('auto_scale', True):
                    self.config = {**default_config, **saved_config}
                    self.config.update({
                        "window_width": self.calculated_width,
                        "window_height": self.calculated_height,
                        "window_x": self.calculated_x,
                        "window_y": self.calculated_y,
                        "font_size": self.scaled_font_size
                    })
                else:
                    self.config = {**default_config, **saved_config}
            else:
                self.config = default_config
        except:
            self.config = default_config

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass

    def create_screen_border(self):
        """Create always-visible screen border"""
        border_width = max(2, int(2 * self.dpi_scale))
        border_color = "#00ff41"
        
        self.border_windows = []
        
        # Top border
        top_border = tk.Toplevel()
        top_border.geometry(f"{self.screen_width}x{border_width}+0+0")
        top_border.configure(bg=border_color)
        top_border.overrideredirect(True)
        top_border.attributes('-topmost', True)
        top_border.attributes('-alpha', 0.6)
        self.border_windows.append(top_border)
        
        # Left border
        left_border = tk.Toplevel()
        left_border.geometry(f"{border_width}x{self.screen_height}+0+0")
        left_border.configure(bg=border_color)
        left_border.overrideredirect(True)
        left_border.attributes('-topmost', True)
        left_border.attributes('-alpha', 0.6)
        self.border_windows.append(left_border)
        
        # Right border
        right_border = tk.Toplevel()
        right_border.geometry(f"{border_width}x{self.screen_height}+{self.screen_width-border_width}+0")
        right_border.configure(bg=border_color)
        right_border.overrideredirect(True)
        right_border.attributes('-topmost', True)
        right_border.attributes('-alpha', 0.6)
        self.border_windows.append(right_border)

    def create_hotkey_display(self):
        """Create persistent hotkey display at bottom of screen"""
        hotkey_height = max(30, int(30 * self.dpi_scale))
        hotkey_font_size = max(8, int(9 * self.dpi_scale))
        
        self.hotkey_window = tk.Toplevel()
        self.hotkey_window.geometry(f"{self.screen_width}x{hotkey_height}+0+{self.screen_height-hotkey_height}")
        
        self.hotkey_window.configure(bg='black')
        self.hotkey_window.overrideredirect(True)
        self.hotkey_window.attributes('-topmost', True)
        self.hotkey_window.attributes('-transparentcolor', 'black')
        self.hotkey_window.attributes('-alpha', 0.8)
        
        hotkeys_text = "HOTKEYS: Ctrl+Alt+T=Toggle | Drag=Move | Ctrl+Alt+N=New | Ctrl+Alt+O=Open | Ctrl+Alt+S=Save | Ctrl+Alt+P=Preview | Ctrl+Alt++=Font+ | Ctrl+Alt+-=Font- | Ctrl+Alt+C=Code | Ctrl+Alt+1-4=Corners | Ctrl+Alt+5=Center | Ctrl+Alt+M=NextDisplay | Esc=Hide | Ctrl+Alt+Q=Exit | Ctrl+Alt+R=Reset"
        
        hotkey_label = tk.Label(
            self.hotkey_window,
            text=hotkeys_text,
            bg='black',
            fg='#00ff41',
            font=('Consolas', hotkey_font_size, 'bold'),
            pady=5
        )
        hotkey_label.pack(fill=tk.BOTH, expand=True)
        
        # Add border line
        border_height = max(1, int(1 * self.dpi_scale))
        bottom_border = tk.Toplevel()
        bottom_border.geometry(f"{self.screen_width}x{border_height}+0+{self.screen_height-hotkey_height-border_height}")
        bottom_border.configure(bg='#00ff41')
        bottom_border.overrideredirect(True)
        bottom_border.attributes('-topmost', True)
        bottom_border.attributes('-alpha', 0.4)
        self.border_windows.append(bottom_border)

    def create_overlay(self):
        """Create the main overlay window - HUD style"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("HUD Notes")
        
        self.root.attributes('-alpha', 0)
        
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}+"
                          f"{self.config['window_x']}+{self.config['window_y']}")
        
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.resizable(True, True)
        
        self.setup_theme()
        self.create_hud_interface()
        
        # Add custom resize handles
        self.create_resize_handles()
        
        self.root.attributes('-alpha', self.config['hud_transparency'])
        
        self.root.bind('<Escape>', lambda e: self.hide_overlay())
        self.root.bind('<FocusOut>', self.on_focus_out)
        self.root.bind('<FocusIn>', self.on_focus_in)

    def setup_theme(self):
        """Setup HUD dark theme"""
        self.bg_color = '#0a0a0a'
        self.fg_color = '#00ff41'
        self.select_bg = '#1a3d1a'
        self.button_bg = '#1a1a1a'
        self.button_fg = '#00ff41'
        self.accent_color = '#ff6600'
        
        self.root.configure(bg=self.bg_color)

    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#2a2a2a', relief=tk.SOLID, bd=1)
            
            label = tk.Label(tooltip, text=text, bg='#2a2a2a', fg='#ffffff',
                           font=('Consolas', 9), padx=8, pady=4)
            label.pack()
            
            # Position tooltip near cursor
            x = event.x_root + 10
            y = event.y_root - 10
            tooltip.geometry(f"+{x}+{y}")
            
            # Store tooltip reference
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def create_hud_interface(self):
        """Create streamlined HUD interface"""
        title_height = max(35, int(35 * self.dpi_scale))
        button_size = max(3, int(3 * self.dpi_scale))
        title_font_size = max(8, int(10 * self.dpi_scale))
        
        # Title bar with drag functionality
        title_frame = tk.Frame(self.root, bg='#333333', height=title_height, relief=tk.RAISED, bd=1)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_frame.bind('<Button-1>', self.start_drag)
        title_frame.bind('<B1-Motion>', self.on_drag) 
        title_frame.bind('<ButtonRelease-1>', self.stop_drag)
        title_frame.bind('<Double-Button-1>', self.reset_to_quarter_screen)
        
        # Title and controls
        title_left = tk.Frame(title_frame, bg='#333333')
        title_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.file_label = tk.Label(title_left, text="HUD NOTES [D1/1]", 
                                  bg='#333333', fg=self.accent_color,
                                  font=('Consolas', title_font_size, 'bold'))
        self.file_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Make draggable
        self.file_label.bind('<Button-1>', self.start_drag)
        self.file_label.bind('<B1-Motion>', self.on_drag)
        self.file_label.bind('<ButtonRelease-1>', self.stop_drag)
        self.file_label.bind('<Double-Button-1>', self.reset_to_quarter_screen)
        
        # Drag indicator
        drag_label = tk.Label(title_left, text="[DRAG HERE]", 
                             bg='#333333', fg='#666666',
                             font=('Consolas', max(8, int(8 * self.dpi_scale))))
        drag_label.pack(side=tk.RIGHT, padx=10, pady=2)
        drag_label.bind('<Button-1>', self.start_drag)
        drag_label.bind('<B1-Motion>', self.on_drag)
        drag_label.bind('<ButtonRelease-1>', self.stop_drag)
        drag_label.bind('<Double-Button-1>', self.reset_to_quarter_screen)
        
        # Control buttons - larger and with tooltips
        controls = tk.Frame(title_frame, bg='#333333')
        controls.pack(side=tk.RIGHT, padx=5)
        
        button_font_size = max(10, int(10 * self.dpi_scale))
        button_width = max(3, int(3.5 * self.dpi_scale))
        button_height = max(1, int(1.2 * self.dpi_scale))
        
        # Font controls
        font_minus_btn = tk.Button(controls, text="A-", command=self.decrease_font,
                 bg=self.button_bg, fg='#ffcc00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        font_minus_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(font_minus_btn, "Decrease Font Size")
        
        font_plus_btn = tk.Button(controls, text="A+", command=self.increase_font,
                 bg=self.button_bg, fg='#ffcc00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        font_plus_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(font_plus_btn, "Increase Font Size")
        
        # Other controls with tooltips
        code_btn = tk.Button(controls, text="</>", command=self.open_code_window,
                 bg=self.button_bg, fg='#00ccff', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        code_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(code_btn, "Code Input Window")
        
        new_btn = tk.Button(controls, text="●", command=self.new_note,
                 bg=self.button_bg, fg='#ffff00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        new_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(new_btn, "New Note (with Template)")
        
        open_btn = tk.Button(controls, text="▲", command=self.open_note,
                 bg=self.button_bg, fg='#00ffff', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        open_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(open_btn, "Open Note")
        
        save_btn = tk.Button(controls, text="■", command=self.save_note,
                 bg=self.button_bg, fg='#00ff00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        save_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(save_btn, "Save Note")
        
        saveas_btn = tk.Button(controls, text="▫", command=self.save_as_note,
                 bg=self.button_bg, fg='#00cc00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        saveas_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(saveas_btn, "Save As...")
        
        preview_btn = tk.Button(controls, text="◊", command=self.toggle_preview,
                 bg=self.button_bg, fg='#ff00ff', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        preview_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(preview_btn, "Toggle Preview")
        
        reset_btn = tk.Button(controls, text="↻", command=self.reset_to_quarter_screen,
                 bg=self.button_bg, fg='#ffaa00', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        reset_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(reset_btn, "Reset Window Position")
        
        settings_btn = tk.Button(controls, text="⚙", command=self.open_settings,
                 bg=self.button_bg, fg='#cccccc', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        settings_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(settings_btn, "Settings")
        
        close_btn = tk.Button(controls, text="✕", command=self.hide_overlay,
                 bg='#330000', fg='#ff0000', font=('Arial', button_font_size, 'bold'),
                 width=button_width, height=button_height, relief=tk.FLAT)
        close_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(close_btn, "Hide Overlay")
        
        # Status line
        status_height = max(20, int(20 * self.dpi_scale))
        status_frame = tk.Frame(self.root, bg='#1a1a1a', height=status_height)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        status_font_size = max(8, int(8 * self.dpi_scale))
        
        self.status_label = tk.Label(status_frame, text="Ready | Display Scale: {:.0f}%".format(self.dpi_scale * 100), 
                                   bg='#1a1a1a', fg=self.fg_color,
                                   font=('Consolas', status_font_size))
        self.status_label.pack(side=tk.LEFT, padx=5, pady=1)
        
        # Transparency controls
        trans_frame = tk.Frame(status_frame, bg='#1a1a1a')
        trans_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(trans_frame, text="α:", bg='#1a1a1a', fg=self.fg_color,
                font=('Consolas', status_font_size)).pack(side=tk.LEFT)
        
        trans_minus_btn = tk.Button(trans_frame, text="-", command=self.decrease_transparency,
                 bg=self.button_bg, fg=self.fg_color, font=('Arial', status_font_size),
                 width=button_size, height=1, relief=tk.FLAT)
        trans_minus_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(trans_minus_btn, "Decrease Transparency")
        
        trans_plus_btn = tk.Button(trans_frame, text="+", command=self.increase_transparency,
                 bg=self.button_bg, fg=self.fg_color, font=('Arial', status_font_size),
                 width=button_size, height=1, relief=tk.FLAT)
        trans_plus_btn.pack(side=tk.LEFT, padx=1)
        self.create_tooltip(trans_plus_btn, "Increase Transparency")
        
        # Main text area
        self.create_hud_editor()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def create_hud_editor(self):
        """Create the HUD-style text editor with syntax highlighting"""
        editor_frame = tk.Frame(self.root, bg=self.bg_color)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.text_area = ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.select_bg,
            font=('Consolas', self.config['font_size']),
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.accent_color,
            highlightbackground='#333333',
            undo=True,
            maxundo=50
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        self.setup_syntax_highlighting()
        
        self.text_area.bind('<KeyRelease>', self.on_text_change_with_highlighting)
        self.text_area.bind('<Button-1>', self.on_text_change)
        
        self.create_context_menu()

    def setup_syntax_highlighting(self):
        """Setup syntax highlighting tags"""
        # Code blocks
        self.text_area.tag_configure("code_block", background="#2a2a2a", foreground="#e6e6e6", 
                                    font=('Consolas', self.config['font_size'], 'normal'))
        
        # Keywords
        self.text_area.tag_configure("keyword", foreground="#ff6b6b", font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("builtin", foreground="#4ecdc4", font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("string", foreground="#95e1d3", font=('Consolas', self.config['font_size'], 'normal'))
        self.text_area.tag_configure("comment", foreground="#888888", font=('Consolas', self.config['font_size'], 'italic'))
        self.text_area.tag_configure("number", foreground="#ffd93d", font=('Consolas', self.config['font_size'], 'bold'))
        
        # File paths
        self.text_area.tag_configure("filepath", foreground="#ff9f43", background="#3a2a1a", 
                                    font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("directory", foreground="#3742fa", background="#1a1a3a",
                                    font=('Consolas', self.config['font_size'], 'bold'))
        
        # URLs
        self.text_area.tag_configure("url", foreground="#70a1ff", underline=True,
                                    font=('Consolas', self.config['font_size'], 'normal'))
        
        # Markdown
        self.text_area.tag_configure("heading", foreground="#ff6348", 
                                    font=('Consolas', self.config['font_size'] + 2, 'bold'))
        self.text_area.tag_configure("bold", foreground="#ffffff", 
                                    font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("italic", foreground="#cccccc", 
                                    font=('Consolas', self.config['font_size'], 'italic'))
        self.text_area.tag_configure("list_item", foreground="#52c41a",
                                    font=('Consolas', self.config['font_size'], 'normal'))
        
        # Special
        self.text_area.tag_configure("important", foreground="#ff4757", background="#3a1a1a",
                                    font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("todo", foreground="#ffa502", background="#3a2a1a",
                                    font=('Consolas', self.config['font_size'], 'bold'))
        self.text_area.tag_configure("done", foreground="#2ed573", background="#1a3a1a",
                                    font=('Consolas', self.config['font_size'], 'bold'))

    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to the entire text"""
        content = self.text_area.get(1.0, tk.END)
        
        # Clear existing tags
        for tag in self.text_area.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_area.tag_delete(tag)
        
        # Reapply highlighting
        self.highlight_markdown(content)
        self.highlight_code_blocks(content)
        self.highlight_file_paths(content)
        self.highlight_urls(content)
        self.highlight_special_keywords(content)

    def highlight_markdown(self, content):
        """Highlight markdown elements"""
        import re
        
        # Headers
        header_pattern = r'^#+\s.*'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("heading", start_pos, end_pos)
        
        # Bold
        bold_pattern = r'\*\*[^*]+\*\*'
        for match in re.finditer(bold_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("bold", start_pos, end_pos)
        
        # Italic
        italic_pattern = r'\*[^*]+\*'
        for match in re.finditer(italic_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("italic", start_pos, end_pos)
        
        # List items
        list_pattern = r'^[\s]*[-*+]\s.*'
        for match in re.finditer(list_pattern, content, re.MULTILINE):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("list_item", start_pos, end_pos)

    def highlight_code_blocks(self, content):
        """Highlight code blocks"""
        import re
        
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("code_block", start_pos, end_pos)

    def highlight_file_paths(self, content):
        """Highlight file paths and directories"""
        import re
        
        # File patterns
        file_patterns = [
            r'[A-Za-z]:\\(?:[^\\/:*?"<>|\n]+\\)*[^\\/:*?"<>|\n]*\.[A-Za-z0-9]+',
            r'/(?:[^/\n]+/)*[^/\n]*\.[A-Za-z0-9]+',
            r'\.\/[^\s\n]+',
            r'~\/[^\s\n]+',
        ]
        
        for pattern in file_patterns:
            for match in re.finditer(pattern, content):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_area.tag_add("filepath", start_pos, end_pos)

    def highlight_urls(self, content):
        """Highlight URLs"""
        import re
        
        url_pattern = r'https?://[^\s\n]+'
        for match in re.finditer(url_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_area.tag_add("url", start_pos, end_pos)

    def highlight_special_keywords(self, content):
        """Highlight special keywords"""
        import re
        
        special_patterns = {
            'todo': r'\b(?:TODO|FIXME|HACK|BUG)\b[^\n]*',
            'important': r'\b(?:IMPORTANT|CRITICAL|WARNING|ERROR)\b[^\n]*',
            'done': r'\b(?:DONE|COMPLETED|FIXED|RESOLVED)\b[^\n]*'
        }
        
        for tag, pattern in special_patterns.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_area.tag_add(tag, start_pos, end_pos)

    def on_text_change_with_highlighting(self, event=None):
        """Handle text changes with syntax highlighting"""
        self.on_text_change(event)
        
        if hasattr(self, '_highlight_timer'):
            self.root.after_cancel(self._highlight_timer)
        
        self._highlight_timer = self.root.after(300, self.apply_syntax_highlighting)

    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.button_bg, fg=self.fg_color)
        self.context_menu.add_command(label="Undo", command=lambda: self.text_area.edit_undo())
        self.context_menu.add_command(label="Redo", command=lambda: self.text_area.edit_redo())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=lambda: self.text_area.event_generate("<<SelectAll>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Insert Code Block", command=self.open_code_window)
        self.context_menu.add_command(label="New Note (Template)", command=self.new_note)
        
        def show_context_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
        
        self.text_area.bind("<Button-3>", show_context_menu)

    def create_resize_handles(self):
        """Create custom resize handles for the window"""
        self.resize_border_width = 8
        self.resizing = False
        self.resize_direction = None
        
        # Bind mouse events for resize detection
        self.root.bind('<Motion>', self.on_mouse_motion)
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_release)
        
    def on_mouse_motion(self, event):
        """Handle mouse motion for resize cursor changes"""
        if self.resizing or hasattr(self, 'dragging') and self.dragging:
            return
            
        x, y = event.x, event.y
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Skip if in title bar area (for dragging)
        title_height = max(35, int(35 * self.dpi_scale))
        if y <= title_height:
            self.resize_direction = None
            return
        
        # Determine resize direction based on mouse position
        cursor = ""
        self.resize_direction = None
        
        # Right edge
        if width - self.resize_border_width <= x <= width:
            if height - self.resize_border_width <= y <= height:
                cursor = "bottom_right_corner"
                self.resize_direction = "se"
            elif title_height <= y <= self.resize_border_width + title_height:
                cursor = "top_right_corner"
                self.resize_direction = "ne"
            else:
                cursor = "sb_h_double_arrow"
                self.resize_direction = "e"
        
        # Left edge
        elif 0 <= x <= self.resize_border_width:
            if height - self.resize_border_width <= y <= height:
                cursor = "bottom_left_corner"
                self.resize_direction = "sw"
            elif title_height <= y <= self.resize_border_width + title_height:
                cursor = "top_left_corner"
                self.resize_direction = "nw"
            else:
                cursor = "sb_h_double_arrow"
                self.resize_direction = "w"
        
        # Bottom edge
        elif height - self.resize_border_width <= y <= height:
            cursor = "sb_v_double_arrow"
            self.resize_direction = "s"
        
        # Top edge (below title bar)
        elif title_height <= y <= self.resize_border_width + title_height:
            cursor = "sb_v_double_arrow"
            self.resize_direction = "n"
        
        else:
            cursor = ""
            self.resize_direction = None
        
        self.root.config(cursor=cursor)

    def on_mouse_click(self, event):
        """Handle mouse click for resize start"""
        if self.resize_direction:
            self.resizing = True
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_width = self.root.winfo_width()
            self.resize_start_height = self.root.winfo_height()
            self.resize_start_window_x = self.root.winfo_x()
            self.resize_start_window_y = self.root.winfo_y()
            self.update_status("Resizing window...")
            return "break"  # Prevent other click handlers

    def on_mouse_drag(self, event):
        """Handle mouse drag for resizing"""
        if not self.resizing:
            return
        
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        
        new_width = self.resize_start_width
        new_height = self.resize_start_height
        new_x = self.resize_start_window_x
        new_y = self.resize_start_window_y
        
        # Minimum window size
        min_width, min_height = 300, 200
        
        if 'e' in self.resize_direction:  # East (right)
            new_width = max(min_width, self.resize_start_width + dx)
        
        if 'w' in self.resize_direction:  # West (left)
            new_width = max(min_width, self.resize_start_width - dx)
            if new_width > min_width:
                new_x = self.resize_start_window_x + dx
        
        if 's' in self.resize_direction:  # South (bottom)
            new_height = max(min_height, self.resize_start_height + dy)
        
        if 'n' in self.resize_direction:  # North (top)
            new_height = max(min_height, self.resize_start_height - dy)
            if new_height > min_height:
                new_y = self.resize_start_window_y + dy
        
        # Apply the new geometry
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def on_mouse_release(self, event):
        """Handle mouse release to end resizing"""
        if self.resizing:
            self.resizing = False
            self.resize_direction = None
            self.root.config(cursor="")
            
            # Update config with new size
            geometry = self.root.geometry()
            if '+' in geometry:
                try:
                    size, position = geometry.split('+', 1)
                    width, height = size.split('x')
                    x, y = position.split('+')
                    self.config.update({
                        'window_width': int(width),
                        'window_height': int(height),
                        'window_x': int(x),
                        'window_y': int(y)
                    })
                    self.save_config()
                    self.update_status(f"Window resized to {width}x{height}")
                except:
                    pass

    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("HUD Notes Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg='#1a1a1a')
        settings_window.attributes('-topmost', True)
        settings_window.resizable(True, True)
        
        # Center the window
        current_display = self.displays[self.current_display]
        x = current_display['x'] + (current_display['width'] - 600) // 2
        y = current_display['y'] + (current_display['height'] - 500) // 2
        settings_window.geometry(f"600x500+{x}+{y}")
        
        # Ensure it shows properly
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_force()
        
        # Main frame with scrollable content
        main_frame = tk.Frame(settings_window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="⚙ HUD Notes Settings", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#333333', foreground='#ffffff', 
                       padding=[20, 8], borderwidth=1)
        style.map('TNotebook.Tab', background=[('selected', '#00ff41'), ('active', '#555555')],
                 foreground=[('selected', '#000000')])
        
        # Colors Tab
        colors_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(colors_frame, text='Colors & Theme')
        
        self.create_colors_tab(colors_frame)
        
        # Hotkeys Tab
        hotkeys_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(hotkeys_frame, text='Hotkeys')
        
        self.create_hotkeys_tab(hotkeys_frame)
        
        # Advanced Tab (placeholder)
        advanced_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(advanced_frame, text='Advanced')
        
        self.create_advanced_tab(advanced_frame)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X)
        
        def apply_settings():
            """Apply settings and close dialog"""
            self.apply_color_settings()
            self.apply_hotkey_settings()
            self.apply_advanced_settings()
            self.save_config()
            settings_window.destroy()
            self.update_status("Settings applied")
        
        def reset_defaults():
            """Reset to default settings"""
            if messagebox.askyesno("Reset Settings", 
                                  "Reset all settings to defaults? This cannot be undone."):
                self.reset_default_settings()
                settings_window.destroy()
                self.open_settings()  # Reopen with defaults
        
        # Button styling
        button_style = {
            'font': ('Consolas', 11, 'bold'),
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8
        }
        
        tk.Button(button_frame, text="✓ Apply & Close", command=apply_settings,
                 bg='#006600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Reset Defaults", command=reset_defaults,
                 bg='#cc6600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✗ Cancel", command=settings_window.destroy,
                 bg='#660000', fg='white', **button_style).pack(side=tk.RIGHT, padx=5)
        
        # Keyboard shortcuts
        settings_window.bind('<Return>', lambda e: apply_settings())
        settings_window.bind('<Escape>', lambda e: settings_window.destroy())
        
        # Handle window close button
        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

    def create_colors_tab(self, parent):
        """Create colors and theme settings tab"""
        # Color schemes
        schemes_frame = tk.LabelFrame(parent, text="Color Schemes", 
                                     bg='#1a1a1a', fg='#00ff41',
                                     font=('Consolas', 12, 'bold'))
        schemes_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.color_scheme_var = tk.StringVar(value=self.config.get('color_scheme', 'Matrix Green'))
        
        color_schemes = {
            'Matrix Green': {'bg': '#0a0a0a', 'fg': '#00ff41', 'accent': '#ff6600', 'select': '#1a3d1a'},
            'Cyber Blue': {'bg': '#0a0a1a', 'fg': '#00ccff', 'accent': '#ff6600', 'select': '#1a1a3d'},
            'Neon Purple': {'bg': '#1a0a1a', 'fg': '#cc00ff', 'accent': '#ffff00', 'select': '#3d1a3d'},
            'Hacker Orange': {'bg': '#1a1a0a', 'fg': '#ff9900', 'accent': '#00ff00', 'select': '#3d3d1a'},
            'Terminal White': {'bg': '#000000', 'fg': '#ffffff', 'accent': '#ffff00', 'select': '#333333'},
            'Blood Red': {'bg': '#1a0000', 'fg': '#ff3333', 'accent': '#ffff00', 'select': '#3d1a1a'},
        }
        
        for i, (scheme_name, colors) in enumerate(color_schemes.items()):
            row = i // 2
            col = i % 2
            
            scheme_frame = tk.Frame(schemes_frame, bg='#1a1a1a')
            scheme_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            # Radio button
            rb = tk.Radiobutton(scheme_frame, text=scheme_name, 
                               variable=self.color_scheme_var, value=scheme_name,
                               bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                               font=('Consolas', 10))
            rb.pack(side=tk.LEFT)
            
            # Color preview
            preview_frame = tk.Frame(scheme_frame, bg=colors['bg'], width=60, height=20,
                                   relief=tk.SOLID, bd=1)
            preview_frame.pack(side=tk.LEFT, padx=10)
            preview_frame.pack_propagate(False)
            
            preview_label = tk.Label(preview_frame, text="ABC", 
                                   bg=colors['bg'], fg=colors['fg'],
                                   font=('Consolas', 8, 'bold'))
            preview_label.pack(expand=True)
        
        # Custom colors section
        custom_frame = tk.LabelFrame(parent, text="Custom Colors", 
                                   bg='#1a1a1a', fg='#00ff41',
                                   font=('Consolas', 12, 'bold'))
        custom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Store color variables
        self.custom_bg_var = tk.StringVar(value=self.config.get('custom_bg_color', '#0a0a0a'))
        self.custom_fg_var = tk.StringVar(value=self.config.get('custom_fg_color', '#00ff41'))
        self.custom_accent_var = tk.StringVar(value=self.config.get('custom_accent_color', '#ff6600'))
        
        def choose_color(color_var, color_name):
            """Open color chooser dialog"""
            import tkinter.colorchooser as colorchooser
            color = colorchooser.askcolor(initialcolor=color_var.get())
            if color[1]:  # If user didn't cancel
                color_var.set(color[1])
        
        # Background color
        bg_frame = tk.Frame(custom_frame, bg='#1a1a1a')
        bg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(bg_frame, text="Background:", bg='#1a1a1a', fg='#ffffff',
                font=('Consolas', 10)).pack(side=tk.LEFT)
        
        bg_color_btn = tk.Button(bg_frame, text="█████", 
                               fg=self.custom_bg_var.get(), bg=self.custom_bg_var.get(),
                               font=('Consolas', 10, 'bold'),
                               command=lambda: choose_color(self.custom_bg_var, "Background"))
        bg_color_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Label(bg_frame, textvariable=self.custom_bg_var, bg='#1a1a1a', fg='#888888',
                font=('Consolas', 9)).pack(side=tk.LEFT, padx=10)
        
        # Foreground color
        fg_frame = tk.Frame(custom_frame, bg='#1a1a1a')
        fg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(fg_frame, text="Text Color:", bg='#1a1a1a', fg='#ffffff',
                font=('Consolas', 10)).pack(side=tk.LEFT)
        
        fg_color_btn = tk.Button(fg_frame, text="█████", 
                               fg=self.custom_fg_var.get(), bg=self.custom_fg_var.get(),
                               font=('Consolas', 10, 'bold'),
                               command=lambda: choose_color(self.custom_fg_var, "Text"))
        fg_color_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Label(fg_frame, textvariable=self.custom_fg_var, bg='#1a1a1a', fg='#888888',
                font=('Consolas', 9)).pack(side=tk.LEFT, padx=10)
        
        # Accent color
        accent_frame = tk.Frame(custom_frame, bg='#1a1a1a')
        accent_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(accent_frame, text="Accent Color:", bg='#1a1a1a', fg='#ffffff',
                font=('Consolas', 10)).pack(side=tk.LEFT)
        
        accent_color_btn = tk.Button(accent_frame, text="█████", 
                                   fg=self.custom_accent_var.get(), bg=self.custom_accent_var.get(),
                                   font=('Consolas', 10, 'bold'),
                                   command=lambda: choose_color(self.custom_accent_var, "Accent"))
        accent_color_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Label(accent_frame, textvariable=self.custom_accent_var, bg='#1a1a1a', fg='#888888',
                font=('Consolas', 9)).pack(side=tk.LEFT, padx=10)

    def create_hotkeys_tab(self, parent):
        """Create hotkeys settings tab"""
        # Instructions
        instructions = tk.Label(parent, 
                               text="Click on a hotkey field and press your desired key combination.\n"
                                   "Use combinations like Ctrl+Alt+T, Ctrl+Shift+N, etc.",
                               bg='#1a1a1a', fg='#cccccc', font=('Consolas', 10),
                               justify=tk.LEFT, wraplength=550)
        instructions.pack(pady=10, padx=10, anchor='w')
        
        # Hotkeys frame
        hotkeys_frame = tk.Frame(parent, bg='#1a1a1a')
        hotkeys_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Default hotkeys
        default_hotkeys = {
            'toggle_overlay': 'Ctrl+Alt+T',
            'new_note': 'Ctrl+Alt+N',
            'open_note': 'Ctrl+Alt+O',
            'save_note': 'Ctrl+Alt+S',
            'save_as': 'Ctrl+Alt+Shift+S',
            'code_window': 'Ctrl+Alt+C',
            'toggle_preview': 'Ctrl+Alt+P',
            'reset_position': 'Ctrl+Alt+R',
            'move_corner_1': 'Ctrl+Alt+1',
            'move_corner_2': 'Ctrl+Alt+2',
            'move_corner_3': 'Ctrl+Alt+3',
            'move_corner_4': 'Ctrl+Alt+4',
            'center_window': 'Ctrl+Alt+5',
        }
        
        # Store hotkey variables
        self.hotkey_vars = {}
        
        hotkey_descriptions = {
            'toggle_overlay': 'Toggle HUD Overlay',
            'new_note': 'New Note',
            'open_note': 'Open Note',
            'save_note': 'Save Note',
            'save_as': 'Save As...',
            'code_window': 'Code Input Window',
            'toggle_preview': 'Toggle Preview',
            'reset_position': 'Reset Window Position',
            'move_corner_1': 'Move to Top-Left',
            'move_corner_2': 'Move to Top-Right',
            'move_corner_3': 'Move to Bottom-Left',
            'move_corner_4': 'Move to Bottom-Right',
            'center_window': 'Center Window',
        }
        
        for i, (key, description) in enumerate(hotkey_descriptions.items()):
            row_frame = tk.Frame(hotkeys_frame, bg='#1a1a1a')
            row_frame.pack(fill=tk.X, pady=2)
            
            # Description
            desc_label = tk.Label(row_frame, text=description + ":", 
                                 bg='#1a1a1a', fg='#ffffff',
                                 font=('Consolas', 10), width=20, anchor='w')
            desc_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Hotkey entry
            current_hotkey = self.config.get('hotkeys', {}).get(key, default_hotkeys[key])
            hotkey_var = tk.StringVar(value=current_hotkey)
            self.hotkey_vars[key] = hotkey_var
            
            hotkey_entry = tk.Entry(row_frame, textvariable=hotkey_var,
                                  bg='#333333', fg='#ffffff', font=('Consolas', 10),
                                  insertbackground='#00ff41', width=20, state='readonly')
            hotkey_entry.pack(side=tk.LEFT, padx=(0, 10))
            
            def bind_hotkey_capture(entry, var, action_key):
                def capture_hotkey(event):
                    # Capture the key combination
                    modifiers = []
                    if event.state & 0x4:  # Control
                        modifiers.append('Ctrl')
                    if event.state & 0x8:  # Alt
                        modifiers.append('Alt')
                    if event.state & 0x1:  # Shift
                        modifiers.append('Shift')
                    
                    key = event.keysym
                    if key not in ['Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R']:
                        hotkey_string = '+'.join(modifiers + [key])
                        var.set(hotkey_string)
                        entry.config(state='readonly')
                
                def enable_capture(event):
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, "Press key combination...")
                    entry.bind('<KeyPress>', capture_hotkey)
                
                entry.bind('<Button-1>', enable_capture)
            
            bind_hotkey_capture(hotkey_entry, hotkey_var, key)
            
            # Reset button
            reset_btn = tk.Button(row_frame, text="Reset", 
                                command=lambda k=key: self.hotkey_vars[k].set(default_hotkeys[k]),
                                bg='#555555', fg='#ffffff', font=('Consolas', 8),
                                relief=tk.FLAT, padx=10, pady=2)
            reset_btn.pack(side=tk.LEFT)

    def create_advanced_tab(self, parent):
        """Create advanced settings tab"""
        # Auto-show/hide settings
        autohide_frame = tk.LabelFrame(parent, text="Auto Show/Hide Features", 
                                     bg='#1a1a1a', fg='#00ff41',
                                     font=('Consolas', 12, 'bold'))
        autohide_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Mouse hover trigger
        hover_frame = tk.Frame(autohide_frame, bg='#1a1a1a')
        hover_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.mouse_hover_var = tk.BooleanVar(value=self.config.get('mouse_hover_show', False))
        hover_cb = tk.Checkbutton(hover_frame, text="Show overlay when hovering top-left corner", 
                              variable=self.mouse_hover_var,
                              bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                              font=('Consolas', 10))
        hover_cb.pack(anchor='w')
        
        hover_desc = tk.Label(hover_frame, 
                            text="When overlay is hidden, hover mouse in top-left corner (50x50 pixels) to show it",
                            bg='#1a1a1a', fg='#888888', font=('Consolas', 9),
                            wraplength=500, justify=tk.LEFT)
        hover_desc.pack(anchor='w', padx=20, pady=(5, 0))
        
        # Click outside to hide
        clickhide_frame = tk.Frame(autohide_frame, bg='#1a1a1a')
        clickhide_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.click_hide_var = tk.BooleanVar(value=self.config.get('click_outside_hide', False))
        click_cb = tk.Checkbutton(clickhide_frame, text="Hide overlay when clicking outside", 
                              variable=self.click_hide_var,
                              bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                              font=('Consolas', 10))
        click_cb.pack(anchor='w')
        
        click_desc = tk.Label(clickhide_frame, 
                            text="Click anywhere outside the overlay window to hide it automatically",
                            bg='#1a1a1a', fg='#888888', font=('Consolas', 9),
                            wraplength=500, justify=tk.LEFT)
        click_desc.pack(anchor='w', padx=20, pady=(5, 0))
        
        # Separator
        separator = tk.Frame(parent, bg='#333333', height=2)
        separator.pack(fill=tk.X, padx=20, pady=20)
        
        # Future features placeholder
        placeholder_frame = tk.Frame(parent, bg='#1a1a1a')
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(placeholder_frame, text="🚧 Future Advanced Features", 
                bg='#1a1a1a', fg='#00ff41',
                font=('Consolas', 14, 'bold')).pack(pady=(0, 15))
        
        tk.Label(placeholder_frame, 
                text="Additional features planned for future releases:\n\n"
                     "• Plugin system configuration\n"
                     "• Advanced syntax highlighting rules\n"
                     "• Custom template variables\n"
                     "• Export/import settings\n"
                     "• Performance optimization options\n"
                     "• Integration with external tools\n"
                     "• Auto-backup settings\n"
                     "• Multiple window profiles\n\n"
                     "Have suggestions? Let us know!",
                bg='#1a1a1a', fg='#cccccc', font=('Consolas', 10),
                justify=tk.LEFT).pack(anchor='w')

    def apply_color_settings(self):
        """Apply selected color scheme"""
        scheme = self.color_scheme_var.get()
        
        color_schemes = {
            'Matrix Green': {'bg': '#0a0a0a', 'fg': '#00ff41', 'accent': '#ff6600', 'select': '#1a3d1a'},
            'Cyber Blue': {'bg': '#0a0a1a', 'fg': '#00ccff', 'accent': '#ff6600', 'select': '#1a1a3d'},
            'Neon Purple': {'bg': '#1a0a1a', 'fg': '#cc00ff', 'accent': '#ffff00', 'select': '#3d1a3d'},
            'Hacker Orange': {'bg': '#1a1a0a', 'fg': '#ff9900', 'accent': '#00ff00', 'select': '#3d3d1a'},
            'Terminal White': {'bg': '#000000', 'fg': '#ffffff', 'accent': '#ffff00', 'select': '#333333'},
            'Blood Red': {'bg': '#1a0000', 'fg': '#ff3333', 'accent': '#ffff00', 'select': '#3d1a1a'},
        }
        
        if scheme in color_schemes:
            colors = color_schemes[scheme]
            self.config['color_scheme'] = scheme
            self.config['bg_color'] = colors['bg']
            self.config['fg_color'] = colors['fg']
            self.config['accent_color'] = colors['accent']
            self.config['select_bg'] = colors['select']
        else:
            # Custom colors
            self.config['color_scheme'] = 'Custom'
            self.config['bg_color'] = self.custom_bg_var.get()
            self.config['fg_color'] = self.custom_fg_var.get()
            self.config['accent_color'] = self.custom_accent_var.get()
            self.config['select_bg'] = '#333333'
        
        # Apply colors immediately
        self.apply_theme_colors()

    def apply_hotkey_settings(self):
        """Apply hotkey settings"""
        hotkeys = {}
        for key, var in self.hotkey_vars.items():
            hotkeys[key] = var.get()
        
        self.config['hotkeys'] = hotkeys
        # Note: Hotkey rebinding would require restarting the global hotkey listener

    def apply_advanced_settings(self):
        """Apply advanced settings"""
        # Apply auto show/hide settings
        self.config['mouse_hover_show'] = self.mouse_hover_var.get()
        self.config['click_outside_hide'] = self.click_hide_var.get()
        
        # Setup or remove mouse hover monitoring
        if self.config['mouse_hover_show']:
            self.setup_mouse_hover_monitor()
        else:
            self.stop_mouse_hover_monitor()
        
        # Setup or remove click outside monitoring
        if self.config['click_outside_hide']:
            self.setup_click_outside_monitor()
        else:
            self.stop_click_outside_monitor()

    def apply_theme_colors(self):
        """Apply current theme colors to the interface"""
        # Update theme colors
        self.bg_color = self.config.get('bg_color', '#0a0a0a')
        self.fg_color = self.config.get('fg_color', '#00ff41')
        self.accent_color = self.config.get('accent_color', '#ff6600')
        self.select_bg = self.config.get('select_bg', '#1a3d1a')
        
        # Apply to root window
        self.root.configure(bg=self.bg_color)
        
        # Apply to text area
        self.text_area.configure(bg=self.bg_color, fg=self.fg_color, 
                                selectbackground=self.select_bg,
                                insertbackground=self.fg_color)
        
        # Apply to file label
        self.file_label.configure(fg=self.accent_color)
        
        # Apply to status label
        self.status_label.configure(bg='#1a1a1a', fg=self.fg_color)
        
        # Reapply syntax highlighting with new colors
        self.setup_syntax_highlighting()
        self.apply_syntax_highlighting()

    def reset_default_settings(self):
        """Reset all settings to defaults"""
        defaults = {
            'color_scheme': 'Matrix Green',
            'bg_color': '#0a0a0a',
            'fg_color': '#00ff41',
            'accent_color': '#ff6600',
            'select_bg': '#1a3d1a',
            'mouse_hover_show': False,
            'click_outside_hide': False,
            'hotkeys': {
                'toggle_overlay': 'Ctrl+Alt+T',
                'new_note': 'Ctrl+Alt+N',
                'open_note': 'Ctrl+Alt+O',
                'save_note': 'Ctrl+Alt+S',
                'save_as': 'Ctrl+Alt+Shift+S',
                'code_window': 'Ctrl+Alt+C',
                'toggle_preview': 'Ctrl+Alt+P',
                'reset_position': 'Ctrl+Alt+R',
                'move_corner_1': 'Ctrl+Alt+1',
                'move_corner_2': 'Ctrl+Alt+2',
                'move_corner_3': 'Ctrl+Alt+3',
                'move_corner_4': 'Ctrl+Alt+4',
                'center_window': 'Ctrl+Alt+5',
            }
        }
        
        for key, value in defaults.items():
            self.config[key] = value
        
        self.apply_theme_colors()
        self.save_config()
        self.update_status("Settings reset to defaults")

    def setup_mouse_hover_monitor(self):
        """Setup mouse hover monitoring for top-left corner"""
        if hasattr(self, 'hover_monitor_thread') and self.hover_monitor_thread.is_alive():
            return
        
        self.hover_monitor_active = True
        
        def hover_monitor():
            import time
            while self.hover_monitor_active:
                try:
                    if not self.overlay_visible:
                        # Get mouse position
                        mouse_x = self.root.winfo_pointerx()
                        mouse_y = self.root.winfo_pointery()
                        
                        # Check if mouse is in top-left corner (50x50 pixels)
                        if mouse_x <= 50 and mouse_y <= 50:
                            # Show overlay
                            self.root.after(0, self.show_overlay)
                            time.sleep(1)  # Prevent rapid toggling
                    
                    time.sleep(0.1)  # Check every 100ms
                except Exception as e:
                    print(f"Hover monitor error: {e}")
                    break
        
        self.hover_monitor_thread = threading.Thread(target=hover_monitor, daemon=True)
        self.hover_monitor_thread.start()

    def stop_mouse_hover_monitor(self):
        """Stop mouse hover monitoring"""
        self.hover_monitor_active = False
        if hasattr(self, 'hover_monitor_thread'):
            try:
                self.hover_monitor_thread.join(timeout=1)
            except:
                pass

    def setup_click_outside_monitor(self):
        """Setup click outside monitoring"""
        def on_global_click(x, y, button, pressed):
            if pressed and self.overlay_visible:
                # Get overlay window bounds
                try:
                    win_x = self.root.winfo_x()
                    win_y = self.root.winfo_y()
                    win_width = self.root.winfo_width()
                    win_height = self.root.winfo_height()
                    
                    # Check if click is outside overlay
                    if not (win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height):
                        # Hide overlay
                        self.root.after(0, self.hide_overlay)
                except:
                    pass
        
        if not hasattr(self, 'click_listener') or not self.click_listener.running:
            from pynput import mouse
            self.click_listener = mouse.Listener(on_click=on_global_click)
            self.click_listener.start()

    def stop_click_outside_monitor(self):
        """Stop click outside monitoring"""
        if hasattr(self, 'click_listener') and self.click_listener.running:
            self.click_listener.stop()

    def setup_hotkey(self):
        """Setup global hotkey"""
        def on_hotkey():
            self.toggle_overlay()
        
        def hotkey_listener():
            try:
                with keyboard.GlobalHotKeys({'<ctrl>+<alt>+t': on_hotkey}):
                    import time
                    while True:
                        time.sleep(0.1)
            except Exception as e:
                print(f"Hotkey listener error: {e}")
        
        hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        hotkey_thread.start()

    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay_visible:
            self.hide_overlay()
        else:
            self.show_overlay()

    def show_overlay(self):
        """Show the overlay"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.overlay_visible = True
        self.text_area.focus()
        self.update_status("HUD Activated")

    def hide_overlay(self):
        """Hide the overlay"""
        geometry = self.root.geometry()
        if '+' in geometry:
            try:
                size, position = geometry.split('+', 1)
                width, height = size.split('x')
                x, y = position.split('+')
                self.config.update({
                    'window_width': int(width),
                    'window_height': int(height),
                    'window_x': int(x),
                    'window_y': int(y)
                })
            except:
                pass
        
        self.root.withdraw()
        self.overlay_visible = False
        self.save_config()

    def on_closing(self):
        """Handle application closing"""
        if self.current_file and self.text_area.get(1.0, tk.END).strip():
            self.auto_save()
        
        # Stop advanced feature monitors
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
        
        if hasattr(self, 'border_windows'):
            for border in self.border_windows:
                try:
                    border.destroy()
                except:
                    pass
        
        if hasattr(self, 'hotkey_window'):
            try:
                self.hotkey_window.destroy()
            except:
                pass
        
        self.save_config()
        self.root.quit()
        self.root.destroy()

    def reset_to_quarter_screen(self, event=None):
        """Reset window to right 1/4 of current display"""
        self.get_display_settings()
        
        self.config.update({
            'window_width': self.calculated_width,
            'window_height': self.calculated_height,
            'window_x': self.calculated_x,
            'window_y': self.calculated_y,
            'font_size': self.scaled_font_size
        })
        
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}+"
                          f"{self.config['window_x']}+{self.config['window_y']}")
        
        self.update_fonts()
        self.save_config()
        
        display_name = self.displays[self.current_display]['name']
        self.update_status(f"Reset to right 1/4 of {display_name}")

    def start_drag(self, event):
        """Start window dragging"""
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()
        self.dragging = True
        self.root.config(cursor="fleur")
        event.widget.config(cursor="fleur")
        self.update_status("Dragging window...")

    def on_drag(self, event):
        """Handle window dragging"""
        if hasattr(self, 'dragging') and self.dragging:
            x = event.x_root - self.drag_x
            y = event.y_root - self.drag_y
            
            x = max(0, min(x, self.screen_width - self.config['window_width']))
            y = max(0, min(y, self.screen_height - self.config['window_height'] - 50))
            
            self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        """Stop window dragging"""
        self.dragging = False
        self.root.config(cursor="")
        event.widget.config(cursor="")
        self.update_status("Window positioned")
        
        geometry = self.root.geometry()
        if '+' in geometry:
            try:
                size, position = geometry.split('+', 1)
                x, y = position.split('+')
                self.config['window_x'] = int(x)
                self.config['window_y'] = int(y)
                self.save_config()
            except:
                pass

    def on_focus_in(self, event):
        """Handle focus in"""
        self.root.attributes('-alpha', min(1.0, self.config['hud_transparency'] + 0.1))

    def on_focus_out(self, event):
        """Handle focus out"""
        self.root.attributes('-alpha', self.config['hud_transparency'])

    def increase_transparency(self):
        """Increase transparency"""
        self.config['hud_transparency'] = max(0.3, self.config['hud_transparency'] - 0.1)
        self.root.attributes('-alpha', self.config['hud_transparency'])
        self.update_status(f"Transparency: {int(self.config['hud_transparency']*100)}%")

    def decrease_transparency(self):
        """Decrease transparency"""
        self.config['hud_transparency'] = min(1.0, self.config['hud_transparency'] + 0.1)
        self.root.attributes('-alpha', self.config['hud_transparency'])
        self.update_status(f"Transparency: {int(self.config['hud_transparency']*100)}%")

    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text=f"Ready | Display Scale: {int(self.dpi_scale * 100)}%"))

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-Alt-n>', lambda e: self.new_note())
        self.root.bind('<Control-Alt-o>', lambda e: self.open_note())
        self.root.bind('<Control-Alt-s>', lambda e: self.save_note())
        self.root.bind('<Control-Alt-S>', lambda e: self.save_as_note())
        self.root.bind('<Control-Alt-p>', lambda e: self.toggle_preview())
        self.root.bind('<Control-Alt-plus>', lambda e: self.increase_font())
        self.root.bind('<Control-Alt-minus>', lambda e: self.decrease_font())
        self.root.bind('<Control-Alt-c>', lambda e: self.open_code_window())
        self.root.bind('<Control-Alt-q>', lambda e: self.on_closing())
        self.root.bind('<Control-Alt-r>', lambda e: self.reset_to_quarter_screen())
        self.root.bind('<Control-Alt-m>', lambda e: self.move_to_next_display())
        self.root.bind('<Control-Alt-g>', lambda e: self.open_settings())  # Settings hotkey
        
        # Window positioning shortcuts - multiple binding formats for compatibility
        self.root.bind('<Control-Alt-Key-1>', lambda e: self.move_to_corner('top-left'))
        self.root.bind('<Control-Alt-1>', lambda e: self.move_to_corner('top-left'))
        self.root.bind('<Control-Alt-Key-2>', lambda e: self.move_to_corner('top-right'))
        self.root.bind('<Control-Alt-2>', lambda e: self.move_to_corner('top-right'))
        self.root.bind('<Control-Alt-Key-3>', lambda e: self.move_to_corner('bottom-left'))
        self.root.bind('<Control-Alt-3>', lambda e: self.move_to_corner('bottom-left'))
        self.root.bind('<Control-Alt-Key-4>', lambda e: self.move_to_corner('bottom-right'))
        self.root.bind('<Control-Alt-4>', lambda e: self.move_to_corner('bottom-right'))
        self.root.bind('<Control-Alt-Key-5>', lambda e: self.center_window())
        self.root.bind('<Control-Alt-5>', lambda e: self.center_window())
        
        # Also bind to text area to ensure they work when typing
        self.text_area.bind('<Control-Alt-Key-1>', lambda e: self.move_to_corner('top-left'))
        self.text_area.bind('<Control-Alt-1>', lambda e: self.move_to_corner('top-left'))
        self.text_area.bind('<Control-Alt-Key-2>', lambda e: self.move_to_corner('top-right'))
        self.text_area.bind('<Control-Alt-2>', lambda e: self.move_to_corner('top-right'))
        self.text_area.bind('<Control-Alt-Key-3>', lambda e: self.move_to_corner('bottom-left'))
        self.text_area.bind('<Control-Alt-3>', lambda e: self.move_to_corner('bottom-left'))
        self.text_area.bind('<Control-Alt-Key-4>', lambda e: self.move_to_corner('bottom-right'))
        self.text_area.bind('<Control-Alt-4>', lambda e: self.move_to_corner('bottom-right'))
        self.text_area.bind('<Control-Alt-Key-5>', lambda e: self.center_window())
        self.text_area.bind('<Control-Alt-5>', lambda e: self.center_window())
        
        # Add debug messages for testing
        def debug_corner_move(corner, event=None):
            print(f"Moving to {corner}")
            self.move_to_corner(corner)
            return "break"  # Prevent further processing
            
        def debug_center(event=None):
            print("Centering window")
            self.center_window()
            return "break"
        
        # Bind with debug versions for troubleshooting
        self.root.bind('<Control-Alt-KeyPress-1>', lambda e: debug_corner_move('top-left', e))
        self.root.bind('<Control-Alt-KeyPress-2>', lambda e: debug_corner_move('top-right', e))
        self.root.bind('<Control-Alt-KeyPress-3>', lambda e: debug_corner_move('bottom-left', e))
        self.root.bind('<Control-Alt-KeyPress-4>', lambda e: debug_corner_move('bottom-right', e))
        self.root.bind('<Control-Alt-KeyPress-5>', lambda e: debug_center(e))

    def open_code_window(self):
        """Open code input window"""
        code_window = tk.Toplevel(self.root)
        code_window.title("Code Input")
        code_window.geometry("600x400")
        code_window.configure(bg=self.bg_color)
        code_window.attributes('-topmost', True)
        
        current_display = self.displays[self.current_display]
        x = current_display['x'] + (current_display['width'] - 600) // 2
        y = current_display['y'] + (current_display['height'] - 400) // 2
        code_window.geometry(f"600x400+{x}+{y}")
        
        # Language selection
        lang_frame = tk.Frame(code_window, bg=self.bg_color)
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(lang_frame, text="Language:", bg=self.bg_color, fg=self.fg_color,
                font=('Consolas', 10, 'bold')).pack(side=tk.LEFT)
        
        languages = [
            'bash', 'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 'go', 'rust',
            'php', 'ruby', 'swift', 'kotlin', 'scala', 'html', 'css', 'sql', 'xml',
            'json', 'yaml', 'markdown', 'powershell', 'dockerfile', 'typescript', 'r'
        ]
        
        lang_var = tk.StringVar(value='bash')
        lang_dropdown = ttk.Combobox(lang_frame, textvariable=lang_var, values=languages,
                                   state='readonly', width=15)
        lang_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Code input area
        code_frame = tk.Frame(code_window, bg=self.bg_color)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(code_frame, text="Code:", bg=self.bg_color, fg=self.fg_color,
                font=('Consolas', 10, 'bold')).pack(anchor=tk.W)
        
        code_text = ScrolledText(
            code_frame,
            wrap=tk.NONE,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.select_bg,
            font=('Consolas', self.config['font_size']),
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.accent_color,
            highlightbackground='#333333',
            height=15
        )
        code_text.pack(fill=tk.BOTH, expand=True)
        
        code_text.focus()
        
        # Buttons
        button_frame = tk.Frame(code_window, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def insert_code():
            language = lang_var.get()
            code_content = code_text.get(1.0, tk.END).strip()
            
            if code_content:
                formatted_code = f"\n```{language}\n{code_content}\n```\n\n"
                cursor_pos = self.text_area.index(tk.INSERT)
                self.text_area.insert(cursor_pos, formatted_code)
                self.update_status(f"Inserted {language} code block")
                code_window.destroy()
            else:
                self.update_status("No code to insert")
        
        tk.Button(button_frame, text="Insert Code", command=insert_code,
                 bg='#006600', fg='white', font=('Consolas', 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=code_window.destroy,
                 bg='#660000', fg='white', font=('Consolas', 10),
                 relief=tk.FLAT, padx=20).pack(side=tk.RIGHT, padx=5)
        
        # Keyboard shortcuts
        code_window.bind('<Control-Return>', lambda e: insert_code())
        code_window.bind('<Escape>', lambda e: code_window.destroy())
        
        self.update_status("Code input window opened")

    def move_to_next_display(self):
        """Move to next display"""
        if len(self.displays) <= 1:
            self.update_status("Only one display detected")
            return
        
        self.current_display = (self.current_display + 1) % len(self.displays)
        self.calculate_display_layout()
        
        self.config.update({
            'window_width': self.calculated_width,
            'window_height': self.calculated_height,
            'window_x': self.calculated_x,
            'window_y': self.calculated_y
        })
        
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}+"
                          f"{self.config['window_x']}+{self.config['window_y']}")
        
        self.save_config()
        
        display_name = self.displays[self.current_display]['name']
        self.update_status(f"Moved to {display_name}")
        self.update_file_label()

    def center_window(self, event=None):
        """Center window on current display"""
        current_display = self.displays[self.current_display]
        
        x = current_display['x'] + (current_display['width'] - self.config['window_width']) // 2
        y = current_display['y'] + (current_display['height'] - self.config['window_height']) // 2
        
        self.root.geometry(f"+{x}+{y}")
        self.config['window_x'] = x
        self.config['window_y'] = y
        self.save_config()
        self.update_status(f"Window centered")

    def move_to_corner(self, position):
        """Move window to specified corner"""
        current_display = self.displays[self.current_display]
        margin = max(20, int(20 * self.dpi_scale))
        
        if position == 'top-left':
            x = current_display['x'] + margin
            y = current_display['y'] + margin
        elif position == 'top-right':
            x = current_display['x'] + current_display['width'] - self.config['window_width'] - margin
            y = current_display['y'] + margin
        elif position == 'bottom-left':
            x = current_display['x'] + margin
            y = current_display['y'] + current_display['height'] - self.config['window_height'] - 80
        elif position == 'bottom-right':
            x = current_display['x'] + current_display['width'] - self.config['window_width'] - margin
            y = current_display['y'] + current_display['height'] - self.config['window_height'] - 80
        
        self.root.geometry(f"+{x}+{y}")
        self.config['window_x'] = x
        self.config['window_y'] = y
        self.save_config()
        self.update_status(f"Moved to {position}")

    def new_note(self):
        """Create a new note with template selection"""
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno("New Note", "Save current note before creating new one?"):
                self.save_note()
        
        # Show template selection dialog
        self.show_template_selection()

    def open_note(self):
        """Open an existing note"""
        filename = filedialog.askopenfilename(
            initialdir=self.notes_dir,
            title="Open Note",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = filename
                self.config['last_file'] = filename
                self.update_file_label()
                self.update_status(f"Opened: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_note(self):
        """Save current note"""
        if not self.current_file:
            self.save_as_note()
            return
        
        try:
            content = self.text_area.get(1.0, tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.update_file_label()
            self.update_status(f"Saved: {os.path.basename(self.current_file)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def save_as_note(self):
        """Save note with new filename"""
        filename = filedialog.asksaveasfilename(
            initialdir=self.notes_dir,
            title="Save Note As",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.current_file = filename
            self.config['last_file'] = filename
            self.save_note()

    def update_file_label(self):
        """Update file label"""
        display_info = f"D{self.current_display + 1}/{len(self.displays)}"
        
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.config(text=f"{filename} [{display_info}]")
        else:
            self.file_label.config(text=f"UNSAVED [{display_info}]")

    def on_text_change(self, event=None):
        """Handle text changes"""
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        
        if self.current_file:
            self._save_timer = self.root.after(2000, self.auto_save)

    def auto_save(self):
        """Auto-save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status("Auto-saved")
            except:
                pass

    def toggle_preview(self):
        """Toggle markdown preview"""
        if hasattr(self, 'preview_frame') and self.preview_frame.winfo_viewable():
            self.preview_frame.pack_forget()
            self.text_area.pack(fill=tk.BOTH, expand=True)
            self.update_status("Preview hidden")
        else:
            if not hasattr(self, 'preview_frame'):
                self.preview_frame = self.create_preview()
            
            self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            self.update_preview()
            self.update_status("Preview shown")

    def create_preview(self):
        """Create markdown preview pane"""
        preview_frame = tk.Frame(self.root, bg=self.bg_color)
        
        self.preview_area = ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg='#cccccc',
            font=('Arial', self.config['font_size']),
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.preview_area.pack(fill=tk.BOTH, expand=True)
        
        return preview_frame

    def update_preview(self):
        """Update markdown preview"""
        if hasattr(self, 'preview_area') and self.preview_frame.winfo_viewable():
            try:
                content = self.text_area.get(1.0, tk.END)
                html = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
                
                import re
                text = re.sub(r'<[^>]+>', '', html)
                text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                
                self.preview_area.config(state=tk.NORMAL)
                self.preview_area.delete(1.0, tk.END)
                self.preview_area.insert(1.0, text)
                self.preview_area.config(state=tk.DISABLED)
                
            except:
                pass

    def increase_font(self):
        """Increase font size"""
        self.config['font_size'] = min(24, self.config['font_size'] + 1)
        self.update_fonts()
        self.update_status(f"Font size: {self.config['font_size']}")

    def decrease_font(self):
        """Decrease font size"""
        self.config['font_size'] = max(8, self.config['font_size'] - 1)
        self.update_fonts()
        self.update_status(f"Font size: {self.config['font_size']}")

    def update_fonts(self):
        """Update font sizes"""
        self.text_area.config(font=('Consolas', self.config['font_size']))
        if hasattr(self, 'preview_area'):
            self.preview_area.config(font=('Arial', self.config['font_size']))
        
        self.setup_syntax_highlighting()
        self.apply_syntax_highlighting()

    def run(self):
        """Start the application"""
        if not hasattr(self, 'setup_complete') or not self.setup_complete:
            print("Setup cancelled or failed. Exiting...")
            return
            
        print("🚀 HUD Notes Production Version Started")
        print(f"  • Notes Directory: {self.notes_dir}")
        print(f"  • Templates Directory: {self.templates_dir}")
        print(f"  • Available Templates: {', '.join(self.template_manager.get_template_names())}")
        print(f"  • Display Settings: {self.screen_width}x{self.screen_height} (Scale: {self.dpi_scale:.1f}x)")
        print(f"  • Window Position: {self.calculated_width}x{self.calculated_height} at ({self.calculated_x}, {self.calculated_y})")
        print("  • Press Ctrl+Alt+T to toggle HUD overlay")
        print("  • Use A-/A+ buttons for font size, α -/+ for transparency")
        print("  • Right-click in text area for context menu")
        print("  • Drag from title bar or [DRAG HERE] to move window")
        print("  • See hotkey bar at bottom of screen for all shortcuts")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

def main():
    """Main entry point with argument handling"""
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--version', '-v']:
            print("HUD Notes v1.0.3")
            print("A HUD-style overlay note-taking application")
            print("Author: jLaHire")
            print("License: MIT")
            return
        elif arg in ['--help', '-h']:
            print("HUD Notes - Overlay Note-Taking Application")
            print("")
            print("Usage:")
            print("  hud_notes.py [options]")
            print("")
            print("Options:")
            print("  -h, --help     Show this help message")
            print("  -v, --version  Show version information")
            print("")
            print("First Run:")
            print("  On first run, a setup dialog will appear to configure:")
            print("  - Notes directory location")
            print("  - Author name for templates")
            print("  - Initial note title")
            print("  - Default template selection")
            print("")
            print("Hotkeys:")
            print("  Ctrl+Alt+t     Toggle HUD overlay")
            print("  Ctrl+Alt+g     Settings")
            print("  Ctrl+Alt+n     New note")
            print("  Ctrl+Alt+o     Open note")
            print("  Ctrl+Alt+s     Save note")
            print("  Ctrl+Alt+c     Code input window")
            print("  Ctrl+Alt+p     Toggle preview")
            print("  Ctrl+Alt+m     Move to next display")
            print("  Ctrl+Alt+r     Reset window position")
            print("  Ctrl+Alt+1-4   Move to corners")
            print("  Ctrl+Alt+5     Center window")
            print("  Esc           Hide overlay")
            print("")
            print("For more information, see README.md")
            return
    
    try:
        app = NoteOverlay()
        if hasattr(app, 'setup_complete') and app.setup_complete:
            app.run()
        else:
            print("Setup was cancelled. Exiting...")
    except KeyboardInterrupt:
        print("\nShutting down HUD Notes...")
    except Exception as e:
        print(f"Error starting HUD Notes: {e}")
        print("Please check that all dependencies are installed:")
        print("  pip3 install -r requirements.txt")
        print("\nFor help, see README.md or run with --help")
        
        # Only pause on Windows or if we're in an interactive session
        import sys, os
        if os.name == 'nt' or (hasattr(sys, 'ps1') or sys.stdin.isatty()):
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()