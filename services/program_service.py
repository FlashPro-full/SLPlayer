"""
Program Service - Business logic for program management
"""
from typing import Optional, List, Dict
from datetime import datetime
import uuid

from core.program_manager import ProgramManager, Program
from core.screen_manager import ScreenManager
from core.event_bus import event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class ProgramService:
    """
    Service layer for program management operations.
    Separates business logic from UI components.
    """
    
    def __init__(self, program_manager: ProgramManager):
        self.program_manager = program_manager
    
    def create_program(self, name: str = None, width: int = 1920, 
                      height: int = 1080, screen_name: str = None) -> Optional[Program]:
        """
        Create a new program.
        
        Args:
            name: Program name (auto-generated if None)
            width: Canvas width
            height: Canvas height
            screen_name: Screen name (auto-generated if None)
            
        Returns:
            Created Program or None on error
        """
        try:
            if not name:
                # Auto-generate name
                existing_names = [p.name for p in self.program_manager.programs]
                n = 1
                while True:
                    candidate = f"Program {n}"
                    if candidate not in existing_names:
                        name = candidate
                        break
                    n += 1
            
            program = Program(name, width, height)
            
            # Set up screen properties
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            
            if screen_name:
                program.properties["screen"]["screen_name"] = screen_name
            else:
                # Use ScreenManager to determine screen name
                screen_name = ScreenManager.determine_screen_name(program)
            
            self.program_manager.programs.append(program)
            self.program_manager.current_program = program
            
            # Emit event
            event_bus.program_created.emit(program)
            event_bus.screen_created.emit(screen_name)
            
            logger.info(f"Created program: {name} on screen: {screen_name}")
            return program
            
        except Exception as e:
            logger.error(f"Error creating program: {e}", exc_info=True)
            return None
    
    def get_program(self, program_id: str) -> Optional[Program]:
        """Get program by ID"""
        return self.program_manager.get_program_by_id(program_id)
    
    def get_current_program(self) -> Optional[Program]:
        """Get current program"""
        return self.program_manager.current_program
    
    def set_current_program(self, program_id: str) -> bool:
        """
        Set current program.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            program = self.program_manager.get_program_by_id(program_id)
            if program:
                self.program_manager.current_program = program
                event_bus.program_selected.emit(program_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting current program: {e}")
            return False
    
    def update_program(self, program_id: str, updates: Dict) -> bool:
        """
        Update program properties.
        
        Args:
            program_id: Program ID
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(program, key):
                    setattr(program, key, value)
                elif key in program.properties:
                    program.properties[key] = value
            
            program.modified = datetime.now().isoformat()
            
            # Emit event
            event_bus.program_updated.emit(program)
            
            return True
        except Exception as e:
            logger.error(f"Error updating program: {e}", exc_info=True)
            return False
    
    def rename_program(self, program_id: str, new_name: str) -> bool:
        """Rename a program"""
        return self.update_program(program_id, {"name": new_name})
    
    def delete_program(self, program_id: str) -> bool:
        """
        Delete a program.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return False
            
            # Remove from list
            if program in self.program_manager.programs:
                self.program_manager.programs.remove(program)
            
            # Clear current if it was deleted
            if self.program_manager.current_program == program:
                self.program_manager.current_program = None
                if self.program_manager.programs:
                    self.program_manager.current_program = self.program_manager.programs[0]
            
            # Emit event
            event_bus.program_deleted.emit(program_id)
            
            logger.info(f"Deleted program: {program_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting program: {e}", exc_info=True)
            return False
    
    def duplicate_program(self, program_id: str) -> Optional[Program]:
        """
        Duplicate a program.
        
        Returns:
            New Program or None on error
        """
        try:
            program = self.program_manager.get_program_by_id(program_id)
            if not program:
                return None
            
            # Create copy
            program_data = program.to_dict()
            new_program = Program()
            new_program.from_dict(program_data)
            new_program.id = f"program_{uuid.uuid4().hex[:12]}"
            new_program.name = f"{program.name} (Copy)"
            new_program.created = datetime.now().isoformat()
            new_program.modified = datetime.now().isoformat()
            
            # Copy screen properties
            if "screen" in program.properties:
                new_program.properties["screen"] = program.properties["screen"].copy()
            
            self.program_manager.programs.append(new_program)
            self.program_manager.current_program = new_program
            
            # Emit event
            event_bus.program_created.emit(new_program)
            
            logger.info(f"Duplicated program: {program_id} -> {new_program.id}")
            return new_program
            
        except Exception as e:
            logger.error(f"Error duplicating program: {e}", exc_info=True)
            return None
    
    def get_programs_for_screen(self, screen_name: str) -> List[Program]:
        """Get all programs for a screen"""
        return ScreenManager.get_programs_for_screen(
            self.program_manager.programs, screen_name
        )
    
    def get_all_programs(self) -> List[Program]:
        """Get all programs"""
        return self.program_manager.programs.copy()

