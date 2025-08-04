"""
File operations for HUD Notes
"""

import os
from typing import Optional


class FileManager:
    """Handles file I/O operations"""
    
    def __init__(self, notes_dir: str, settings):
        self.notes_dir = notes_dir
        self.settings = settings
        
        # Ensure notes directory exists
        os.makedirs(notes_dir, exist_ok=True)
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
    
    def get_file_list(self, extension: str = None) -> list:
        """Get list of files in notes directory"""
        try:
            files = []
            for file in os.listdir(self.notes_dir):
                if extension:
                    if file.endswith(extension):
                        files.append(os.path.join(self.notes_dir, file))
                else:
                    files.append(os.path.join(self.notes_dir, file))
            return sorted(files)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_safe_filename(self, title: str) -> str:
        """Generate safe filename from title"""
        safe_chars = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        return safe_chars.strip()
    
    def auto_save_file(self, file_path: str, content: str) -> bool:
        """Auto-save file with backup"""
        try:
            # Create backup first
            backup_path = file_path + '.backup'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Write new content
            return self.write_file(file_path, content)
            
        except Exception as e:
            print(f"Error auto-saving file {file_path}: {e}")
            return False