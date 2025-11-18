"""
Screen parameters utility - provides centralized access to screen dimensions
"""
from typing import Optional, Tuple
from core.program_manager import Program


class ScreenParams:
    """Utility class for accessing screen parameters"""
    
    @staticmethod
    def get_screen_dimensions(program: Optional[Program]) -> Tuple[Optional[int], Optional[int]]:
        """
        Get screen width and height from program's screen properties.
        
        Args:
            program: The Program object to get screen dimensions from
            
        Returns:
            Tuple of (width, height) or (None, None) if not available
            
        Note:
            Screen dimensions come from screen/controller settings, NOT from
            program canvas dimensions (program.width/height).
        """
        if not program:
            return None, None
        
        screen_props = program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        
        # Only return if both are set and valid
        if width and height and width > 0 and height > 0:
            return int(width), int(height)
        
        return None, None
    
    @staticmethod
    def get_screen_rotation(program: Optional[Program]) -> int:
        """
        Get screen rotation angle from program's screen properties.
        
        Args:
            program: The Program object to get screen rotation from
            
        Returns:
            Rotation angle in degrees (default: 0)
        """
        if not program:
            return 0
        
        screen_props = program.properties.get("screen", {})
        return screen_props.get("rotate", 0)
    
    @staticmethod
    def has_screen_properties(program: Optional[Program]) -> bool:
        """
        Check if program has valid screen properties.
        
        Args:
            program: The Program object to check
            
        Returns:
            True if screen properties exist with valid width/height
        """
        if not program:
            return False
        
        screen_props = program.properties.get("screen", {})
        width = screen_props.get("width")
        height = screen_props.get("height")
        
        return bool(width and height and width > 0 and height > 0)
    
    @staticmethod
    def set_screen_dimensions(program: Optional[Program], width: int, height: int, 
                             rotate: int = 0) -> bool:
        """
        Set screen dimensions in program's screen properties.
        
        Args:
            program: The Program object to set screen dimensions for
            width: Screen width in pixels
            height: Screen height in pixels
            rotate: Screen rotation angle in degrees (default: 0)
            
        Returns:
            True if successful, False if program is None
        """
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
        """
        Get all screen properties from program.
        
        Args:
            program: The Program object to get screen properties from
            
        Returns:
            Dictionary of screen properties (empty dict if not available)
        """
        if not program:
            return {}
        
        return program.properties.get("screen", {}).copy()

