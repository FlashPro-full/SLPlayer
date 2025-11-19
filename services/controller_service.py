from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal

from controllers.base_controller import BaseController, ConnectionStatus, ControllerType
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController
from core.controller_discovery import ControllerDiscovery, ControllerInfo
from core.event_bus import event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class ControllerService(QObject):
    
    def __init__(self):
        super().__init__()
        self.current_controller: Optional[BaseController] = None
        self.discovered_controllers: List[ControllerInfo] = []
        self.discovery = ControllerDiscovery()
    
    def discover_controllers(self, timeout: int = 5) -> List[ControllerInfo]:
        try:
            self.discovered_controllers = self.discovery.discover_all(timeout=timeout)
            event_bus.controller_discovered.emit(self.discovered_controllers)
            logger.info(f"Discovered {len(self.discovered_controllers)} controllers")
            return self.discovered_controllers
        except Exception as e:
            logger.error(f"Error discovering controllers: {e}", exc_info=True)
            event_bus.controller_error.emit(f"Discovery error: {e}")
            return []
    
    def connect_to_controller(self, ip: str, port: int, 
                            controller_type: str) -> bool:
        try:
            if self.current_controller:
                self.disconnect()
            
            if controller_type.lower() == 'novastar':
                self.current_controller = NovaStarController(ip, port)
            elif controller_type.lower() == 'huidu':
                self.current_controller = HuiduController(ip, port)
            else:
                logger.error(f"Unknown controller type: {controller_type}")
                return False
            
            result = self.current_controller.connect()
            if result:
                event_bus.controller_connected.emit(self.current_controller)
                logger.info(f"Connected to {controller_type} controller at {ip}:{port}")
            else:
                event_bus.controller_error.emit(f"Failed to connect to {ip}:{port}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error connecting to controller: {e}", exc_info=True)
            event_bus.controller_error.emit(f"Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.current_controller:
                self.current_controller.disconnect()
                self.current_controller = None
                event_bus.controller_disconnected.emit()
                logger.info("Disconnected from controller")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {e}", exc_info=True)
            return False
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        try:
            if not self.current_controller:
                return None
            
            info = self.current_controller.get_device_info()
            return info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
            return None
    
    def send_program(self, program: 'Program') -> bool:
        try:
            if not self.current_controller:
                logger.warning("No controller connected")
                event_bus.controller_error.emit("No controller connected")
                return False
            
            if not self.is_connected():
                logger.warning("Controller not connected")
                event_bus.controller_error.emit("Controller not connected")
                return False
            
            program_dict = program.to_dict() if hasattr(program, 'to_dict') else program
            result = self.current_controller.upload_program(program_dict)
            
            if result:
                event_bus.program_sent.emit(program)
                logger.info(f"Program '{program.name if hasattr(program, 'name') else 'Unknown'}' sent successfully")
            else:
                event_bus.controller_error.emit("Failed to send program")
            
            return result
        except Exception as e:
            logger.error(f"Error sending program: {e}", exc_info=True)
            event_bus.controller_error.emit(f"Error sending program: {e}")
            return False
    
    def export_to_usb(self, program: 'Program', usb_path: str) -> bool:
        try:
            from core.xml_exporter import XMLExporter
            from pathlib import Path
            
            usb_path_obj = Path(usb_path)
            if not usb_path_obj.exists():
                logger.error(f"USB path does not exist: {usb_path}")
                event_bus.controller_error.emit(f"USB path does not exist: {usb_path}")
                return False
            
            if not usb_path_obj.is_dir():
                logger.error(f"USB path is not a directory: {usb_path}")
                event_bus.controller_error.emit(f"USB path is not a directory: {usb_path}")
                return False
            
            screen_properties = program.properties.get("screen", {}) if hasattr(program, 'properties') else {}
            program_name = program.name if hasattr(program, 'name') else "Program"
            safe_name = "".join(c for c in program_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            xml_file_path = usb_path_obj / f"{safe_name}.xml"
            
            result = XMLExporter.export_program(program, str(xml_file_path), screen_properties)
            
            if result:
                event_bus.program_exported_to_usb.emit(program, str(usb_path))
                logger.info(f"Program '{program_name}' exported to USB: {xml_file_path}")
            else:
                event_bus.controller_error.emit("Failed to export program to USB")
            
            return result
        except Exception as e:
            logger.error(f"Error exporting program to USB: {e}", exc_info=True)
            event_bus.controller_error.emit(f"Error exporting program to USB: {e}")
            return False
    
    def get_connection_status(self) -> ConnectionStatus:
        if not self.current_controller:
            return ConnectionStatus.DISCONNECTED
        return self.current_controller.get_connection_status()
    
    def is_connected(self) -> bool:
        return (self.current_controller is not None and 
                self.get_connection_status() == ConnectionStatus.CONNECTED)

