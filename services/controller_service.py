"""
Controller Service - Business logic for controller operations
"""
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
    """
    Service layer for controller operations.
    Handles connection, discovery, and controller management.
    """
    
    def __init__(self):
        super().__init__()
        self.current_controller: Optional[BaseController] = None
        self.discovered_controllers: List[ControllerInfo] = []
        self.discovery = ControllerDiscovery()
    
    def discover_controllers(self, timeout: int = 5) -> List[ControllerInfo]:
        """
        Discover controllers on the network.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered controllers
        """
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
        """
        Connect to a controller.
        
        Args:
            ip: Controller IP address
            port: Controller port
            controller_type: 'novastar' or 'huidu'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Disconnect existing connection
            if self.current_controller:
                self.disconnect()
            
            # Create appropriate controller
            if controller_type.lower() == 'novastar':
                self.current_controller = NovaStarController(ip, port)
            elif controller_type.lower() == 'huidu':
                self.current_controller = HuiduController(ip, port)
            else:
                logger.error(f"Unknown controller type: {controller_type}")
                return False
            
            # Connect
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
        """
        Disconnect from current controller.
        
        Returns:
            True if successful, False otherwise
        """
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
        """
        Get device information from connected controller.
        
        Returns:
            Device info dictionary or None on error
        """
        try:
            if not self.current_controller:
                return None
            
            info = self.current_controller.get_device_info()
            return info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
            return None
    
    def upload_program(self, program: 'Program') -> bool:
        """
        Upload a program to the connected controller.
        
        Args:
            program: Program to upload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_controller:
                logger.warning("No controller connected")
                return False
            
            # Convert program to controller format and upload
            # This would need to be implemented based on controller protocol
            result = self.current_controller.upload_program(program)
            return result
        except Exception as e:
            logger.error(f"Error uploading program: {e}", exc_info=True)
            return False
    
    def download_program(self) -> Optional['Program']:
        """
        Download a program from the connected controller.
        
        Returns:
            Program object or None on error
        """
        try:
            if not self.current_controller:
                logger.warning("No controller connected")
                return None
            
            # Download program from controller
            # This would need to be implemented based on controller protocol
            program = self.current_controller.download_program()
            return program
        except Exception as e:
            logger.error(f"Error downloading program: {e}", exc_info=True)
            return None
    
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        if not self.current_controller:
            return ConnectionStatus.DISCONNECTED
        return self.current_controller.get_connection_status()
    
    def is_connected(self) -> bool:
        """Check if currently connected to a controller"""
        return (self.current_controller is not None and 
                self.get_connection_status() == ConnectionStatus.CONNECTED)

