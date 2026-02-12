"""
Tab management system for HUD Notes
"""

import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import os
import sys
from typing import Dict, List, Optional


class Tab:
    """Individual tab data"""
    
    def __init__(self, tab_id: int, title: str = "Untitled", file_path: str = None):
        self.tab_id = tab_id
        self.title = title
        self.file_path = file_path
        self.content = ""
        self.modified = False
        self.text_widget = None
    
    def get_display_title(self) -> str:
        """Get title for display with modification indicator"""
        title = self.title
        if self.modified:
            title += "*"
        return title
    
    def set_modified(self, modified: bool):
        """Set modification status"""
        self.modified = modified


class TabManager:
    """Manages multiple document tabs"""
    
    def __init__(self, parent, app, theme_manager=None):
        self.parent = parent
        self.app = app
        self.theme_manager = theme_manager
        self.tabs: Dict[int, Tab] = {}
        self.active_tab_id: Optional[int] = None
        self.next_tab_id = 1
        self.untitled_counter = 1
        
        # UI components
        self.tab_frame = None
        self.content_frame = None
        self.tab_buttons: Dict[int, tk.Button] = {}
        
        self._create_ui()
        
        # Create initial tab
        self.create_new_tab()
    
    def _get_theme_color(self, key, default):
        """Get color from theme or fall back to default"""
        if self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            if theme:
                return theme.get_color(key, default)
        return default

    def _create_ui(self):
        """Create tab interface"""
        # Tab bar frame
        tab_bg = self._get_theme_color('status_bg', '#2a2a2a')
        self.tab_frame = tk.Frame(self.parent, bg=tab_bg, height=30)
        self.tab_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        self.tab_frame.pack_propagate(False)

        # Content frame for text areas
        self.content_frame = tk.Frame(self.parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def create_new_tab(self, title: str = None, content: str = "", file_path: str = None) -> int:
        """Create a new tab"""
        tab_id = self.next_tab_id
        self.next_tab_id += 1
        
        # Generate title if not provided
        if not title:
            if file_path:
                title = os.path.basename(file_path)
            else:
                title = f"Untitled {self.untitled_counter}"
                self.untitled_counter += 1
        
        # Create tab object
        tab = Tab(tab_id, title, file_path)
        tab.content = content
        self.tabs[tab_id] = tab
        
        # Create text widget
        self._create_text_widget(tab)
        
        # Create tab button
        self._create_tab_button(tab)
        
        # Switch to new tab
        self.switch_to_tab(tab_id)
        
        return tab_id
    
    def _create_text_widget(self, tab: Tab):
        """Create text widget for tab"""
        tab.text_widget = ScrolledText(
            self.content_frame,
            wrap=tk.WORD,
            font=('Consolas', self.app.settings.get('font_size', 12)),
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#333333',
            undo=True,
            maxundo=50
        )
        
        # Apply theme (if theme manager is available)
        if self.theme_manager:
            self.theme_manager.apply_theme_to_text_widget(tab.text_widget)
        
        # Insert content
        if tab.content:
            tab.text_widget.insert(1.0, tab.content)
        
        # Bind events
        tab.text_widget.bind('<KeyRelease>', lambda e: self._on_text_change(tab.tab_id))
        
        # Setup shortcuts
        if hasattr(self.app, 'hotkey_manager'):
            self.app.hotkey_manager.setup_text_area_shortcuts(tab.text_widget)
        
        # Hide initially
        tab.text_widget.pack_forget()
    
    def _create_tab_button(self, tab: Tab):
        """Create tab button"""
        tab_bg = self._get_theme_color('status_bg', '#2a2a2a')
        btn_bg = self._get_theme_color('button_bg', '#3a3a3a')
        btn_fg = self._get_theme_color('fg_color', '#ffffff')

        button_frame = tk.Frame(self.tab_frame, bg=tab_bg)
        button_frame.pack(side=tk.LEFT, padx=1)

        # Tab button
        tab_btn = tk.Button(
            button_frame,
            text=tab.get_display_title(),
            command=lambda: self.switch_to_tab(tab.tab_id),
            bg=btn_bg,
            fg=btn_fg,
            font=('Consolas', 9),
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        tab_btn.pack(side=tk.LEFT)

        # Close button
        close_btn = tk.Button(
            button_frame,
            text="×",
            command=lambda: self.close_tab(tab.tab_id),
            bg=btn_bg,
            fg='#ff6666',
            font=('Arial', 8, 'bold'),
            relief=tk.FLAT,
            width=2,
            pady=2,
            cursor="hand2"
        )
        close_btn.pack(side=tk.LEFT)

        self.tab_buttons[tab.tab_id] = {
            'frame': button_frame,
            'tab_btn': tab_btn,
            'close_btn': close_btn
        }
    
    def switch_to_tab(self, tab_id: int):
        """Switch to specified tab"""
        if tab_id not in self.tabs:
            return

        btn_bg = self._get_theme_color('button_bg', '#3a3a3a')
        btn_active = self._get_theme_color('button_active', '#4a4a4a')

        # Hide current tab
        if self.active_tab_id and self.active_tab_id in self.tabs:
            current_tab = self.tabs[self.active_tab_id]
            if current_tab.text_widget:
                current_tab.text_widget.pack_forget()

            # Update button appearance
            if self.active_tab_id in self.tab_buttons:
                self.tab_buttons[self.active_tab_id]['tab_btn'].config(bg=btn_bg)

        # Show new tab
        new_tab = self.tabs[tab_id]
        if new_tab.text_widget:
            new_tab.text_widget.pack(fill=tk.BOTH, expand=True)
            new_tab.text_widget.focus()

        # Update button appearance
        if tab_id in self.tab_buttons:
            self.tab_buttons[tab_id]['tab_btn'].config(bg=btn_active)

        self.active_tab_id = tab_id

        # Update window title (if overlay is ready)
        if hasattr(self.app, 'overlay') and self.app.overlay:
            self.app.overlay.update_file_label()
    
    def close_tab(self, tab_id: int):
        """Close specified tab"""
        if tab_id not in self.tabs:
            return
        
        tab = self.tabs[tab_id]
        
        # Check for unsaved changes
        if tab.modified:
            # Temporarily disable overrideredirect so dialogs don't freeze on Linux
            overlay = self.app.overlay if hasattr(self.app, 'overlay') else None
            if overlay:
                overlay.prepare_for_dialog()
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes to '{tab.title}' before closing?"
            )
            if overlay:
                overlay.restore_after_dialog()
            if response is True:  # Yes - save first
                if not self._save_tab(tab):
                    return  # Save failed, don't close
            elif response is None:  # Cancel
                return  # Don't close
            # response is False means No - close without saving
        
        # Remove UI elements
        if tab_id in self.tab_buttons:
            self.tab_buttons[tab_id]['frame'].destroy()
            del self.tab_buttons[tab_id]
        
        if tab.text_widget:
            # ScrolledText wraps the Text widget inside a container Frame
            # (text_widget.frame). Destroying only the Text leaves the
            # container Frame orphaned with a default white background.
            if hasattr(tab.text_widget, 'frame'):
                tab.text_widget.frame.destroy()
            else:
                tab.text_widget.destroy()

        # Remove from tabs dict
        del self.tabs[tab_id]
        
        # Handle active tab
        if self.active_tab_id == tab_id:
            self.active_tab_id = None
            
            # Switch to another tab if available
            if self.tabs:
                self.switch_to_tab(next(iter(self.tabs.keys())))
            else:
                # No tabs left, create a new one
                self.create_new_tab()
    
    def get_active_tab(self) -> Optional[Tab]:
        """Get currently active tab"""
        if self.active_tab_id and self.active_tab_id in self.tabs:
            return self.tabs[self.active_tab_id]
        return None
    
    def get_active_text_widget(self) -> Optional[ScrolledText]:
        """Get text widget of active tab"""
        active_tab = self.get_active_tab()
        return active_tab.text_widget if active_tab else None
    
    def _on_text_change(self, tab_id: int):
        """Handle text changes in tab"""
        if tab_id not in self.tabs:
            return
        
        tab = self.tabs[tab_id]
        if tab.text_widget:
            # Update content
            tab.content = tab.text_widget.get(1.0, tk.END)
            
            # Mark as modified
            if not tab.modified:
                tab.set_modified(True)
                self._update_tab_title(tab_id)
            
            # Trigger auto-save
            if hasattr(self.app, 'overlay'):
                self.app.overlay._on_text_change()
    
    def _update_tab_title(self, tab_id: int):
        """Update tab button title"""
        if tab_id not in self.tabs or tab_id not in self.tab_buttons:
            return
        
        tab = self.tabs[tab_id]
        self.tab_buttons[tab_id]['tab_btn'].config(text=tab.get_display_title())
    
    def _save_tab(self, tab: Tab) -> bool:
        """Save tab content"""
        overlay = self.app.overlay if hasattr(self.app, 'overlay') else None
        if not tab.file_path:
            # Need to choose file path
            from tkinter import filedialog
            if overlay:
                overlay.prepare_for_dialog()
            filename = filedialog.asksaveasfilename(
                initialdir=self.app.notes_dir,
                title="Save Note As",
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if overlay:
                overlay.restore_after_dialog()
            if not filename:
                return False
            tab.file_path = filename
            tab.title = os.path.basename(filename)

        # Save content
        try:
            with open(tab.file_path, 'w', encoding='utf-8') as f:
                f.write(tab.content)

            tab.set_modified(False)
            self._update_tab_title(tab.tab_id)
            return True
        except Exception as e:
            if overlay:
                overlay.prepare_for_dialog()
            messagebox.showerror("Error", f"Could not save file: {e}")
            if overlay:
                overlay.restore_after_dialog()
            return False
    
    def save_active_tab(self) -> bool:
        """Save currently active tab"""
        active_tab = self.get_active_tab()
        if active_tab:
            # Update content from text widget
            if active_tab.text_widget:
                active_tab.content = active_tab.text_widget.get(1.0, tk.END)
            return self._save_tab(active_tab)
        return False
    
    def open_file_in_new_tab(self, file_path: str):
        """Open file in new tab"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = os.path.basename(file_path)
            self.create_new_tab(title=title, content=content, file_path=file_path)
            
        except Exception as e:
            overlay = self.app.overlay if hasattr(self.app, 'overlay') else None
            if overlay:
                overlay.prepare_for_dialog()
            messagebox.showerror("Error", f"Could not open file: {e}")
            if overlay:
                overlay.restore_after_dialog()
    
    def update_font_size(self, font_size: int):
        """Update font size for all tabs"""
        for tab in self.tabs.values():
            if tab.text_widget:
                tab.text_widget.config(font=('Consolas', font_size))
    
    def apply_theme(self, theme_manager):
        """Apply theme to all tabs"""
        self.theme_manager = theme_manager
        for tab in self.tabs.values():
            if tab.text_widget:
                theme_manager.apply_theme_to_text_widget(tab.text_widget)

        # Update tab bar background
        tab_bg = self._get_theme_color('status_bg', '#2a2a2a')
        self.tab_frame.config(bg=tab_bg)

        # Update tab buttons
        theme = theme_manager.get_current_theme()
        if theme:
            btn_bg = theme.get_color('button_bg', '#3a3a3a')
            btn_active = theme.get_color('button_active', '#4a4a4a')
            fg_color = theme.get_color('fg_color', '#ffffff')

            for tab_id, buttons in self.tab_buttons.items():
                buttons['tab_btn'].config(bg=btn_bg, fg=fg_color)
                buttons['close_btn'].config(bg=btn_bg)
                buttons['frame'].config(bg=tab_bg)

                # Highlight active tab
                if tab_id == self.active_tab_id:
                    buttons['tab_btn'].config(bg=btn_active)
    
    def cleanup(self):
        """Clean up resources"""
        for tab in self.tabs.values():
            if tab.text_widget:
                if hasattr(tab.text_widget, 'frame'):
                    tab.text_widget.frame.destroy()
                else:
                    tab.text_widget.destroy()
        self.tabs.clear()
        self.tab_buttons.clear()