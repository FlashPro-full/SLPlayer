"""
Background network operations to prevent UI blocking
"""
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional
from controllers.network_manager import NetworkManager
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkConnectThread(QThread):
    """Thread for network connection operations"""
    finished = pyqtSignal(bool, object, object)  # success, socket, error
    progress = pyqtSignal(str)
    
    def __init__(self, network_manager: NetworkManager, ip_address: str, port: int):
        super().__init__()
        self.network_manager = network_manager
        self.ip_address = ip_address
        self.port = port
    
    def run(self):
        try:
            self.progress.emit(f"Connecting to {self.ip_address}:{self.port}...")
            sock = self.network_manager.connect(self.ip_address, self.port)
            if sock:
                self.progress.emit("Connected successfully")
                self.finished.emit(True, sock, None)
            else:
                self.progress.emit("Connection failed")
                self.finished.emit(False, None, Exception("Connection failed"))
        except Exception as e:
            logger.error(f"Error in network connect thread: {e}", exc_info=True)
            self.finished.emit(False, None, e)


class NetworkPingThread(QThread):
    """Thread for network ping operations"""
    finished = pyqtSignal(bool, str, int)  # success, ip_address, port
    
    def __init__(self, network_manager: NetworkManager, ip_address: str, port: int, timeout: int = 2):
        super().__init__()
        self.network_manager = network_manager
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
    
    def run(self):
        try:
            result = self.network_manager.ping(self.ip_address, self.port, self.timeout)
            self.finished.emit(result, self.ip_address, self.port)
        except Exception as e:
            logger.error(f"Error in network ping thread: {e}", exc_info=True)
            self.finished.emit(False, self.ip_address, self.port)


class NetworkSendThread(QThread):
    """Thread for sending data over network"""
    finished = pyqtSignal(bool, object)  # success, error
    progress = pyqtSignal(str)
    
    def __init__(self, network_manager: NetworkManager, sock, data: bytes):
        super().__init__()
        self.network_manager = network_manager
        self.sock = sock
        self.data = data
    
    def run(self):
        try:
            self.progress.emit("Sending data...")
            result = self.network_manager.send_data(self.sock, self.data)
            if result:
                self.progress.emit("Data sent successfully")
            else:
                self.progress.emit("Failed to send data")
            self.finished.emit(result, None)
        except Exception as e:
            logger.error(f"Error in network send thread: {e}", exc_info=True)
            self.finished.emit(False, e)

