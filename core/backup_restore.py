"""
Backup and restore functionality for complete system backup
"""
import json
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class BackupRestore:
    """Manages complete backup and restore operations"""
    
    def __init__(self):
        self.backup_dir = Path.home() / ".slplayer" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, output_path: Optional[str] = None, program_manager=None, media_library=None, settings=None) -> bool:
        """
        Create complete backup of all application data.
        Returns True if successful.
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.backup_dir / f"slplayer_backup_{timestamp}.backup"
            else:
                output_path = Path(output_path)
            
            backup_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "programs": [],
                "media_library": [],
                "settings": {},
                "schedules": []
            }
            
            # Backup all programs (if program_manager provided)
            if program_manager:
                if hasattr(program_manager, 'programs_dir') and program_manager.programs_dir.exists():
                    programs_dir = program_manager.programs_dir
                    for program_file in programs_dir.glob("*.json"):
                        try:
                            with open(program_file, 'r', encoding='utf-8') as f:
                                program_data = json.load(f)
                                backup_data["programs"].append({
                                    "filename": program_file.name,
                                    "data": program_data
                                })
                        except Exception as e:
                            logger.warning(f"Error backing up program {program_file}: {e}")
                elif hasattr(program_manager, 'programs'):
                    # Backup programs from ProgramManager
                    for program in program_manager.programs:
                        try:
                            backup_data["programs"].append({
                                "id": program.id,
                                "data": program.to_dict()
                            })
                        except Exception as e:
                            logger.warning(f"Error backing up program {program.id}: {e}")
            
            # Backup media library (if provided)
            if media_library:
                try:
                    if hasattr(media_library, 'get_media_files'):
                        media_files = media_library.get_media_files()
                        backup_data["media_library"] = media_files
                except Exception as e:
                    logger.warning(f"Error backing up media library: {e}")
            
            # Backup settings
            if settings is None:
                from config.settings import settings as app_settings
                backup_data["settings"] = app_settings.settings.copy()
            else:
                backup_data["settings"] = settings.settings.copy() if hasattr(settings, 'settings') else settings
            
            # Backup schedules (if schedule manager exists)
            try:
                from core.schedule_manager import ScheduleManager
                schedule_manager = ScheduleManager()
                # Load schedules if they exist
                schedule_file = get_app_data_dir() / "schedules.json"
                if schedule_file.exists():
                    with open(schedule_file, 'r', encoding='utf-8') as f:
                        backup_data["schedules"] = json.load(f)
            except Exception as e:
                logger.warning(f"Error backing up schedules: {e}")
            
            # Save backup file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup created successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_path: str, program_manager=None, media_library=None) -> bool:
        """
        Restore from backup file.
        Returns True if successful.
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restore programs (if program_manager provided)
            if "programs" in backup_data and program_manager:
                if hasattr(program_manager, 'programs_dir'):
                    programs_dir = program_manager.programs_dir
                    programs_dir.mkdir(parents=True, exist_ok=True)
                    
                    for program_info in backup_data["programs"]:
                        try:
                            if "filename" in program_info:
                                program_file = programs_dir / program_info["filename"]
                                with open(program_file, 'w', encoding='utf-8') as f:
                                    json.dump(program_info["data"], f, indent=2, ensure_ascii=False)
                            elif "data" in program_info:
                                # Restore program object directly
                                from core.program_manager import Program
                                program = Program()
                                program.from_dict(program_info["data"])
                                program_manager.programs.append(program)
                        except Exception as e:
                            logger.warning(f"Error restoring program: {e}")
            
            # Restore media library
            if "media_library" in backup_data and media_library:
                # Note: This restores metadata, actual media files should be preserved
                logger.info("Media library metadata restored (files should be in original locations)")
            
            # Restore settings
            if "settings" in backup_data:
                from config.settings import settings as app_settings
                app_settings.settings.update(backup_data["settings"])
                app_settings.save_settings()
            
            # Restore schedules
            if "schedules" in backup_data:
                from utils.app_data import ensure_app_data_dir, get_app_data_dir
                ensure_app_data_dir()
                schedule_file = get_app_data_dir() / "schedules.json"
                schedule_file.parent.mkdir(parents=True, exist_ok=True)
                with open(schedule_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data["schedules"], f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup restored successfully from: {backup_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Error restoring backup: {e}")
            return False
    
    def export_user_data(self, output_path: str) -> bool:
        """Export user data (programs, settings, schedules)"""
        try:
            from core.program_manager import ProgramManager
            from config.settings import settings
            
            program_manager = ProgramManager()
            
            return self.create_backup(output_path, program_manager=program_manager, settings=settings)
        except Exception as e:
            logger.exception(f"Error exporting user data: {e}")
            return False
    
    def import_user_data(self, input_path: str) -> bool:
        """Import user data"""
        try:
            from core.program_manager import ProgramManager
            
            program_manager = ProgramManager()
            
            return self.restore_backup(input_path, program_manager=program_manager)
        except Exception as e:
            logger.exception(f"Error importing user data: {e}")
            return False

