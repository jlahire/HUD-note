"""
Reusable UI components for HUD Notes
"""

import tkinter as tk
from tkinter import Menu
from utils.display_utils import PlatformManager

class StatusBar:
    """Status bar component"""
    
    def __init__(self, parent, settings, display_manager, theme_manager=None, app=None):
        self.settings = settings
        self.display_manager = display_manager
        self.theme_manager = theme_manager
        
        # Create status frame
        status_height = display_manager.get_scaled_dimension(20)
        self.frame = tk.Frame(parent, bg='#1a1a1a', height=status_height)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)
        
        font_size = display_manager.get_scaled_dimension(8)
        
        # Status label
        self.status_label = tk.Label(
            self.frame,
            text=f"Ready | Display Scale: {int(display_manager.dpi_scale * 100)}%",
            bg='#1a1a1a',
            fg=settings.get('fg_color', '#00ff41'),
            font=('Consolas', font_size)
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=1)

        # Add tooltip to status label
        create_tooltip(self.status_label, "Status Bar\nShows current application state and messages")

        # Transparency controls
        self._create_transparency_controls(app)
    
    def _create_transparency_controls(self, app=None):
        """Create transparency control widgets"""
        trans_frame = tk.Frame(self.frame, bg='#1a1a1a')
        trans_frame.pack(side=tk.RIGHT, padx=5)
        
        font_size = self.display_manager.get_scaled_dimension(8)
        button_size = self.display_manager.get_scaled_dimension(15)  # Width in pixels
        
        # Current transparency display
        current_alpha = int(self.settings.get('hud_transparency', 0.85) * 100)
        self.transparency_label = tk.Label(trans_frame, text=f"α:{current_alpha}%", 
                                        bg='#1a1a1a', 
                                        fg=self.settings.get('fg_color', '#00ff41'),
                                        font=('Consolas', font_size))
        self.transparency_label.pack(side=tk.LEFT, padx=2)

        # Add tooltip to transparency label
        create_tooltip(self.transparency_label, "Current Transparency\nShows window opacity percentage")

        if app:  # Only create buttons if app reference is provided
            # Transparency decrease button (more transparent)
            alpha_minus_btn = tk.Button(trans_frame, text="α-", 
                                    command=app.increase_transparency,
                                    bg='#1a1a1a', fg='#88ccff',
                                    font=('Consolas', font_size, 'bold'),
                                    width=button_size, height=1,
                                    relief=tk.FLAT, cursor="hand2")
            alpha_minus_btn.pack(side=tk.LEFT, padx=1)
            print(f"Creating transparency button α- with command: {app.increase_transparency}")
            try:
                create_tooltip(alpha_minus_btn, "Decrease Transparency\n(More Transparent)\nHotkey: Alt+-", self.settings)
                print("✓ α- tooltip created")
            except Exception as e:
                print(f"✗ α- tooltip failed: {e}")
            
            # Transparency increase button (more opaque)
            alpha_plus_btn = tk.Button(trans_frame, text="α+", 
                                    command=app.decrease_transparency,
                                    bg='#1a1a1a', fg='#88ccff',
                                    font=('Consolas', font_size, 'bold'),
                                    width=button_size, height=1,
                                    relief=tk.FLAT, cursor="hand2")
            alpha_plus_btn.pack(side=tk.LEFT, padx=1)
            create_tooltip(alpha_plus_btn, "Increase Transparency\n(More Opaque)\nHotkey: Alt++", self.settings)

    def update_transparency_display(self, transparency_value):
        """Update transparency percentage display"""
        if hasattr(self, 'transparency_label'):
            percentage = int(transparency_value * 100)
            self.transparency_label.config(text=f"α:{percentage}%")
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.config(text=message)
        # Auto-clear status after 3 seconds
        self.frame.after(3000, lambda: self.status_label.config(
            text=f"Ready | Display Scale: {int(self.display_manager.dpi_scale * 100)}%"
        ))
    
    def apply_theme(self, theme_manager=None):
        """Apply current theme to status bar"""
        if theme_manager:
            self.theme_manager = theme_manager
        
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            if current_theme:
                bg_color = current_theme.get_color('status_bg', '#1a1a1a')
                fg_color = current_theme.get_color('fg_color', '#00ff41')
                
                self.frame.configure(bg=bg_color)
                self.status_label.configure(bg=bg_color, fg=fg_color)
        else:
            # Fallback to settings
            self.frame.configure(bg='#1a1a1a')
            self.status_label.configure(
                bg='#1a1a1a',
                fg=self.settings.get('fg_color', '#00ff41')
            )
    
    def _reset_window_cursor(self):
        """Reset window cursor when interacting with UI elements"""
        if hasattr(self.app, 'window_manager') and self.app.window_manager:
            self.app.window_manager.reset_cursor()


