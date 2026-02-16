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

        # Track whether a click landed inside the overlay window.
        # Set to True by a Tkinter <Button-1> binding on the overlay root,
        # checked by the pynput click handler to avoid coordinate comparison
        # (which breaks on Windows with DPI scaling).
        self._click_was_inside = False

        self._setup_features()
        self._start_queue_processor()

    def _setup_features(self):
        """Setup auto features based on settings"""
        if self.app.settings.get('mouse_hover_show', False):
            self.setup_mouse_hover_monitor()

        if self.app.settings.get('click_outside_hide', False):
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
                            if not self.app.overlay_visible:
                                self.app.show_overlay()
                        elif command[0] == 'hide_overlay':
                            if self.app.overlay_visible:
                                self.app.hide_overlay()
                        elif command[0] == 'check_click_outside':
                            if self.app.overlay_visible and self.app.overlay and self.app.overlay.root:
                                # If Tkinter received a <Button-1> on our
                                # window, the click was inside — skip hide.
                                if self._click_was_inside:
                                    self._click_was_inside = False
                                else:
                                    self.app.hide_overlay()
                    except queue.Empty:
                        break
            except Exception:
                pass

            # Schedule next check
            if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                try:
                    self.app.overlay.root.after(100, process_commands)
                except:
                    pass

        # Start the processor
        if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
            self.app.overlay.root.after(200, process_commands)

    def mark_click_inside(self, event=None):
        """Called by Tkinter <Button-1> binding on the overlay root.
        Tells the pynput handler that this click was inside our window."""
        self._click_was_inside = True

    def setup_mouse_hover_monitor(self):
        """Setup mouse hover monitoring for top-left corner - THREAD SAFE VERSION"""
        if hasattr(self, 'hover_monitor_thread') and self.hover_monitor_thread and self.hover_monitor_thread.is_alive():
            return

        self.hover_monitor_active = True

        def hover_monitor():
            """Monitor mouse position for top-left corner hover"""
            while self.hover_monitor_active:
                try:
                    if not self.app.overlay_visible:
                        try:
                            from pynput.mouse import Controller
                            mouse_controller = Controller()
                            mouse_x, mouse_y = mouse_controller.position

                            # Check if mouse is in top-left corner (50x50 pixels)
                            if mouse_x <= 50 and mouse_y <= 50 and mouse_x > 0 and mouse_y > 0:
                                self.command_queue.put(('show_overlay',))
                                time.sleep(1)  # Prevent rapid toggling
                        except Exception:
                            pass

                    time.sleep(0.1)  # Check every 100ms

                except Exception:
                    time.sleep(0.5)  # Wait longer on error
                    continue

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
                try:
                    self.command_queue.put(('check_click_outside', x, y))
                except Exception:
                    pass

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
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
        self._setup_features()

    def shutdown(self):
        """Shutdown all auto features"""
        self.stop_mouse_hover_monitor()
        self.stop_click_outside_monitor()
