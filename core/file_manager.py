"""
File Manager for loading and saving .soo files
Handles both JSON and XML formats
"""
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from utils.logger import get_logger
from utils.app_data import get_app_data_dir
from core.program_manager import ProgramManager, Program
from core.screen_manager import ScreenManager
from core.xml_importer import XMLImporter
from core.xml_exporter import XMLExporter

logger = get_logger(__name__)


class FileManager:
    """Manages loading and saving of .soo files"""
    
    def __init__(self, program_manager: ProgramManager, screen_manager: Optional[ScreenManager] = None):
        """
        Initialize file manager.
        
        Args:
            program_manager: ProgramManager instance
            screen_manager: Optional ScreenManager instance
        """
        self.program_manager = program_manager
        self.screen_manager = screen_manager
        self.work_dir = get_app_data_dir() / "work"
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def load_soo_file(self, file_path: str, clear_existing: bool = False) -> bool:
        """
        Load a .soo file (JSON or XML format).
        
        Args:
            file_path: Path to .soo file
            clear_existing: If True, clear existing programs before loading
        
        Returns:
            True if successful, False otherwise
        """
        try:
            soo_path = Path(file_path)
            if not soo_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Clear existing if requested
            if clear_existing:
                self.program_manager.programs.clear()
                self.program_manager._programs_by_id.clear()
                if self.screen_manager:
                    self.screen_manager.screens.clear()
                    self.screen_manager._screens_by_name.clear()
                    self.screen_manager._screens_by_id.clear()
                    self.screen_manager._programs_by_id.clear()
            
            # Determine file format
            if soo_path.suffix.lower() == '.xml' or self._is_xml_file(soo_path):
                return self._load_xml_file(soo_path)
            else:
                return self._load_json_file(soo_path)
                
        except Exception as e:
            logger.exception(f"Error loading .soo file {file_path}: {e}")
            return False
    
    def _is_xml_file(self, file_path: Path) -> bool:
        """Check if file is XML format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                return first_line.startswith('<?xml') or first_line.startswith('<Node')
        except Exception:
            return False
    
    def _load_json_file(self, file_path: Path) -> bool:
        """Load JSON format .soo file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle old format (direct program data)
            if isinstance(data, dict) and "id" in data and "elements" in data:
                # Single program in old format
                program = Program()
                program.from_dict(data)
                
                # Update screen properties
                screen_properties = data.get("screen_properties", {})
                if screen_properties:
                    if "screen" not in program.properties:
                        program.properties["screen"] = {}
                    if isinstance(program.properties["screen"], dict):
                        program.properties["screen"].update(screen_properties)
                
                program.properties["working_file_path"] = str(file_path)
                
                # Add to program manager
                existing = self.program_manager.get_program_by_id(program.id)
                if existing:
                    existing.from_dict(data)
                    self.program_manager.current_program = existing
                else:
                    self.program_manager.programs.append(program)
                    if hasattr(self.program_manager, '_programs_by_id'):
                        self.program_manager._programs_by_id[program.id] = program
                    
                    # Add to screen if screen_manager available
                    if self.screen_manager:
                        screen_name = screen_properties.get("screen_name", "Screen")
                        screen = self.screen_manager.get_screen_by_name(screen_name)
                        if not screen:
                            screen = self.screen_manager.create_screen(
                                screen_name,
                                screen_properties.get("width", program.width),
                                screen_properties.get("height", program.height)
                            )
                            screen.file_path = str(file_path)
                        screen.add_program(program)
                        # Maintain global index
                        if hasattr(self.screen_manager, '_programs_by_id'):
                            self.screen_manager._programs_by_id[program.id] = program
                
                logger.info(f"Loaded program from JSON: {file_path}")
                return True
            
            # Handle new format (with screen_properties and programs)
            elif isinstance(data, dict):
                screen_properties = data.get("screen_properties", {})
                programs_data = data.get("programs", [])
                
                screen_name = screen_properties.get("screen_name", file_path.stem)
                screen_width = screen_properties.get("width", 640)
                screen_height = screen_properties.get("height", 480)
                
                # Create or get screen
                screen = None
                if self.screen_manager:
                    screen = self.screen_manager.get_screen_by_name(screen_name)
                    if not screen:
                        screen = self.screen_manager.create_screen(screen_name, screen_width, screen_height)
                        screen.file_path = str(file_path)
                    else:
                        screen.width = screen_width
                        screen.height = screen_height
                        screen.file_path = str(file_path)
                
                programs_added = 0
                for prog_data in programs_data:
                    program = Program()
                    program.from_dict(prog_data)
                    if "screen" not in program.properties:
                        program.properties["screen"] = {}
                    if isinstance(program.properties["screen"], dict):
                        program.properties["screen"].update(screen_properties)
                    program.properties["working_file_path"] = str(file_path)
                    
                    # Add to program manager
                    existing = self.program_manager.get_program_by_id(program.id)
                    if existing:
                        existing.from_dict(prog_data)
                        self.program_manager.current_program = existing
                    else:
                        self.program_manager.programs.append(program)
                        if hasattr(self.program_manager, '_programs_by_id'):
                            self.program_manager._programs_by_id[program.id] = program
                        if self.screen_manager and screen:
                            screen.add_program(program)
                            # Maintain global index
                            if hasattr(self.screen_manager, '_programs_by_id'):
                                self.screen_manager._programs_by_id[program.id] = program
                        programs_added += 1
                
                if programs_added > 0:
                    logger.info(f"Loaded {programs_added} program(s) from JSON {file_path.name}")
                return True
            
            else:
                logger.error(f"Invalid JSON format in {file_path}")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            return False
        except Exception as e:
            logger.exception(f"Error loading JSON file {file_path}: {e}")
            return False
    
    def _load_xml_file(self, file_path: Path) -> bool:
        """Load XML format .soo file"""
        try:
            # Use XMLImporter to parse XML
            program = XMLImporter.import_xml_file(str(file_path))
            if not program:
                logger.error(f"Failed to import XML file: {file_path}")
                return False
            
            # Update working file path
            program.properties["working_file_path"] = str(file_path)
            
            # Get screen properties
            screen_properties = program.properties.get("screen", {})
            screen_name = screen_properties.get("screen_name", file_path.stem)
            
            # Add to program manager
            existing = self.program_manager.get_program_by_id(program.id)
            if existing:
                existing.from_dict(program.to_dict())
                self.program_manager.current_program = existing
            else:
                self.program_manager.programs.append(program)
                if hasattr(self.program_manager, '_programs_by_id'):
                    self.program_manager._programs_by_id[program.id] = program
                
                # Add to screen if screen_manager available
                if self.screen_manager:
                    screen = self.screen_manager.get_screen_by_name(screen_name)
                    if not screen:
                        screen = self.screen_manager.create_screen(
                            screen_name,
                            screen_properties.get("width", program.width),
                            screen_properties.get("height", program.height)
                        )
                        screen.file_path = str(file_path)
                    else:
                        screen.add_program(program)
                        # Maintain global index
                        if hasattr(self.screen_manager, '_programs_by_id'):
                            self.screen_manager._programs_by_id[program.id] = program
            
            logger.info(f"Loaded program from XML: {file_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Error loading XML file {file_path}: {e}")
            return False
    
    def save_soo_file_for_screen(self, program: Program, file_path: Optional[str] = None) -> bool:
        """
        Save program to .soo file for a screen.
        
        Args:
            program: Program to save
            file_path: Optional custom file path (defaults to work_dir/{screen_name}.soo)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get screen name from program
            screen_name = ScreenManager.get_screen_name_from_program(program)
            if not screen_name:
                import time
                screen_name = f"Screen_{int(time.time())}"
                logger.warning(f"No screen name found, generating: {screen_name}")
            
            safe_name = ScreenManager.sanitize_screen_name(screen_name)
            
            # Determine file path
            if file_path:
                soo_file = Path(file_path)
            else:
                soo_file = self.work_dir / f"{safe_name}.soo"
            
            # Get screen properties
            screen_props_raw = program.properties.get("screen", {})
            screen_properties = screen_props_raw.copy() if isinstance(screen_props_raw, dict) else {}
            screen_properties["screen_name"] = screen_name
            
            # Get all programs for this screen
            if self.screen_manager:
                screen = self.screen_manager.get_screen_by_name(screen_name)
                if screen:
                    screen_programs = screen.programs
                    if not screen_properties.get("width") and screen.width:
                        screen_properties["width"] = screen.width
                    if not screen_properties.get("height") and screen.height:
                        screen_properties["height"] = screen.height
                else:
                    screen_programs = ScreenManager.get_programs_for_screen(
                        self.program_manager.programs, screen_name
                    )
            else:
                screen_programs = ScreenManager.get_programs_for_screen(
                    self.program_manager.programs, screen_name
                )
            
            # Collect screen properties from all programs
            for p in screen_programs:
                p_screen_props_raw = p.properties.get("screen", {})
                p_screen_props = p_screen_props_raw if isinstance(p_screen_props_raw, dict) else {}
                
                if isinstance(p_screen_props, dict):
                    if ("width" not in screen_properties or not screen_properties.get("width")) and "width" in p_screen_props:
                        try:
                            screen_properties["width"] = int(p_screen_props["width"])
                        except (ValueError, TypeError):
                            pass
                    
                    if ("height" not in screen_properties or not screen_properties.get("height")) and "height" in p_screen_props:
                        try:
                            screen_properties["height"] = int(p_screen_props["height"])
                        except (ValueError, TypeError):
                            pass
            
            # Always save .soo files as XML format
            if soo_file.suffix.lower() in ['.soo', '.xml']:
                # Save as XML
                return XMLExporter.export_program(program, str(soo_file), screen_properties)
            else:
                # Save as JSON for other extensions
                return self._save_json_file(soo_file, screen_properties, screen_programs)
                
        except Exception as e:
            logger.exception(f"Error saving .soo file: {e}")
            return False
    
    def _save_json_file(self, file_path: Path, screen_properties: Dict, programs: List[Program]) -> bool:
        """Save programs to JSON format .soo file"""
        try:
            data = {
                "screen_properties": screen_properties,
                "programs": [p.to_dict() for p in programs]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(programs)} program(s) to JSON: {file_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Error saving JSON file {file_path}: {e}")
            return False
    
    def load_latest_soo_files(self, progress_callback=None):
        """
        Load all .soo files from work directory.
        
        Args:
            progress_callback: Optional callback function(file_name, current, total) for progress updates
        
        Returns:
            Tuple of (success, files_loaded, files_total)
        """
        try:
            if not self.work_dir.exists():
                self.work_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Work directory does not exist, created it")
                return (False, 0, 0)
            
            soo_files = list(self.work_dir.glob("*.soo"))
            if not soo_files:
                logger.info("No .soo files found in work directory")
                return (False, 0, 0)
            
            total_files = len(soo_files)
            logger.info(f"Found {total_files} .soo file(s) in work directory")
            
            initial_program_count = len(self.program_manager.programs)
            files_processed = 0
            files_with_errors = 0
            
            for idx, soo_file in enumerate(sorted(soo_files), 1):
                try:
                    if progress_callback:
                        progress_callback(soo_file.name, idx, total_files)
                    logger.info(f"Loading .soo file: {soo_file.name}")
                    result = self.load_soo_file(str(soo_file), clear_existing=(idx == 1))
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
            
            success = final_program_count > 0
            return (success, files_processed, total_files)
        except Exception as e:
            logger.error(f"Error loading .soo files: {e}", exc_info=True)
            return (False, 0, 0)
    
    def import_xml_file(self, file_path: str) -> bool:
        """
        Import XML file (alias for load_soo_file for XML files).
        
        Args:
            file_path: Path to XML file
        
        Returns:
            True if successful, False otherwise
        """
        return self.load_soo_file(file_path, clear_existing=False)
    
    def export_to_xml(self, program: Program, file_path: str) -> bool:
        """
        Export program to XML format.
        
        Args:
            program: Program to export
            file_path: Output XML file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            screen_props_raw = program.properties.get("screen", {})
            screen_properties = screen_props_raw if isinstance(screen_props_raw, dict) else {}
            return XMLExporter.export_program(program, file_path, screen_properties)
        except Exception as e:
            logger.error(f"Error exporting to XML: {e}", exc_info=True)
            return False

