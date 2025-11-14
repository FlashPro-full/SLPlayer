"""
Base controller interface for LED display controllers
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Callable
from enum import Enum
from datetime import datetime


class ConnectionStatus(Enum):
    """Controller connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ControllerType(Enum):
    """Controller type"""
    NOVASTAR = "novastar"
    HUIDU = "huidu"


class BaseController(ABC):
    """Base class for all controller implementations"""
    
    def __init__(self, controller_type: ControllerType, ip_address: str, port: int = 5000):
        self.controller_type = controller_type
        self.ip_address = ip_address
        self.port = port
        self.status = ConnectionStatus.DISCONNECTED
        self.device_info: Optional[Dict] = None
        self.on_status_changed: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the controller"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the controller"""
        pass
    
    @abstractmethod
    def get_device_info(self) -> Optional[Dict]:
        """Get controller device information"""
        pass
    
    def get_controller_id(self) -> Optional[str]:
        """
        Get controller ID for license activation.
        This should be a unique identifier for the display.
        
        Uses multiple fallback methods:
        1. Try to get from device_info (protocol-specific)
        2. Use device name + model from device_info
        3. Use MAC address + IP address
        4. Use IP address as final fallback
        
        Returns:
            Controller ID string (e.g., "HD-M30-00123456") or None if not available
        """
        # Method 1: Try to get from device_info (protocol-specific fields)
        device_info = self.get_device_info()
        if device_info:
            # Try common field names for controller ID
            controller_id = (
                device_info.get('controller_id') or 
                device_info.get('controllerId') or
                device_info.get('id') or
                device_info.get('serial_number') or
                device_info.get('serial') or
                device_info.get('device_id')
            )
            if controller_id:
                return str(controller_id)
            
            # Method 2: Use device name + model as identifier
            device_name = device_info.get('device_name') or device_info.get('name') or device_info.get('display_name')
            model = device_info.get('model') or device_info.get('model_number') or device_info.get('type')
            
            if device_name and model:
                # Create ID from device name and model
                safe_name = device_name.replace(' ', '-').replace('_', '-').upper()
                safe_model = model.replace(' ', '-').replace('_', '-').upper()
                return f"{safe_model}-{safe_name}"
            elif model:
                # Use model + IP as fallback
                safe_model = model.replace(' ', '-').replace('_', '-').upper()
                safe_ip = self.ip_address.replace('.', '-')
                return f"{safe_model}-{safe_ip}"
            elif device_name:
                # Use device name + IP as fallback
                safe_name = device_name.replace(' ', '-').replace('_', '-').upper()
                safe_ip = self.ip_address.replace('.', '-')
                return f"{safe_name}-{safe_ip}"
        
        # Method 3: Try to get MAC address from network interface
        mac_address = self._get_mac_address()
        if mac_address:
            # Use MAC address + IP as identifier
            safe_mac = mac_address.replace(':', '-').upper()
            safe_ip = self.ip_address.replace('.', '-')
            return f"CTRL-{safe_mac}-{safe_ip}"
        
        # Method 4: Final fallback - use IP address with controller type
        controller_type_str = self.controller_type.value.upper()
        safe_ip = self.ip_address.replace('.', '-')
        return f"{controller_type_str}-{safe_ip}"
    
    def _get_mac_address(self) -> Optional[str]:
        """
        Get MAC address of the network interface used to reach the controller.
        This is a best-effort attempt and may not always work.
        """
        try:
            import socket
            import subprocess
            import platform
            
            # Try to get MAC address from ARP table or network interface
            system = platform.system()
            
            if system == "Windows":
                # Windows: Use arp command
                try:
                    result = subprocess.run(
                        ['arp', '-a', self.ip_address],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        # Parse MAC address from arp output
                        for line in result.stdout.split('\n'):
                            if self.ip_address in line:
                                parts = line.split()
                                for part in parts:
                                    if ':' in part or '-' in part:
                                        # Found MAC address
                                        return part.replace('-', ':')
                except:
                    pass
            
            elif system in ["Linux", "Darwin"]:
                # Linux/Mac: Use arp command
                try:
                    result = subprocess.run(
                        ['arp', '-n', self.ip_address],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        # Parse MAC address from arp output
                        for line in result.stdout.split('\n'):
                            if self.ip_address in line:
                                parts = line.split()
                                for part in parts:
                                    if ':' in part or '-' in part:
                                        # Found MAC address
                                        return part.replace('-', ':')
                except:
                    pass
            
            # Fallback: Try to get MAC from network interface
            # This is more complex and may not always work
            try:
                import psutil
                # Get network interfaces
                interfaces = psutil.net_if_addrs()
                for interface_name, addresses in interfaces.items():
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            # Check if this interface can reach the controller IP
                            # This is a simplified check
                            if addr.address:
                                # Try to get MAC address for this interface
                                for mac_addr in addresses:
                                    if mac_addr.family == psutil.AF_LINK:
                                        return mac_addr.address
            except ImportError:
                # psutil not available, skip
                pass
            except:
                pass
                
        except Exception:
            # If all methods fail, return None
            pass
        
        return None
    
    @abstractmethod
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        """Upload program to controller"""
        pass
    
    @abstractmethod
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        """Download program from controller"""
        pass
    
    @abstractmethod
    def get_program_list(self) -> List[Dict]:
        """Get list of programs on controller"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to controller"""
        pass
    
    def is_connected(self) -> bool:
        """Check if controller is connected"""
        return self.status == ConnectionStatus.CONNECTED
    
    def upload_schedule(self, schedule_data: Dict) -> bool:
        """
        Upload schedule to controller.
        Default implementation - can be overridden by specific controllers.
        """
        # Default: try to upload as generic data
        if hasattr(self, 'upload_data'):
            return self.upload_data("schedule", schedule_data)
        return False
    
    def set_time(self, time: datetime) -> bool:
        """
        Set controller time.
        Default implementation - can be overridden by specific controllers.
        """
        # Default implementation - should be overridden
        return False
    
    def get_brightness(self) -> Optional[int]:
        """
        Get brightness from controller.
        Returns brightness value (0-100) or None if not supported.
        """
        # Default implementation - should be overridden
        return None
    
    def set_brightness(self, brightness: int) -> bool:
        """
        Set controller brightness.
        brightness: 0-100
        """
        # Default implementation - should be overridden
        return False
    
    def set_power_schedule(self, on_time: str, off_time: str, enabled: bool = True) -> bool:
        """
        Set power on/off schedule.
        on_time: "HH:MM:SS" format
        off_time: "HH:MM:SS" format
        """
        # Default implementation - should be overridden
        return False
    
    def set_status(self, status: ConnectionStatus):
        """Set connection status and notify"""
        self.status = status
        if self.on_status_changed:
            self.on_status_changed(status)
    
    def set_progress(self, progress: int, message: str = ""):
        """Set upload/download progress"""
        if self.on_progress:
            self.on_progress(progress, message)

