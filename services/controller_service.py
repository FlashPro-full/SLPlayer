from typing import List, Dict, Optional, TYPE_CHECKING
from PyQt5.QtCore import QObject

from controllers.huidu import HuiduController
from core.controller_database import get_controller_database
from core.sync_manager import SyncManager
from core.event_bus import event_bus
from utils.logger import get_logger
import json

if TYPE_CHECKING:
    from core.program_manager import Program

logger = get_logger(__name__)

class ControllerService(QObject):
    
    def __init__(self) -> None:
        super().__init__()
        self.controller_db = get_controller_database()
        self.online_controller_ids: List[str] = []
        self.all_controllers: List[Dict] = []
        self.current_controller: Optional[Dict] = None

    def discover_controllers(self):
        try:
            self.all_controllers.clear()
            self.get_online_controller_ids()
            self.get_huidu_device_property()
            self.load_controllers_from_db()
            self.all_controllers = [c for c in self.all_controllers if c.get('controller_id') in self.online_controller_ids]
            event_bus.controller_discovered.emit(self.all_controllers)
            return {
                "online_controller_ids": self.online_controller_ids,
                "all_controllers": self.all_controllers
            }
        except Exception as e:
            error_msg = f"Error discovering controllers: {str(e)}"
            logger.error(error_msg)
            event_bus.controller_error.emit(error_msg)
            return {
                "online_controller_ids": self.online_controller_ids,
                "all_controllers": self.all_controllers
            }
    
    def get_current_controller(self) -> Optional[Dict]:
        return self.current_controller
    
    def set_current_controller(self, controller_id: str):
        for controller in self.all_controllers:
            if controller['controller_id'] == controller_id:
                self.current_controller = controller
                break
        if self.current_controller:
            self.current_controller['is_online'] = controller_id in self.online_controller_ids
    
    def load_controllers_from_db(self):
        huidu_controllers = self.controller_db.get_all_huidu_controllers()
        self.all_controllers.extend(huidu_controllers)
    
    def get_online_controller_ids(self):
        try:
            controller = HuiduController()
            response = controller.get_online_devices()
            if response.get("message") == "ok" and int(response.get("total")) > 0:
                self.online_controller_ids = response.get("data")
            else:
                error_msg = f"Error getting online controllers: {response.get('data')}"
                logger.error(error_msg)
                event_bus.controller_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Error getting online controller IDs: {str(e)}"
            logger.error(error_msg)
            event_bus.controller_error.emit(error_msg)

    def get_huidu_device_property(self):
        try:
            controller = HuiduController()
            if len(self.online_controller_ids) > 0:
                response = controller.get_all_device_property(self.online_controller_ids)
                if response.get("message") == "ok" and response.get("data"):
                    for controller_data in response.get("data"):
                        logger.info(f"Controller data: {json.dumps(controller_data, indent=2, default=str)}")
                        if controller_data.get("message") == "ok":
                            controller_id = controller_data.get("id")
                            existing_controller = self.controller_db.find_huidu_controller_by_id(controller_id)
                            if existing_controller:
                                self.controller_db.update_huidu_controller_by_id(controller_id, controller_data.get("data"))
                            else:
                                controller_properties = controller_data.get("data", {})
                                controller_properties["controller_id"] = controller_id
                                self.controller_db.add_huidu_controller(controller_properties)
                else:
                    error_msg = f"Error getting device property: {response.get('data')}"
                    logger.error(error_msg)
                    event_bus.controller_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Error getting Huidu device property: {str(e)}"
            logger.error(error_msg)
            event_bus.controller_error.emit(error_msg)

    def disconnect_controller(self) -> None:
        self.current_controller = None
    
    def is_online(self) -> bool:
        if not self.current_controller:
            return False
        controller_id = self.current_controller.get("controller_id")
        return controller_id is not None and controller_id in self.online_controller_ids


_controller_service_instance = None

def get_controller_service() -> ControllerService:
    global _controller_service_instance
    if _controller_service_instance is None:
        _controller_service_instance = ControllerService()
    return _controller_service_instance