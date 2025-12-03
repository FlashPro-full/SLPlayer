from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import hashlib
import shutil
from utils.logger import get_logger

logger = get_logger(__name__)


class SyncManager:
    
    def __init__(self):
        from utils.app_data import get_app_data_dir
        self.local_db_path = get_app_data_dir() / "local_db.json"
        self.media_dir = get_app_data_dir() / "sync_media"
        self.media_dir.mkdir(parents=True, exist_ok=True)
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
                "controller_id": None,
                "programs": {},
                "media": {},
                "time": None,
                "brightness": None,
                "power_schedule": None,
                "network": None,
                "screen_resolution": None,
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
    
    def import_from_controller(self, controller, screen_manager=None, program_manager=None) -> Dict[str, Any]:
        imported_data = {
            "programs": {},
            "media": {},
            "time": None,
            "brightness": None,
            "power_schedule": None,
            "network": None,
            "screen_resolution": None
        }
        
        try:
            controller_id = controller.get_controller_id()
            imported_data["controller_id"] = controller_id
            
            logger.info(f"Starting import from controller {controller_id}")
            
            if hasattr(controller, 'get_program_list'):
                program_list = controller.get_program_list()
                logger.info(f"Found {len(program_list)} programs on controller")
                
                controller_type = "novastar" if hasattr(controller, '_device_sn') or str(type(controller)).lower().find('novastar') >= 0 else "huidu"
                
                for program_info in program_list:
                    program_id = program_info.get("id") or program_info.get("name")
                    if program_id:
                        sdk_program_data = controller.download_program(program_id)
                        if sdk_program_data:
                            # Convert SDK format to *.soo format
                            from core.program_converter import ProgramConverter
                            soo_program_data = ProgramConverter.sdk_to_soo(sdk_program_data, controller_type)
                            
                            imported_data["programs"][program_id] = {
                                "data": soo_program_data,
                                "hash": self.calculate_hash(soo_program_data),
                                "modified": datetime.now().isoformat()
                            }
                            
                            # Save as *.soo file
                            if screen_manager:
                                from core.file_manager import FileManager
                                from utils.app_data import get_app_data_dir
                                from core.screen_manager import Screen
                                from core.program_manager import Program
                                
                                file_manager = FileManager(screen_manager)
                                work_dir = get_app_data_dir() / "work"
                                work_dir.mkdir(parents=True, exist_ok=True)
                                
                                program_name = soo_program_data.get("name", f"Imported_{program_id}")
                                safe_name = program_name.replace(' ', '_').replace('/', '_')
                                soo_file_path = str(work_dir / f"{safe_name}_{program_id}.soo")
                                
                                # Create screen for imported program if needed
                                screen_name = f"Imported_{controller_id}"
                                existing_screen = screen_manager.get_screen_by_name(screen_name)
                                if not existing_screen:
                                    screen_resolution = imported_data.get("screen_resolution", {})
                                    screen_width = screen_resolution.get("width", 640) if screen_resolution else 640
                                    screen_height = screen_resolution.get("height", 480) if screen_resolution else 480
                                    existing_screen = screen_manager.create_screen(screen_name, screen_width, screen_height)
                                
                                # Create and add program
                                program = Program()
                                program.from_dict(soo_program_data)
                                existing_screen.add_program(program)
                                
                                # Save to *.soo file
                                file_manager.save_screen_to_file(existing_screen, soo_file_path)
                                logger.info(f"Saved downloaded program to {soo_file_path}")
                            
                            media_files = self._extract_media_from_program(soo_program_data)
                            for media_path in media_files:
                                if media_path and Path(media_path).exists():
                                    media_hash = self._download_media_file(media_path)
                                    if media_hash:
                                        imported_data["media"][media_hash] = {
                                            "original_path": media_path,
                                            "local_path": str(self.media_dir / f"{media_hash}{Path(media_path).suffix}"),
                                            "hash": media_hash
                                        }
            
            if hasattr(controller, 'get_time'):
                imported_data["time"] = controller.get_time()
            
            if hasattr(controller, 'get_brightness'):
                imported_data["brightness"] = controller.get_brightness()
            
            if hasattr(controller, 'get_power_schedule'):
                imported_data["power_schedule"] = controller.get_power_schedule()
            
            if hasattr(controller, 'get_network_config'):
                imported_data["network"] = controller.get_network_config()
            
            device_info = controller.get_device_info()
            if device_info:
                if not imported_data["brightness"]:
                    imported_data["brightness"] = device_info.get("brightness")
                if not imported_data["network"]:
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
            
            self.local_db["controller_id"] = controller_id
            self.local_db.update(imported_data)
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.save_local_db()
            
            if screen_manager and program_manager:
                self._import_programs_to_manager(imported_data["programs"], screen_manager, program_manager, imported_data.get("screen_resolution"))
            
            logger.info(f"Successfully imported {len(imported_data['programs'])} programs from controller")
            return imported_data
            
        except Exception as e:
            logger.exception(f"Error importing from controller: {e}")
            return imported_data
    
    def _extract_media_from_program(self, program_data: Dict) -> List[str]:
        media_files = []
        elements = program_data.get("elements", [])
        for element in elements:
            element_type = element.get("type", "")
            properties = element.get("properties", {})
            
            if element_type in ["photo", "image", "picture"]:
                file_path = properties.get("file_path") or properties.get("image_path")
                if file_path:
                    media_files.append(file_path)
            elif element_type == "video":
                file_path = properties.get("file_path") or properties.get("video_path")
                if file_path:
                    media_files.append(file_path)
        
        return list(set(media_files))
    
    def _download_media_file(self, media_path: str) -> Optional[str]:
        try:
            source_path = Path(media_path)
            if not source_path.exists():
                return None
            
            with open(source_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            dest_path = self.media_dir / f"{file_hash}{source_path.suffix}"
            if not dest_path.exists():
                shutil.copy2(source_path, dest_path)
            
            return file_hash
        except Exception as e:
            logger.warning(f"Error downloading media file {media_path}: {e}")
            return None
    
    def _import_programs_to_manager(self, programs: Dict, screen_manager, program_manager, screen_resolution: Optional[Dict]):
        try:
            screen_width = screen_resolution.get("width") if screen_resolution else 640
            screen_height = screen_resolution.get("height") if screen_resolution else 480
            
            controller_id = self.local_db.get("controller_id", "Controller")
            screen_name = f"Imported_{controller_id}"
            
            existing_screen = screen_manager.get_screen_by_name(screen_name)
            if not existing_screen:
                existing_screen = screen_manager.create_screen(screen_name, screen_width, screen_height)
            
            from core.file_manager import FileManager
            from utils.app_data import get_app_data_dir
            file_manager = FileManager(screen_manager)
            work_dir = get_app_data_dir() / "work"
            work_dir.mkdir(parents=True, exist_ok=True)
            
            for program_id, program_info in programs.items():
                program_data = program_info.get("data", {})
                
                # Program data is already in *.soo format (converted during download)
                from core.program_manager import Program
                program = Program()
                program.from_dict(program_data)
                
                existing_screen.add_program(program)
                if program_manager:
                    program_manager.programs.append(program)
                    program_manager._programs_by_id[program.id] = program
                
                # Save to *.soo file for persistence
                program_name = program_data.get("name", f"Program_{program_id}")
                safe_name = program_name.replace(' ', '_').replace('/', '_')
                soo_file_path = str(work_dir / f"{safe_name}_{program_id}.soo")
                file_manager.save_screen_to_file(existing_screen, soo_file_path)
                
                # Load the *.soo file so it appears in UI
                if screen_manager:
                    screen_manager.current_screen = existing_screen
                from core.program_manager import Program
                program = Program()
                program.from_dict(program_data)
                
                existing_program = screen_manager.get_program_by_id(program.id)
                if existing_program:
                    existing_program.from_dict(program_data)
                else:
                    existing_screen.add_program(program)
                    if program not in program_manager.programs:
                        program_manager.programs.append(program)
                        program_manager._programs_by_id[program.id] = program
            
            logger.info(f"Imported {len(programs)} programs to screen '{screen_name}'")
        except Exception as e:
            logger.exception(f"Error importing programs to manager: {e}")
    
    def compare_and_sync(self, controller, program_manager, screen_manager=None) -> Dict[str, Any]:
        changes = {
            "programs_to_upload": [],
            "programs_to_delete": [],
            "parameters_to_update": {},
            "media_to_upload": []
        }
        
        try:
            current_programs = {}
            all_programs = []
            
            if screen_manager:
                all_programs = screen_manager.get_all_programs()
            elif program_manager:
                all_programs = program_manager.programs
            
            for program in all_programs:
                program_dict = program.to_dict()
                program_id = program.id
                current_programs[program_id] = {
                    "data": program_dict,
                    "hash": self.calculate_hash(program_dict),
                    "program": program
                }
            
            controller_id = controller.get_controller_id()
            local_programs = self.local_db.get("programs", {})
            
            for program_id, program_info in current_programs.items():
                local_program = local_programs.get(program_id)
                program_hash = program_info["hash"]
                
                if not local_program or local_program.get("hash") != program_hash:
                    changes["programs_to_upload"].append(program_info["data"])
                    
                    media_files = self._extract_media_from_program(program_info["data"])
                    for media_path in media_files:
                        if media_path and Path(media_path).exists():
                            changes["media_to_upload"].append(media_path)
            
            controller_programs = {}
            if hasattr(controller, 'get_program_list'):
                controller_program_list = controller.get_program_list()
                for prog_info in controller_program_list:
                    prog_id = prog_info.get("id") or prog_info.get("name")
                    if prog_id:
                        controller_programs[prog_id] = True
            
            for program_id in local_programs.keys():
                if program_id not in current_programs and program_id in controller_programs:
                    changes["programs_to_delete"].append(program_id)
            
            if hasattr(controller, 'get_brightness'):
                controller_brightness = controller.get_brightness()
                local_brightness = self.local_db.get("brightness")
                if controller_brightness != local_brightness:
                    changes["parameters_to_update"]["brightness"] = local_brightness
            
            if hasattr(controller, 'get_power_schedule'):
                controller_schedule = controller.get_power_schedule()
                local_schedule = self.local_db.get("power_schedule")
                if controller_schedule != local_schedule:
                    changes["parameters_to_update"]["power_schedule"] = local_schedule
            
            if hasattr(controller, 'get_network_config'):
                controller_network = controller.get_network_config()
                local_network = self.local_db.get("network")
                if controller_network != local_network:
                    changes["parameters_to_update"]["network"] = local_network
            
            return changes
            
        except Exception as e:
            logger.exception(f"Error comparing and syncing: {e}")
            return changes
    
    def export_to_controller(self, controller, program_manager, screen_manager=None) -> bool:
        try:
            # Step 1: Save current working state as *.soo files
            if screen_manager:
                from core.file_manager import FileManager
                file_manager = FileManager(screen_manager)
                for screen in screen_manager.screens:
                    if screen.file_path:
                        file_manager.save_screen_to_file(screen, screen.file_path)
                    else:
                        from utils.app_data import get_app_data_dir
                        work_dir = get_app_data_dir() / "work"
                        work_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = screen.name.replace(' ', '_').replace('/', '_')
                        soo_file_path = str(work_dir / f"{safe_name}.soo")
                        file_manager.save_screen_to_file(screen, soo_file_path)
                        screen.file_path = soo_file_path
            
            changes = self.compare_and_sync(controller, program_manager, screen_manager)
            
            controller_type = "novastar" if hasattr(controller, '_device_sn') or str(type(controller)).lower().find('novastar') >= 0 else "huidu"
            success_count = 0
            fail_count = 0
            
            for program_data in changes["programs_to_upload"]:
                # Convert *.soo format to SDK format
                from core.program_converter import ProgramConverter
                sdk_program_data = ProgramConverter.soo_to_sdk(program_data, controller_type)
                
                if controller.upload_program(sdk_program_data):
                    success_count += 1
                    program_id = program_data.get("id", "")
                    if program_id:
                        self.local_db["programs"][program_id] = {
                            "data": program_data,
                            "hash": self.calculate_hash(program_data),
                            "modified": datetime.now().isoformat()
                        }
                else:
                    fail_count += 1
                    logger.warning(f"Failed to upload program {program_data.get('name', 'Unknown')}")
            
            for program_id in changes["programs_to_delete"]:
                if hasattr(controller, 'delete_program'):
                    controller.delete_program(program_id)
                    self.local_db["programs"].pop(program_id, None)
            
            params = changes["parameters_to_update"]
            if params.get("brightness") is not None and hasattr(controller, 'set_brightness'):
                controller.set_brightness(params["brightness"])
                self.local_db["brightness"] = params["brightness"]
            
            if params.get("power_schedule") and hasattr(controller, 'set_power_schedule'):
                schedule = params["power_schedule"]
                controller.set_power_schedule(
                    schedule.get("on_time", ""),
                    schedule.get("off_time", ""),
                    schedule.get("enabled", True)
                )
                self.local_db["power_schedule"] = schedule
            
            if params.get("network") and hasattr(controller, 'set_network_config'):
                controller.set_network_config(params["network"])
                self.local_db["network"] = params["network"]
            
            if params.get("time") and hasattr(controller, 'set_time'):
                controller.set_time(params["time"])
                self.local_db["time"] = params["time"]
            
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.local_db["controller_id"] = controller.get_controller_id()
            self.save_local_db()
            
            logger.info(f"Export complete: {success_count} uploaded, {fail_count} failed")
            return fail_count == 0
            
        except Exception as e:
            logger.exception(f"Error exporting to controller: {e}")
            return False

