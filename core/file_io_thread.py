"""
Background file I/O operations to prevent UI blocking
"""
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, List
from pathlib import Path
from core.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FileLoadThread(QThread):
    """Thread for loading .soo files in background"""
    finished = pyqtSignal(bool, str, object)  # success, file_path, error
    progress = pyqtSignal(str)  # progress message
    
    def __init__(self, file_path: str, file_manager: FileManager, clear_existing: bool = False):
        super().__init__()
        self.file_path = file_path
        self.file_manager = file_manager
        self.clear_existing = clear_existing
    
    def run(self):
        try:
            self.progress.emit(f"Loading {Path(self.file_path).name}...")
            result = self.file_manager.load_soo_file(self.file_path, self.clear_existing)
            if result:
                self.progress.emit("File loaded successfully")
            else:
                self.progress.emit("Failed to load file")
            self.finished.emit(result, self.file_path, None)
        except Exception as e:
            logger.error(f"Error in file load thread: {e}", exc_info=True)
            self.finished.emit(False, self.file_path, e)


class FileSaveThread(QThread):
    """Thread for saving .soo files in background"""
    finished = pyqtSignal(bool, str, object)  # success, file_path, error
    progress = pyqtSignal(str)  # progress message
    
    def __init__(self, program, file_manager: FileManager, file_path: Optional[str] = None):
        super().__init__()
        self.program = program
        self.file_manager = file_manager
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit("Saving file...")
            result = self.file_manager.save_soo_file_for_screen(self.program, self.file_path)
            if result:
                self.progress.emit("File saved successfully")
            else:
                self.progress.emit("Failed to save file")
            self.finished.emit(result, self.file_path or "", None)
        except Exception as e:
            logger.error(f"Error in file save thread: {e}", exc_info=True)
            self.finished.emit(False, self.file_path or "", e)


class BatchFileLoadThread(QThread):
    """Thread for loading multiple .soo files in background"""
    finished = pyqtSignal(bool, int, int)  # success, files_loaded, files_total
    progress = pyqtSignal(str, int, int)  # message, current, total
    
    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager
    
    def run(self):
        try:
            # Use the existing FileManager method with progress callback
            def progress_callback(file_name, current, total):
                self.progress.emit(f"Loading {file_name}...", current, total)
            
            success, files_loaded, files_total = self.file_manager.load_latest_soo_files(progress_callback)
            self.finished.emit(success, files_loaded, files_total)
        except Exception as e:
            logger.error(f"Error in batch file load thread: {e}", exc_info=True)
            self.finished.emit(False, 0, 0)

