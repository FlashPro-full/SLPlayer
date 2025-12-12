import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class SLPlayerLogger:

    _instance: Optional['SLPlayerLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._setup_logger()
    
    def _setup_logger(self):

        logger = logging.getLogger('SLPlayer')
        logger.setLevel(logging.DEBUG)
        

        if logger.handlers:
            return

        is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        if is_exe:
            if sys.platform == "win32":
                exe_path = Path(sys.executable)
                log_dir = exe_path.parent / "logs"
            else:
                log_dir = Path.home() / ".slplayer" / "logs"
        else:
            log_dir = Path.home() / ".slplayer" / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "slplayer.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        self._logger = logger
    
    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._setup_logger()
        return self._logger
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)


_logger_instance = SLPlayerLogger()
logger = _logger_instance.logger


def get_logger(name: str = None) -> logging.Logger:
    if name:
        return logging.getLogger(f'SLPlayer.{name}')
    return logger


def get_log_directory() -> Path:
    is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    if is_exe:
        if sys.platform == "win32":
            exe_path = Path(sys.executable)
            return exe_path.parent / "logs"
        else:
            return Path.home() / ".slplayer" / "logs"
    else:
        return Path.home() / ".slplayer" / "logs"


def export_all_logs(output_path: Path) -> bool:
    try:
        log_dir = get_log_directory()
        
        if not log_dir.exists():
            return False
        
        log_files = []
        main_log = log_dir / "slplayer.log"
        if main_log.exists():
            log_files.append(main_log)
        
        for i in range(1, 10):
            backup_log = log_dir / f"slplayer.log.{i}"
            if backup_log.exists():
                log_files.append(backup_log)
            else:
                break
        
        if not log_files:
            return False
        
        all_log_entries = []
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        all_log_entries.append({
                            'file': log_file.name,
                            'content': content
                        })
            except Exception as e:
                logger.warning(f"Could not read log file {log_file}: {e}")
        
        if not all_log_entries:
            return False
        
        from datetime import datetime
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SLPlayer - Complete Log Export\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in reversed(all_log_entries):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Log File: {entry['file']}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(entry['content'])
                f.write("\n\n")
        
        return True
        
    except Exception as e:
        logger.exception(f"Error exporting logs: {e}")
        return False