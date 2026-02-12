"""
Main application class for HUD Notes
"""

import os
from datetime import datetime

from config.settings import SettingsManager
from core.template_manager import TemplateManager
from ui.overlay import OverlayWindow
from ui.dialogs import StartupDialog
from features.hotkeys import HotkeyManager
from features.auto_features import AutoFeatureManager
from features.window_manager import WindowManager
from utils.display_utils import DisplayManager


class HUDNotesApp:
    """Main HUD Notes application"""
    
    def __init__(self):
        self.setup_complete = False
        self.overlay_visible = False
        self.current_file = None
        self.notes_dir = None
        self.author_name = None
        self.note_title = None
        self.templates_dir = None
        
        # Initialize managers
        self.settings = SettingsManager()
        self.display_manager = DisplayManager()
        self.window_manager = None
        self.template_manager = None
        self.hotkey_manager = None
        self.auto_features = None
        self.overlay = None
        self.tk_root = None  # Shared Tk root to avoid multiple Tk() instances

        # Show startup configuration
        if not self._show_startup_config():
            return
        
        # Initialize remaining components
        self._initialize_components()
        
        self.setup_complete = True
    
    def _show_startup_config(self) -> bool:
        """Show startup configuration dialog"""
        startup_dialog = StartupDialog(self.display_manager)
        result = startup_dialog.show()

        if result:
            self.notes_dir = result['notes_dir']
            self.templates_dir = result['templates_dir']
            self.author_name = result['author_name']
            self.note_title = result['note_title']
            # Keep the Tk root alive for reuse by the overlay
            self.tk_root = startup_dialog.get_root()
            return True

        return False
    
    def _initialize_components(self):
        """Initialize all application components"""
        # Set up settings with proper paths
        config_file = os.path.join(self.notes_dir, ".note_config.json")
        self.settings.set_config_file(config_file)
        
        # Update settings with startup values
        self.settings.update({
            'notes_directory': self.notes_dir,
            'templates_directory': self.templates_dir,
            'author_name': self.author_name
        })
        
        # Apply display-aware defaults
        display_layout = self.display_manager.get_quarter_screen_layout()
        self.settings.update({
            'window_width': display_layout['width'],
            'window_height': display_layout['height'],
            'window_x': display_layout['x'],
            'window_y': display_layout['y'],
            'font_size': self.display_manager.get_scaled_font_size()
        })
        
        # Load existing config (will override defaults if available)
        self.settings.load_config()
        self.settings.validate_config()
        
        # Ensure directories exist
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize template manager
        self.template_manager = TemplateManager(self.templates_dir)
        
        # Initialize window manager
        self.window_manager = WindowManager(self.display_manager, self.settings)
        
        # Initialize hotkey manager BEFORE overlay (so it exists when overlay creates components)
        self.hotkey_manager = HotkeyManager(self)
        
        # Initialize overlay window LAST (after all dependencies are ready)
        self.overlay = OverlayWindow(self)      
          
        # Initialize auto features
        self.auto_features = AutoFeatureManager(self)
        
        # Make sure queue processors start
        if hasattr(self.auto_features, '_start_queue_processor'):
            self.auto_features._start_queue_processor()
        
        if hasattr(self.hotkey_manager, '_start_queue_processor'):
            self.hotkey_manager._start_queue_processor()
        

    
    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay_visible:
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def show_overlay(self):
        """Show the overlay"""
        if self.overlay:
            self.overlay.show()
            self.overlay_visible = True
    
    def hide_overlay(self):
        """Hide the overlay"""
        if self.overlay:
            self.overlay.hide()
            self.overlay_visible = False
    
    def new_note(self):
        """Create a new note with template selection"""
        if self.overlay:
            self.overlay.new_note()
    
    def open_note(self):
        """Open an existing note"""
        if self.overlay:
            self.overlay.open_note()
    
    def save_note(self):
        """Save current note"""
        if self.overlay:
            self.overlay.save_note()
    
    def save_as_note(self):
        """Save note with new filename"""
        if self.overlay:
            self.overlay.save_as_note()
    
    def open_code_window(self):
        """Open code input window"""
        if self.overlay:
            self.overlay.open_code_window()
    
    def toggle_preview(self):
        """Toggle markdown preview"""
        if self.overlay:
            self.overlay.toggle_preview()
    
    def open_settings(self):
        """Open settings dialog"""
        if self.overlay:
            self.overlay.open_settings()
    
    def increase_font(self):
        """Increase font size"""
        if self.overlay:
            self.overlay.increase_font()
    
    def decrease_font(self):
        """Decrease font size"""
        if self.overlay:
            self.overlay.decrease_font()
    
    def reset_position(self):
        """Reset window to quarter screen"""
        if self.window_manager:
            self.window_manager.reset_to_quarter_screen()
    
    def move_to_corner(self, position: str):
        """Move window to specified corner"""
        if self.window_manager:
            self.window_manager.move_to_corner(position)
    
    def center_window(self):
        """Center window on current display"""
        if self.window_manager:
            self.window_manager.center_window()
    
    def move_to_next_display(self):
        """Move to next display"""
        if self.window_manager:
            self.window_manager.move_to_next_display()
    
    def increase_transparency(self):
        """Increase transparency (make more transparent)"""
        if self.overlay:
            self.overlay.increase_transparency()

    def decrease_transparency(self):
        """Decrease transparency (make more opaque)"""
        if self.overlay:
            self.overlay.decrease_transparency()
        
    def get_current_file(self) -> str:
        """Get current file path"""
        return self.current_file
    
    def set_current_file(self, file_path: str):
        """Set current file path"""
        self.current_file = file_path
        self.settings.set('last_file', file_path)
    
    def update_status(self, message: str):
        """Update status message"""
        if self.overlay:
            self.overlay.update_status(message)
    
    def get_template_overview_content(self) -> str:
        """Get template overview content for startup"""
        if self.template_manager:
            return self.template_manager.create_template_overview(self.author_name)
        return "# HUD Notes\n\nWelcome to HUD Notes!"
    
    def run(self):
        """Start the application"""
        if not self.setup_complete:
            print("Setup not completed. Cannot start application.")
            return

        print("HUD Notes Started")
        print(f"  Notes Directory: {self.notes_dir}")
        print(f"  Press Ctrl+Alt+H to toggle HUD overlay")

        try:
            if self.overlay:
                self.overlay.run()
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of the application"""
        print("Shutting down HUD Notes...")
        
        # Auto-save current file if needed
        if self.current_file and self.overlay:
            self.overlay.auto_save()
        
        # Stop auto features
        if self.auto_features:
            self.auto_features.shutdown()
        
        # Stop hotkey manager
        if self.hotkey_manager:
            self.hotkey_manager.shutdown()
        
        # Save configuration
        self.settings.save_config()
        
        # Cleanup overlay
        if self.overlay:
            self.overlay.cleanup()
        
        print("HUD Notes shutdown complete.")