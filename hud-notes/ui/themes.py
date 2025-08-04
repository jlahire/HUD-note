"""
Theme and styling system for HUD Notes
"""

from typing import Dict, List, Optional
import tkinter as tk


class Theme:
    """Individual theme configuration"""
    
    def __init__(self, name: str, colors: Dict[str, str], description: str = ""):
        self.name = name
        self.colors = colors
        self.description = description
    
    def get_color(self, key: str, default: str = "#000000") -> str:
        """Get color value by key"""
        return self.colors.get(key, default)
    
    def apply_to_widget(self, widget, widget_type: str = "default"):
        """Apply theme colors to a widget"""
        try:
            if widget_type == 'frame':
                widget.config(bg=self.colors.get('bg_color', '#0a0a0a'))
            elif widget_type == 'text':
                widget.config(
                    bg=self.colors.get('bg_color', '#0a0a0a'),
                    fg=self.colors.get('fg_color', '#00ff41'),
                    insertbackground=self.colors.get('fg_color', '#00ff41'),
                    selectbackground=self.colors.get('select_bg', '#1a3d1a')
                )
            elif widget_type == 'button':
                widget.config(
                    bg=self.colors.get('button_bg', '#1a1a1a'),
                    fg=self.colors.get('button_fg', '#00ff41')
                )
            else:
                # Default case - no more KeyError!
                widget.config(
                    bg=self.colors.get('bg_color', '#0a0a0a'),
                    fg=self.colors.get('fg_color', '#00ff41')
                )
        except Exception as e:
            print(f"Warning: Could not apply theme to widget: {e}")
            pass


