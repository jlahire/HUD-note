"""
Dialog windows for HUD Notes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
from datetime import datetime
from typing import Dict, Optional
from ui.components import create_tooltip


class StartupDialog:
    """Startup configuration dialog"""
    
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.result = None
        self.root = None
        self.dialog = None
    
    def show(self) -> Optional[Dict]:
        """Show startup configuration dialog"""
        # Create hidden root window first
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.attributes('-alpha', 0.85)
        self.root.geometry("1x1+0+0")
        
        # Create the actual config window
        self.dialog = tk.Toplevel(self.root)
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.title("HUD Notes - Initial Setup")
        # GET display info
        display_info = self.display_manager.get_display_info()
        
        # Calculate proper window size with DPI scaling
        base_width = 650
        base_height = 550
        dpi_scale = display_info.get('scale', 1.0)

        window_width = int(base_width * max(1.0, dpi_scale))
        window_height = int(base_height * max(1.0, dpi_scale))

        # Ensure it fits on screen
        screen_width = display_info['width']
        screen_height = display_info['height']
        window_width = min(window_width, screen_width - 100)
        window_height = min(window_height, screen_height - 100)

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.dialog.configure(bg='#1a1a1a')
        self.dialog.attributes('-topmost', True)
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        # Ensure window is shown properly
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()
        
        self._create_ui()
        
        # Handle window close button
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel_setup)
        
        # Run the dialog
        self.dialog.mainloop()
        
        return self.result
    
    def _create_ui(self):
        """Create the startup dialog UI"""
        # Create main frame with scrollable content
        main_frame = tk.Frame(self.dialog, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 HUD Notes Setup", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notes directory selection
        self._create_directory_section(main_frame)
        
        # Author name
        self._create_author_section(main_frame)
        
        # Note title
        self._create_title_section(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
        
        # Info text
        self._create_info_section(main_frame)
    
    def _create_directory_section(self, parent):
        """Create directory selection section"""
        dir_frame = tk.Frame(parent, bg='#1a1a1a')
        dir_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(dir_frame, text="📁 Notes Directory:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        default_notes_dir = os.path.expanduser("~/Documents/HUD_Notes")
        self.dir_var = tk.StringVar(value=default_notes_dir)
        
        dir_entry_frame = tk.Frame(dir_frame, bg='#1a1a1a')
        dir_entry_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = tk.Entry(dir_entry_frame, textvariable=self.dir_var, 
                            bg='#333333', fg='#ffffff', font=('Consolas', 10),
                            insertbackground='#00ff41', relief=tk.FLAT)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(dir_entry_frame, text="Browse...", command=self._browse_directory,
                            bg='#0066cc', fg='white', font=('Consolas', 10),
                            relief=tk.FLAT, padx=15, pady=5)
        browse_btn.pack(side=tk.RIGHT)
        create_tooltip(browse_btn, "Browse for Directory\nSelect where to store your notes")
    
    def _create_author_section(self, parent):
        """Create author name section"""
        author_frame = tk.Frame(parent, bg='#1a1a1a')
        author_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(author_frame, text="👤 Author Name:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        self.author_var = tk.StringVar(value=os.getenv('USERNAME', os.getenv('USER', 'User')))
        tk.Entry(author_frame, textvariable=self.author_var,
                bg='#333333', fg='#ffffff', font=('Consolas', 10),
                insertbackground='#00ff41', relief=tk.FLAT).pack(fill=tk.X, pady=5)
    
    def _create_title_section(self, parent):
        """Create note title section"""
        title_frame = tk.Frame(parent, bg='#1a1a1a')
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(title_frame, text="📝 Initial Note Title:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        self.title_var = tk.StringVar(value=f"Notes - {datetime.now().strftime('%Y-%m-%d')}")
        tk.Entry(title_frame, textvariable=self.title_var,
                bg='#333333', fg='#ffffff', font=('Consolas', 10),
                insertbackground='#00ff41', relief=tk.FLAT).pack(fill=tk.X, pady=5)
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Button styling
        button_style = {
            'font': ('Consolas', 12, 'bold'),
            'relief': tk.FLAT,
            'padx': 25,
            'pady': 8
        }
        
        start_btn = tk.Button(button_frame, text="✓ Start HUD Notes", command=self._save_config,
                            bg='#006600', fg='white', **button_style)
        start_btn.pack(side=tk.LEFT, padx=10)
        create_tooltip(start_btn, "Start HUD Notes\nSave configuration and launch application\nHotkey: Enter")

        cancel_btn = tk.Button(button_frame, text="✗ Cancel", command=self._cancel_setup,
                            bg='#660000', fg='white', **button_style)
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        create_tooltip(cancel_btn, "Cancel Setup\nExit without saving configuration\nHotkey: Escape")
        
        # Keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self._save_config())
        self.dialog.bind('<Escape>', lambda e: self._cancel_setup())
    
    def _create_info_section(self, parent):
        """Create info text section"""
        info_frame = tk.Frame(parent, bg='#1a1a1a')
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = ("💡 This setup creates your notes directory and templates folder.\n"
                    "You can add custom templates to the templates/ directory later.\n"
                    "Configuration will be saved to .note_config.json in your notes directory.")
        
        tk.Label(info_frame, 
                text=info_text,
                bg='#1a1a1a', fg='#888888', font=('Consolas', 10),
                wraplength=560, justify=tk.LEFT).pack()
    
    def _browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=self.dir_var.get(), title="Select Notes Directory")
        if directory:
            self.dir_var.set(directory)
    
    def _save_config(self):
        """Save configuration and close"""
        self.result = {
            'notes_dir': self.dir_var.get(),
            'templates_dir': os.path.join(self.dir_var.get(), "templates"),
            'author_name': self.author_var.get(),
            'note_title': self.title_var.get()
        }
        self.dialog.destroy()
        self.root.destroy()
    
    def _cancel_setup(self):
        """Cancel setup"""
        self.result = None
        self.dialog.destroy()
        self.root.destroy()


class TemplateSelectionDialog:
    """Template selection dialog"""
    
    def __init__(self, parent, template_manager, author_name, note_title, notes_manager=None, theme_manager=None):
        self.parent = parent
        self.template_manager = template_manager
        self.author_name = author_name
        self.note_title = note_title
        self.notes_manager = notes_manager
        self.theme_manager = theme_manager
        self.result = None
        self.window = None
    
    def show(self) -> Optional[Dict]:
        """Show template selection dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("Select Template")
        
        # Calculate required size based on content and DPI
        template_count = len(self.template_manager.get_template_names())
        base_height = 200  # Minimum height for UI elements
        content_height = max(300, template_count * 25 + 150)  # Dynamic based on templates
        total_height = base_height + content_height
        
        # Scale for DPI
        try:
            # Get DPI scaling from parent window
            dpi_scale = 1.0
            if hasattr(self.parent, 'tk'):
                dpi_x = self.parent.winfo_fpixels('1i')
                dpi_scale = max(1.0, dpi_x / 96.0)
        except:
            dpi_scale = 1.0
        
        # Calculate scaled dimensions
        scaled_width = int(600 * dpi_scale)
        scaled_height = int(total_height * dpi_scale)
        
        # Ensure minimum size
        scaled_width = max(500, scaled_width)
        scaled_height = max(400, scaled_height)
        
        # Ensure it fits on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        final_width = min(scaled_width, screen_width - 100)
        final_height = min(scaled_height, screen_height - 100)
        
        self.window.geometry(f"{final_width}x{final_height}")
        self.window.configure(bg='#1a1a1a')
        self.window.attributes('-topmost', True)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.resizable(True, True)
        
        # Center the window after setting size
        center_x = (screen_width - final_width) // 2
        center_y = (screen_height - final_height) // 2
        self.window.geometry(f"{final_width}x{final_height}+{center_x}+{center_y}")

        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._create_ui()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Wait for dialog to complete
        try:
            self.window.wait_window()
        except:
            pass  # Window was destroyed or closed
        
        return self.result
    
    def _create_ui(self):
        """Create template selection UI"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="📋 Choose Note Template", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Template list and preview
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Template list
        list_frame = tk.Frame(content_frame, bg='#1a1a1a')
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(list_frame, text="Templates:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        self._create_template_list(list_frame)
        
        # Preview
        preview_frame = tk.Frame(content_frame, bg='#1a1a1a')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(preview_frame, text="Preview:", 
                bg='#1a1a1a', fg='#00ff41', font=('Consolas', 12, 'bold')).pack(anchor=tk.W)
        
        self._create_preview(preview_frame)
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_template_list(self, parent):
        """Create template list"""
        listbox_frame = tk.Frame(parent, bg='#333333', relief=tk.SOLID, bd=1)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.template_listbox = tk.Listbox(
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
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.template_listbox.yview)
        
        # Populate listbox
        self.template_names = self.template_manager.get_template_names()
        for i, template_name in enumerate(sorted(self.template_names)):
            self.template_listbox.insert(tk.END, f"📝 {template_name}")
            if template_name == "Basic":
                self.template_listbox.selection_set(i)
        
        self.template_listbox.bind('<<ListboxSelect>>', self._update_preview)
        self.template_listbox.bind('<Double-Button-1>', lambda e: self._create_with_template())
    
    def _create_preview(self, parent):
        """Create preview area"""
        self.preview_text = ScrolledText(
            parent,
            wrap=tk.WORD,
            bg='#2a2a2a',
            fg='#cccccc',
            font=('Consolas', 9),
            relief=tk.FLAT,
            borderwidth=1,
            height=18,
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initial preview
        if self.template_listbox.curselection():
            self._update_preview()
    
    def _update_preview(self, event=None):
        """Update preview when selection changes"""
        selection = self.template_listbox.curselection()
        if selection:
            template_name = sorted(self.template_names)[selection[0]]
            template_content = self.template_manager.get_template_content(template_name)
            
            # Format template with current values
            formatted_content = self.template_manager.format_template(
                template_name,
                title=self.note_title,
                author=self.author_name,
                date=datetime.now().strftime('%Y-%m-%d %H:%M')
            )
            
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, formatted_content)
            self.preview_text.config(state=tk.DISABLED)
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill=tk.X)
        
        button_style = {
            'font': ('Consolas', 11, 'bold'),
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8
        }
        
        tk.Button(button_frame, text="✓ Create with Template", command=self._create_with_template,
                 bg='#006600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📄 Create Blank", command=self._create_blank,
                 bg='#333333', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✗ Cancel", command=self._cancel,
                 bg='#660000', fg='white', **button_style).pack(side=tk.RIGHT, padx=5)
        
        # Keyboard shortcuts
        self.window.bind('<Return>', lambda e: self._create_with_template())
        self.window.bind('<Escape>', lambda e: self._cancel())
    
    def _create_with_template(self):
        """Create note with selected template"""
        selection = self.template_listbox.curselection()
        if selection:
            template_name = sorted(self.template_names)[selection[0]]
            formatted_content = self.template_manager.format_template(
                template_name,
                title=self.note_title,
                author=self.author_name,
                date=datetime.now().strftime('%Y-%m-%d %H:%M')
            )
            
            self.result = {
                'action': 'template',
                'template_name': template_name,
                'content': formatted_content
            }
        else:
            messagebox.showwarning("No Selection", "Please select a template first.")
            return
        
        # Proper window cleanup
        if self.window:
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass
            self.window = None

    def _create_blank(self):
        """Create blank note"""
        self.result = {
            'action': 'blank',
            'content': ''
        }
        # Proper window cleanup
        if self.window:
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass
            self.window = None
    
    def _cancel(self):
        """Cancel template selection"""
        self.result = None
        if self.window:
            try:
                self.window.quit()  # Exit the mainloop first
                self.window.destroy()  # Then destroy the window
            except:
                pass
            self.window = None


class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, settings, display_manager, theme_manager=None):
        self.parent = parent
        self.settings = settings
        self.display_manager = display_manager
        self.theme_manager = theme_manager
        self.window = None
        
        # Variables for UI elements
        self.color_scheme_var = None
        self.custom_bg_var = None
        self.custom_fg_var = None
        self.custom_accent_var = None
        self.mouse_hover_var = None
        self.click_hide_var = None
        self.tooltips_var = None
        self.hotkey_vars = {}
    
    def show(self):
        """Show settings dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("HUD Notes Settings")
        
        # Get screen dimensions directly
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate size - make it bigger to ensure content fits
        window_width = min(750, screen_width - 200)  # Leave 200px margin
        window_height = min(700, screen_height - 150)  # Leave 150px margin
        
        # Ensure minimum size
        window_width = max(650, window_width)
        window_height = max(600, window_height)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Apply geometry
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.configure(bg='#1a1a1a')
        self.window.attributes('-topmost', True)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.resizable(True, True)
        
        self.window.transient(self.parent)
        
        self._create_ui()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        
        # Keyboard shortcuts
        self.window.bind('<Return>', lambda e: self._apply_settings())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        print(f"Settings window created: {window_width}x{window_height}")  # Debug output
    
    def _create_ui(self):
        """Create settings UI"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="⚙ HUD Notes Settings", 
                              bg='#1a1a1a', fg='#00ff41',
                              font=('Consolas', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs with proper sizing
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Ensure notebook gets proper height allocation
        main_frame.grid_rowconfigure(1, weight=1)  # Make notebook expandable
        
        self._configure_notebook_style()
        
        # Create tabs
        self._create_colors_tab()
        self._create_hotkeys_tab()
        self._create_advanced_tab()
        # Add some spacing before buttons
        spacer_frame = tk.Frame(main_frame, bg='#1a1a1a', height=10)
        spacer_frame.pack(fill=tk.X)
        # Buttons
        self._create_buttons(main_frame)
    
    def _configure_notebook_style(self):
        """Configure notebook tab styling"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#333333', foreground='#ffffff', 
                       padding=[20, 8], borderwidth=1)
        style.map('TNotebook.Tab', background=[('selected', '#00ff41'), ('active', '#555555')],
                 foreground=[('selected', '#000000')])
    
    def _create_colors_tab(self):
        """Create colors and theme settings tab"""
        colors_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(colors_frame, text='Colors & Theme')
        
        # Color schemes section
        schemes_frame = tk.LabelFrame(colors_frame, text="Color Schemes", 
                                     bg='#1a1a1a', fg='#00ff41',
                                     font=('Consolas', 12, 'bold'))
        schemes_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.color_scheme_var = tk.StringVar(value=self.settings.get('color_scheme', 'Matrix Green'))
        
        color_schemes = self.settings.get_color_schemes()
        
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
        self._create_custom_colors_section(colors_frame)
    
    def _create_custom_colors_section(self, parent):
        """Create custom colors section"""
        custom_frame = tk.LabelFrame(parent, text="Custom Colors", 
                                   bg='#1a1a1a', fg='#00ff41',
                                   font=('Consolas', 12, 'bold'))
        custom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Store color variables
        self.custom_bg_var = tk.StringVar(value=self.settings.get('bg_color', '#0a0a0a'))
        self.custom_fg_var = tk.StringVar(value=self.settings.get('fg_color', '#00ff41'))
        self.custom_accent_var = tk.StringVar(value=self.settings.get('accent_color', '#ff6600'))
        
        # Background, foreground, and accent color pickers would go here
        # For brevity, showing simplified version
        tk.Label(custom_frame, text="Custom color pickers would be implemented here",
                bg='#1a1a1a', fg='#888888', font=('Consolas', 10)).pack(pady=10)
    
    def _create_hotkeys_tab(self):
        """Create hotkeys settings tab"""
        hotkeys_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(hotkeys_frame, text='Hotkeys')
        
        # Instructions
        instructions = tk.Label(hotkeys_frame, 
                               text="Click on a hotkey field and press your desired key combination.\n"
                                   "Use combinations like Ctrl+Alt+T, Ctrl+Shift+N, etc.",
                               bg='#1a1a1a', fg='#cccccc', font=('Consolas', 10),
                               justify=tk.LEFT, wraplength=550)
        instructions.pack(pady=10, padx=10, anchor='w')
        
        # Hotkeys list
        hotkeys_list_frame = tk.Frame(hotkeys_frame, bg='#1a1a1a')
        hotkeys_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        hotkey_descriptions = self.settings.get_hotkey_descriptions()
        current_hotkeys = self.settings.get('hotkeys', {})
        
        for key, description in hotkey_descriptions.items():
            row_frame = tk.Frame(hotkeys_list_frame, bg='#1a1a1a')
            row_frame.pack(fill=tk.X, pady=2)
            
            # Description
            desc_label = tk.Label(row_frame, text=description + ":", 
                                 bg='#1a1a1a', fg='#ffffff',
                                 font=('Consolas', 10), width=20, anchor='w')
            desc_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Hotkey entry
            current_hotkey = current_hotkeys.get(key, 'Ctrl+Alt+T')
            hotkey_var = tk.StringVar(value=current_hotkey)
            self.hotkey_vars[key] = hotkey_var
            
            hotkey_entry = tk.Entry(row_frame, textvariable=hotkey_var,
                                  bg='#333333', fg='#ffffff', font=('Consolas', 10),
                                  insertbackground='#00ff41', width=20, state='readonly')
            hotkey_entry.pack(side=tk.LEFT, padx=(0, 10))
            
            # Reset button
            reset_btn = tk.Button(row_frame, text="Reset", 
                                command=lambda k=key: self._reset_hotkey(k),
                                bg='#555555', fg='#ffffff', font=('Consolas', 8),
                                relief=tk.FLAT, padx=10, pady=2)
            reset_btn.pack(side=tk.LEFT)
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(advanced_frame, text='Advanced')
        
        # Auto-show/hide settings
        autohide_frame = tk.LabelFrame(advanced_frame, text="Auto Show/Hide Features", 
                                     bg='#1a1a1a', fg='#00ff41',
                                     font=('Consolas', 12, 'bold'))
        autohide_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Mouse hover
        self.mouse_hover_var = tk.BooleanVar(value=self.settings.get('mouse_hover_show', False))
        hover_cb = tk.Checkbutton(autohide_frame, text="Show overlay when hovering top-left corner", 
                              variable=self.mouse_hover_var,
                              bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                              font=('Consolas', 10))
        hover_cb.pack(anchor='w', padx=10, pady=5)
        
        # Click outside to hide
        self.click_hide_var = tk.BooleanVar(value=self.settings.get('click_outside_hide', False))
        click_cb = tk.Checkbutton(autohide_frame, text="Hide overlay when clicking outside", 
                              variable=self.click_hide_var,
                              bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                              font=('Consolas', 10))
        click_cb.pack(anchor='w', padx=10, pady=5)
        
        # Tooltip toggle
        self.tooltips_var = tk.BooleanVar(value=self.settings.get('show_tooltips', True))
        tooltips_cb = tk.Checkbutton(autohide_frame, text="Show tooltips when hovering over buttons", 
                                variable=self.tooltips_var,
                                bg='#1a1a1a', fg='#ffffff', selectcolor='#333333',
                                font=('Consolas', 10))
        tooltips_cb.pack(anchor='w', padx=10, pady=5)
        
        # Future features placeholder
        placeholder_frame = tk.Frame(advanced_frame, bg='#1a1a1a')
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(placeholder_frame, text="🚧 Future Advanced Features", 
                bg='#1a1a1a', fg='#00ff41',
                font=('Consolas', 14, 'bold')).pack(pady=(0, 15))
        
        features_text = ("Additional features planned for future releases:\n\n"
                        "• Plugin system configuration\n"
                        "• Advanced syntax highlighting rules\n"
                        "• Custom template variables\n"
                        "• Export/import settings\n"
                        "• Performance optimization options\n"
                        "• Integration with external tools\n"
                        "• Auto-backup settings\n"
                        "• Multiple window profiles")
        
        tk.Label(placeholder_frame, text=features_text,
                bg='#1a1a1a', fg='#cccccc', font=('Consolas', 10),
                justify=tk.LEFT).pack(anchor='w')
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill=tk.X)
        
        button_style = {
            'font': ('Consolas', 11, 'bold'),
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8
        }
        
        tk.Button(button_frame, text="✓ Apply & Close", command=self._apply_settings,
                 bg='#006600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Reset Defaults", command=self._reset_defaults,
                 bg='#cc6600', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✗ Cancel", command=self.window.destroy,
                 bg='#660000', fg='white', **button_style).pack(side=tk.RIGHT, padx=5)
    
    def _reset_hotkey(self, key):
        """Reset individual hotkey to default"""
        default_hotkeys = {
            'toggle_overlay': 'Ctrl+Alt+H',
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
        
        if key in self.hotkey_vars and key in default_hotkeys:
            self.hotkey_vars[key].set(default_hotkeys[key])
    
    def _apply_settings(self):
        """Apply settings and close dialog"""
        # Apply color scheme
        scheme = self.color_scheme_var.get()
        if scheme != 'Custom':
            self.settings.apply_color_scheme(scheme)
        else:
            self.settings.update({
                'color_scheme': 'Custom',
                'bg_color': self.custom_bg_var.get(),
                'fg_color': self.custom_fg_var.get(),
                'accent_color': self.custom_accent_var.get()
            })
        
        # Apply hotkeys
        hotkeys = {}
        for key, var in self.hotkey_vars.items():
            hotkeys[key] = var.get()
        self.settings.set('hotkeys', hotkeys)
        
        # Apply advanced settings
        self.settings.update({
            'mouse_hover_show': self.mouse_hover_var.get(),
            'click_outside_hide': self.click_hide_var.get(),
            'show_tooltips': self.tooltips_var.get()
        })
        
        self.settings.save_config()
        self.window.destroy()
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "Reset all settings to defaults? This cannot be undone."):
            self.settings.reset_to_defaults()
            self.window.destroy()


