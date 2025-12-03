from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from typing import Optional, Dict
from core.program_manager import Program


class BasePropertiesComponent(QWidget):
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict] = None
        self.main_window = parent
    
    def set_program(self, program: Optional[Program]):
        self.current_program = program
    
    def set_element(self, element: Optional[Dict], program: Optional[Program]):
        self.current_element = element
        self.current_program = program
    
    def _get_screen_bounds(self):
        from core.screen_params import ScreenParams
        return ScreenParams.get_screen_dimensions(self.current_program)
    
    def _constrain_to_screen(self, x, y, width, height):
        screen_width, screen_height = self._get_screen_bounds()
        if not screen_width or not screen_height:
            return x, y, width, height
        
        width = min(width, screen_width)
        height = min(height, screen_height)
        
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        return x, y, width, height
    
    def _trigger_autosave(self):
        if self.main_window and self.current_program:
            if hasattr(self.main_window, '_save_and_refresh'):
                self.main_window._save_and_refresh(self.current_program)
            elif hasattr(self.main_window, 'auto_save_manager'):
                self.main_window.auto_save_manager.save_current_program()
    
    def update_properties(self):
        pass
    
    @staticmethod
    def get_available_borders():
        # Border images removed - Reference folder no longer used
        return []

