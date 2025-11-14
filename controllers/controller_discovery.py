"""
Controller discovery for auto-detecting controllers on network
"""
import socket
import threading
from typing import List, Dict, Optional
from controllers.base_controller import BaseController
from controllers.novastar import NovaStarController
from controllers.huidu import HuiduController


class ControllerDiscovery:
    """Discovers controllers on the network"""
    
    def __init__(self):
        self.discovered_controllers: List[Dict] = []
        self.scanning = False
    
    def scan_network(self, ip_range: str = "192.168.1", timeout: float = 1.0) -> List[Dict]:
        """Scan network for controllers"""
        self.discovered_controllers = []
        self.scanning = True
        
        # Default ports for controllers
        ports = [5200, 5201, 5000]  # NovaStar: 5200/5201, Huidu: 5000
        
        def scan_ip(ip: str):
            """Scan a single IP address"""
            for port in ports:
                if not self.scanning:
                    break
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        # Port is open, try to identify controller type
                        controller_type = self.identify_controller(ip, port)
                        if controller_type:
                            self.discovered_controllers.append({
                                "ip": ip,
                                "port": port,
                                "type": controller_type,
                                "name": f"{controller_type} Controller"
                            })
                except:
                    pass
        
        # Scan IP range (e.g., 192.168.1.1 to 192.168.1.254)
        threads = []
        for i in range(1, 255):
            if not self.scanning:
                break
            ip = f"{ip_range}.{i}"
            thread = threading.Thread(target=scan_ip, args=(ip,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=timeout * 2)
        
        self.scanning = False
        return self.discovered_controllers
    
    def identify_controller(self, ip: str, port: int) -> Optional[str]:
        """Identify controller type by port"""
        if port in [5200, 5201]:
            return "NovaStar"
        elif port == 5000:
            return "Huidu"
        return None
    
    def stop_scan(self):
        """Stop network scan"""
        self.scanning = False
    
    def get_discovered_controllers(self) -> List[Dict]:
        """Get list of discovered controllers"""
        return self.discovered_controllers


