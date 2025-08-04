"""
Window positioning and management for HUD Notes
"""

from typing import Tuple


class WindowManager:
    """Manages window positioning, resizing, and multi-monitor support"""
    
    def __init__(self, display_manager, settings):
        self.display_manager = display_manager
        self.settings = settings
        self.window = None
        
        # Dragging state
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        
        # Resizing state
        self.resizing = False
        self.resize_direction = None
        self.resize_border_width = 8
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0
        self.resize_start_window_x = 0
        self.resize_start_window_y = 0
    
    def set_window(self, window):
        """Set the window reference"""
        self.window = window
        self._setup_window_events()
    
    def _setup_window_events(self):
        """Setup window event handlers"""
        if self.window:
            # Mouse events for resize detection
            self.window.bind('<Motion>', self._on_mouse_motion)
            self.window.bind('<Button-1>', self._on_mouse_click)
            self.window.bind('<B1-Motion>', self._on_mouse_drag)
            self.window.bind('<ButtonRelease-1>', self._on_mouse_release)
    
    def setup_drag_handlers(self, widget):
        """Setup drag handlers for a widget"""
        widget.bind('<Button-1>', self._start_drag)
        widget.bind('<B1-Motion>', self._on_drag)
        widget.bind('<ButtonRelease-1>', self._stop_drag)
        widget.bind('<Double-Button-1>', lambda e: self.reset_to_quarter_screen())
    
    def _start_drag(self, event):
        """Start window dragging"""
        if self.window:
            self.drag_x = event.x_root - self.window.winfo_x()
            self.drag_y = event.y_root - self.window.winfo_y()
            self.dragging = True
            self.window.config(cursor="fleur")
            event.widget.config(cursor="fleur")
    
    def _on_drag(self, event):
        """Handle window dragging"""
        if self.dragging and self.window:
            x = event.x_root - self.drag_x
            y = event.y_root - self.drag_y
            
            # Keep window within screen bounds
            x, y = self.display_manager.get_window_bounds(
                x, y, 
                self.settings.get('window_width', 400),
                self.settings.get('window_height', 600)
            )
            
            self.window.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event):
        """Stop window dragging"""
        if self.window:
            self.dragging = False
            self.window.config(cursor="")
            event.widget.config(cursor="")
            
            # Save new position
            self._save_window_geometry()
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion for resize cursor changes"""
        if self.resizing or self.dragging or not self.window:
            return
        
        x, y = event.x, event.y
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Skip if in title bar area (for dragging)
        title_height = self.display_manager.get_scaled_dimension(35)
        if y <= title_height:
            self.resize_direction = None
            self.window.config(cursor="")
            return
        
        # Check if mouse is in UI control area (top 70 pixels) - no resize here
        ui_zone_height = self.display_manager.get_scaled_dimension(70)
        if y <= ui_zone_height:
            self.resize_direction = None
            self.window.config(cursor="")
            return
        
        # Determine resize direction based on mouse position
        cursor = ""
        self.resize_direction = None
        
        # Right edge
        if width - self.resize_border_width <= x <= width:
            if height - self.resize_border_width <= y <= height:
                cursor = "bottom_right_corner"
                self.resize_direction = "se"
            elif ui_zone_height <= y <= self.resize_border_width + ui_zone_height:
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
            elif ui_zone_height <= y <= self.resize_border_width + ui_zone_height:
                cursor = "top_left_corner"
                self.resize_direction = "nw"
            else:
                cursor = "sb_h_double_arrow"
                self.resize_direction = "w"
        
        # Bottom edge
        elif height - self.resize_border_width <= y <= height:
            cursor = "sb_v_double_arrow"
            self.resize_direction = "s"
        
        # Top edge (below UI zone)
        elif ui_zone_height <= y <= self.resize_border_width + ui_zone_height:
            cursor = "sb_v_double_arrow"
            self.resize_direction = "n"
        
        else:
            cursor = ""
            self.resize_direction = None
        
        self.window.config(cursor=cursor)
        
    def reset_cursor(self):
        """Reset cursor to default"""
        if self.window:
            self.window.config(cursor="")
            self.resize_direction = None
    
    def _on_mouse_click(self, event):
        """Handle mouse click for resize start"""
        if self.resize_direction and self.window:
            self.resizing = True
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_width = self.window.winfo_width()
            self.resize_start_height = self.window.winfo_height()
            self.resize_start_window_x = self.window.winfo_x()
            self.resize_start_window_y = self.window.winfo_y()
            return "break"  # Prevent other click handlers
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag for resizing"""
        if not self.resizing or not self.window:
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
        self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    
    def _on_mouse_release(self, event):
        """Handle mouse release to end resizing"""
        if self.resizing and self.window:
            self.resizing = False
            self.resize_direction = None
            self.window.config(cursor="")
            
            # Save new geometry
            self._save_window_geometry()
    
    def _save_window_geometry(self):
        """Save current window geometry to settings"""
        if not self.window:
            return
        
        geometry = self.window.geometry()
        if '+' in geometry:
            try:
                size, position = geometry.split('+', 1)
                width, height = size.split('x')
                x, y = position.split('+')
                self.settings.update({
                    'window_width': int(width),
                    'window_height': int(height),
                    'window_x': int(x),
                    'window_y': int(y)
                })
                self.settings.save_config()
            except:
                pass
    
    def reset_to_quarter_screen(self):
        """Reset window to right 1/4 of current display"""
        if not self.window:
            return
        
        # Refresh display settings in case of changes
        self.display_manager.refresh_display_settings()
        
        # Get new layout
        layout = self.display_manager.get_quarter_screen_layout()
        
        # Update settings
        self.settings.update({
            'window_width': layout['width'],
            'window_height': layout['height'],
            'window_x': layout['x'],
            'window_y': layout['y'],
            'font_size': self.display_manager.get_scaled_font_size()
        })
        
        # Apply geometry
        self.window.geometry(f"{layout['width']}x{layout['height']}+{layout['x']}+{layout['y']}")
        
        self.settings.save_config()
        
        display = self.display_manager.get_current_display()
        return f"Reset to right 1/4 of {display['name']}"
    
    def move_to_corner(self, position: str):
        """Move window to specified corner"""
        if not self.window:
            return
        
        width = self.settings.get('window_width', 400)
        height = self.settings.get('window_height', 600)
        
        x, y = self.display_manager.get_corner_position(position, width, height)
        
        self.window.geometry(f"+{x}+{y}")
        self.settings.update({'window_x': x, 'window_y': y})
        self.settings.save_config()
        
        return f"Moved to {position}"
    
    def center_window(self):
        """Center window on current display"""
        if not self.window:
            return
        
        width = self.settings.get('window_width', 400)
        height = self.settings.get('window_height', 600)
        
        x, y = self.display_manager.get_center_position(width, height)
        
        self.window.geometry(f"+{x}+{y}")
        self.settings.update({'window_x': x, 'window_y': y})
        self.settings.save_config()
        
        return "Window centered"
    
    def move_to_next_display(self):
        """Move to next display"""
        displays = self.display_manager.get_all_displays()
        if len(displays) <= 1:
            return "Only one display detected"
        
        # Move to next display
        next_display = self.display_manager.get_next_display_index()
        self.display_manager.set_current_display(next_display)
        
        # Get new layout for the display
        layout = self.display_manager.get_quarter_screen_layout()
        
        # Update settings and apply
        self.settings.update({
            'window_width': layout['width'],
            'window_height': layout['height'],
            'window_x': layout['x'],
            'window_y': layout['y']
        })
        
        if self.window:
            self.window.geometry(f"{layout['width']}x{layout['height']}+{layout['x']}+{layout['y']}")
        
        self.settings.save_config()
        
        display = self.display_manager.get_current_display()
        return f"Moved to {display['name']}"
    
    def get_window_position_info(self) -> str:
        """Get current window position information"""
        if not self.window:
            return "No window available"
        
        display = self.display_manager.get_current_display()
        display_index = self.display_manager.current_display
        total_displays = len(self.display_manager.get_all_displays())
        
        return f"D{display_index + 1}/{total_displays}"
    
    def apply_window_geometry(self):
        """Apply stored window geometry"""
        if not self.window:
            return
        
        width = self.settings.get('window_width', 400)
        height = self.settings.get('window_height', 600)
        x = self.settings.get('window_x', 100)
        y = self.settings.get('window_y', 100)
        
        # Ensure position is within bounds
        x, y = self.display_manager.get_window_bounds(x, y, width, height)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def get_title_bar_height(self) -> int:
        """Get title bar height scaled for DPI"""
        return self.display_manager.get_scaled_dimension(35)