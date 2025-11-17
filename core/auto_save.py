"""
Auto-save functionality for programs
"""
import threading
import time
from typing import Optional
from core.program_manager import ProgramManager
from core.file_manager import FileManager
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class AutoSaveManager:
    """Manages automatic saving of programs"""
    
    def __init__(self, program_manager: ProgramManager, file_manager: FileManager = None):
        self.program_manager = program_manager
        self.file_manager = file_manager
        self.enabled = settings.get("auto_save", True)
        self.interval = settings.get("auto_save_interval", 300)  # seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start auto-save thread"""
        if not self.enabled or self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop auto-save thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _auto_save_loop(self):
        """Auto-save loop running in background thread"""
        while self.running:
            time.sleep(self.interval)
            if self.running and self.program_manager.current_program:
                self.save_current_program()
    
    def save_current_program(self):
        """Save current program to work directory as .soo file with screen name"""
        if not self.program_manager.current_program:
            return
        
        if not self.file_manager:
            # Create file manager if not provided
            from core.file_manager import FileManager
            self.file_manager = FileManager(self.program_manager)
        
        try:
            program = self.program_manager.current_program
            self.file_manager.save_soo_file_for_screen(program)
        except Exception as e:
            logger.error(f"Auto-save error: {e}")
    

