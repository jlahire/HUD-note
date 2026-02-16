"""
Auto show/hide features for HUD Notes - THREAD SAFE VERSION
"""

import sys
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

        # DPI scale factor: pynput uses physical pixels, Tkinter may use
        # logical pixels on Windows.  Detect once and cache.
        self._dpi_scale = self._detect_dpi_scale()

        self._setup_features()
        self._start_queue_processor()

    def _detect_dpi_scale(self) -> float:
        """Detect DPI scale factor for coordinate conversion.

        On Windows, pynput reports physical screen coordinates while Tkinter
        may report logical (DPI-scaled) coordinates depending on the process
        DPI awareness setting.  We compute the ratio so we can convert between
        the two coordinate spaces.
        """
        if sys.platform != 'win32':
            return 1.0
        try:
            import ctypes
            # Try to make the process per-monitor DPI aware (no-op if already set)
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                pass
            # Get the DPI for the primary monitor (default 96 = 100%)
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except Exception:
            return 1.0

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
                                click_x, click_y = command[1], command[2]
                                try:
                                    self._handle_click_outside(click_x, click_y)
                                except Exception:
                                    pass
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

    def _handle_click_outside(self, click_x, click_y):
        """Check if click is outside the overlay window and hide if so.

        Accounts for DPI scaling differences between pynput (physical pixels)
        and Tkinter (possibly logical pixels) on Windows.
        """
        root = self.app.overlay.root
        # Tkinter-reported geometry (may be logical pixels on Windows)
        win_x = root.winfo_rootx()
        win_y = root.winfo_rooty()
        win_w = root.winfo_width()
        win_h = root.winfo_height()

        # Scale Tkinter coordinates to physical pixels to match pynput
        scale = self._dpi_scale
        if scale != 1.0:
            win_x = int(win_x * scale)
            win_y = int(win_y * scale)
            win_w = int(win_w * scale)
            win_h = int(win_h * scale)

        # Add a margin to avoid false-positive hides from clicks on the
        # window border or due to rounding from DPI conversion.
        margin = 10
        if not (win_x - margin <= click_x <= win_x + win_w + margin and
                win_y - margin <= click_y <= win_y + win_h + margin):
            self.app.hide_overlay()

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