class CodeInputDialog:
    """Code input dialog window"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.result = None
        self.window = None
    
    def show(self) -> Optional[str]:
        """Show code input dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.lift()
        self.window.focus_force()
        self.window.title("Code Input")
        # Calculate scaled size for code input dialog
        dpi_scale = 1.0
        try:
            dpi_x = self.window.winfo_fpixels('1i')
            dpi_scale = max(1.0, dpi_x / 96.0)
        except:
            pass

        base_width = 650
        base_height = 450
        scaled_width = int(base_width * dpi_scale)
        scaled_height = int(base_height * dpi_scale)

        # Ensure reasonable bounds
        final_width = max(500, min(scaled_width, 800))
        final_height = max(350, min(scaled_height, 600))

        # Center on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = (screen_width - final_width) // 2
        center_y = (screen_height - final_height) // 2

        self.window.geometry(f"{final_width}x{final_height}+{center_x}+{center_y}")
        self.window.configure(bg=self.settings.get('bg_color', '#0a0a0a'))
        self.window.attributes('-topmost', True)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._create_ui()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Keyboard shortcuts
        self.window.bind('<Control-Return>', lambda e: self._insert_code())
        self.window.bind('<Escape>', lambda e: self._cancel())
        
        # Wait for dialog to complete
        self.window.wait_window()
        
        return self.result
    
    def _create_ui(self):
        """Create code input UI"""
        main_frame = tk.Frame(self.window, bg=self.settings.get('bg_color', '#0a0a0a'))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Language selection
        lang_frame = tk.Frame(main_frame, bg=self.settings.get('bg_color', '#0a0a0a'))
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(lang_frame, text="Language:", 
                bg=self.settings.get('bg_color', '#0a0a0a'), 
                fg=self.settings.get('fg_color', '#00ff41'),
                font=('Consolas', 10, 'bold')).pack(side=tk.LEFT)
        
        languages = [
            'bash', 'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 'go', 'rust',
            'php', 'ruby', 'swift', 'kotlin', 'scala', 'html', 'css', 'sql', 'xml',
            'json', 'yaml', 'markdown', 'powershell', 'dockerfile', 'typescript', 'r'
        ]
        
        self.lang_var = tk.StringVar(value='bash')
        lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=languages,
                                   state='readonly', width=15)
        lang_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Code input area
        code_frame = tk.Frame(main_frame, bg=self.settings.get('bg_color', '#0a0a0a'))
        code_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(code_frame, text="Code:", 
                bg=self.settings.get('bg_color', '#0a0a0a'), 
                fg=self.settings.get('fg_color', '#00ff41'),
                font=('Consolas', 10, 'bold')).pack(anchor=tk.W)
        
        self.code_text = ScrolledText(
            code_frame,
            wrap=tk.NONE,
            bg=self.settings.get('bg_color', '#0a0a0a'),
            fg=self.settings.get('fg_color', '#00ff41'),
            insertbackground=self.settings.get('fg_color', '#00ff41'),
            selectbackground=self.settings.get('select_bg', '#1a3d1a'),
            font=('Consolas', self.settings.get('font_size', 12)),
            relief=tk.SOLID,
            borderwidth=1,
            height=15
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.focus()
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg=self.settings.get('bg_color', '#0a0a0a'))
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Insert Code", command=self._insert_code,
                 bg='#006600', fg='white', font=('Consolas', 10, 'bold'),
                 relief=tk.FLAT, padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=self._cancel,
                 bg='#660000', fg='white', font=('Consolas', 10),
                 relief=tk.FLAT, padx=20).pack(side=tk.RIGHT, padx=5)
    
    def _insert_code(self):
        """Insert code and close"""
        language = self.lang_var.get()
        code_content = self.code_text.get(1.0, tk.END).strip()
        
        if code_content:
            self.result = f"\n```{language}\n{code_content}\n```\n\n"
        
        self.window.destroy()
    
    def _cancel(self):
        """Cancel and close"""
        self.result = None
        self.window.destroy()