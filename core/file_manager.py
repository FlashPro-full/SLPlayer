"""
File management - Handles .soo file operations
"""
import json
from pathlib import Path
from typing import Optional, List, Dict
from core.program_manager import Program, ProgramManager
from core.screen_manager import ScreenManager
from utils.app_data import get_app_data_dir
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manages .soo file operations"""
    
    def __init__(self, program_manager: ProgramManager):
        self.program_manager = program_manager
        self.work_dir = get_app_data_dir() / "work"
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False) -> bool:
        """
        Load a .soo file.
        
        Args:
            file_path: Path to .soo file
            clear_existing: Whether to clear existing programs before loading
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            soo_path = Path(file_path)
            if not soo_path.exists():
                logger.error(f".soo file not found: {file_path}")
                return False
            
            if clear_existing:
                self.program_manager.programs.clear()
                self.program_manager.current_program = None
            
            with open(soo_path, 'r', encoding='utf-8') as f:
                screen_data = json.load(f)
            
            screen_properties = screen_data.get("screen_properties", {})
            programs_data = screen_data.get("programs", [])
            
            screen_name = soo_path.stem
            logger.info(f"Loading .soo file '{soo_path.name}' as screen '{screen_name}'")
            
            # Ensure screen_properties has required fields
            screen_properties["screen_name"] = screen_name
            screen_properties["working_file_path"] = str(soo_path)
            
            # CRITICAL: Validate that width/height exist in screen_properties (controller screen dimensions)
            # If missing, log a warning - these should always be set from screen settings dialog or controller
            if "width" not in screen_properties or "height" not in screen_properties:
                logger.warning(
                    f"Screen '{screen_name}' missing width/height in screen_properties. "
                    f"Width: {screen_properties.get('width', 'MISSING')}, "
                    f"Height: {screen_properties.get('height', 'MISSING')}. "
                    f"This should be the actual controller screen resolution, not PC canvas size."
                )
            
            programs_added = 0
            for prog_data in programs_data:
                program = Program()
                program.from_dict(prog_data)
                if "screen" not in program.properties:
                    program.properties["screen"] = {}
                
                program.properties["screen"]["screen_name"] = screen_name
                program.properties["screen"].update(screen_properties)
                program.properties["working_file_path"] = str(soo_path)
                
                # Check if program already exists
                existing_program = None
                for existing in self.program_manager.programs:
                    existing_screen_name = ScreenManager.get_screen_name_from_program(existing)
                    if existing.id == program.id and existing_screen_name == screen_name:
                        existing_program = existing
                        if "screen" not in existing.properties:
                            existing.properties["screen"] = {}
                        existing.properties["screen"]["screen_name"] = screen_name
                        existing.properties["screen"].update(screen_properties)
                        existing.properties["working_file_path"] = str(soo_path)
                        break
                
                if not existing_program:
                    self.program_manager.programs.append(program)
                    programs_added += 1
            
            if programs_added > 0:
                logger.info(f"Added {programs_added} program(s) from {soo_path.name}")
            elif len(programs_data) > 0:
                logger.info(f"File {soo_path.name} had {len(programs_data)} program(s) but all already exist")
            
            if len(self.program_manager.programs) > 0:
                if not self.program_manager.current_program:
                    self.program_manager.current_program = self.program_manager.programs[0]
                return True
            else:
                logger.warning(f"Loaded .soo file but no programs were processed: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading .soo file {file_path}: {e}", exc_info=True)
            return False
    
    def load_latest_soo_files(self) -> bool:
        """
        Load all .soo files from work directory.
        
        Returns:
            True if any files were loaded successfully, False otherwise
        """
        try:
            if not self.work_dir.exists():
                self.work_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Work directory does not exist, created it")
                return False
            
            soo_files = list(self.work_dir.glob("*.soo"))
            if not soo_files:
                logger.info("No .soo files found in work directory")
                return False
            
            logger.info(f"Found {len(soo_files)} .soo file(s) in work directory")
            
            initial_program_count = len(self.program_manager.programs)
            files_processed = 0
            files_with_errors = 0
            
            for soo_file in sorted(soo_files):
                try:
                    logger.info(f"Loading .soo file: {soo_file.name}")
                    result = self.load_soo_file(str(soo_file), clear_existing=False)
                    if result:
                        files_processed += 1
                        logger.info(f"Successfully processed .soo file: {soo_file.name}")
                    else:
                        logger.warning(f"Failed to process .soo file: {soo_file.name}")
                except Exception as e:
                    files_with_errors += 1
                    logger.error(f"Error loading .soo file {soo_file.name}: {e}", exc_info=True)
            
            final_program_count = len(self.program_manager.programs)
            programs_added = final_program_count - initial_program_count
            
            logger.info(f"Loaded {files_processed} .soo file(s) from work directory")
            logger.info(f"Total programs: {initial_program_count} -> {final_program_count} (added {programs_added})")
            
            if files_with_errors > 0:
                logger.warning(f"{files_with_errors} file(s) had errors during loading")
            
            return final_program_count > 0
        except Exception as e:
            logger.error(f"Error loading .soo files: {e}", exc_info=True)
            return False
    
    def save_soo_file_for_screen(self, program: Program, file_path: Optional[str] = None) -> bool:
        """
        Create or update .soo file for a screen.
        
        Args:
            program: Program to save (used to determine screen)
            file_path: Optional custom file path
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if not screen_name:
                import time
                screen_name = f"Screen_{int(time.time())}"
                logger.warning(f"No screen name found, generating: {screen_name}")
            
            safe_name = ScreenManager.sanitize_screen_name(screen_name)
            
            if file_path:
                soo_file = Path(file_path)
            else:
                soo_file = self.work_dir / f"{safe_name}.soo"
            
            # Collect screen properties from all programs in the screen
            screen_programs = ScreenManager.get_programs_for_screen(
                self.program_manager.programs, screen_name
            )
            
            # Start with the current program's screen properties as base
            screen_properties = program.properties.get("screen", {}).copy()
            screen_properties["screen_name"] = screen_name
            
            # Merge screen properties from all programs in this screen
            # CRITICAL: Use screen properties from programs, NEVER program.width/height (which is PC canvas size)
            # The screen_properties["width"] and ["height"] MUST be the actual controller screen dimensions
            # Priority: Use the first non-None width/height found, or keep existing if already set
            for p in screen_programs:
                p_screen_props = p.properties.get("screen", {})
                
                # CRITICAL: Always collect width/height from screen properties (controller screen dimensions)
                # Use the first valid width/height found, or keep existing if already valid
                if "width" not in screen_properties or not screen_properties.get("width"):
                    screen_width = p_screen_props.get("width")
                    if screen_width is not None:
                        try:
                            screen_properties["width"] = int(screen_width)
                        except (ValueError, TypeError):
                            pass
                
                if "height" not in screen_properties or not screen_properties.get("height"):
                    screen_height = p_screen_props.get("height")
                    if screen_height is not None:
                        try:
                            screen_properties["height"] = int(screen_height)
                        except (ValueError, TypeError):
                            pass
                
                # Other properties can be merged (only if not already set)
                if "rotate" not in screen_properties and "rotate" in p_screen_props:
                    screen_properties["rotate"] = p_screen_props["rotate"]
                if "brand" not in screen_properties and "brand" in p_screen_props:
                    screen_properties["brand"] = p_screen_props["brand"]
                if "model" not in screen_properties and "model" in p_screen_props:
                    screen_properties["model"] = p_screen_props["model"]
                if "controller_type" not in screen_properties and "controller_type" in p_screen_props:
                    screen_properties["controller_type"] = p_screen_props["controller_type"]
                if "controller_id" not in screen_properties and "controller_id" in p_screen_props:
                    screen_properties["controller_id"] = p_screen_props["controller_id"]
            
            # CRITICAL: Ensure width/height are always in screen_properties before saving
            # If still missing, use defaults or log warning
            if "width" not in screen_properties or not screen_properties.get("width"):
                logger.warning(f"Screen '{screen_name}' missing width in screen_properties, using default 640")
                screen_properties["width"] = 640
            if "height" not in screen_properties or not screen_properties.get("height"):
                logger.warning(f"Screen '{screen_name}' missing height in screen_properties, using default 480")
                screen_properties["height"] = 480
            
            # Prepare programs data
            # Remove program-level width/height (PC canvas) but keep screen-level width/height (controller screen)
            programs = []
            for p in screen_programs:
                program_dict = p.to_dict()
                # Remove PC canvas dimensions (program.width/height) - these are not controller screen dimensions
                program_dict.pop("width", None)
                program_dict.pop("height", None)
                
                # Keep screen properties but ensure width/height are preserved from screen_properties
                if "screen" in program_dict.get("properties", {}):
                    screen_props_copy = program_dict["properties"]["screen"].copy()
                    # Don't remove width/height from screen properties - they are controller screen dimensions
                    # They will be overwritten by screen_properties anyway, but keep them for reference
                    # Only remove if they're the PC canvas dimensions (which shouldn't be in screen properties)
                    # Actually, keep them - they should be the controller screen dimensions
                    program_dict["properties"]["screen"] = screen_props_copy
                programs.append(program_dict)
            
            screen_data = {
                "screen_name": screen_name,
                "screen_properties": screen_properties,
                "programs": programs
            }
            
            with open(soo_file, 'w', encoding='utf-8') as f:
                json.dump(screen_data, f, indent=2, ensure_ascii=False)
            
            # Update program with file path
            program.properties["working_file_path"] = str(soo_file)
            if "screen" not in program.properties:
                program.properties["screen"] = {}
            program.properties["screen"]["screen_name"] = screen_name
            program.properties["screen"]["working_file_path"] = str(soo_file)
            
            logger.info(f"Created .soo file: {soo_file.name} for screen: {screen_name} with {len(programs)} program(s)")
            return True
        except Exception as e:
            logger.error(f"Error creating .soo file: {e}", exc_info=True)
            return False
    
    def cleanup_orphaned_files(self, current_screen_names: set):
        """
        Remove .soo files from work directory that don't correspond to any current screen.
        
        Args:
            current_screen_names: Set of screen names that currently exist in the program list
        """
        try:
            if not self.work_dir.exists():
                return
            
            # Get all .soo files in work directory
            soo_files = list(self.work_dir.glob("*.soo"))
            
            if not soo_files:
                return
            
            # Create set of sanitized current screen names for comparison
            sanitized_current_names = {ScreenManager.sanitize_screen_name(name) for name in current_screen_names}
            
            deleted_count = 0
            for soo_file in soo_files:
                # Get screen name from filename (remove .soo extension)
                file_stem = soo_file.stem
                
                # Check if this file corresponds to a current screen
                if file_stem not in sanitized_current_names:
                    try:
                        soo_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted orphaned autosave file: {soo_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete orphaned file {soo_file.name}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} orphaned autosave file(s)")
        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}", exc_info=True)