class HUDInterface:
    """Main HUD interface with title bar and controls"""
    
    def __init__(self, parent, app, theme_manager=None):
        self.parent = parent
        self.app = app
        self.theme_manager = theme_manager
        self.file_label = None
        
        self._create_interface()
    
    def _create_interface(self):
        """Create the HUD interface"""
        title_height = self.app.display_manager.get_scaled_dimension(35)
        
        # Title bar with drag functionality
        self.title_frame = tk.Frame(self.parent, bg='#333333', height=title_height, 
                                   relief=tk.RAISED, bd=1)
        self.title_frame.pack(fill=tk.X)
        self.title_frame.pack_propagate(False)
        
        # Setup drag handlers
        self.app.window_manager.setup_drag_handlers(self.title_frame)
        
        # Title and controls
        self._create_title_section()
        self._create_control_buttons()
    
    def _create_title_section(self):
        """Create title section with file label"""
        title_left = tk.Frame(self.title_frame, bg='#333333')
        title_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        font_size = self.app.display_manager.get_scaled_dimension(10)
        
        self.file_label = tk.Label(
            title_left, 
            text="HUD NOTES [D1/1]",
            bg='#333333', 
            fg=self.app.settings.get('accent_color', '#ff6600'),
            font=('Consolas', font_size, 'bold')
        )
        self.file_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add tooltip to file label
        create_tooltip(self.file_label, "Current File\nShows active note filename and display info")
        
        # Make draggable
        self.app.window_manager.setup_drag_handlers(self.file_label)
        
        # Drag indicator
        drag_label = tk.Label(
            title_left, 
            text="[DRAG HERE]",
            bg='#333333', 
            fg='#666666',
            font=('Consolas', self.app.display_manager.get_scaled_dimension(8))
        )
        
        drag_label.pack(side=tk.RIGHT, padx=10, pady=2)
        self.app.window_manager.setup_drag_handlers(drag_label)

        # Add tooltip to test tooltip system
        create_tooltip(drag_label, "Drag to move window\nDouble-click to reset position", self.app.settings)
        
    
    def _create_control_buttons(self):
        """Create control buttons"""
        controls = tk.Frame(self.title_frame, bg='#333333')
        controls.pack(side=tk.RIGHT, padx=5)
        
        # Larger button dimensions for better usability
        button_font_size = self.app.display_manager.get_scaled_dimension(11)
        button_width = self.app.display_manager.get_scaled_dimension(4)
        button_height = self.app.display_manager.get_scaled_dimension(1.5)
        
        # Button configurations
        buttons = [
            ("A-", self.app.decrease_font, '#ffcc00', "Decrease Font Size", "Ctrl+Alt+-"),
            ("A+", self.app.increase_font, '#ffcc00', "Increase Font Size", "Ctrl+Alt++"),
            ("α-", self.app.increase_transparency, '#88ccff', "Decrease Transparency", "Alt+-"),
            ("α+", self.app.decrease_transparency, '#88ccff', "Increase Transparency", "Alt++"),
            ("</>", self.app.open_code_window, '#00ccff', "Code Input Window", "Ctrl+Alt+C"),
            ("●", self.app.new_note, '#ffff00', "New Note (with Template)", "Ctrl+Alt+N"),
            ("▲", self.app.open_note, '#00ffff', "Open Note", "Ctrl+Alt+O"),
            ("■", self.app.save_note, '#00ff00', "Save Note", "Ctrl+Alt+S"),
            ("▫", self.app.save_as_note, '#00cc00', "Save As...", "Ctrl+Alt+Shift+S"),
            ("◊", self.app.toggle_preview, '#ff00ff', "Toggle Preview", "Ctrl+Alt+P"),
            ("↻", self.app.reset_position, '#ffaa00', "Reset Window Position", "Ctrl+Alt+R"),
            ("⚙", self.app.open_settings, '#cccccc', "Settings", None),
            ("✕", self.app.hide_overlay, '#ff0000', "Hide Overlay", "Esc")
        ]
        
        for button_data in buttons:
            text, command, color, tooltip = button_data[:4]
            hotkey = button_data[4] if len(button_data) > 4 else None
            
            btn = tk.Button(
                controls,
                text=text,
                command=command,
                bg='#1a1a1a',
                fg=color,
                font=('Arial', button_font_size, 'bold'),
                width=int(button_width),
                height=int(button_height),
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)
            
            # Enhanced tooltip with hotkey
            full_tooltip = tooltip
            if hotkey:
                full_tooltip += f"\nHotkey: {hotkey}"
            
            create_tooltip(btn, full_tooltip, self.app.settings)
            
            
    def update_file_label(self, text: str):
        """Update file label text"""
        if self.file_label:
            self.file_label.config(text=text)
    
    def apply_theme(self, theme_manager=None):
        """Apply current theme to HUD interface"""
        if theme_manager:
            self.theme_manager = theme_manager
        
        if self.file_label and self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            if current_theme:
                accent_color = current_theme.get_color('accent_color', '#ff6600')
                self.file_label.configure(fg=accent_color)

    def _reset_window_cursor(self):
        """Reset window cursor when interacting with UI elements"""
        if hasattr(self.app, 'window_manager') and self.app.window_manager:
            self.app.window_manager.reset_cursor()
            
    def _on_button_enter(self, event, button):
        """Handle button enter event"""
        print(f"Button entered: {button['text']}")
        self._reset_window_cursor()

