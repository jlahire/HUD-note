"""
Minimal hotkey management - ONLY toggle show/hide - THREAD SAFE VERSION
"""

import threading
from pynput import keyboard
from typing import Dict, Callable
import queue


class HotkeyManager:
    """Manages only the essential toggle hotkey with thread-safe communication"""
    
    def __init__(self, app):
        self.app = app
        self.listener = None
        self.hotkey_thread = None
        self.running = False
        
        # Thread-safe communication queue
        self.command_queue = queue.Queue()
        
        # Only one hotkey - toggle overlay
        self.toggle_hotkey = self.app.settings.get('hotkeys', {}).get('toggle_overlay', 'Ctrl+Alt+H')
        
        self._setup_toggle_hotkey()
        self._start_queue_processor()
    
    def _setup_toggle_hotkey(self):
        """Setup only the toggle hotkey with thread-safe queue communication"""
        def hotkey_listener():
            try:
                # Convert hotkey string to pynput format
                pynput_hotkey = self._convert_hotkey_string(self.toggle_hotkey)
                
                if pynput_hotkey:
                    print(f"DEBUG: Setting up toggle hotkey: {self.toggle_hotkey} -> {pynput_hotkey}")
                    
                    # Create simple toggle action that uses queue
                    def toggle_action():
                        print(f"DEBUG: Toggle hotkey triggered - queuing command")
                        try:
                            # Put command in queue instead of direct GUI access
                            self.command_queue.put(('toggle_overlay',))
                        except Exception as e:
                            print(f"DEBUG: Queue error: {e}")
                    
                    # Start global hotkey listener with only toggle
                    hotkey_map = {pynput_hotkey: toggle_action}
                    
                    with keyboard.GlobalHotKeys(hotkey_map):
                        self.running = True
                        while self.running:
                            import time
                            time.sleep(0.1)
                else:
                    print(f"DEBUG: Could not setup hotkey: {self.toggle_hotkey}")
                        
            except Exception as e:
                print(f"Toggle hotkey listener error: {e}")
                self.running = False
        
        # Start hotkey listener in separate thread
        self.hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        self.hotkey_thread.start()
    
    def _start_queue_processor(self):
        """Start the queue processor in the main thread"""
        def process_commands():
            """Process commands from the queue - runs in main thread"""
            try:
                while True:
                    try:
                        command = self.command_queue.get_nowait()
                        if command[0] == 'toggle_overlay':
                            print(f"DEBUG: Processing toggle command from queue")
                            # This runs in main thread, so it's safe
                            if self.app.overlay_visible:
                                self.app.hide_overlay()
                                print("DEBUG: Overlay hidden via queue")
                            else:
                                self.app.show_overlay()
                                print("DEBUG: Overlay shown via queue")
                    except queue.Empty:
                        break
            except Exception as e:
                print(f"DEBUG: Queue processor error: {e}")
            
            # Schedule next check
            if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
                try:
                    self.app.overlay.root.after(50, process_commands)  # Check every 50ms
                except:
                    pass
        
        # Start the processor
        if hasattr(self.app, 'overlay') and self.app.overlay and self.app.overlay.root:
            self.app.overlay.root.after(100, process_commands)
    
    def _convert_hotkey_string(self, hotkey_string: str) -> str:
        """Convert hotkey string to pynput format"""
        try:
            parts = hotkey_string.lower().split('+')
            
            modifiers = []
            key = None
            
            for part in parts:
                part = part.strip()
                if part == 'ctrl':
                    modifiers.append('<ctrl>')
                elif part == 'alt':
                    modifiers.append('<alt>')
                elif part == 'shift':
                    modifiers.append('<shift>')
                elif part == 'cmd' or part == 'super':
                    modifiers.append('<cmd>')
                else:
                    # This should be the key
                    if len(part) == 1:
                        key = part
                    else:
                        # Handle special keys
                        key_mappings = {
                            'enter': 'enter', 'return': 'enter', 'space': 'space',
                            'tab': 'tab', 'escape': 'esc', 'esc': 'esc',
                            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
                            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
                            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
                        }
                        key = key_mappings.get(part, part)
            
            if key:
                if modifiers:
                    return '+'.join(modifiers) + '+' + key
                else:
                    return key
            
            return None
            
        except Exception as e:
            print(f"Error converting hotkey string '{hotkey_string}': {e}")
            return None
    
    def setup_window_shortcuts(self, window):
        """Setup window-specific keyboard shortcuts - FULL FEATURE SET"""
        print("DEBUG: Setting up window shortcuts (no global hotkeys)")
        
        # All the functionality via window shortcuts (when window has focus)
        shortcuts = {
            '<Control-Alt-n>': lambda e: self.app.new_note(),
            '<Control-Alt-o>': lambda e: self.app.open_note(),
            '<Control-Alt-s>': lambda e: self.app.save_note(),
            '<Control-Alt-S>': lambda e: self.app.save_as_note(),
            '<Control-Alt-p>': lambda e: self.app.toggle_preview(),
            '<Control-Alt-plus>': lambda e: self.app.increase_font(),
            '<Control-Alt-minus>': lambda e: self.app.decrease_font(),
            '<Control-Alt-c>': lambda e: self.app.open_code_window(),
            '<Control-Alt-g>': lambda e: self.app.open_settings(),
            '<Control-Alt-r>': lambda e: self.app.reset_position(),
            '<Control-Alt-m>': lambda e: self.app.move_to_next_display(),
            '<Control-Alt-q>': lambda e: self.app.shutdown(),
            '<Escape>': lambda e: self.app.hide_overlay(),
            
            # Window positioning
            '<Control-Alt-1>': lambda e: self.app.move_to_corner('top-left'),
            '<Control-Alt-2>': lambda e: self.app.move_to_corner('top-right'),
            '<Control-Alt-3>': lambda e: self.app.move_to_corner('bottom-left'),
            '<Control-Alt-4>': lambda e: self.app.move_to_corner('bottom-right'),
            '<Control-Alt-5>': lambda e: self.app.center_window(),
        }
        
        # Bind all shortcuts (these work when window has focus - no threading issues)
        for shortcut, action in shortcuts.items():
            try:
                window.bind(shortcut, action)
                print(f"DEBUG: Bound window shortcut {shortcut}")
            except Exception as e:
                print(f"Error binding shortcut {shortcut}: {e}")
    
    def setup_text_area_shortcuts(self, text_area):
        """Setup text area specific shortcuts"""
        print("DEBUG: Setting up text area shortcuts")
        
        # Position shortcuts work in text area too
        position_shortcuts = {
            '<Control-Alt-1>': lambda e: (self.app.move_to_corner('top-left'), "break")[1],
            '<Control-Alt-2>': lambda e: (self.app.move_to_corner('top-right'), "break")[1],
            '<Control-Alt-3>': lambda e: (self.app.move_to_corner('bottom-left'), "break")[1],
            '<Control-Alt-4>': lambda e: (self.app.move_to_corner('bottom-right'), "break")[1],
            '<Control-Alt-5>': lambda e: (self.app.center_window(), "break")[1],
        }
        
        for shortcut, action in position_shortcuts.items():
            try:
                text_area.bind(shortcut, action)
            except Exception as e:
                print(f"Error binding text area shortcut {shortcut}: {e}")
    
    def update_hotkeys(self, new_hotkeys: Dict[str, str]):
        """Update hotkey configuration - only toggle supported"""
        if 'toggle_overlay' in new_hotkeys:
            self.toggle_hotkey = new_hotkeys['toggle_overlay']
            self.shutdown()
            self._setup_toggle_hotkey()
    
    def shutdown(self):
        """Shutdown hotkey manager"""
        print("DEBUG: Shutting down thread-safe hotkey manager")
        self.running = False
        
        if self.hotkey_thread and self.hotkey_thread.is_alive():
            try:
                self.hotkey_thread.join(timeout=1)
            except:
                pass