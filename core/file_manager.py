import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from core.screen_manager import ScreenManager, Screen
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    
    def __init__(self, screen_manager: Optional[ScreenManager] = None):
        self.screen_manager = screen_manager
    
    def save_screen_to_file(self, screen: Screen, file_path: str, properties_panel=None) -> bool:
        try:
            from core.soo_file_config import SOOFileConfig, ScreenPropertiesConfig
            from core.screen_config import get_screen_config
            from core.schedule_manager import ScheduleManager
            
            if properties_panel:
                properties_panel.save_all_current_properties()
            
            screen_config = get_screen_config()
            
            screen_props = ScreenPropertiesConfig(
                screen_name=screen.name,
                width=screen.width,
                height=screen.height,
                brand=screen_config.get("brand", "") if screen_config else "",
                model=screen_config.get("model", "") if screen_config else "",
                rotation=screen_config.get("rotate", 0) if screen_config else 0
            )
            
            schedule_data = None
            try:
                from utils.app_data import get_app_data_dir
                schedule_file = get_app_data_dir() / "schedules.json"
                if schedule_file.exists():
                    with open(schedule_file, 'r', encoding='utf-8') as f:
                        schedule_data = json.load(f)
            except Exception as e:
                logger.debug(f"Could not load schedule data for saving: {e}")
            
            file_config = SOOFileConfig(
                screen_properties=screen_props,
                programs=[p.to_dict() for p in screen.programs],
                schedule=schedule_data
            )
            
            data = file_config.to_dict()
            
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            screen.file_path = file_path
            screen.modified = datetime.now().isoformat()
            
            logger.info(f"Screen saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving screen: {e}", exc_info=True)
            return False

    def load_screen_from_file(self, file_path: str) -> Optional[Screen]:
        try:
            from core.soo_file_config import SOOFileConfig
            from core.screen_config import set_screen_config
            from core.schedule_manager import ScheduleManager
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_config = SOOFileConfig.from_dict(data)
            screen_props = file_config.screen_properties
            
            screen = Screen(
                screen_props.screen_name,
                screen_props.width,
                screen_props.height
            )
            
            for program_data in file_config.programs:
                from core.program_manager import Program
                program = Program()
                program.from_dict(program_data)
                screen.add_program(program)
            
            if file_config.schedule:
                try:
                    from utils.app_data import get_app_data_dir
                    schedule_file = get_app_data_dir() / "schedules.json"
                    schedule_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(schedule_file, 'w', encoding='utf-8') as f:
                        json.dump(file_config.schedule, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.debug(f"Could not save schedule data: {e}")
            
            screen.file_path = file_path
            
            set_screen_config(
                screen_props.brand,
                screen_props.model,
                screen_props.width,
                screen_props.height,
                screen_props.rotation,
                screen_props.screen_name
            )
            
            return screen
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file '{file_path}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading screen from '{file_path}': {e}", exc_info=True)
            return None

    def load_autosaved_screens(self) -> List[Screen]:
        try:
            from utils.app_data import get_app_data_dir
            
            work_dir = get_app_data_dir() / "work"
            if not work_dir.exists():
                return []
            
            screens = []
            for soo_file in work_dir.glob("*.soo"):
                screen = self.load_screen_from_file(str(soo_file))
                if screen:
                    screens.append(screen)
            
            screens.sort(key=lambda s: s.modified or "", reverse=True)
            return screens
            
        except Exception as e:
            logger.error(f"Error loading autosaved screens: {e}", exc_info=True)
            return []

    def load_soo_file(self, file_path: str, clear_existing: bool = False) -> bool:
        try:            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            if not self.screen_manager:
                logger.error("ScreenManager not available")
                return False
            
            if clear_existing:
                self.screen_manager.screens.clear()
                self.screen_manager._screens_by_name.clear()
                self.screen_manager._screens_by_id.clear()
                self.screen_manager._programs_by_id.clear()
            
            screen = self.load_screen_from_file(file_path)
            if screen:
                if screen.id not in self.screen_manager._screens_by_id:
                    self.screen_manager.screens.append(screen)
                    self.screen_manager._screens_by_name[screen.name] = screen
                    self.screen_manager._screens_by_id[screen.id] = screen
                    self.screen_manager.current_screen = screen
                    
                    for program in screen.programs:
                        self.screen_manager._programs_by_id[program.id] = program
                    
                    logger.info(f"Loaded screen from {file_path}")
                    return True
                else:
                    logger.warning(f"Screen {screen.id} already exists")
                    return False
            else:
                logger.error(f"Failed to load screen from {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading .soo file: {e}", exc_info=True)
            return False

    def save_all_screens(self) -> int:
        if not self.screen_manager:
            return 0
        
        try:
            from utils.app_data import get_app_data_dir
            from core.screen_manager import ScreenManager
            
            work_dir = get_app_data_dir() / "work"
            work_dir.mkdir(parents=True, exist_ok=True)
            
            saved_count = 0
            for screen in self.screen_manager.screens:
                if screen.file_path:
                    file_path = screen.file_path
                else:
                    safe_name = ScreenManager.sanitize_screen_name(screen.name)
                    file_path = str(work_dir / f"{safe_name}.soo")
                
                if self.save_screen_to_file(screen, file_path):
                    saved_count += 1
            
            return saved_count
        except Exception as e:
            logger.error(f"Error saving all screens: {e}", exc_info=True)
            return 0