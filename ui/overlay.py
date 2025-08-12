"""
Main overlay window for HUD Notes - Enhanced with Theme Integration
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
from datetime import datetime

from ui.dialogs import TemplateSelectionDialog, SettingsDialog, CodeInputDialog
from ui.components import StatusBar, HUDInterface, ScreenBorder
from ui.themes import ThemeManager
from features.syntax_highlighting import SyntaxHighlighter
from utils.file_operations import FileManager
from ui.tab_manager import TabManager


class OverlayWindow:
    """Main overlay window class with full theme integration"""
    
    
    def __init__(self, app):
        self.app = app
        self.root = None
        self.tab_manager = None
        self.text_area = None
        self.status_bar = None
        self.syntax_highlighter = None
        self.file_manager = None
        
        # Theme manager
        self.theme_manager = ThemeManager(self.app.settings)
        
        # UI components  
        self.hud_interface = None
        self.screen_border = None
        
        # State
        self.preview_frame = None
        self.preview_area = None
        
        self._create_overlay()
    
    def _create_overlay(self):
        """Create the main overlay window"""
        self.root = tk.Tk()
        self.root.withdraw()  # Start hidden
        self.root.title("HUD Notes")
        
        # Configure window
        self.root.attributes('-alpha', 0.85)
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.resizable(True, True)
        
        # Apply geometry from settings
        self.app.window_manager.set_window(self.root)
        self.app.window_manager.apply_window_geometry()
        
        # Setup theme and interface
        self._setup_theme()
        
        # Create UI components
        self._create_components()
        
        # Setup keyboard shortcuts
        self.app.hotkey_manager.setup_window_shortcuts(self.root)
        
        # Bind events
        self._bind_events()
        
        # Set transparency
        transparency = self.app.settings.get('hud_transparency', 0.85)
        self.root.attributes('-alpha', transparency)
        
        # Initialize file manager
        self.file_manager = FileManager(self.app.notes_dir, self.app.settings)
        
        # Initialize syntax highlighter without a specific text widget
        self.syntax_highlighter = SyntaxHighlighter(
            None,  # No text widget initially
            self.app.settings,
            self.theme_manager
        )
        
        # Load startup content
        self._load_startup_content()
    
    def _setup_theme(self):
        """Setup HUD theme using ThemeManager"""
        # Apply theme to main window
        self.theme_manager.apply_theme_to_window(self.root, "main")
    
    def _create_components(self):
        """Create all UI components with theme support"""
        # Create screen border (always visible)
        self.screen_border = ScreenBorder(self.app.display_manager, self.theme_manager)
        
        # Create main HUD interface
        self.hud_interface = HUDInterface(self.root, self.app, self.theme_manager)
        
        # Create text area
        self._create_text_area()
        
        # Create status bar
        self.status_bar = StatusBar(
            self.root, 
            self.app.settings, 
            self.app.display_manager,
            self.theme_manager,
            self.app
        )
    
    def _create_text_area(self):
        """Create the main text editing area with tab management"""
        # Create editor frame with themed background
        editor_frame = tk.Frame(self.root)
        self.theme_manager.get_current_theme().apply_to_widget(editor_frame, 'frame')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create tab manager instead of single text area
        self.tab_manager = TabManager(editor_frame, self.app, self.theme_manager)
    
    def _bind_events(self):
        """Bind window events"""
        self.root.bind('<Escape>', lambda e: self.hide())
        self.root.bind('<FocusOut>', self._on_focus_out)
        self.root.bind('<FocusIn>', self._on_focus_in)
        self.root.protocol("WM_DELETE_WINDOW", self.app.shutdown)
    
    def _load_startup_content(self):
        """Load startup content into first tab"""
        content = self.app.get_template_overview_content()
        
        if self.tab_manager:
            # Replace content of first tab
            active_tab = self.tab_manager.get_active_tab()
            if active_tab and active_tab.text_widget:
                active_tab.text_widget.delete(1.0, tk.END)
                active_tab.text_widget.insert(1.0, content)
                
                if self.syntax_highlighter:
                    self.syntax_highlighter.set_text_widget(active_tab.text_widget)
                    self.syntax_highlighter.apply_highlighting()
        
        self.update_file_label()
        self.update_status("Template overview loaded")
    
    def show(self):
            """Show the overlay - THREAD SAFE VERSION"""
            try:
                if self.root:
                    try:
                        self.root.deiconify()
                        self.root.lift()
                        self.root.focus_force()
                        print("DEBUG: Successfully showed overlay window")
                    except RuntimeError as e:
                        if "main thread is not in main loop" in str(e):
                            print("DEBUG: Cannot show window from background thread")
                            # Schedule the show operation for the main thread
                            try:
                                self.root.after(0, self._safe_show)
                                print("DEBUG: Scheduled window show for main thread")
                            except Exception as e2:
                                print(f"DEBUG: Could not schedule show operation: {e2}")
                                # Last resort - try direct show despite the error
                                try:
                                    self.root.deiconify()
                                    self.root.lift()
                                    self.root.focus_force()
                                    print("DEBUG: Direct show succeeded unexpectedly")
                                except:
                                    print("DEBUG: All show attempts failed")
                        else:
                            print(f"DEBUG: Unexpected show error: {e}")
                            raise
                    except Exception as e:
                        print(f"DEBUG: Error showing overlay: {e}")
                
                # Focus active tab instead of self.text_area
                if self.tab_manager:
                    active_text = self.tab_manager.get_active_text_widget()
                    if active_text:
                        try:
                            active_text.focus()
                        except:
                            print("DEBUG: Could not focus active text widget")
                
                self.update_status("HUD Activated")
            except Exception as e:
                print(f"DEBUG: Error in show method: {e}")
        
    def _safe_show(self):
            """Safely show window in main thread"""
            try:
                if self.root:
                    self.root.deiconify()
                    self.root.lift() 
                    self.root.focus_force()
                    print("DEBUG: Window shown safely in main thread")
                    
                    # Focus active tab
                    if self.tab_manager:
                        active_text = self.tab_manager.get_active_text_widget()
                        if active_text:
                            active_text.focus()
            except Exception as e:
                print(f"DEBUG: Error in safe show: {e}")
        
            self.update_status("HUD Activated")
    
    def hide(self):
            """Hide the overlay - THREAD SAFE VERSION"""
            try:
                # Save window geometry before hiding (now thread-safe)
                if hasattr(self.app, 'window_manager') and self.app.window_manager:
                    self.app.window_manager._save_window_geometry()
                
                # Try to withdraw the window
                if self.root:
                    try:
                        self.root.withdraw()
                        print("DEBUG: Successfully hid overlay window")
                    except RuntimeError as e:
                        if "main thread is not in main loop" in str(e):
                            print("DEBUG: Cannot hide window from background thread")
                            # Schedule the hide operation for the main thread
                            try:
                                self.root.after(0, self._safe_withdraw)
                                print("DEBUG: Scheduled window hide for main thread")
                            except Exception as e2:
                                print(f"DEBUG: Could not schedule hide operation: {e2}")
                                # Last resort - try direct withdraw despite the error
                                try:
                                    self.root.withdraw()
                                except:
                                    print("DEBUG: All hide attempts failed")
                        else:
                            print(f"DEBUG: Unexpected hide error: {e}")
                            raise
                    except Exception as e:
                        print(f"DEBUG: Error hiding overlay: {e}")
            except Exception as e:
                print(f"DEBUG: Error in hide method: {e}")
        
    def _safe_withdraw(self):
            """Safely withdraw window in main thread"""
            try:
                if self.root:
                    self.root.withdraw()
                    print("DEBUG: Window withdrawn safely in main thread")
            except Exception as e:
                print(f"DEBUG: Error in safe withdraw: {e}")
    
    def new_note(self):
        """Create a new note with template selection"""
        # Show template selection dialog with theme support
        dialog = TemplateSelectionDialog(
            self.root, 
            self.app.template_manager, 
            self.app.author_name, 
            self.app.note_title,
            self.theme_manager
        )
        result = dialog.show()
        
        # Handle dialog result properly
        if result is None:
            # User cancelled template selection
            self.update_status("New note cancelled")
            return
        
        if result['action'] == 'template':
            # Create new tab with template content
            tab_id = self.tab_manager.create_new_tab(content=result['content'])
            self.update_status(f"Created note with {result['template_name']} template")
            
        elif result['action'] == 'blank':
            # Create new blank tab
            tab_id = self.tab_manager.create_new_tab()
            self.update_status("Created blank note")
        
        # Update UI
        self.update_file_label()
        if self.syntax_highlighter:
            # Apply highlighting to new tab
            active_text = self.tab_manager.get_active_text_widget()
            if active_text:
                self.syntax_highlighter.set_text_widget(active_text)
                self.syntax_highlighter.apply_highlighting()
    
    def open_note(self):
        """Open an existing note in new tab"""
        filename = filedialog.askopenfilename(
            initialdir=self.app.notes_dir,
            title="Open Note",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.tab_manager.open_file_in_new_tab(filename)
            self.update_file_label()
            self.update_status(f"Opened: {os.path.basename(filename)}")
            
            if self.syntax_highlighter:
                # Apply highlighting to new tab
                active_text = self.tab_manager.get_active_text_widget()
                if active_text:
                    self.syntax_highlighter.set_text_widget(active_text)
                    self.syntax_highlighter.apply_highlighting()
    
    def save_note(self):
        """Save current tab"""
        if self.tab_manager.save_active_tab():
            active_tab = self.tab_manager.get_active_tab()
            if active_tab and active_tab.file_path:
                self.app.set_current_file(active_tab.file_path)
                self.update_file_label()
                self.update_status(f"Saved: {os.path.basename(active_tab.file_path)}")
    
    def save_as_note(self):
        """Save note with new filename"""
        filename = filedialog.asksaveasfilename(
            initialdir=self.app.notes_dir,
            title="Save Note As",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.app.set_current_file(filename)
            self.save_note()
    
    def open_code_window(self):
        """Open code input window with theme support"""
        dialog = CodeInputDialog(self.root, self.app.settings)
        result = dialog.show()
        
        if result:
            # Get active text widget instead of self.text_area
            active_text = self.tab_manager.get_active_text_widget()
            if active_text:
                cursor_pos = active_text.index(tk.INSERT)
                active_text.insert(cursor_pos, result)
                self.update_status("Inserted code block")
                
                if self.syntax_highlighter:
                    self.syntax_highlighter.set_text_widget(active_text)
                    self.syntax_highlighter.apply_highlighting()
    
    def toggle_preview(self):
        """Toggle markdown preview with theme support"""
        if hasattr(self, 'preview_frame') and self.preview_frame and self.preview_frame.winfo_viewable():
            self.preview_frame.pack_forget()
            # No need to repack text_area since we're using tabs
            self.update_status("Preview hidden")
        else:
            if not hasattr(self, 'preview_frame') or not self.preview_frame:
                self._create_preview()
            
            # Show preview alongside tab manager
            self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            self._update_preview()
            self.update_status("Preview shown")
    
    def _create_preview(self):
        """Create markdown preview pane with theme support"""
        self.preview_frame = tk.Frame(self.root)
        self.theme_manager.get_current_theme().apply_to_widget(self.preview_frame, 'frame')
        
        self.preview_area = ScrolledText(
            self.preview_frame,
            wrap=tk.WORD,
            font=('Arial', self.app.settings.get('font_size', 12)),
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=1
        )
        
        # Apply theme to preview area
        current_theme = self.theme_manager.get_current_theme()
        if current_theme:
            self.preview_area.configure(
                bg=current_theme.get_color('bg_color'),
                fg='#cccccc'  # Use a neutral color for preview
            )
        
        self.preview_area.pack(fill=tk.BOTH, expand=True)
    
    def _update_preview(self):
        """Update markdown preview"""
        if hasattr(self, 'preview_area') and self.preview_area and self.preview_frame.winfo_viewable():
            try:
                import markdown2
                # Get content from active tab instead of self.text_area
                active_text = self.tab_manager.get_active_text_widget()
                if active_text:
                    content = active_text.get(1.0, tk.END)
                    html = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
                    
                    import re
                    text = re.sub(r'<[^>]+>', '', html)
                    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                    
                    self.preview_area.config(state=tk.NORMAL)
                    self.preview_area.delete(1.0, tk.END)
                    self.preview_area.insert(1.0, text)
                    self.preview_area.config(state=tk.DISABLED)
                    
            except Exception as e:
                print(f"Preview update error: {e}")
    
    def open_settings(self):
        """Open settings dialog with theme support"""
        dialog = SettingsDialog(
            self.root, 
            self.app.settings, 
            self.app.display_manager,
            self.theme_manager
        )
        dialog.show()
        
        # Reload theme in case it changed
        self.theme_manager.reload_theme()
        
        # Apply any theme changes
        self._apply_theme_changes()
    
    def increase_font(self):
        """Increase font size"""
        current_size = self.app.settings.get('font_size', 12)
        new_size = min(24, current_size + 1)
        self.app.settings.set('font_size', new_size)
        self._update_fonts()
        self.update_status(f"Font size: {new_size}")
    
    def decrease_font(self):
        """Decrease font size"""
        current_size = self.app.settings.get('font_size', 12)
        new_size = max(8, current_size - 1)
        self.app.settings.set('font_size', new_size)
        self._update_fonts()
        self.update_status(f"Font size: {new_size}")
    
    def _update_fonts(self):
        """Update font sizes for all tabs"""
        font_size = self.app.settings.get('font_size', 12)
        if self.tab_manager:
            self.tab_manager.update_font_size(font_size)
        
        if hasattr(self, 'preview_area') and self.preview_area:
            self.preview_area.config(font=('Arial', font_size))
        
        if self.syntax_highlighter:
            self.syntax_highlighter.update_font_size(font_size)
    
    def increase_transparency(self):
        """Increase transparency (make more transparent)"""
        current = self.app.settings.get('hud_transparency', 0.85)
        new_transparency = max(0.3, current - 0.05)  # Smaller increments
        self.app.settings.set('hud_transparency', new_transparency)
        self.root.attributes('-alpha', new_transparency)
        self.update_status(f"Transparency: {int(new_transparency*100)}%")
        
        # Update status bar display
        if self.status_bar:
            self.status_bar.update_transparency_display(new_transparency)

    def decrease_transparency(self):
        """Decrease transparency (make more opaque)"""
        current = self.app.settings.get('hud_transparency', 0.85)
        new_transparency = min(1.0, current + 0.05)  # Smaller increments
        self.app.settings.set('hud_transparency', new_transparency)
        self.root.attributes('-alpha', new_transparency)
        self.update_status(f"Transparency: {int(new_transparency*100)}%")
        
        # Update status bar display
        if self.status_bar:
            self.status_bar.update_transparency_display(new_transparency)
    
    def update_file_label(self):
        """Update file label display"""
        if self.hud_interface:
            position_info = self.app.window_manager.get_window_position_info()
            
            if self.tab_manager:
                active_tab = self.tab_manager.get_active_tab()
                if active_tab:
                    if active_tab.file_path:
                        filename = os.path.basename(active_tab.file_path)
                        self.hud_interface.update_file_label(f"{filename} [{position_info}]")
                    else:
                        self.hud_interface.update_file_label(f"{active_tab.title} [{position_info}]")
                else:
                    self.hud_interface.update_file_label(f"No tabs open [{position_info}]")
            else:
                self.hud_interface.update_file_label(f"Loading... [{position_info}]")

    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_bar:
            self.status_bar.update_status(message)
    
    def auto_save(self):
        """Auto-save the current tab"""
        if self.tab_manager:
            active_tab = self.tab_manager.get_active_tab()
            if active_tab and active_tab.file_path and active_tab.text_widget:
                # Update tab content from text widget
                active_tab.content = active_tab.text_widget.get(1.0, tk.END)
                # Save the tab
                if self.tab_manager._save_tab(active_tab):
                    self.update_status("Auto-saved")
    
    def _on_text_change(self, event=None):
        """Handle text changes"""
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        
        # The tab manager handles auto-saving individual tabs
        if self.tab_manager:
            active_tab = self.tab_manager.get_active_tab()
            if active_tab and active_tab.file_path:
                self._save_timer = self.root.after(2000, self.auto_save)

    
    def _on_text_change_with_highlighting(self, event=None):
        """Handle text changes with syntax highlighting"""
        self._on_text_change(event)
        
        if self.syntax_highlighter:
            if hasattr(self, '_highlight_timer'):
                self.root.after_cancel(self._highlight_timer)
            
            # Update syntax highlighter to use active tab
            active_text = self.tab_manager.get_active_text_widget()
            if active_text:
                self.syntax_highlighter.set_text_widget(active_text)
                self._highlight_timer = self.root.after(300, 
                                                    self.syntax_highlighter.apply_highlighting)
        
        # Update preview if visible
        if hasattr(self, 'preview_frame') and self.preview_frame and self.preview_frame.winfo_viewable():
            self._update_preview()

    
    def _on_focus_in(self, event):
        """Handle focus in"""
        transparency = self.app.settings.get('hud_transparency', 0.85)
        self.root.attributes('-alpha', min(1.0, transparency + 0.1))
    
    def _on_focus_out(self, event):
        """Handle focus out"""
        transparency = self.app.settings.get('hud_transparency', 0.85)
        self.root.attributes('-alpha', transparency)
    
    def _apply_theme_changes(self):
        """Apply comprehensive theme changes after settings update"""
        # Apply theme to main window
        self.theme_manager.apply_theme_to_window(self.root, "main")
        
        # Apply theme to all tabs
        if self.tab_manager:
            self.tab_manager.apply_theme(self.theme_manager)
        
        # Update preview area if it exists
        if hasattr(self, 'preview_area') and self.preview_area:
            current_theme = self.theme_manager.get_current_theme()
            if current_theme:
                self.preview_area.configure(
                    bg=current_theme.get_color('bg_color'),
                    fg='#cccccc'
                )
        
        # Update other components
        if self.hud_interface:
            self.hud_interface.apply_theme(self.theme_manager)
        
        if self.status_bar:
            self.status_bar.apply_theme(self.theme_manager)
        
        # Update syntax highlighter with new theme colors
        if self.syntax_highlighter:
            self.syntax_highlighter.update_theme(self.theme_manager)
            active_text = self.tab_manager.get_active_text_widget()
            if active_text:
                self.syntax_highlighter.set_text_widget(active_text)
                self.syntax_highlighter.apply_highlighting()
        
        # Update screen border colors
        if self.screen_border:
            self.screen_border.update_theme(self.theme_manager)

    
    def run(self):
        """Start the overlay main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.app.shutdown()
    
    def cleanup(self):
        """Clean up resources"""
        if self.screen_border:
            self.screen_border.cleanup()
        
        if self.tab_manager:
            self.tab_manager.cleanup()
        
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass