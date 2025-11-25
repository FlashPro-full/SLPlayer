from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Callable
from enum import Enum
from datetime import datetime


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ControllerType(Enum):
    NOVASTAR = "novastar"
    HUIDU = "huidu"


class BaseController(ABC):
    
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
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def get_device_info(self) -> Optional[Dict]:
        pass
    
    def get_controller_id(self) -> Optional[str]:
        device_info = self.get_device_info()
        if device_info:
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
            
            device_name = device_info.get('device_name') or device_info.get('name') or device_info.get('display_name')
            model = device_info.get('model') or device_info.get('model_number') or device_info.get('type')
            
            if device_name and model:
                safe_name = device_name.replace(' ', '-').replace('_', '-').upper()
                safe_model = model.replace(' ', '-').replace('_', '-').upper()
                return f"{safe_model}-{safe_name}"
            elif model:
                safe_model = model.replace(' ', '-').replace('_', '-').upper()
                safe_ip = self.ip_address.replace('.', '-')
                return f"{safe_model}-{safe_ip}"
            elif device_name:
                safe_name = device_name.replace(' ', '-').replace('_', '-').upper()
                safe_ip = self.ip_address.replace('.', '-')
                return f"{safe_name}-{safe_ip}"
        
        mac_address = self._get_mac_address()
        if mac_address:
            safe_mac = mac_address.replace(':', '-').upper()
            safe_ip = self.ip_address.replace('.', '-')
            return f"CTRL-{safe_mac}-{safe_ip}"
        
        controller_type_str = self.controller_type.value.upper()
        safe_ip = self.ip_address.replace('.', '-')
        return f"{controller_type_str}-{safe_ip}"
    
    def _get_mac_address(self) -> Optional[str]:
        try:
            import socket
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Windows":
                try:
                    result = subprocess.run(
                        ['arp', '-a', self.ip_address],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if self.ip_address in line:
                                parts = line.split()
                                for part in parts:
                                    if ':' in part or '-' in part:
                                        return part.replace('-', ':')
                except (OSError, subprocess.SubprocessError, IndexError, AttributeError):
                    pass
            
            elif system in ["Linux", "Darwin"]:
                try:
                    result = subprocess.run(
                        ['arp', '-n', self.ip_address],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if self.ip_address in line:
                                parts = line.split()
                                for part in parts:
                                    if ':' in part or '-' in part:
                                        return part.replace('-', ':')
                except (OSError, subprocess.SubprocessError, IndexError, AttributeError):
                    pass
            
            try:
                import psutil
                interfaces = psutil.net_if_addrs()
                for interface_name, addresses in interfaces.items():
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            if addr.address:
                                for mac_addr in addresses:
                                    if mac_addr.family == psutil.AF_LINK:
                                        return mac_addr.address
            except ImportError:
                pass
            except (OSError, AttributeError, KeyError):
                pass
                
        except Exception:
            pass
        
        return None
    
    @abstractmethod
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        pass
    
    @abstractmethod
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def get_program_list(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass
    
    def is_connected(self) -> bool:
        return self.status == ConnectionStatus.CONNECTED
    
    def get_connection_status(self) -> ConnectionStatus:
        return self.status
    
    def upload_schedule(self, schedule_data: Dict) -> bool:
        if hasattr(self, 'upload_data'):
            return self.upload_data("schedule", schedule_data)
        return False
    
    def get_time(self) -> Optional[datetime]:
        return None
    
    def set_time(self, time: datetime) -> bool:
        return False
    
    def get_brightness(self) -> Optional[int]:
        return None
    
    def set_brightness(self, brightness: int) -> bool:
        return False
    
    def get_power_schedule(self) -> Optional[Dict]:
        return None
    
    def set_power_schedule(self, on_time: str, off_time: str, enabled: bool = True) -> bool:
        return False
    
    def get_network_config(self) -> Optional[Dict]:
        return None
    
    def set_network_config(self, network_config: Dict) -> bool:
        return False
    
    def delete_program(self, program_id: str) -> bool:
        return False
    
    def set_status(self, status: ConnectionStatus):
        self.status = status
        if self.on_status_changed:
            self.on_status_changed(status)
    
    def set_progress(self, progress: int, message: str = ""):
        if self.on_progress:
            self.on_progress(progress, message)

