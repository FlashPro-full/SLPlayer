from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import hashlib
from utils.logger import get_logger

logger = get_logger(__name__)


class SyncManager:
    
    def __init__(self):
        from utils.app_data import get_app_data_dir
        self.local_db_path = get_app_data_dir() / "local_db.json"
        self.local_db: Dict = {}
        self.load_local_db()
    
    def load_local_db(self):
        if self.local_db_path.exists():
            try:
                with open(self.local_db_path, 'r', encoding='utf-8') as f:
                    self.local_db = json.load(f)
            except Exception as e:
                logger.exception(f"Error loading local DB: {e}")
                self.local_db = {}
        else:
            self.local_db = {
                "programs": {},
                "media": {},
                "time": None,
                "brightness": None,
                "power_schedule": None,
                "network": None,
                "last_sync": None
            }
    
    def save_local_db(self):
        try:
            self.local_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.local_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Error saving local DB: {e}")
    
    def calculate_hash(self, data: Any) -> str:
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def import_from_controller(self, controller) -> Dict[str, Any]:
        imported_data = {
            "programs": {},
            "media": {},
            "time": None,
            "brightness": None,
            "power_schedule": None,
            "network": None
        }
        
        try:
            if hasattr(controller, 'get_program_list'):
                program_list = controller.get_program_list()
                for program_info in program_list:
                    program_id = program_info.get("id", "")
                    if program_id:
                        program_data = controller.download_program(program_id)
                        if program_data:
                            imported_data["programs"][program_id] = {
                                "data": program_data,
                                "hash": self.calculate_hash(program_data),
                                "modified": datetime.now().isoformat()
                            }
            
            device_info = controller.get_device_info()
            if device_info:
                imported_data["brightness"] = device_info.get("brightness")
                imported_data["network"] = device_info.get("network")
                
                resolution = (
                    device_info.get("display_resolution") or
                    device_info.get("resolution") or
                    device_info.get("screen_resolution") or
                    device_info.get("screen_size")
                )
                
                screen_resolution = {}
                if resolution:
                    if isinstance(resolution, str) and "x" in resolution.lower():
                        try:
                            parts = resolution.lower().replace(" ", "").split("x")
                            if len(parts) == 2:
                                screen_resolution["width"] = int(parts[0])
                                screen_resolution["height"] = int(parts[1])
                        except (ValueError, IndexError):
                            pass
                    elif isinstance(resolution, dict):
                        screen_resolution["width"] = resolution.get("width") or resolution.get("w")
                        screen_resolution["height"] = resolution.get("height") or resolution.get("h")
                
                if not screen_resolution:
                    ctrl_width = device_info.get("width") or device_info.get("screen_width")
                    ctrl_height = device_info.get("height") or device_info.get("screen_height")
                    if ctrl_width and ctrl_height:
                        screen_resolution["width"] = int(ctrl_width)
                        screen_resolution["height"] = int(ctrl_height)
                
                if screen_resolution:
                    imported_data["screen_resolution"] = screen_resolution
                    logger.info(f"Imported controller screen resolution: {screen_resolution.get('width')}x{screen_resolution.get('height')}")
            
            self.local_db.update(imported_data)
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.save_local_db()
            
            logger.info("Successfully imported data from controller")
            return imported_data
            
        except Exception as e:
            logger.exception(f"Error importing from controller: {e}")
            return imported_data
    
    def compare_and_sync(self, controller, program_manager) -> Dict[str, Any]:
        changes = {
            "programs_to_upload": [],
            "programs_to_delete": [],
            "parameters_to_update": {}
        }
        
        try:
            current_programs = {}
            programs_dir = program_manager.programs_dir
            if programs_dir.exists():
                for program_file in programs_dir.glob("*.json"):
                    try:
                        with open(program_file, 'r', encoding='utf-8') as f:
                            program_data = json.load(f)
                            program_id = program_data.get("id", "")
                            if program_id:
                                current_programs[program_id] = {
                                    "data": program_data,
                                    "hash": self.calculate_hash(program_data)
                                }
                    except Exception as e:
                        logger.warning(f"Error reading program {program_file}: {e}")
            
            local_programs = self.local_db.get("programs", {})
            
            for program_id, program_info in current_programs.items():
                local_program = local_programs.get(program_id)
                if not local_program or local_program.get("hash") != program_info["hash"]:
                    changes["programs_to_upload"].append(program_info["data"])
            
            for program_id in local_programs.keys():
                if program_id not in current_programs:
                    changes["programs_to_delete"].append(program_id)
            
            return changes
            
        except Exception as e:
            logger.exception(f"Error comparing and syncing: {e}")
            return changes
    
    def export_to_controller(self, controller, program_manager) -> bool:
        try:
            changes = self.compare_and_sync(controller, program_manager)
            
            for program_data in changes["programs_to_upload"]:
                if not controller.upload_program(program_data):
                    logger.warning(f"Failed to upload program {program_data.get('name', 'Unknown')}")
            
            for program_id in changes["programs_to_delete"]:
                logger.info(f"Program {program_id} marked for deletion")
            
            if changes["parameters_to_update"]:
                pass
            
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.save_local_db()
            
            logger.info("Successfully exported changes to controller")
            return True
            
        except Exception as e:
            logger.exception(f"Error exporting to controller: {e}")
            return False

