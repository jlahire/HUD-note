"""
Global hotkey management for HUD Notes
"""

import threading
from pynput import keyboard
from typing import Dict, Callable


class HotkeyManager:
    """Manages global hotkeys and keyboard shortcuts"""
    
    def __init__(self, app):
        self.app = app
        self.listener = None
        self.hotkey_thread = None
        self.running = False
        
        # Hotkey action mappings
        self.hotkey_actions = {
            'toggle_overlay': self.app.toggle_overlay,
            'new_note': self.app.new_note,
            'open_note': self.app.open_note,
            'save_note': self.app.save_note,
            'save_as': self.app.save_as_note,
            'code_window': self.app.open_code_window,
            'toggle_preview': self.app.toggle_preview,
            'reset_position': self.app.reset_position,
            'move_corner_1': lambda: self.app.move_to_corner('top-left'),
            'move_corner_2': lambda: self.app.move_to_corner('top-right'),
            'move_corner_3': lambda: self.app.move_to_corner('bottom-left'),
            'move_corner_4': lambda: self.app.move_to_corner('bottom-right'),
            'center_window': self.app.center_window,
            'quit_app': self.app.shutdown,  # Added quit functionality
        }
        
        self._setup_hotkeys()
    
    def _setup_hotkeys(self):
        """Setup global hotkeys"""
        def hotkey_listener():
            try:
                # Get hotkey configuration
                hotkeys = self.app.settings.get('hotkeys', {})
                
                # Create hotkey mappings
                hotkey_map = {}
                for action, hotkey_string in hotkeys.items():
                    if action in self.hotkey_actions:
                        # Convert hotkey string to pynput format
                        pynput_hotkey = self._convert_hotkey_string(hotkey_string)
                        if pynput_hotkey:
                            # Wrap the action to ensure it runs in main thread
                            action_func = self._create_thread_safe_action(self.hotkey_actions[action])
                            hotkey_map[pynput_hotkey] = action_func
                
                # Start global hotkey listener
                if hotkey_map:
                    with keyboard.GlobalHotKeys(hotkey_map):
                        self.running = True
                        while self.running:
                            import time
                            time.sleep(0.1)
                        
            except Exception as e:
                print(f"Hotkey listener error: {e}")
                self.running = False
        
        # Start hotkey listener in separate thread
        self.hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        self.hotkey_thread.start()
    
    def _create_thread_safe_action(self, action):
        """Create a thread-safe wrapper for GUI actions"""
        def safe_action():
            try:
                # Simple approach: just call the action directly
                # The action methods should handle their own thread safety
                action()
            except Exception as e:
                print(f"Error executing hotkey action: {e}")
        
        return safe_action

    def _process_pending_actions(self):
        """Process any pending actions in the main thread"""
        if hasattr(self.app, '_pending_actions') and self.app._pending_actions:
            actions_to_process = self.app._pending_actions.copy()
            self.app._pending_actions.clear()
            
            for action in actions_to_process:
                try:
                    action()
                except Exception as e:
                    print(f"Error processing pending action: {e}")
    
    def _convert_hotkey_string(self, hotkey_string: str) -> str:
        """Convert hotkey string to pynput format"""
        try:
            # Handle common hotkey formats
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
                            'enter': 'enter',
                            'return': 'enter',
                            'space': 'space',
                            'tab': 'tab',
                            'escape': 'esc',
                            'esc': 'esc',
                            'backspace': 'backspace',
                            'delete': 'delete',
                            'up': 'up',
                            'down': 'down',
                            'left': 'left',
                            'right': 'right',
                            'home': 'home',
                            'end': 'end',
                            'page_up': 'page_up',
                            'page_down': 'page_down',
                            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
                            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
                            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
                        }
                        key = key_mappings.get(part, part)
            
            if key:
                # Build pynput hotkey string
                if modifiers:
                    return '+'.join(modifiers) + '+' + key
                else:
                    return key
            
            return None
            
        except Exception as e:
            print(f"Error converting hotkey string '{hotkey_string}': {e}")
            return None
    
    def setup_window_shortcuts(self, window):
        """Setup window-specific keyboard shortcuts"""
        # Standard shortcuts that work when window has focus
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
            '<Control-Alt-q>': lambda e: self.app.shutdown(),  # Added quit hotkey
            '<Escape>': lambda e: self.app.hide_overlay(),
        }
        
        # Window positioning shortcuts
        position_shortcuts = {
            '<Control-Alt-Key-1>': lambda e: self.app.move_to_corner('top-left'),
            '<Control-Alt-1>': lambda e: self.app.move_to_corner('top-left'),
            '<Control-Alt-Key-2>': lambda e: self.app.move_to_corner('top-right'),
            '<Control-Alt-2>': lambda e: self.app.move_to_corner('top-right'),
            '<Control-Alt-Key-3>': lambda e: self.app.move_to_corner('bottom-left'),
            '<Control-Alt-3>': lambda e: self.app.move_to_corner('bottom-left'),
            '<Control-Alt-Key-4>': lambda e: self.app.move_to_corner('bottom-right'),
            '<Control-Alt-4>': lambda e: self.app.move_to_corner('bottom-right'),
            '<Control-Alt-Key-5>': lambda e: self.app.center_window(),
            '<Control-Alt-5>': lambda e: self.app.center_window(),
        }
        
        # Bind all shortcuts
        all_shortcuts = {**shortcuts, **position_shortcuts}
        
        for shortcut, action in all_shortcuts.items():
            try:
                window.bind(shortcut, action)
            except Exception as e:
                print(f"Error binding shortcut {shortcut}: {e}")
    
    def setup_text_area_shortcuts(self, text_area):
        """Setup text area specific shortcuts"""
        # Position shortcuts also work in text area
        position_shortcuts = {
            '<Control-Alt-Key-1>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('top-left')),
            '<Control-Alt-1>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('top-left')),
            '<Control-Alt-Key-2>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('top-right')),
            '<Control-Alt-2>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('top-right')),
            '<Control-Alt-Key-3>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('bottom-left')),
            '<Control-Alt-3>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('bottom-left')),
            '<Control-Alt-Key-4>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('bottom-right')),
            '<Control-Alt-4>': lambda e: self._text_area_action(lambda: self.app.move_to_corner('bottom-right')),
            '<Control-Alt-Key-5>': lambda e: self._text_area_action(lambda: self.app.center_window()),
            '<Control-Alt-5>': lambda e: self._text_area_action(lambda: self.app.center_window()),
        }
        
        for shortcut, action in position_shortcuts.items():
            try:
                text_area.bind(shortcut, action)
            except Exception as e:
                print(f"Error binding text area shortcut {shortcut}: {e}")
    
    def _text_area_action(self, action: Callable) -> str:
        """Execute action and return 'break' to prevent further processing"""
        try:
            action()
        except Exception as e:
            print(f"Error executing text area action: {e}")
        return "break"
    
    def create_hotkey_display_text(self) -> str:
        """Create hotkey display text for the bottom bar"""
        hotkeys = self.app.settings.get('hotkeys', {})
        
        # Create simplified hotkey display
        key_display = []
        
        # Main hotkeys
        if 'toggle_overlay' in hotkeys:
            key_display.append(f"{hotkeys['toggle_overlay']}=Toggle")
        
        key_display.extend([
            "Drag=Move",
            f"{hotkeys.get('new_note', 'Ctrl+Alt+N')}=New",
            f"{hotkeys.get('open_note', 'Ctrl+Alt+O')}=Open",
            f"{hotkeys.get('save_note', 'Ctrl+Alt+S')}=Save",
            f"{hotkeys.get('toggle_preview', 'Ctrl+Alt+P')}=Preview",
            "Ctrl+Alt++=Font+",
            "Ctrl+Alt+-=Font-",
            f"{hotkeys.get('code_window', 'Ctrl+Alt+C')}=Code",
            f"{hotkeys.get('move_corner_1', 'Ctrl+Alt+1-4')}=Corners",
            f"{hotkeys.get('center_window', 'Ctrl+Alt+5')}=Center",
            f"{hotkeys.get('reset_position', 'Ctrl+Alt+M')}=NextDisplay",
            "Esc=Hide",
            "Ctrl+Alt+Q=Exit",
            f"{hotkeys.get('reset_position', 'Ctrl+Alt+R')}=Reset"
        ])
        
        return "HOTKEYS: " + " | ".join(key_display)
    
    def update_hotkeys(self, new_hotkeys: Dict[str, str]):
        """Update hotkey configuration"""
        # Stop current listener
        self.shutdown()
        
        # Update settings
        self.app.settings.set('hotkeys', new_hotkeys)
        
        # Restart with new hotkeys
        self._setup_hotkeys()
    
    def shutdown(self):
        """Shutdown hotkey manager"""
        self.running = False
        
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        
        if self.hotkey_thread and self.hotkey_thread.is_alive():
            try:
                self.hotkey_thread.join(timeout=1)
            except:
                pass
    
    def get_available_modifiers(self) -> list:
        """Get list of available modifier keys"""
        return ['Ctrl', 'Alt', 'Shift', 'Cmd', 'Super']
    
    def get_available_keys(self) -> list:
        """Get list of available keys"""
        return [
            # Letters
            *[chr(i) for i in range(ord('a'), ord('z') + 1)],
            # Numbers
            *[str(i) for i in range(10)],
            # Function keys
            *[f'f{i}' for i in range(1, 13)],
            # Special keys
            'Enter', 'Return', 'Space', 'Tab', 'Escape', 'Esc',
            'Backspace', 'Delete', 'Up', 'Down', 'Left', 'Right',
            'Home', 'End', 'Page_Up', 'Page_Down'
        ]
    
    def validate_hotkey(self, hotkey_string: str) -> bool:
        """Validate hotkey string format"""
        try:
            return self._convert_hotkey_string(hotkey_string) is not None
        except:
            return False