class ScreenBorder:
    """Always-visible screen border"""
    
    def __init__(self, display_manager, theme_manager=None):
        self.display_manager = display_manager
        self.theme_manager = theme_manager
        self.border_windows = []
        self._create_borders()
    
    def _create_borders(self):
        """Create screen border windows"""
        border_dims = self.display_manager.get_border_dimensions()
        border_width = border_dims['width']
        screen_width = border_dims['screen_width']
        screen_height = border_dims['screen_height']
        
        # Get border color from theme if available
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            border_color = current_theme.get_color('border_color', '#00ff41') if current_theme else '#00ff41'
        else:
            border_color = "#00ff41"
        
        # Top border
        top_border = tk.Toplevel()
        top_border.geometry(f"{screen_width}x{border_width}+0+0")
        top_border.configure(bg=border_color)
        top_border.overrideredirect(True)
        top_border.attributes('-topmost', True)
        top_border.attributes('-alpha', 0.6)
        self.border_windows.append(top_border)
        
        # Left border
        left_border = tk.Toplevel()
        left_border.geometry(f"{border_width}x{screen_height}+0+0")
        left_border.configure(bg=border_color)
        left_border.overrideredirect(True)
        left_border.attributes('-topmost', True)
        left_border.attributes('-alpha', 0.6)
        self.border_windows.append(left_border)
        
        # Right border
        right_border = tk.Toplevel()
        right_border.geometry(f"{border_width}x{screen_height}+{screen_width-border_width}+0")
        right_border.configure(bg=border_color)
        right_border.overrideredirect(True)
        right_border.attributes('-topmost', True)
        right_border.attributes('-alpha', 0.6)
        self.border_windows.append(right_border)
    
    def update_theme(self, theme_manager):
        """Update border colors when theme changes"""
        self.theme_manager = theme_manager
        current_theme = theme_manager.get_current_theme()
        if current_theme:
            border_color = current_theme.get_color('border_color', '#00ff41')
            for border in self.border_windows:
                try:
                    border.configure(bg=border_color)
                except:
                    pass
    
    def cleanup(self):
        """Clean up border windows"""
        for border in self.border_windows:
            try:
                border.destroy()
            except:
                pass


