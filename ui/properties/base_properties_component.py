from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from typing import Optional, Dict, Any
from core.program_manager import Program

class BasePropertiesComponent(QWidget):
    
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_program: Optional[Program] = None
        self.current_element: Optional[Dict[str, Any]] = None
        self.main_window: Optional[QWidget] = parent
    
    def set_program(self, program: Optional[Program]) -> None:
        self.current_program = program
    
    def set_element(self, element: Optional[Dict[str, Any]], program: Optional[Program]) -> None:
        self.current_element = element
        self.current_program = program
    
    def _get_screen_bounds(self) -> tuple:
        """Get screen dimensions from program or screen config"""
        # First try to get dimensions from the program
        if self.current_program:
            if hasattr(self.current_program, 'width') and hasattr(self.current_program, 'height'):
                width = self.current_program.width
                height = self.current_program.height
                if width and height and width > 0 and height > 0:
                    return (width, height)
        
        # Fall back to screen config
        from core.screen_config import get_screen_config
        screen_config = get_screen_config()
        if screen_config:
            width = screen_config.get("width")
            height = screen_config.get("height")
            if width and height and width > 0 and height > 0:
                return (width, height)
        
        # Default fallback
        from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
        return (DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT)
    
    def _constrain_to_screen(self, x: int, y: int, width: int, height: int) -> tuple:
        screen_width, screen_height = self._get_screen_bounds()
        if not screen_width or not screen_height:
            return x, y, width, height
        
        width = min(width, screen_width)
        height = min(height, screen_height)
        
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        return x, y, width, height
    
    def _trigger_autosave(self) -> None:
        if self.main_window and self.current_program:
            if hasattr(self.main_window, '_save_and_refresh'):
                self.main_window._save_and_refresh(self.current_program)
            elif hasattr(self.main_window, 'auto_save_manager'):
                self.main_window.auto_save_manager.save_current_program()
    
    def update_properties(self) -> None:
        pass
    
    @staticmethod
    def get_available_borders() -> list:
        return []

