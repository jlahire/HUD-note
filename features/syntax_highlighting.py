"""
Syntax highlighting system for HUD Notes
"""

import re
import tkinter as tk


class SyntaxHighlighter:
    """Handles syntax highlighting for the text editor"""
    
    def __init__(self, text_widget=None, settings=None, theme_manager=None):
        self.text_widget = text_widget
        self.settings = settings
        self.theme_manager = theme_manager
        
        # Only setup tags if we have a text widget
        if self.text_widget:
            self.setup_tags()
    
    def set_text_widget(self, text_widget):
        """Set or change the text widget for highlighting"""
        self.text_widget = text_widget
        if self.text_widget:
            self.setup_tags()
    
    def setup_tags(self):
        """Setup syntax highlighting tags"""
        if not self.text_widget:
            return
            
        font_size = self.settings.get('font_size', 12) if self.settings else 12
        
        # Code blocks
        self.text_widget.tag_configure("code_block", 
                                      background="#2a2a2a", 
                                      foreground="#e6e6e6", 
                                      font=('Consolas', font_size, 'normal'))
        
        # Keywords and programming elements
        self.text_widget.tag_configure("keyword", 
                                      foreground="#ff6b6b", 
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("builtin", 
                                      foreground="#4ecdc4", 
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("string", 
                                      foreground="#95e1d3", 
                                      font=('Consolas', font_size, 'normal'))
        self.text_widget.tag_configure("comment", 
                                      foreground="#888888", 
                                      font=('Consolas', font_size, 'italic'))
        self.text_widget.tag_configure("number", 
                                      foreground="#ffd93d", 
                                      font=('Consolas', font_size, 'bold'))
        
        # File paths
        self.text_widget.tag_configure("filepath", 
                                      foreground="#ff9f43", 
                                      background="#3a2a1a", 
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("directory", 
                                      foreground="#3742fa", 
                                      background="#1a1a3a",
                                      font=('Consolas', font_size, 'bold'))
        
        # URLs
        self.text_widget.tag_configure("url", 
                                      foreground="#70a1ff", 
                                      underline=True,
                                      font=('Consolas', font_size, 'normal'))
        
        # Markdown elements
        self.text_widget.tag_configure("heading", 
                                      foreground="#ff6348", 
                                      font=('Consolas', font_size + 2, 'bold'))
        self.text_widget.tag_configure("bold", 
                                      foreground="#ffffff", 
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("italic", 
                                      foreground="#cccccc", 
                                      font=('Consolas', font_size, 'italic'))
        self.text_widget.tag_configure("list_item", 
                                      foreground="#52c41a",
                                      font=('Consolas', font_size, 'normal'))
        
        # Special keywords
        self.text_widget.tag_configure("important", 
                                      foreground="#ff4757", 
                                      background="#3a1a1a",
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("todo", 
                                      foreground="#ffa502", 
                                      background="#3a2a1a",
                                      font=('Consolas', font_size, 'bold'))
        self.text_widget.tag_configure("done", 
                                      foreground="#2ed573", 
                                      background="#1a3a1a",
                                      font=('Consolas', font_size, 'bold'))
    
    def apply_highlighting(self):
        """Apply syntax highlighting to the entire text"""
        if not self.text_widget:
            return
            
        content = self.text_widget.get(1.0, tk.END)
        
        # Clear existing tags
        for tag in self.text_widget.tag_names():
            if tag not in ['sel', 'insert']:
                self.text_widget.tag_remove(tag, "1.0", tk.END)

        # Re-setup tags (ensures they exist after removal)
        self.setup_tags()

        # Reapply highlighting
        self._highlight_markdown(content)
        self._highlight_code_blocks(content)
        self._highlight_file_paths(content)
        self._highlight_urls(content)
        self._highlight_special_keywords(content)
    
    def _highlight_markdown(self, content):
        """Highlight markdown elements"""
        if not self.text_widget:
            return
            
        # Headers
        header_pattern = r'^#+\s.*'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("heading", start_pos, end_pos)
        
        # Bold text
        bold_pattern = r'\*\*[^*]+\*\*'
        for match in re.finditer(bold_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("bold", start_pos, end_pos)
        
        # Italic text
        italic_pattern = r'\*[^*]+\*'
        for match in re.finditer(italic_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("italic", start_pos, end_pos)
        
        # List items
        list_pattern = r'^[\s]*[-*+]\s.*'
        for match in re.finditer(list_pattern, content, re.MULTILINE):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("list_item", start_pos, end_pos)
    
    def _highlight_code_blocks(self, content):
        """Highlight code blocks"""
        if not self.text_widget:
            return
            
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("code_block", start_pos, end_pos)
    
    def _highlight_file_paths(self, content):
        """Highlight file paths and directories"""
        if not self.text_widget:
            return
            
        # File patterns
        file_patterns = [
            r'[A-Za-z]:\\(?:[^\\/:*?"<>|\n]+\\)*[^\\/:*?"<>|\n]*\.[A-Za-z0-9]+',
            r'/(?:[^/\n]+/)*[^/\n]*\.[A-Za-z0-9]+',
            r'\.\/[^\s\n]+',
            r'~\/[^\s\n]+',
        ]
        
        for pattern in file_patterns:
            for match in re.finditer(pattern, content):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_widget.tag_add("filepath", start_pos, end_pos)
    
    def _highlight_urls(self, content):
        """Highlight URLs"""
        if not self.text_widget:
            return
            
        url_pattern = r'https?://[^\s\n]+'
        for match in re.finditer(url_pattern, content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_widget.tag_add("url", start_pos, end_pos)
    
    def _highlight_special_keywords(self, content):
        """Highlight special keywords"""
        if not self.text_widget:
            return
            
        special_patterns = {
            'todo': r'\b(?:TODO|FIXME|HACK|BUG)\b[^\n]*',
            'important': r'\b(?:IMPORTANT|CRITICAL|WARNING|ERROR)\b[^\n]*',
            'done': r'\b(?:DONE|COMPLETED|FIXED|RESOLVED)\b[^\n]*'
        }
        
        for tag, pattern in special_patterns.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start_pos = f"1.0+{match.start()}c"
                end_pos = f"1.0+{match.end()}c"
                self.text_widget.tag_add(tag, start_pos, end_pos)
    
    def update_font_size(self, font_size):
        """Update font size for all tags"""
        if self.settings:
            self.settings.set('font_size', font_size)
        self.setup_tags()
        self.apply_highlighting()
    
    def update_theme(self, theme_manager):
        """Update theme manager and reapply highlighting"""
        self.theme_manager = theme_manager
        self.setup_tags()
        self.apply_highlighting()