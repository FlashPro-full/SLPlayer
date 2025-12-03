"""
Logging utility for SLPlayer application
"""
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class SLPlayerLogger:
    """Centralized logging system for SLPlayer"""
    
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
        """Setup the logger with file and console handlers"""
        # Create logger
        logger = logging.getLogger('SLPlayer')
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return
        
        # Determine log directory
        # When running as exe, save logs next to the exe for easy access
        # Otherwise, use the standard location
        is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        if is_exe:
            # Running as executable - save logs next to exe
            if sys.platform == "win32":
                exe_path = Path(sys.executable)
                log_dir = exe_path.parent / "logs"
            else:
                log_dir = Path.home() / ".slplayer" / "logs"
        else:
            # Running as script - use standard location
            log_dir = Path.home() / ".slplayer" / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler with rotation (10MB max, keep 5 backups)
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
        
        # Console handler (only INFO and above)
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
        """Get the logger instance"""
        if self._logger is None:
            self._setup_logger()
        return self._logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, **kwargs)


# Global logger instance
_logger_instance = SLPlayerLogger()
logger = _logger_instance.logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance, optionally with a specific name"""
    if name:
        return logging.getLogger(f'SLPlayer.{name}')
    return logger


def get_log_directory() -> Path:
    """Get the log directory path"""
    # When running as exe, logs are next to the exe
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
    """
    Export all log files (including rotated backups) to a single text file.
    
    Args:
        output_path: Path where the exported log file should be saved
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        log_dir = get_log_directory()
        
        if not log_dir.exists():
            return False
        
        # Find all log files (main log + rotated backups)
        log_files = []
        main_log = log_dir / "slplayer.log"
        if main_log.exists():
            log_files.append(main_log)
        
        # Find rotated log files (slplayer.log.1, slplayer.log.2, etc.)
        for i in range(1, 10):  # Check up to 9 backup files
            backup_log = log_dir / f"slplayer.log.{i}"
            if backup_log.exists():
                log_files.append(backup_log)
            else:
                break
        
        if not log_files:
            return False
        
        # Read all log files and combine them
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
                # If we can't read a file, skip it but continue
                logger.warning(f"Could not read log file {log_file}: {e}")
        
        if not all_log_entries:
            return False
        
        # Write combined logs to output file
        from datetime import datetime
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SLPlayer - Complete Log Export\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write logs in reverse order (oldest first, newest last)
            # Rotated files are numbered with higher numbers being older
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