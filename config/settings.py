"""
Configuration management for HUD Notes
"""

import json
import os
from typing import Dict, Any


class SettingsManager:
    """Manages application settings and configuration"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.config = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration"""
        self.config = {
            "window_width": 400,
            "window_height": 600,
            "window_x": 100,
            "window_y": 100,
            "last_file": None,
            "font_size": 12,
            "theme": "dark",
            "hud_transparency": 0.65,
            "auto_scale": True,
            "notes_directory": None,
            "templates_directory": None,
            "author_name": None,
            "syntax_highlighting": True,
            "auto_save_interval": 2000,
            "color_scheme": "Matrix Green",
            "bg_color": "#0a0a0a",
            "fg_color": "#00ff41",
            "accent_color": "#ff6600",
            "select_bg": "#1a3d1a",
            "mouse_hover_show": False,
            "click_outside_hide": False,
            "show_tooltips": True,
            "hotkeys": {
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
                'quit_app': 'Ctrl+Alt+Q',  # Added quit hotkey
            }
        }
    
    def set_config_file(self, config_file: str):
        """Set the configuration file path"""
        self.config_file = config_file
    
    def load_config(self):
        """Load configuration from file"""
        if not self.config_file or not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
                self.config.update(saved_config)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        if not self.config_file:
            return
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        saved_paths = {
            'notes_directory': self.config.get('notes_directory'),
            'templates_directory': self.config.get('templates_directory'),
            'author_name': self.config.get('author_name')
        }
        
        self._load_defaults()
        
        # Restore important paths
        for key, value in saved_paths.items():
            if value:
                self.config[key] = value
    
    def get_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Get available color schemes"""
        return {
            'Matrix Green': {'bg': '#0a0a0a', 'fg': '#00ff41', 'accent': '#ff6600', 'select': '#1a3d1a'},
            'Cyber Blue': {'bg': '#0a0a1a', 'fg': '#00ccff', 'accent': '#ff6600', 'select': '#1a1a3d'},
            'Neon Purple': {'bg': '#1a0a1a', 'fg': '#cc00ff', 'accent': '#ffff00', 'select': '#3d1a3d'},
            'Hacker Orange': {'bg': '#1a1a0a', 'fg': '#ff9900', 'accent': '#00ff00', 'select': '#3d3d1a'},
            'Terminal White': {'bg': '#000000', 'fg': '#ffffff', 'accent': '#ffff00', 'select': '#333333'},
            'Blood Red': {'bg': '#1a0000', 'fg': '#ff3333', 'accent': '#ffff00', 'select': '#3d1a1a'},
        }
    
    def apply_color_scheme(self, scheme_name: str):
        """Apply a color scheme"""
        schemes = self.get_color_schemes()
        if scheme_name in schemes:
            colors = schemes[scheme_name]
            self.config.update({
                'color_scheme': scheme_name,
                'bg_color': colors['bg'],
                'fg_color': colors['fg'],
                'accent_color': colors['accent'],
                'select_bg': colors['select']
            })
    
    def get_hotkey_descriptions(self) -> Dict[str, str]:
        """Get hotkey descriptions"""
        return {
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
            'quit_app': 'Quit Application',  # Added quit description
        }
    
    def validate_config(self):
        """Validate configuration values"""
        # Ensure numeric values are within reasonable ranges
        self.config['font_size'] = max(8, min(24, self.config.get('font_size', 12)))
        self.config['hud_transparency'] = max(0.3, min(1.0, self.config.get('hud_transparency', 0.85)))
        self.config['auto_save_interval'] = max(1000, min(10000, self.config.get('auto_save_interval', 2000)))
        
        # Ensure directories exist if specified
        notes_dir = self.config.get('notes_directory')
        if notes_dir:
            os.makedirs(notes_dir, exist_ok=True)
        
        templates_dir = self.config.get('templates_directory')
        if templates_dir:
            os.makedirs(templates_dir, exist_ok=True)