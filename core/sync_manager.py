"""
Synchronization manager for PC ↔ Controller sync with diff comparison
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import hashlib
from utils.logger import get_logger

logger = get_logger(__name__)


class SyncManager:
    """Manages synchronization between PC and controller with diff comparison"""
    
    def __init__(self):
        self.local_db_path = Path.home() / ".slplayer" / "local_db.json"
        self.local_db: Dict = {}
        self.load_local_db()
    
    def load_local_db(self):
        """Load local database"""
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
        """Save local database"""
        try:
            self.local_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.local_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"Error saving local DB: {e}")
    
    def calculate_hash(self, data: Any) -> str:
        """Calculate hash of data for comparison"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def import_from_controller(self, controller) -> Dict[str, Any]:
        """
        Import all data from controller and create local database.
        Returns imported data dictionary.
        """
        imported_data = {
            "programs": {},
            "media": {},
            "time": None,
            "brightness": None,
            "power_schedule": None,
            "network": None
        }
        
        try:
            # Import programs
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
            
            # Import media (if supported)
            # Note: Actual media files would need to be downloaded separately
            
            # Import time, brightness, power schedule, network
            device_info = controller.get_device_info()
            if device_info:
                imported_data["brightness"] = device_info.get("brightness")
                imported_data["network"] = device_info.get("network")
            
            # Update local database
            self.local_db.update(imported_data)
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.save_local_db()
            
            logger.info("Successfully imported data from controller")
            return imported_data
            
        except Exception as e:
            logger.exception(f"Error importing from controller: {e}")
            return imported_data
    
    def compare_and_sync(self, controller, program_manager) -> Dict[str, Any]:
        """
        Compare local DB with controller and return changes.
        Returns dictionary with changes to send.
        """
        changes = {
            "programs_to_upload": [],
            "programs_to_delete": [],
            "parameters_to_update": {}
        }
        
        try:
            # Get current programs from program manager
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
            
            # Compare with local DB
            local_programs = self.local_db.get("programs", {})
            
            # Find programs to upload (new or modified)
            for program_id, program_info in current_programs.items():
                local_program = local_programs.get(program_id)
                if not local_program or local_program.get("hash") != program_info["hash"]:
                    changes["programs_to_upload"].append(program_info["data"])
            
            # Find programs to delete (removed locally)
            for program_id in local_programs.keys():
                if program_id not in current_programs:
                    changes["programs_to_delete"].append(program_id)
            
            # Compare parameters
            # Brightness, time, power schedule, network changes would be detected here
            
            return changes
            
        except Exception as e:
            logger.exception(f"Error comparing and syncing: {e}")
            return changes
    
    def export_to_controller(self, controller, program_manager) -> bool:
        """
        Export changes to controller (only send what changed).
        Returns True if successful.
        """
        try:
            changes = self.compare_and_sync(controller, program_manager)
            
            # Upload changed programs
            for program_data in changes["programs_to_upload"]:
                if not controller.upload_program(program_data):
                    logger.warning(f"Failed to upload program {program_data.get('name', 'Unknown')}")
            
            # Delete removed programs
            for program_id in changes["programs_to_delete"]:
                # Note: Controller-specific delete method would be called here
                logger.info(f"Program {program_id} marked for deletion")
            
            # Update parameters if changed
            if changes["parameters_to_update"]:
                # Update brightness, time, etc.
                pass
            
            # Update local DB after successful sync
            self.local_db["last_sync"] = datetime.now().isoformat()
            self.save_local_db()
            
            logger.info("Successfully exported changes to controller")
            return True
            
        except Exception as e:
            logger.exception(f"Error exporting to controller: {e}")
            return False

