from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer, QThread
import threading

from controllers.base_controller import BaseController, ConnectionStatus, ControllerType
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController
from core.controller_discovery import ControllerDiscovery, ControllerInfo
from core.controller_database import get_controller_database
from core.sync_manager import SyncManager
from core.event_bus import event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class ControllerService(QObject):
    
    def __init__(self):
        super().__init__()
        self.current_controller: Optional[BaseController] = None
        self.discovered_controllers: List[ControllerInfo] = []
        self.discovery = ControllerDiscovery()
        self._discovery_loop: Optional[QEventLoop] = None
        self._discovery_timer: Optional[QTimer] = None
        self.sync_manager = SyncManager()
        self.controller_db = get_controller_database()
    
    def discover_controllers(self, timeout: int = 5, 
                            ip_range: Optional[List[str]] = None,
                            mobile_network_ranges: Optional[List[Dict[str, str]]] = None) -> List[ControllerInfo]:
        try:
            self.discovered_controllers = []
            
            self.discovery.start_scan(ip_range=ip_range, mobile_network_ranges=mobile_network_ranges)
            
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            finished = False
            
            def on_timeout():
                nonlocal finished
                if not finished and self.discovery.is_scanning:
                    self.discovery.stop_scan()
                finished = True
                loop.quit()
            
            def on_finished():
                nonlocal finished
                if not finished:
                    timer.stop()
                    finished = True
                    loop.quit()
            
            timer.timeout.connect(on_timeout)
            self.discovery.discovery_finished.connect(on_finished)
            
            timer.start(timeout * 1000)
            
            loop.exec()
            
            self.discovery.discovery_finished.disconnect(on_finished)
            self.discovered_controllers = self.discovery.get_discovered_controllers()
            event_bus.controller_discovered.emit(self.discovered_controllers)
            logger.info(f"Discovered {len(self.discovered_controllers)} controllers")
            return self.discovered_controllers
        except Exception as e:
            logger.error(f"Error discovering controllers: {e}", exc_info=True)
            event_bus.controller_error.emit(f"Discovery error: {e}")
            return []
    
    def connect_to_controller(self, ip: str, port: int, 
                            controller_type: str, controller_info: Optional['ControllerInfo'] = None) -> bool:
        try:
            if self.current_controller:
                self.disconnect()
            
            if controller_type.lower() == 'novastar':
                self.current_controller = NovaStarController(ip, port)
                if controller_info and hasattr(controller_info, 'mac_address') and controller_info.mac_address:
                    self.current_controller._device_sn = controller_info.mac_address
                    logger.info(f"Using discovered SN for NovaStar: {controller_info.mac_address}")
            elif controller_type.lower() == 'huidu':
                self.current_controller = HuiduController(ip, port)
            else:
                logger.error(f"Unknown controller type: {controller_type}")
                return False
            
            result = self.current_controller.connect()
            if result:
                controller_id = self.current_controller.get_controller_id()
                
                device_info = self.current_controller.get_device_info()
                
                if hasattr(self.current_controller, 'get_brightness'):
                    try:
                        brightness = self.current_controller.get_brightness()
                        if brightness is not None:
                            if not device_info:
                                device_info = {}
                            device_info['brightness'] = brightness
                            logger.info(f"Read brightness from controller at startup: {brightness}%")
                    except Exception as e:
                        logger.debug(f"Could not read brightness at startup: {e}")
                
                self.controller_db.add_or_update_controller(
                    controller_id, ip, port, controller_type, device_info
                )
                
                db_record = self.controller_db.get_controller(controller_id)
                is_first_connection = db_record and db_record.get("connection_count", 0) == 1
                
                if is_first_connection:
                    logger.info(f"First connection to controller {controller_id}, starting full data import...")
                    self._import_controller_data_async()
                
                event_bus.controller_connected.emit(self.current_controller)
                logger.info(f"Connected to {controller_type} controller at {ip}:{port}")
            else:
                logger.warning(f"Failed to connect to {controller_type} controller at {ip}:{port}")
                event_bus.controller_disconnected.emit()
            
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
    
    def send_program(self, program: 'Program', program_manager=None, screen_manager=None) -> bool:
        try:
            if not self.current_controller:
                logger.warning("No controller connected")
                event_bus.controller_error.emit("No controller connected")
                return False
            
            if not self.is_connected():
                logger.warning("Controller not connected")
                event_bus.controller_error.emit("Controller not connected")
                return False
            
            from core.file_manager import FileManager
            from utils.app_data import get_app_data_dir
            from pathlib import Path
            
            if not screen_manager:
                logger.warning("ScreenManager not available, cannot save *.soo file")
            else:
                file_manager = FileManager(screen_manager)
                work_dir = get_app_data_dir() / "work"
                work_dir.mkdir(parents=True, exist_ok=True)
                
                current_screen = screen_manager.current_screen
                if current_screen:
                    safe_name = current_screen.name.replace(' ', '_').replace('/', '_')
                    soo_file_path = str(work_dir / f"{safe_name}.soo")
                    if file_manager.save_screen_to_file(current_screen, soo_file_path):
                        logger.info(f"Saved current state to {soo_file_path} before upload")
            
            program_dict = program.to_dict() if hasattr(program, 'to_dict') else program
            controller_type = "novastar" if isinstance(self.current_controller, NovaStarController) else "huidu"
            
            from core.program_converter import ProgramConverter
            sdk_program_dict = ProgramConverter.soo_to_sdk(program_dict, controller_type)
            
            result = self.current_controller.upload_program(sdk_program_dict)
            
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
    
    def _import_controller_data_async(self):
        def import_data():
            try:
                if not self.current_controller:
                    return
                
                logger.info("Starting full import from controller...")
                
                screen_manager = None
                program_manager = None
                
                try:
                    from PyQt5.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        for widget in app.allWidgets():
                            if hasattr(widget, 'screen_manager') and widget.screen_manager:
                                screen_manager = widget.screen_manager
                            if hasattr(widget, 'program_manager') and widget.program_manager:
                                program_manager = widget.program_manager
                            if screen_manager and program_manager:
                                break
                except:
                    pass
                
                if not screen_manager or not program_manager:
                    logger.warning("Could not get screen_manager/program_manager from UI, using new instances")
                    from core.screen_manager import ScreenManager
                    from core.program_manager import ProgramManager
                    screen_manager = ScreenManager()
                    program_manager = ProgramManager()
                
                imported = self.sync_manager.import_from_controller(
                    self.current_controller, 
                    screen_manager, 
                    program_manager
                )
                
                if imported:
                    logger.info(f"Successfully imported controller data: {len(imported.get('programs', {}))} programs, {len(imported.get('media', {}))} media files")
                    event_bus.controller_data_imported.emit(imported)
                else:
                    logger.warning("No data imported from controller")
                    
            except Exception as e:
                logger.exception(f"Error importing controller data: {e}")
        
        thread = threading.Thread(target=import_data, daemon=True)
        thread.start()

