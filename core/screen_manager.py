"""
Screen management - Centralized screen name generation and management
"""
from typing import Optional, List
from pathlib import Path
from core.program_manager import Program
from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenManager:
    """Manages screen-related operations and naming"""
    
    @staticmethod
    def get_screen_name_from_program(program: Program) -> str:
        """
        Get screen name from program, using stored value or filename-based fallback.
        
        Args:
            program: Program to get screen name for
            
        Returns:
            Screen name string
        """
        screen_props = program.properties.get("screen", {})
        screen_name = screen_props.get("screen_name")
        
        if not screen_name:
            working_file = screen_props.get("working_file_path", "")
            if working_file:
                try:
                    file_path = Path(working_file)
                    screen_name = file_path.stem
                except Exception:
                    screen_name = ScreenManager._generate_default_screen_name(program)
        else:
            # Validate and store screen name
            screen_props["screen_name"] = screen_name
            
        if not screen_name:
            screen_name = ScreenManager._generate_default_screen_name(program)
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            program.properties["screen"]["screen_name"] = screen_name
            
        return screen_name
    
    @staticmethod
    def _generate_default_screen_name(program: Program) -> str:
        """Generate default screen name based on program ID"""
        return "Screen4" if hash(program.id) % 2 == 0 else "Screen5"
    
    @staticmethod
    def determine_screen_name(program: Program) -> str:
        """
        Determine screen name for a program, creating it if needed.
        
        Args:
            program: Program to determine screen name for
            
        Returns:
            Screen name string
        """
        if "screen" not in program.properties:
            program.properties["screen"] = {}
        
        screen_name = program.properties["screen"].get("screen_name")
        if not screen_name:
            screen_name = ScreenManager._generate_default_screen_name(program)
            program.properties["screen"]["screen_name"] = screen_name
            
        return screen_name
    
    @staticmethod
    def generate_unique_program_name(programs: List[Program], screen_name: str) -> str:
        """
        Generate a unique program name for a given screen (Program1, Program2, etc.).
        
        Args:
            programs: List of all programs
            screen_name: Screen name to generate program name for
            
        Returns:
            Unique program name like "Program1", "Program2", etc.
        """
        existing_numbers = set()
        for program in programs:
            program_screen_name = ScreenManager.get_screen_name_from_program(program)
            if program_screen_name == screen_name:
                program_name = program.name
                if program_name.startswith("Program"):
                    try:
                        num_str = program_name[7:]
                        if num_str.isdigit():
                            existing_numbers.add(int(num_str))
                    except Exception:
                        pass
        
        counter = 1
        while counter in existing_numbers:
            counter += 1
        
        return f"Program{counter}"
    
    @staticmethod
    def sanitize_screen_name(screen_name: str) -> str:
        """
        Sanitize screen name for use in filenames.
        
        Args:
            screen_name: Original screen name
            
        Returns:
            Sanitized screen name safe for filenames
        """
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = screen_name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")
        return sanitized
    
    @staticmethod
    def get_programs_for_screen(programs: List[Program], screen_name: str) -> List[Program]:
        """
        Get all programs belonging to a specific screen.
        
        Args:
            programs: List of all programs
            screen_name: Screen name to filter by
            
        Returns:
            List of programs for the screen
        """
        screen_programs = []
        for program in programs:
            program_screen_name = ScreenManager.get_screen_name_from_program(program)
            if program_screen_name == screen_name:
                screen_programs.append(program)
        return screen_programs
    
    @staticmethod
    def get_all_screen_names(programs: List[Program]) -> set:
        """
        Get all unique screen names from programs.
        
        Args:
            programs: List of all programs
            
        Returns:
            Set of unique screen names
        """
        screen_names = set()
        for program in programs:
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if screen_name:
                screen_names.add(screen_name)
        return screen_names