class HotkeyDisplay:
    """Persistent hotkey display at bottom of screen"""
    
    def __init__(self, display_manager, hotkey_manager, theme_manager=None):
        self.display_manager = display_manager
        self.hotkey_manager = hotkey_manager
        self.theme_manager = theme_manager
        self.hotkey_window = None
        self.border_window = None
        self._create_display()
    
    def _create_display(self):
        """Create hotkey display window with platform-aware transparency"""
        hotkey_dims = self.display_manager.get_hotkey_bar_dimensions()
        
        # Safety check for None return
        if not hotkey_dims:
            print("Warning: Could not get hotkey bar dimensions, using defaults")
            hotkey_dims = {
                'width': 1920,
                'height': 30,
                'y_position': 1050,
                'font_size': 9
            }
        
        self.hotkey_window = tk.Toplevel()
        self.hotkey_window.geometry(f"{hotkey_dims['width']}x{hotkey_dims['height']}+0+{hotkey_dims['y_position']}")
        
        self.hotkey_window.configure(bg='black')
        self.hotkey_window.overrideredirect(True)
        self.hotkey_window.attributes('-topmost', True)
        PlatformManager.apply_transparency(self.hotkey_window, 0.8)
        
        # Get hotkey text
        hotkeys_text = self.hotkey_manager.create_hotkey_display_text()
        
        # Get colors from theme if available
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            fg_color = current_theme.get_color('fg_color', '#00ff41') if current_theme else '#00ff41'
            border_color = current_theme.get_color('border_color', '#00ff41') if current_theme else '#00ff41'
        else:
            fg_color = '#00ff41'
            border_color = '#00ff41'
        
        hotkey_label = tk.Label(
            self.hotkey_window,
            text=hotkeys_text,
            bg='black',
            fg=fg_color,
            font=('Consolas', hotkey_dims['font_size'], 'bold'),
            pady=5
        )
        hotkey_label.pack(fill=tk.BOTH, expand=True)
        
        # Add border line
        border_height = max(1, int(1 * self.display_manager.dpi_scale))
        self.border_window = tk.Toplevel()
        self.border_window.geometry(f"{hotkey_dims['width']}x{border_height}+0+{hotkey_dims['y_position']-border_height}")
        self.border_window.configure(bg=border_color)
        self.border_window.overrideredirect(True)
        self.border_window.attributes('-topmost', True)
        self.border_window.attributes('-alpha', 0.4)
    
    def update_theme(self, theme_manager):
        """Update hotkey display colors when theme changes"""
        self.theme_manager = theme_manager
        # For hotkey display updates, we'd need to recreate the display
        # This is a simplified version - full implementation would recreate the display
        pass
    
    def cleanup(self):
        """Clean up hotkey display"""
        if self.hotkey_window:
            try:
                self.hotkey_window.destroy()
            except:
                pass
        
        if self.border_window:
            try:
                self.border_window.destroy()
            except:
                pass


class ContextMenu:
    """Context menu for text area"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.menu = None
        self._create_menu()
    
    def _create_menu(self):
        """Create context menu"""
        self.menu = Menu(self.parent, tearoff=0, 
                        bg='#1a1a1a', fg=self.app.settings.get('fg_color', '#00ff41'))
        
        self.menu.add_command(label="Undo", command=lambda: self.parent.edit_undo())
        self.menu.add_command(label="Redo", command=lambda: self.parent.edit_redo())
        self.menu.add_separator()
        self.menu.add_command(label="Cut", command=lambda: self.parent.event_generate("<<Cut>>"))
        self.menu.add_command(label="Copy", command=lambda: self.parent.event_generate("<<Copy>>"))
        self.menu.add_command(label="Paste", command=lambda: self.parent.event_generate("<<Paste>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=lambda: self.parent.event_generate("<<SelectAll>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Insert Code Block", command=self.app.open_code_window)
        self.menu.add_command(label="New Note (Template)", command=self.app.new_note)
    
    def show(self, event):
        """Show context menu"""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

def create_tooltip(widget, text, settings=None):
    """Create tooltip for widget - simplified working version with toggle support"""
    
    def show_tooltip(event):
        # Check if tooltips are enabled
        if settings and not settings.get('show_tooltips', True):
            return  # Don't show tooltip if disabled
        
        # Remove any existing tooltip
        if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
            try:
                widget.tooltip_window.destroy()
            except:
                pass
            widget.tooltip_window = None
        
        # Create new tooltip
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg='#2a2a2a', relief=tk.SOLID, bd=1)
        tooltip.attributes('-topmost', True)
        
        # Create label
        label = tk.Label(tooltip, text=text, bg='#2a2a2a', fg='#ffffff',
                    font=('Consolas', 9), padx=8, pady=4, justify=tk.LEFT)
        label.pack()
        
        # Position tooltip
        x = event.x_root + 15
        y = event.y_root - 25
        
        # Keep tooltip on screen
        try:
            tooltip.update_idletasks()
            tooltip_width = tooltip.winfo_reqwidth()
            tooltip_height = tooltip.winfo_reqheight()
            
            screen_width = tooltip.winfo_screenwidth()
            screen_height = tooltip.winfo_screenheight()
            
            if x + tooltip_width > screen_width:
                x = event.x_root - tooltip_width - 5
            if y + tooltip_height > screen_height:
                y = event.y_root - tooltip_height - 5
            if y < 0:
                y = event.y_root + 25
        except:
            pass
        
        tooltip.geometry(f"+{x}+{y}")
        
        # Store reference
        widget.tooltip_window = tooltip
        
        print(f"Tooltip shown: {text[:30]}...")  # Debug output
    
    def hide_tooltip(event):
        if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
            try:
                widget.tooltip_window.destroy()
            except:
                pass
            widget.tooltip_window = None
    
    # Initialize tooltip window attribute
    widget.tooltip_window = None
    
    # Bind events directly - no delays
    widget.bind('<Enter>', show_tooltip)
    widget.bind('<Leave>', hide_tooltip)
