"""
Network communication manager for controllers
"""
import socket
import struct
import time
from typing import Optional, Tuple, bytes
from threading import Lock


class NetworkManager:
    """Manages TCP/IP network communication with controllers"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.socket_lock = Lock()
    
    def create_socket(self) -> Optional[socket.socket]:
        """Create a new TCP socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            return sock
        except Exception as e:
            print(f"Error creating socket: {e}")
            return None
    
    def connect(self, ip_address: str, port: int) -> Optional[socket.socket]:
        """Connect to remote host"""
        sock = self.create_socket()
        if not sock:
            return None
        
        try:
            sock.connect((ip_address, port))
            return sock
        except socket.timeout:
            print(f"Connection timeout to {ip_address}:{port}")
            sock.close()
            return None
        except Exception as e:
            print(f"Connection error to {ip_address}:{port}: {e}")
            sock.close()
            return None
    
    def send_data(self, sock: socket.socket, data: bytes) -> bool:
        """Send data over socket"""
        if not sock:
            return False
        
        try:
            with self.socket_lock:
                sock.sendall(data)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive_data(self, sock: socket.socket, size: int = 4096, timeout: float = None) -> Optional[bytes]:
        """Receive data from socket"""
        if not sock:
            return None
        
        try:
            if timeout:
                sock.settimeout(timeout)
            with self.socket_lock:
                data = sock.recv(size)
            return data if data else None
        except socket.timeout:
            print("Receive timeout")
            return None
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None
    
    def close_socket(self, sock: socket.socket):
        """Close socket"""
        if sock:
            try:
                sock.close()
            except:
                pass
    
    def ping(self, ip_address: str, port: int, timeout: int = 2) -> bool:
        """Ping controller to check if it's reachable"""
        sock = self.create_socket()
        if not sock:
            return False
        
        try:
            sock.settimeout(timeout)
            sock.connect((ip_address, port))
            sock.close()
            return True
        except:
            if sock:
                sock.close()
            return False
    
    @staticmethod
    def pack_uint16(value: int) -> bytes:
        """Pack unsigned 16-bit integer (little-endian)"""
        return struct.pack('<H', value)
    
    @staticmethod
    def pack_uint32(value: int) -> bytes:
        """Pack unsigned 32-bit integer (little-endian)"""
        return struct.pack('<I', value)
    
    @staticmethod
    def unpack_uint16(data: bytes) -> int:
        """Unpack unsigned 16-bit integer (little-endian)"""
        return struct.unpack('<H', data)[0]
    
    @staticmethod
    def unpack_uint32(data: bytes) -> int:
        """Unpack unsigned 32-bit integer (little-endian)"""
        return struct.unpack('<I', data)[0]

