"""
Auto-save functionality for programs
"""
import threading
import time
from typing import Optional
from pathlib import Path
from core.program_manager import Program
from config.settings import settings


class AutoSaveManager:
    """Manages automatic saving of programs"""
    
    def __init__(self, program_manager):
        self.program_manager = program_manager
        self.enabled = settings.get("auto_save", True)
        self.interval = settings.get("auto_save_interval", 300)  # seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.auto_save_dir = Path.home() / ".slplayer" / "autosave"
        self.auto_save_dir.mkdir(parents=True, exist_ok=True)
    
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
        """Save current program to auto-save location"""
        if not self.program_manager.current_program:
            return
        
        program = self.program_manager.current_program
        # Create auto-save filename based on program ID
        filename = f"autosave_{program.id}.slp"
        file_path = self.auto_save_dir / filename
        
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(program.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    def load_auto_saved_programs(self) -> list:
        """Load all auto-saved programs"""
        programs = []
        for file_path in self.auto_save_dir.glob("autosave_*.slp"):
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    program = Program()
                    program.from_dict(data)
                    programs.append(program)
            except Exception as e:
                print(f"Error loading auto-saved program {file_path}: {e}")
        
        return programs

