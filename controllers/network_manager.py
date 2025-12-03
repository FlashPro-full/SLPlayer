import socket
import struct
import time
import subprocess
import platform
import re
from typing import Optional, Tuple, List
from threading import Lock
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkManager:
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.socket_lock = Lock()
    
    def create_socket(self) -> Optional[socket.socket]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            return sock
        except Exception as e:
            logger.error(f"Error creating socket: {e}")
            return None
    
    def connect(self, ip_address: str, port: int) -> Optional[socket.socket]:
        sock = self.create_socket()
        if not sock:
            return None
        
        try:
            sock.connect((ip_address, port))
            return sock
        except socket.timeout:
            logger.debug(f"Connection timeout to {ip_address}:{port}")
            sock.close()
            return None
        except Exception as e:
            logger.debug(f"Connection error to {ip_address}:{port}: {e}")
            sock.close()
            return None
    
    def send_data(self, sock: socket.socket, data: bytes) -> bool:
        if not sock:
            return False
        
        try:
            with self.socket_lock:
                sock.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            return False
    
    def receive_data(self, sock: socket.socket, size: int = 4096, timeout: float = None) -> Optional[bytes]:
        if not sock:
            return None
        
        try:
            if timeout:
                sock.settimeout(timeout)
            with self.socket_lock:
                data = sock.recv(size)
            return data if data else None
        except socket.timeout:
            logger.debug("Receive timeout")
            return None
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return None
    
    def close_socket(self, sock: socket.socket):
        if sock:
            try:
                sock.close()
            except (OSError, AttributeError):
                pass
    
    def ping(self, ip_address: str, port: int, timeout: int = 2) -> bool:
        sock = self.create_socket()
        if not sock:
            return False
        
        try:
            sock.settimeout(timeout)
            sock.connect((ip_address, port))
            sock.close()
            return True
        except (OSError, ConnectionError, TimeoutError):
            if sock:
                try:
                    sock.close()
                except (OSError, AttributeError):
                    pass
            return False
    
    @staticmethod
    def pack_uint16(value: int) -> bytes:
        return struct.pack('<H', value)
    
    @staticmethod
    def pack_uint32(value: int) -> bytes:
        return struct.pack('<I', value)
    
    @staticmethod
    def unpack_uint16(data: bytes) -> int:
        return struct.unpack('<H', data)[0]
    
    @staticmethod
    def unpack_uint32(data: bytes) -> int:
        return struct.unpack('<I', data)[0]
    
    def ping_host(self, ip_address: str, count: int = 1) -> bool:
        try:
            if platform.system().lower() == "windows":
                # Windows ping command
                result = subprocess.run(
                    ["ping", ip_address, "-n", str(count)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                # Check if the ping was successful (Response received)
                if "TTL=" in result.stdout or "TTL=" in result.stderr:
                    logger.info(f"Connection to {ip_address} is successful (ping).")
                    return True
                else:
                    logger.debug(f"Connection to {ip_address} failed (ping).")
                    return False
            else:
                # Linux/Mac ping command
                result = subprocess.run(
                    ["ping", "-c", str(count), ip_address],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                # Check if the ping was successful
                if result.returncode == 0:
                    logger.info(f"Connection to {ip_address} is successful (ping).")
                    return True
                else:
                    logger.debug(f"Connection to {ip_address} failed (ping).")
                    return False
        except subprocess.TimeoutExpired:
            logger.debug(f"Ping timeout for {ip_address}")
            return False
        except subprocess.CalledProcessError as e:
            logger.debug(f"Error occurred while pinging {ip_address}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while pinging {ip_address}: {e}")
            return False
    
    def test_port_connection(self, ip_address: str, port: int, timeout: float = 5.0) -> bool:
        try:
            # Create a socket object
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set a timeout for the connection attempt
                s.settimeout(timeout)
                
                # Try to connect to the given IP address and port
                s.connect((ip_address, port))
                logger.info(f"Successfully connected to {ip_address}:{port}")
                return True
        except socket.timeout:
            logger.debug(f"Connection to {ip_address}:{port} timed out.")
            return False
        except (socket.error, OSError) as e:
            logger.debug(f"Connection to {ip_address}:{port} failed. Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing port {ip_address}:{port}: {e}")
            return False
    
    def test_connection(self, ip_address: str, port: Optional[int] = None) -> Tuple[bool, bool, bool]:
        ping_success = self.ping_host(ip_address)
        port_success = True  # Default to True if port not provided
        
        if port is not None:
            port_success = self.test_port_connection(ip_address, port)
        
        overall_success = ping_success and port_success
        
        return (ping_success, port_success, overall_success)
    
    @staticmethod
    def get_connected_wifi_devices() -> List[dict]:
        devices = []
        try:
            if platform.system().lower() == "windows":
                # Windows: Use arp -a command
                result = subprocess.run(
                    ["arp", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parse ARP table output
                # Format: " 192.168.1.1   00-11-22-33-44-55     dynamic"
                pattern = r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(dynamic|static)'
                for line in result.stdout.split('\n'):
                    match = re.search(pattern, line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2)
                        devices.append({"ip": ip, "mac": mac})
            else:
                # Linux/Mac: Use arp -n command
                result = subprocess.run(
                    ["arp", "-n"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parse ARP table output
                pattern = r'(\d+\.\d+\.\d+\.\d+)\s+\S+\s+([0-9a-fA-F:]+)'
                for line in result.stdout.split('\n'):
                    match = re.search(pattern, line)
                    if match:
                        ip = match.group(1)
                        mac = match.group(2)
                        devices.append({"ip": ip, "mac": mac})
        except Exception as e:
            logger.error(f"Error getting connected Wi-Fi devices: {e}")
        
        return devices
    
    @staticmethod
    def get_local_network_ip_range() -> List[str]:
        try:
            import platform
            all_ranges = []
            
            if platform.system().lower() == "windows":
                import subprocess
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'IPv4' in line or 'IP Address' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip_str = parts[-1].strip()
                            if ip_str and not ip_str.startswith('('):
                                try:
                                    ip_parts = ip_str.split('.')
                                    if len(ip_parts) == 4 and all(0 <= int(p) <= 255 for p in ip_parts):
                                        network_prefix = '.'.join(ip_parts[:3])
                                        ip_range = [f"{network_prefix}.{i}" for i in range(1, 255)]
                                        if ip_range not in all_ranges:
                                            all_ranges.append(ip_range)
                                except (ValueError, IndexError):
                                    continue
            else:
                try:
                    import netifaces
                    interfaces = netifaces.interfaces()
                    for interface in interfaces:
                        try:
                            addrs = netifaces.ifaddresses(interface)
                            if netifaces.AF_INET in addrs:
                                for addr_info in addrs[netifaces.AF_INET]:
                                    ip = addr_info.get('addr')
                                    if ip and not ip.startswith('127.'):
                                        ip_parts = ip.split('.')
                                        if len(ip_parts) == 4:
                                            network_prefix = '.'.join(ip_parts[:3])
                                            ip_range = [f"{network_prefix}.{i}" for i in range(1, 255)]
                                            if ip_range not in all_ranges:
                                                all_ranges.append(ip_range)
                        except Exception:
                            continue
                except ImportError:
                    pass
            
            if not all_ranges:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                ip_parts = local_ip.split('.')
                if len(ip_parts) == 4:
                    network_prefix = '.'.join(ip_parts[:3])
                    all_ranges.append([f"{network_prefix}.{i}" for i in range(1, 255)])
            
            if all_ranges:
                combined_range = []
                for ip_range in all_ranges:
                    combined_range.extend(ip_range)
                logger.info(f"Found {len(all_ranges)} network interface(s), total {len(combined_range)} IPs")
                return combined_range
            
            return []
        except Exception as e:
            logger.error(f"Error getting local network IP range: {e}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                ip_parts = local_ip.split('.')
                if len(ip_parts) == 4:
                    network_prefix = '.'.join(ip_parts[:3])
                    return [f"{network_prefix}.{i}" for i in range(1, 255)]
            except Exception:
                pass
            return []
    
    def find_controller_ip(self, controller_type: Optional[str] = None) -> Optional[str]:
        logger.info("Searching for controller IP address on Wi-Fi network...")
        
        # Get connected devices from ARP table
        devices = self.get_connected_wifi_devices()
        logger.info(f"Found {len(devices)} devices in ARP table")
        
        # Common controller ports to test
        controller_ports = {
            "huidu": [30080],  # Huidu SDK uses port 30080 for HTTP API (from cn.huidu.device.sdk-master documentation)
            "novastar": [5200],  # NovaStar SDK returns tcpPort in response (defaults to 5200 when missing)
            None: [30080, 5200]  # All ports if type not specified (Huidu: 30080, NovaStar: 5200)
        }
        
        ports_to_test = controller_ports.get(controller_type, controller_ports[None])
        
        # Test each device
        for device in devices:
            ip = device.get("ip", "")
            if not ip:
                continue
            
            # Skip common non-controller IPs
            if ip.endswith(".1"):  # Usually router
                continue
            
            logger.debug(f"Testing device {ip}...")
            
            # Test ping first (quick check)
            if not self.ping_host(ip, count=1):
                continue
            
            # Test controller ports
            for port in ports_to_test:
                if self.test_port_connection(ip, port, timeout=2.0):
                    logger.info(f"Found controller at {ip}:{port}")
                    return ip
        
        logger.info("No controller IP found on Wi-Fi network")
        return None

