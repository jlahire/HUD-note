"""
Auto show/hide features for HUD Notes - THREAD SAFE VERSION
"""

import threading
import time
from pynput import mouse
import queue
from typing import Optional


class AutoFeatureManager:
    """Manages auto show/hide features like mouse hover and click outside - THREAD SAFE"""
    
    def __init__(self, app):
        self.app = app
        
        # Thread-safe communication queue
        self.command_queue = queue.Queue()
        
        # Mouse hover monitoring
        self.hover_monitor_active = False
        self.hover_monitor_thread = None
        
        # Click outside monitoring
        self.click_listener = None
        
        self._setup_features()
        self._start_queue_processor()
    
    def _setup_features(self):
        """Setup auto features based on settings"""
        print("DEBUG: Setting up auto features...")
        if self.app.settings.get('mouse_hover_show', False):
            print("DEBUG: Mouse hover enabled, starting monitor")
            self.setup_mouse_hover_monitor()
        
        if self.app.settings.get('click_outside_hide', False):
            print("DEBUG: Click outside enabled, starting monitor")
            self.setup_click_outside_monitor()
    
    def _start_queue_processor(self):
        """Start the queue processor in the main thread"""
        def process_commands():
            """Process commands from the queue - runs in main thread"""
            try:
                while True:
                    try:
                        command = self.command_queue.get_nowait()
                        if command[0] == 'show_overlay':
                            print(f"DEBUG: Processing show command from auto features")
                            if not self.app.overlay_visible:
                                self.app.show_overlay()
                        elif command[0] == 'hide_overlay':
                            print(f"DEBUG: Processing hide command from auto features")
                            if self.app.overlay_visible:
                                self.app.hide_overlay()
                    except queue.Empty:
                        break
            except Exception as e:
                print(f"DEBUG: Auto features queue processor error: {e}")
            
            # Schedule next check
            if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                try:
                    self.app.overlay.root.after(100, process_commands)  # Check every 100ms
                except:
                    pass
        
        # Start the processor
        if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
            self.app.overlay.root.after(200, process_commands)
    
    def setup_mouse_hover_monitor(self):
        """Setup mouse hover monitoring for top-left corner - THREAD SAFE VERSION"""
        if hasattr(self, 'hover_monitor_thread') and self.hover_monitor_thread and self.hover_monitor_thread.is_alive():
            return
        
        self.hover_monitor_active = True
        
        def hover_monitor():
            """Monitor mouse position for top-left corner hover"""
            print("DEBUG: Starting hover monitor thread")
            while self.hover_monitor_active:
                try:
                    if not self.app.overlay_visible:
                        # Get mouse position using pynput (thread-safe)
                        try:
                            from pynput.mouse import Listener, Controller
                            mouse_controller = Controller()
                            mouse_x, mouse_y = mouse_controller.position
                            
                            # Check if mouse is in top-left corner (50x50 pixels)
                            if mouse_x <= 50 and mouse_y <= 50 and mouse_x > 0 and mouse_y > 0:
                                print(f"DEBUG: Mouse in hover zone: {mouse_x}, {mouse_y}")
                                # Queue show command instead of direct GUI access
                                try:
                                    self.command_queue.put(('show_overlay',))
                                    time.sleep(1)  # Prevent rapid toggling
                                except Exception as e:
                                    print(f"DEBUG: Hover queue error: {e}")
                            
                        except Exception as e:
                            print(f"DEBUG: Mouse position detection error: {e}")
                    
                    time.sleep(0.1)  # Check every 500ms
                    
                except Exception as e:
                    print(f"Hover monitor error: {e}")
                    time.sleep(0.5)  # Wait longer on error
                    continue
            
            print("DEBUG: Hover monitor thread stopped")
        
        self.hover_monitor_thread = threading.Thread(target=hover_monitor, daemon=True)
        self.hover_monitor_thread.start()
    
    def stop_mouse_hover_monitor(self):
        """Stop mouse hover monitoring"""
        print("DEBUG: Stopping hover monitor")
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
                try:
                    # Queue the hide check instead of direct GUI access
                    self.command_queue.put(('check_click_outside', x, y))
                except Exception as e:
                    print(f"Click outside queue error: {e}")
        
        if not hasattr(self, 'click_listener') or not self.click_listener or not self.click_listener.running:
            try:
                self.click_listener = mouse.Listener(on_click=on_global_click)
                self.click_listener.start()
                print("DEBUG: Click outside listener started")
            except Exception as e:
                print(f"Click outside monitor setup error: {e}")
    
    def stop_click_outside_monitor(self):
        """Stop click outside monitoring"""
        print("DEBUG: Stopping click outside monitor")
        if self.click_listener and self.click_listener.running:
            try:
                self.click_listener.stop()
            except:
                pass
    
    def update_settings(self):
        """Update auto features based on current settings"""
        print("DEBUG: Updating auto feature settings")
        # Stop existing features
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
        
        # Restart based on current settings
        self._setup_features()
    
    def shutdown(self):
        """Shutdown all auto features"""
        print("DEBUG: Shutting down auto features")
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()