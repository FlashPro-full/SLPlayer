from typing import Optional, Tuple
from core.program_manager import Program


class ScreenParams:
    
    @staticmethod
    def get_screen_dimensions(program: Optional[Program]) -> Tuple[Optional[int], Optional[int]]:
        if not program:
            return None, None
        
        screen_props = program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        
        if width and height and width > 0 and height > 0:
            return int(width), int(height)
        
        return None, None
    
    @staticmethod
    def get_screen_rotation(program: Optional[Program]) -> int:
        if not program:
            return 0
        
        screen_props = program.properties.get("screen", {})
        return screen_props.get("rotate", 0)
    
    @staticmethod
    def has_screen_properties(program: Optional[Program]) -> bool:
        if not program:
            return False
        
        screen_props = program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        
        return bool(width and height and width > 0 and height > 0)
    
    @staticmethod
    def set_screen_dimensions(program: Optional[Program], width: int, height: int, 
                             rotate: int = 0) -> bool:
        if not program:
            return False
        
        if "screen" not in program.properties:
            program.properties["screen"] = {}
        
        program.properties["screen"]["width"] = width
        program.properties["screen"]["height"] = height
        program.properties["screen"]["rotate"] = rotate
        
        return True
    
    @staticmethod
    def get_screen_properties(program: Optional[Program]) -> dict:
        if not program:
            return {}
        
        return program.properties.get("screen", {}).copy()

