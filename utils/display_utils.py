"""
Display utilities for HUD Notes - handles DPI scaling and multi-monitor support
"""
import platform
import sys
import tkinter as tk
from tkinter import font
from typing import Dict, List, Tuple


class DisplayManager:
    """Manages display detection, DPI scaling, and window positioning"""

    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.dpi_scale = 1.0
        self.system_font_size = 9
        self.displays = []
        self.current_display = 0
        self._detected = False
    
    def detect_from_root(self, root):
        """Detect display settings using an existing Tk root window.

        Call this once a Tk root exists to get accurate screen dimensions.
        """
        try:
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            self._detect_displays()

            try:
                dpi_x = root.winfo_fpixels('1i')
                self.dpi_scale = dpi_x / 96.0
            except:
                self.dpi_scale = 1.0

            try:
                default_font = font.nametofont("TkDefaultFont")
                self.system_font_size = default_font['size']
                if self.system_font_size < 0:
                    self.system_font_size = int(abs(self.system_font_size) * 72 / dpi_x)
            except:
                self.system_font_size = 9

        except Exception:
            pass  # Keep fallback values

        # Ensure valid values
        if not self.screen_width or self.screen_width <= 0:
            self.screen_width = 1920
        if not self.screen_height or self.screen_height <= 0:
            self.screen_height = 1080
        if not self.dpi_scale or self.dpi_scale <= 0:
            self.dpi_scale = 1.0
        if not self.system_font_size or self.system_font_size <= 0:
            self.system_font_size = 9

        self._detected = True
        print(f"Display settings: {self.screen_width}x{self.screen_height}, DPI scale: {self.dpi_scale}")
    
    def _detect_displays(self):
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
    
    def get_display_info(self) -> Dict:
        """Get current display information"""
        return {
            'width': self.screen_width,
            'height': self.screen_height,
            'scale': self.dpi_scale,
            'system_font_size': self.system_font_size,
            'display_count': len(self.displays),
            'current_display': self.current_display
        }
    
    def get_current_display(self) -> Dict:
        """Get current display configuration"""
        if self.current_display < len(self.displays):
            return self.displays[self.current_display]
        return self.displays[0] if self.displays else {
            'x': 0, 'y': 0, 'width': self.screen_width, 'height': self.screen_height, 'name': 'Default'
        }
    
    def get_all_displays(self) -> List[Dict]:
        """Get all available displays"""
        return self.displays.copy()
    
    def set_current_display(self, display_index: int):
        """Set the current display"""
        if 0 <= display_index < len(self.displays):
            self.current_display = display_index
    
    def get_next_display_index(self) -> int:
        """Get the next display index (circular)"""
        return (self.current_display + 1) % len(self.displays)
    
    def get_quarter_screen_layout(self) -> Dict:
        """Calculate window layout for right 1/4 of current display"""
        current_display = self.get_current_display()
        
        taskbar_height = 40
        hotkey_bar_height = 32
        
        display_width = current_display['width']
        display_height = current_display['height']
        display_x = current_display['x']
        display_y = current_display['y']
        
        calculated_width = int(display_width // 4)
        calculated_height = int(display_height - taskbar_height - hotkey_bar_height)
        calculated_x = int(display_x + display_width - calculated_width)
        calculated_y = display_y
        
        return {
            'width': calculated_width,
            'height': calculated_height,
            'x': calculated_x,
            'y': calculated_y
        }
    
    def get_scaled_font_size(self) -> int:
        """Get font size scaled for current DPI"""
        return max(8, int(self.system_font_size * self.dpi_scale))
    
    def get_scaled_dimension(self, base_size: int) -> int:
        """Get dimension scaled for current DPI"""
        return max(1, int(base_size * self.dpi_scale))
    
    def get_window_bounds(self, x: int, y: int, width: int, height: int) -> Tuple[int, int]:
        """Ensure window stays within screen bounds"""
        max_x = max(0, min(x, self.screen_width - width))
        max_y = max(0, min(y, self.screen_height - height - 50))  # Account for taskbar
        return max_x, max_y
    
    def get_center_position(self, width: int, height: int) -> Tuple[int, int]:
        """Get center position for given window size on current display"""
        current_display = self.get_current_display()
        
        x = current_display['x'] + (current_display['width'] - width) // 2
        y = current_display['y'] + (current_display['height'] - height) // 2
        
        return self.get_window_bounds(x, y, width, height)
    
    def get_corner_position(self, position: str, width: int, height: int, margin: int = 20) -> Tuple[int, int]:
        """Get corner position for given window size"""
        current_display = self.get_current_display()
        margin = self.get_scaled_dimension(margin)
        
        if position == 'top-left':
            x = current_display['x'] + margin
            y = current_display['y'] + margin
        elif position == 'top-right':
            x = current_display['x'] + current_display['width'] - width - margin
            y = current_display['y'] + margin
        elif position == 'bottom-left':
            x = current_display['x'] + margin
            y = current_display['y'] + current_display['height'] - height - 80
        elif position == 'bottom-right':
            x = current_display['x'] + current_display['width'] - width - margin
            y = current_display['y'] + current_display['height'] - height - 80
        else:
            # Default to top-left
            x = current_display['x'] + margin
            y = current_display['y'] + margin
        
        return self.get_window_bounds(x, y, width, height)
    
    def refresh_display_settings(self, root=None):
        """Refresh display settings (useful after display changes).

        Pass the app's existing Tk root to avoid creating a new Tk instance.
        """
        if root:
            self.detect_from_root(root)
    
    def get_border_dimensions(self) -> Dict:
        """Get dimensions for screen borders"""
        border_width = self.get_scaled_dimension(2)
        return {
            'width': border_width,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height
        }
    
    def get_hotkey_bar_dimensions(self) -> Dict:
        """Get dimensions for hotkey display bar"""
        screen_width = self.screen_width or 1920
        screen_height = self.screen_height or 1080
        dpi_scale = self.dpi_scale or 1.0
        
        hotkey_height = max(20, int(30 * dpi_scale))
        font_size = max(8, int(9 * dpi_scale))
        
        return {
            'height': hotkey_height,
            'font_size': font_size,
            'y_position': screen_height - hotkey_height,
            'width': screen_width
        }
        
    def calculate_dialog_size(self, base_width: int, base_height: int, content_items: int = 0) -> tuple:
        """Calculate appropriate dialog size based on DPI and content"""
        # Add extra height for dynamic content
        extra_height = content_items * 25  # 25 pixels per content item
        
        # Apply DPI scaling
        scaled_width = int((base_width + 50) * self.dpi_scale)  # Add padding
        scaled_height = int((base_height + extra_height) * self.dpi_scale)
        
        # Ensure minimum sizes
        min_width = 400
        min_height = 300
        scaled_width = max(min_width, scaled_width)
        scaled_height = max(min_height, scaled_height)
        
        # Ensure it fits on screen (leave 100px margin)
        max_width = self.screen_width - 100
        max_height = self.screen_height - 100
        
        final_width = min(scaled_width, max_width)
        final_height = min(scaled_height, max_height)
        
        return final_width, final_height

    def get_dialog_center_position(self, width: int, height: int) -> tuple:
        """Get center position for dialog window"""
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        
        # Ensure dialog doesn't go off-screen
        x = max(50, min(x, self.screen_width - width - 50))
        y = max(50, min(y, self.screen_height - height - 50))
        
        return x, y


class PlatformManager:
    """Manages platform-specific GUI attributes and behaviors"""
    
    @staticmethod
    def is_windows():
        """Check if running on Windows"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_linux():
        """Check if running on Linux/WSL"""
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def is_wsl():
        """Check if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    @staticmethod
    def apply_transparency(window, alpha_value=0.8):
        """Apply transparency in a platform-appropriate way"""
        try:
            if PlatformManager.is_windows():
                # Windows supports both -alpha and -transparentcolor
                window.attributes('-alpha', alpha_value)
            else:
                # Linux/X11 only supports -alpha
                window.attributes('-alpha', alpha_value)
        except Exception as e:
            print(f"Warning: Could not apply transparency: {e}")
    
    @staticmethod
    def apply_window_attributes(window, **attributes):
        """Apply window attributes in a platform-safe way"""
        safe_attributes = {}
        
        for attr, value in attributes.items():
            if attr == 'transparentcolor':
                # Only apply on Windows
                if PlatformManager.is_windows():
                    safe_attributes['-transparentcolor'] = value
            elif attr == 'alpha':
                safe_attributes['-alpha'] = value
            elif attr == 'topmost':
                safe_attributes['-topmost'] = value
            elif attr in ['zoomed', 'fullscreen', 'type']:
                safe_attributes[f'-{attr}'] = value
        
        # Apply safe attributes
        for attr, value in safe_attributes.items():
            try:
                window.attributes(attr, value)
            except Exception as e:
                print(f"Warning: Could not apply attribute {attr}: {e}")