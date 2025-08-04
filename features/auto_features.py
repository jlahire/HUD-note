"""
Auto show/hide features for HUD Notes
"""

import threading
import time
from pynput import mouse
from typing import Optional


class AutoFeatureManager:
    """Manages auto show/hide features like mouse hover and click outside"""
    
    def __init__(self, app):
        self.app = app
        
        # Mouse hover monitoring
        self.hover_monitor_active = False
        self.hover_monitor_thread = None
        
        # Click outside monitoring
        self.click_listener = None
        
        self._setup_features()
    
    def _setup_features(self):
        """Setup auto features based on settings"""
        if self.app.settings.get('mouse_hover_show', False):
            self.setup_mouse_hover_monitor()
        
        if self.app.settings.get('click_outside_hide', False):
            self.setup_click_outside_monitor()
    
    def setup_mouse_hover_monitor(self):
        """Setup mouse hover monitoring for top-left corner"""
        if hasattr(self, 'hover_monitor_thread') and self.hover_monitor_thread and self.hover_monitor_thread.is_alive():
            return
        
        self.hover_monitor_active = True
        
        def hover_monitor():
            """Monitor mouse position for top-left corner hover"""
            import time
            while self.hover_monitor_active:
                try:
                    if not self.app.overlay_visible:
                        # Get mouse position using a temporary window
                        try:
                            import tkinter as tk
                            
                            # Create temp window in main thread
                            def get_mouse_pos():
                                temp_root = tk.Tk()
                                temp_root.withdraw()
                                mouse_x = temp_root.winfo_pointerx()
                                mouse_y = temp_root.winfo_pointery()
                                temp_root.destroy()
                                return mouse_x, mouse_y
                            
                            # Get mouse position safely
                            if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                                # Use existing root to get mouse position
                                try:
                                    mouse_x = self.app.overlay.root.winfo_pointerx()
                                    mouse_y = self.app.overlay.root.winfo_pointery()
                                except:
                                    # Fallback method
                                    mouse_x, mouse_y = 0, 0
                            else:
                                mouse_x, mouse_y = 0, 0
                            
                            # Check if mouse is in top-left corner (50x50 pixels)
                            if mouse_x <= 50 and mouse_y <= 50:
                                # Show overlay using thread-safe method
                                if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                                    self.app.overlay.root.after(0, self.app.show_overlay)
                                time.sleep(1)  # Prevent rapid toggling
                        
                        except Exception as e:
                            print(f"Mouse position detection error: {e}")
                    
                    time.sleep(0.1)  # Check every 100ms
                    
                except Exception as e:
                    print(f"Hover monitor error: {e}")
                    break
        
        self.hover_monitor_thread = threading.Thread(target=hover_monitor, daemon=True)
        self.hover_monitor_thread.start()
    
    def stop_mouse_hover_monitor(self):
        """Stop mouse hover monitoring"""
        self.hover_monitor_active = False
        if self.hover_monitor_thread:
            try:
                self.hover_monitor_thread.join(timeout=1)
            except:
                pass
    
    def setup_click_outside_monitor(self):
        """Setup click outside monitoring"""
        def on_global_click(x, y, button, pressed):
            """Handle global mouse clicks"""
            if pressed and self.app.overlay_visible:
                # Get overlay window bounds
                try:
                    if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                        # Use thread-safe method to get window info
                        def hide_if_outside():
                            try:
                                win_x = self.app.overlay.root.winfo_x()
                                win_y = self.app.overlay.root.winfo_y()
                                win_width = self.app.overlay.root.winfo_width()
                                win_height = self.app.overlay.root.winfo_height()
                                
                                # Check if click is outside overlay
                                if not (win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height):
                                    # Hide overlay
                                    self.app.hide_overlay()
                            except Exception as e:
                                print(f"Click outside detection error: {e}")
                        
                        # Schedule in main thread
                        self.app.overlay.root.after(0, hide_if_outside)
                
                except Exception as e:
                    print(f"Click outside detection error: {e}")
        
        if not hasattr(self, 'click_listener') or not self.click_listener or not self.click_listener.running:
            try:
                self.click_listener = mouse.Listener(on_click=on_global_click)
                self.click_listener.start()
            except Exception as e:
                print(f"Click outside monitor setup error: {e}")
    
    def stop_click_outside_monitor(self):
        """Stop click outside monitoring"""
        if self.click_listener and self.click_listener.running:
            try:
                self.click_listener.stop()
            except:
                pass
    
    def update_settings(self):
        """Update auto features based on current settings"""
        # Stop existing features
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
        
        # Restart based on current settings
        self._setup_features()
    
    def shutdown(self):
        """Shutdown all auto features"""
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
    
    def get_hover_zone_info(self) -> dict:
        """Get information about the hover zone"""
        return {
            'enabled': self.app.settings.get('mouse_hover_show', False),
            'zone_size': 50,  # 50x50 pixels
            'zone_position': 'top-left',
            'description': 'Hover mouse in top-left corner to show overlay when hidden'
        }
    
    def get_click_outside_info(self) -> dict:
        """Get information about click outside feature"""
        return {
            'enabled': self.app.settings.get('click_outside_hide', False),
            'description': 'Click anywhere outside the overlay to hide it'
        }
    
    def is_hover_monitoring_active(self) -> bool:
        """Check if hover monitoring is currently active"""
        return self.hover_monitor_active and (
            self.hover_monitor_thread and self.hover_monitor_thread.is_alive()
        )
    
    def is_click_monitoring_active(self) -> bool:
        """Check if click outside monitoring is currently active"""
        return self.click_listener and self.click_listener.running