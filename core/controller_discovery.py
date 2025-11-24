"""
Controller auto-discovery module for finding LED display controllers on the network
"""
import socket
import threading
import time
from typing import List, Dict, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)


class ControllerInfo:
    """Information about a discovered controller"""
    
    def __init__(self, ip: str, port: int, controller_type: str = "unknown", name: str = ""):
        self.ip = ip
        self.port = port
        self.controller_type = controller_type  # "novastar", "huidu", "unknown"
        self.name = name or f"{controller_type}_{ip}"
        self.mac_address = ""
        self.firmware_version = ""
        self.display_resolution = ""
        self.last_seen = time.time()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "ip": self.ip,
            "port": self.port,
            "controller_type": self.controller_type,
            "name": self.name,
            "mac_address": self.mac_address,
            "firmware_version": self.firmware_version,
            "display_resolution": self.display_resolution
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ControllerInfo':
        """Create from dictionary"""
        info = cls(data.get("ip", ""), data.get("port", 5200), 
                  data.get("controller_type", "unknown"), data.get("name", ""))
        info.mac_address = data.get("mac_address", "")
        info.firmware_version = data.get("firmware_version", "")
        info.display_resolution = data.get("display_resolution", "")
        return info


class ControllerDiscovery(QObject):
    """Auto-discovery service for LED display controllers"""
    
    controller_found = pyqtSignal(object)  # Emits ControllerInfo
    discovery_finished = pyqtSignal()
    
    # Common controller ports
    NOVASTAR_PORTS = [5200, 5201, 5202]
    HUIDU_PORTS = [5000, 5001, 8080]
    COMMON_PORTS = NOVASTAR_PORTS + HUIDU_PORTS
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.discovered_controllers: List[ControllerInfo] = []
        self.is_scanning = False
        self.scan_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
    
    def get_local_network_range(self) -> List[str]:
        """Get local network IP range"""
        try:
            # Get local IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Extract network prefix (assumes /24 subnet)
            ip_parts = local_ip.split('.')
            if len(ip_parts) == 4:
                network_prefix = '.'.join(ip_parts[:3])
                return [f"{network_prefix}.{i}" for i in range(1, 255)]
            
            return []
        except Exception as e:
            logger.exception(f"Error getting local network range: {e}")
            return []
    
    def scan_port(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        """Check if a port is open on an IP address"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def identify_controller_type(self, ip: str, port: int) -> str:
        """Try to identify controller type by port and response"""
        # NovaStar controllers typically use ports 5200-5202
        if port in self.NOVASTAR_PORTS:
            # Try to connect and check response
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect((ip, port))
                # Could send identification packet here
                sock.close()
                return "novastar"
            except (OSError, ConnectionError, TimeoutError):
                pass
        
        # Huidu controllers typically use port 5000 or 8080
        if port in self.HUIDU_PORTS:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect((ip, port))
                sock.close()
                return "huidu"
            except (OSError, ConnectionError, TimeoutError):
                pass
        
        return "unknown"
    
    def scan_ip(self, ip: str):
        """Scan a single IP address for controllers"""
        if self.stop_event.is_set():
            return
        
        for port in self.COMMON_PORTS:
            if self.stop_event.is_set():
                return
            
            if self.scan_port(ip, port, timeout=0.3):
                controller_type = self.identify_controller_type(ip, port)
                controller_info = ControllerInfo(ip, port, controller_type)
                
                # Check if we already found this controller
                existing = next((c for c in self.discovered_controllers 
                               if c.ip == ip and c.port == port), None)
                if not existing:
                    self.discovered_controllers.append(controller_info)
                    logger.info(f"Found controller: {ip}:{port} ({controller_type})")
                    self.controller_found.emit(controller_info)
    
    def start_scan(self, ip_range: Optional[List[str]] = None):
        """Start scanning for controllers"""
        if self.is_scanning:
            logger.warning("Discovery scan already in progress")
            return
        
        self.is_scanning = True
        self.stop_event.clear()
        self.discovered_controllers.clear()
        
        if ip_range is None:
            ip_range = self.get_local_network_range()
        
        def scan_thread():
            try:
                logger.info(f"Starting controller discovery scan ({len(ip_range)} IPs)")
                for ip in ip_range:
                    if self.stop_event.is_set():
                        break
                    self.scan_ip(ip)
                
                logger.info(f"Discovery scan finished. Found {len(self.discovered_controllers)} controllers")
            except Exception as e:
                logger.exception(f"Error during discovery scan: {e}")
            finally:
                self.is_scanning = False
                self.discovery_finished.emit()
        
        self.scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self.scan_thread.start()
    
    def stop_scan(self):
        """Stop the current scan"""
        if self.is_scanning:
            self.stop_event.set()
            logger.info("Stopping controller discovery scan")
    
    def get_discovered_controllers(self) -> List[ControllerInfo]:
        """Get list of discovered controllers"""
        return self.discovered_controllers.copy()
    
    def scan_single_ip(self, ip: str, callback: Optional[Callable] = None):
        """Scan a single IP address (for manual entry)"""
        def scan():
            self.scan_ip(ip)
            if callback:
                callback()
        
        thread = threading.Thread(target=scan, daemon=True)
        thread.start()

