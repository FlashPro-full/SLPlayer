from typing import Optional, List
from pathlib import Path

from core.file_manager import FileManager
from core.program_manager import ProgramManager, Program
from core.screen_manager import ScreenManager
from core.event_bus import event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class FileService:
    
    def __init__(self, program_manager: ProgramManager, file_manager: FileManager):
        self.program_manager = program_manager
        self.file_manager = file_manager
    
    def load_file(self, file_path: str, clear_existing: bool = False) -> bool:
        try:
            result = self.file_manager.load_soo_file(file_path, clear_existing)
            if result:
                event_bus.file_loaded.emit(file_path)
                event_bus.ui_program_list_refresh.emit()
                logger.info(f"Loaded file: {file_path}")
            else:
                event_bus.file_error.emit(file_path, "Failed to load file")
            return result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
            event_bus.file_error.emit(file_path, error_msg)
            return False
    
    def save_file(self, program: Program, file_path: Optional[str] = None) -> bool:
        try:
            result = self.file_manager.save_soo_file_for_screen(program, file_path)
            if result:
                saved_path = file_path or self._get_default_file_path(program)
                event_bus.program_saved.emit(program, saved_path)
                event_bus.file_saved.emit(saved_path)
                event_bus.ui_program_list_refresh.emit()
                logger.info(f"Saved program to: {saved_path}")
            else:
                error_msg = "Failed to save file"
                event_bus.file_error.emit(
                    file_path or self._get_default_file_path(program),
                    error_msg
                )
            return result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error saving file: {e}", exc_info=True)
            event_bus.file_error.emit(
                file_path or self._get_default_file_path(program),
                error_msg
            )
            return False
    
    def load_latest_files(self) -> bool:
        try:
            result = self.file_manager.load_latest_soo_files()
            if result:
                event_bus.ui_program_list_refresh.emit()
            return result
        except Exception as e:
            logger.error(f"Error loading latest files: {e}", exc_info=True)
            return False
    
    def _get_default_file_path(self, program: Program) -> str:
        screen_name = ScreenManager.get_screen_name_from_program(program)
        sanitized = ScreenManager.sanitize_screen_name(screen_name)
        work_dir = self.file_manager.work_dir
        return str(work_dir / f"{sanitized}.soo")
    
    def get_recent_files(self, limit: int = 10) -> List[str]:
        try:
            work_dir = self.file_manager.work_dir
            if not work_dir.exists():
                return []
            
            soo_files = sorted(
                work_dir.glob("*.soo"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            return [str(f) for f in soo_files[:limit]]
        except Exception as e:
            logger.error(f"Error getting recent files: {e}")
            return []

