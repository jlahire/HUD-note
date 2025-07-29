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
        
        # Create screen border (always visible)
        self.create_screen_border()
        
        # Create persistent hotkey display
        self.create_hotkey_display()
        
        # Create overlay window
        self.create_overlay()
        
        # Setup global hotkey
        self.setup_hotkey()
        
        # Load last opened file or create new with title
        self.load_last_file_or_create_new()

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
        
        # Template selection (will be loaded dynamically)
        template_frame = tk.Frame(main_frame, bg='#1a1a1a')
        template_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(template_frame, text="📋 Note Template:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        # Create templates directory to load available templates
        temp_templates_dir = os.path.join(dir_var.get(), "templates")
        temp_template_manager = TemplateManager(temp_templates_dir)
        
        template_var = tk.StringVar(value="Basic")
        template_dropdown = ttk.Combobox(template_frame, textvariable=template_var, 
                                       values=temp_template_manager.get_template_names(), 
                                       state='readonly', width=30, font=('Consolas', 10))
        template_dropdown.pack(anchor=tk.W, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        def save_config():
            self.notes_dir = dir_var.get()
            self.templates_dir = os.path.join(self.notes_dir, "templates")
            self.author_name = author_var.get()
            self.note_title = title_var.get()
            
            # Get template content
            template_name = template_var.get()
            temp_manager = TemplateManager(self.templates_dir)
            self.note_template = temp_manager.get_template_content(template_name)
            
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

    def create_hud_interface(self):
        """Create streamlined HUD interface"""
        title_height = max(30, int(30 * self.dpi_scale))
        button_size = max(2, int(2 * self.dpi_scale))
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
        
        # Control buttons
        controls = tk.Frame(title_frame, bg='#333333')
        controls.pack(side=tk.RIGHT, padx=5)
        
        button_font_size = max(8, int(8 * self.dpi_scale))
        
        # Font controls
        tk.Button(controls, text="A-", command=self.decrease_font,
                 bg=self.button_bg, fg='#ffcc00', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="A+", command=self.increase_font,
                 bg=self.button_bg, fg='#ffcc00', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        # Other controls
        tk.Button(controls, text="</>", command=self.open_code_window,
                 bg=self.button_bg, fg='#00ccff', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="●", command=self.new_note,
                 bg=self.button_bg, fg='#ffff00', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="▲", command=self.open_note,
                 bg=self.button_bg, fg='#00ffff', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="■", command=self.save_note,
                 bg=self.button_bg, fg='#00ff00', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="◊", command=self.toggle_preview,
                 bg=self.button_bg, fg='#ff00ff', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="↻", command=self.reset_to_quarter_screen,
                 bg=self.button_bg, fg='#ffaa00', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(controls, text="✕", command=self.hide_overlay,
                 bg='#330000', fg='#ff0000', font=('Arial', button_font_size, 'bold'),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
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
        
        tk.Button(trans_frame, text="-", command=self.decrease_transparency,
                 bg=self.button_bg, fg=self.fg_color, font=('Arial', status_font_size),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
        tk.Button(trans_frame, text="+", command=self.increase_transparency,
                 bg=self.button_bg, fg=self.fg_color, font=('Arial', status_font_size),
                 width=button_size, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=1)
        
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
        header_pattern = r'^#+\s.*$'
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
        list_pattern = r'^[\s]*[-*+]\s.*$'
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
        
        def show_context_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
        
        self.text_area.bind("<Button-3>", show_context_menu)

    def load_last_file_or_create_new(self):
        """Load the last opened file or create new with template"""
        if self.config.get('last_file') and os.path.exists(self.config['last_file']):
            try:
                with open(self.config['last_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.text_area.insert(1.0, content)
                self.current_file = self.config['last_file']
                self.update_file_label()
                self.apply_syntax_highlighting()
                
            except:
                self.create_new_note_with_template()
        else:
            self.create_new_note_with_template()

    def create_new_note_with_template(self):
        """Create a new note with the selected template"""
        template_content = self.note_template.format(
            title=self.note_title,
            author=self.author_name,
            date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        self.text_area.insert(1.0, template_content)
        
        # Auto-save with title as filename
        safe_filename = "".join(c for c in self.note_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        self.current_file = os.path.join(self.notes_dir, f"{safe_filename}.md")
        self.save_note()
        self.update_file_label()
        self.apply_syntax_highlighting()

    # Continue with the rest of the methods...
    # (Including all the window management, hotkey setup, file operations, etc.)
    # [I'll include these in the next part due to length constraints]

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
        
        # Window positioning shortcuts
        self.root.bind('<Control-Alt-1>', lambda e: self.move_to_corner('top-left'))
        self.root.bind('<Control-Alt-2>', lambda e: self.move_to_corner('top-right'))
        self.root.bind('<Control-Alt-3>', lambda e: self.move_to_corner('bottom-left'))
        self.root.bind('<Control-Alt-4>', lambda e: self.move_to_corner('bottom-right'))
        self.root.bind('<Control-Alt-5>', lambda e: self.center_window())

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
        """Create a new note"""
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno("New Note", "Save current note before creating new one?"):
                self.save_note()
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.update_file_label()
        self.update_status("New note created")

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
            print("HUD Notes v1.0.0")
            print("A HUD-style overlay note-taking application")
            print("Author: Lahire")
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
            print("  Ctrl+Alt+T     Toggle HUD overlay")
            print("  Ctrl+Alt+N     New note")
            print("  Ctrl+Alt+O     Open note")
            print("  Ctrl+Alt+S     Save note")
            print("  Ctrl+Alt+C     Code input window")
            print("  Ctrl+Alt+P     Toggle preview")
            print("  Ctrl+Alt+M     Move to next display")
            print("  Ctrl+Alt+R     Reset window position")
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