class ThemeManager:
    """Manages themes and styling for HUD Notes"""
    
    def __init__(self, settings):
        self.settings = settings
        self.themes = {}
        self.current_theme = None
        self._initialize_built_in_themes()
        self._load_current_theme()
    
    def _initialize_built_in_themes(self):
        """Initialize built-in themes"""
        
        # Matrix Green - Default HUD theme
        self.themes['Matrix Green'] = Theme(
            name='Matrix Green',
            colors={
                'bg_color': '#0a0a0a',
                'fg_color': '#00ff41',
                'accent_color': '#ff6600',
                'select_bg': '#1a3d1a',
                'button_bg': '#1a1a1a',
                'button_fg': '#00ff41',
                'button_active': '#2a4a2a',
                'title_bg': '#333333',
                'status_bg': '#1a1a1a',
                'border_color': '#00ff41',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Classic Matrix-style green on black theme'
        )
        
        # Cyber Blue - Futuristic blue theme
        self.themes['Cyber Blue'] = Theme(
            name='Cyber Blue',
            colors={
                'bg_color': '#0a0a1a',
                'fg_color': '#00ccff',
                'accent_color': '#ff6600',
                'select_bg': '#1a1a3d',
                'button_bg': '#1a1a2a',
                'button_fg': '#00ccff',
                'button_active': '#2a2a4a',
                'title_bg': '#333344',
                'status_bg': '#1a1a2a',
                'border_color': '#00ccff',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ffaa'
            },
            description='Cyberpunk blue theme with electric accents'
        )
        
        # Neon Purple - Vibrant purple theme
        self.themes['Neon Purple'] = Theme(
            name='Neon Purple',
            colors={
                'bg_color': '#1a0a1a',
                'fg_color': '#cc00ff',
                'accent_color': '#ffff00',
                'select_bg': '#3d1a3d',
                'button_bg': '#2a1a2a',
                'button_fg': '#cc00ff',
                'button_active': '#4a2a4a',
                'title_bg': '#443344',
                'status_bg': '#2a1a2a',
                'border_color': '#cc00ff',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Neon purple theme with electric yellow accents'
        )
        
        # Hacker Orange - Orange and green hacker theme
        self.themes['Hacker Orange'] = Theme(
            name='Hacker Orange',
            colors={
                'bg_color': '#1a1a0a',
                'fg_color': '#ff9900',
                'accent_color': '#00ff00',
                'select_bg': '#3d3d1a',
                'button_bg': '#2a2a1a',
                'button_fg': '#ff9900',
                'button_active': '#4a4a2a',
                'title_bg': '#444433',
                'status_bg': '#2a2a1a',
                'border_color': '#ff9900',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#00ff00'
            },
            description='Hacker-style orange and green theme'
        )
        
        # Terminal White - High contrast white theme
        self.themes['Terminal White'] = Theme(
            name='Terminal White',
            colors={
                'bg_color': '#000000',
                'fg_color': '#ffffff',
                'accent_color': '#ffff00',
                'select_bg': '#333333',
                'button_bg': '#222222',
                'button_fg': '#ffffff',
                'button_active': '#444444',
                'title_bg': '#333333',
                'status_bg': '#222222',
                'border_color': '#ffffff',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Classic terminal white on black theme'
        )
        
        # Blood Red - Dark red theme
        self.themes['Blood Red'] = Theme(
            name='Blood Red',
            colors={
                'bg_color': '#1a0000',
                'fg_color': '#ff3333',
                'accent_color': '#ffff00',
                'select_bg': '#3d1a1a',
                'button_bg': '#2a1a1a',
                'button_fg': '#ff3333',
                'button_active': '#4a2a2a',
                'title_bg': '#441133',
                'status_bg': '#2a1a1a',
                'border_color': '#ff3333',
                'warning_color': '#ffaa00',
                'error_color': '#ff6666',
                'success_color': '#44ff44'
            },
            description='Dark red theme with blood-like accents'
        )
        
        # Stealth Gray - Professional gray theme
        self.themes['Stealth Gray'] = Theme(
            name='Stealth Gray',
            colors={
                'bg_color': '#1a1a1a',
                'fg_color': '#cccccc',
                'accent_color': '#00aaff',
                'select_bg': '#333333',
                'button_bg': '#2a2a2a',
                'button_fg': '#cccccc',
                'button_active': '#444444',
                'title_bg': '#333333',
                'status_bg': '#2a2a2a',
                'border_color': '#cccccc',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Professional stealth gray theme'
        )
        
        # Retro Amber - Classic amber terminal theme
        self.themes['Retro Amber'] = Theme(
            name='Retro Amber',
            colors={
                'bg_color': '#0a0a00',
                'fg_color': '#ffbb00',
                'accent_color': '#00ff00',
                'select_bg': '#3d3d1a',
                'button_bg': '#2a2a1a',
                'button_fg': '#ffbb00',
                'button_active': '#4a4a2a',
                'title_bg': '#444422',
                'status_bg': '#2a2a1a',
                'border_color': '#ffbb00',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Retro amber terminal theme'
        )
        
        # Electric Pink - Vibrant pink theme
        self.themes['Electric Pink'] = Theme(
            name='Electric Pink',
            colors={
                'bg_color': '#1a0a1a',
                'fg_color': '#ff00aa',
                'accent_color': '#00ffff',
                'select_bg': '#3d1a3d',
                'button_bg': '#2a1a2a',
                'button_fg': '#ff00aa',
                'button_active': '#4a2a4a',
                'title_bg': '#442244',
                'status_bg': '#2a1a2a',
                'border_color': '#ff00aa',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ff44'
            },
            description='Electric pink theme with cyan accents'
        )
        
        # Deep Ocean - Blue ocean depths theme
        self.themes['Deep Ocean'] = Theme(
            name='Deep Ocean',
            colors={
                'bg_color': '#001122',
                'fg_color': '#4499ff',
                'accent_color': '#00ffaa',
                'select_bg': '#1a2244',
                'button_bg': '#1a2233',
                'button_fg': '#4499ff',
                'button_active': '#2a3344',
                'title_bg': '#223344',
                'status_bg': '#1a2233',
                'border_color': '#4499ff',
                'warning_color': '#ffaa00',
                'error_color': '#ff4444',
                'success_color': '#44ffaa'
            },
            description='Deep ocean blue theme with aqua accents'
        )
    
    def _load_current_theme(self):
        """Load current theme from settings"""
        theme_name = self.settings.get('color_scheme', 'Matrix Green')
        if theme_name == 'Custom':
            self._create_custom_theme()
        else:
            self.current_theme = self.themes.get(theme_name, self.themes['Matrix Green'])
    
    def _create_custom_theme(self):
        """Create custom theme from settings"""
        custom_colors = {
            'bg_color': self.settings.get('bg_color', '#0a0a0a'),
            'fg_color': self.settings.get('fg_color', '#00ff41'),
            'accent_color': self.settings.get('accent_color', '#ff6600'),
            'select_bg': self.settings.get('select_bg', '#1a3d1a'),
            'button_bg': self.settings.get('button_bg', '#1a1a1a'),
            'button_fg': self.settings.get('button_fg', '#00ff41'),
            'button_active': self.settings.get('button_active', '#333333'),
            'title_bg': self.settings.get('title_bg', '#333333'),
            'status_bg': self.settings.get('status_bg', '#1a1a1a'),
            'border_color': self.settings.get('border_color', '#00ff41'),
            'warning_color': '#ffaa00',
            'error_color': '#ff4444',
            'success_color': '#44ff44'
        }
        
        self.current_theme = Theme(
            name='Custom',
            colors=custom_colors,
            description='User-defined custom theme'
        )
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name)
    
    def get_current_theme(self) -> Theme:
        """Get current active theme"""
        return self.current_theme
    
    def set_theme(self, theme_name: str):
        """Set active theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self._update_settings_from_theme()
        elif theme_name == 'Custom':
            self._create_custom_theme()
    
    def _update_settings_from_theme(self):
        """Update settings with current theme colors"""
        if self.current_theme:
            self.settings.update({
                'color_scheme': self.current_theme.name,
                'bg_color': self.current_theme.get_color('bg_color'),
                'fg_color': self.current_theme.get_color('fg_color'),
                'accent_color': self.current_theme.get_color('accent_color'),
                'select_bg': self.current_theme.get_color('select_bg'),
                'button_bg': self.current_theme.get_color('button_bg'),
                'button_fg': self.current_theme.get_color('button_fg'),
                'title_bg': self.current_theme.get_color('title_bg'),
                'status_bg': self.current_theme.get_color('status_bg'),
                'border_color': self.current_theme.get_color('border_color')
            })
    
    def apply_theme_to_window(self, window, window_type: str = "main"):
        """Apply current theme to a window"""
        if not self.current_theme:
            return
        
        try:
            if window_type == "main":
                window.configure(bg=self.current_theme.get_color('bg_color'))
            elif window_type == "dialog":
                window.configure(bg=self.current_theme.get_color('bg_color'))
            elif window_type == "title":
                window.configure(bg=self.current_theme.get_color('title_bg'))
        except Exception as e:
            print(f"Warning: Could not apply theme to window: {e}")
    
    def apply_theme_to_text_widget(self, text_widget):
        """Apply current theme to a text widget"""
        if self.current_theme:
            self.current_theme.apply_to_widget(text_widget, 'text')
    
    def apply_theme_to_button(self, button, button_type: str = "default"):
        """Apply current theme to a button"""
        if self.current_theme:
            colors = {
                'bg': self.current_theme.get_color('button_bg'),
                'fg': self.current_theme.get_color('button_fg'),
                'activebackground': self.current_theme.get_color('button_active'),
                'activeforeground': self.current_theme.get_color('fg_color')
            }
            
            # Special button types
            if button_type == "accent":
                colors['fg'] = self.current_theme.get_color('accent_color')
            elif button_type == "warning":
                colors['fg'] = self.current_theme.get_color('warning_color')
            elif button_type == "error":
                colors['fg'] = self.current_theme.get_color('error_color')
            elif button_type == "success":
                colors['fg'] = self.current_theme.get_color('success_color')
            
            try:
                button.configure(**colors)
            except Exception as e:
                print(f"Warning: Could not apply theme to button: {e}")
    
    def get_syntax_highlighting_colors(self) -> Dict[str, Dict[str, str]]:
        """Get syntax highlighting colors for current theme"""
        if not self.current_theme:
            return {}
        
        # Generate syntax highlighting colors based on theme
        base_fg = self.current_theme.get_color('fg_color')
        bg_color = self.current_theme.get_color('bg_color')
        
        return {
            'code_block': {
                'background': self._adjust_brightness(bg_color, 0.2),
                'foreground': '#e6e6e6'
            },
            'keyword': {
                'foreground': '#ff6b6b'
            },
            'builtin': {
                'foreground': '#4ecdc4'
            },
            'string': {
                'foreground': '#95e1d3'
            },
            'comment': {
                'foreground': '#888888'
            },
            'number': {
                'foreground': '#ffd93d'
            },
            'heading': {
                'foreground': self.current_theme.get_color('accent_color')
            },
            'bold': {
                'foreground': base_fg
            },
            'italic': {
                'foreground': self._adjust_brightness(base_fg, -0.2)
            },
            'list_item': {
                'foreground': self.current_theme.get_color('success_color')
            },
            'important': {
                'foreground': self.current_theme.get_color('error_color'),
                'background': self._adjust_brightness(bg_color, 0.1)
            },
            'todo': {
                'foreground': self.current_theme.get_color('warning_color'),
                'background': self._adjust_brightness(bg_color, 0.1)
            },
            'done': {
                'foreground': self.current_theme.get_color('success_color'),
                'background': self._adjust_brightness(bg_color, 0.1)
            }
        }
    
    def _adjust_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust brightness of a hex color"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = max(0, min(255, int(r * (1 + factor))))
            g = max(0, min(255, int(g * (1 + factor))))
            b = max(0, min(255, int(b * (1 + factor))))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def create_theme_preview(self, theme_name: str) -> Dict[str, str]:
        """Create preview colors for theme selection"""
        theme = self.themes.get(theme_name)
        if not theme:
            return {}
        
        return {
            'bg': theme.get_color('bg_color'),
            'fg': theme.get_color('fg_color'),
            'accent': theme.get_color('accent_color'),
            'select': theme.get_color('select_bg')
        }
    
    def export_theme(self, theme_name: str) -> Optional[Dict]:
        """Export theme configuration"""
        theme = self.themes.get(theme_name)
        if not theme:
            return None
        
        return {
            'name': theme.name,
            'description': theme.description,
            'colors': theme.colors.copy()
        }
    
    def import_theme(self, theme_data: Dict) -> bool:
        """Import theme from configuration"""
        try:
            name = theme_data.get('name', 'Imported Theme')
            description = theme_data.get('description', 'Imported theme')
            colors = theme_data.get('colors', {})
            
            if not colors:
                return False
            
            self.themes[name] = Theme(name, colors, description)
            return True
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False
    
    def reload_theme(self):
        """Reload current theme (useful after settings changes)"""
        self._load_current_theme()