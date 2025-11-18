"""
Base class for properties components
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from typing import Optional, Dict
from core.program_manager import Program


class BasePropertiesComponent(QWidget):
    """Base class for all properties components"""
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict] = None
        self.main_window = parent
    
    def set_program(self, program: Optional[Program]):
        """Set the current program"""
        self.current_program = program
    
    def set_element(self, element: Optional[Dict], program: Optional[Program]):
        """Set the current element"""
        self.current_element = element
        self.current_program = program
    
    def _get_screen_bounds(self):
        """Get screen bounds (width, height) from current program"""
        from core.screen_params import ScreenParams
        return ScreenParams.get_screen_dimensions(self.current_program)
    
    def _constrain_to_screen(self, x, y, width, height):
        """Constrain content position and size to screen bounds"""
        screen_width, screen_height = self._get_screen_bounds()
        if not screen_width or not screen_height:
            return x, y, width, height
        
        # Constrain width and height to not exceed screen
        width = min(width, screen_width)
        height = min(height, screen_height)
        
        # Constrain position so content doesn't go outside screen
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        return x, y, width, height
    
    def _trigger_autosave(self):
        """Trigger autosave and refresh UI if main window exists"""
        if self.main_window and self.current_program:
            # Use main window's save_and_refresh to ensure UI is updated
            if hasattr(self.main_window, '_save_and_refresh'):
                self.main_window._save_and_refresh(self.current_program)
            elif hasattr(self.main_window, 'auto_save_manager'):
                self.main_window.auto_save_manager.save_current_program()
                # Trigger UI refresh
                if hasattr(self.main_window, 'program_list_panel'):
                    self.main_window.program_list_panel.refresh_programs()
    
    def update_properties(self):
        """Update properties from current element/program - override in subclasses"""
        pass
    
    @staticmethod
    def get_available_borders():
        """Get list of available border image files"""
        from pathlib import Path
        border_dir = Path(__file__).parent.parent.parent / "resources" / "Reference" / "images" / "Border"
        if border_dir.exists():
            borders = sorted([f.stem for f in border_dir.glob("*.png")])
            return borders
        return []

