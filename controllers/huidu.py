"""
Huidu controller protocol handler
"""
import json
from typing import Optional, Dict, List
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.network_manager import NetworkManager


class HuiduController(BaseController):
    """Huidu LED controller implementation"""
    
    DEFAULT_PORT = 5000
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.HUIDU, ip_address, port)
        self.network_manager = NetworkManager(timeout=5)
        self.socket = None
    
    def connect(self) -> bool:
        """Connect to Huidu controller"""
        if self.status == ConnectionStatus.CONNECTED:
            return True
        
        self.set_status(ConnectionStatus.CONNECTING)
        
        self.socket = self.network_manager.connect(self.ip_address, self.port)
        if self.socket:
            # Try to get device info to verify connection
            info = self.get_device_info()
            if info:
                self.set_status(ConnectionStatus.CONNECTED)
                return True
            else:
                self.network_manager.close_socket(self.socket)
                self.socket = None
                self.set_status(ConnectionStatus.ERROR)
                return False
        else:
            self.set_status(ConnectionStatus.ERROR)
            return False
    
    def disconnect(self):
        """Disconnect from controller"""
        if self.socket:
            self.network_manager.close_socket(self.socket)
            self.socket = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
    
    def get_device_info(self) -> Optional[Dict]:
        """Get controller device information"""
        if not self.socket:
            return None
        
        try:
            # Huidu protocol: Send device info request
            request = self._build_info_request()
            if not self.network_manager.send_data(self.socket, request):
                return None
            
            response = self.network_manager.receive_data(self.socket, 1024)
            if response:
                info = self._parse_info_response(response)
                if info:
                    self.device_info = info
                return info
        except Exception as e:
            print(f"Error getting device info: {e}")
        
        return None
    
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        """Upload program to Huidu controller"""
        if not self.socket or self.status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            self.set_progress(0, "Preparing program data...")
            
            # Convert program to Huidu format
            program_bytes = self._convert_program_to_bytes(program_data)
            
            self.set_progress(20, "Uploading program...")
            
            # Send upload command
            upload_cmd = self._build_upload_command(program_bytes)
            if not self.network_manager.send_data(self.socket, upload_cmd):
                return False
            
            self.set_progress(50, "Sending program data...")
            
            # Send program data in chunks
            chunk_size = 4096
            total_size = len(program_bytes)
            sent = 0
            
            for i in range(0, total_size, chunk_size):
                chunk = program_bytes[i:i+chunk_size]
                if not self.network_manager.send_data(self.socket, chunk):
                    return False
                sent += len(chunk)
                progress = 50 + int((sent / total_size) * 40)
                self.set_progress(progress, f"Uploading... {sent}/{total_size} bytes")
            
            self.set_progress(90, "Finalizing...")
            
            # Wait for confirmation
            response = self.network_manager.receive_data(self.socket, 1024, timeout=10)
            if response and self._parse_upload_response(response):
                self.set_progress(100, "Upload complete")
                return True
            
            return False
        except Exception as e:
            print(f"Error uploading program: {e}")
            return False
    
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        """Download program from Huidu controller"""
        if not self.socket or self.status != ConnectionStatus.CONNECTED:
            return None
        
        try:
            self.set_progress(0, "Requesting program...")
            
            request = self._build_download_request(program_id)
            if not self.network_manager.send_data(self.socket, request):
                return None
            
            self.set_progress(20, "Receiving program data...")
            
            data = b''
            while True:
                chunk = self.network_manager.receive_data(self.socket, 4096, timeout=5)
                if not chunk:
                    break
                data += chunk
                self.set_progress(20 + int((len(data) / 100000) * 60), "Downloading...")
            
            if data:
                program = self._parse_program_data(data)
                self.set_progress(100, "Download complete")
                return program
            
            return None
        except Exception as e:
            print(f"Error downloading program: {e}")
            return None
    
    def get_program_list(self) -> List[Dict]:
        """Get list of programs on controller"""
        if not self.socket or self.status != ConnectionStatus.CONNECTED:
            return []
        
        try:
            request = self._build_list_request()
            if not self.network_manager.send_data(self.socket, request):
                return []
            
            response = self.network_manager.receive_data(self.socket, 4096)
            if response:
                return self._parse_list_response(response)
        except Exception as e:
            print(f"Error getting program list: {e}")
        
        return []
    
    def test_connection(self) -> bool:
        """Test connection to controller"""
        return self.network_manager.ping(self.ip_address, self.port, timeout=2)
    
    # Protocol-specific methods (simplified - actual implementation would need protocol docs)
    
    def _build_info_request(self) -> bytes:
        """Build device info request packet"""
        # Simplified - actual protocol would have specific packet structure
        return b'\x01\x00\x00\x00'  # Example packet
    
    def _parse_info_response(self, data: bytes) -> Optional[Dict]:
        """Parse device info response"""
        # Simplified - actual implementation would parse protocol response
        # For license system, controller_id should be extracted from device info
        # Format: "HD-M30-00123456" or similar
        controller_id = f"HD-{self.ip_address.replace('.', '-')}"  # Placeholder - should come from device
        return {
            "name": "Huidu Controller",
            "model": "Unknown",
            "version": "1.0",
            "ip": self.ip_address,
            "controller_id": controller_id,  # For license system
            "controllerId": controller_id,  # Alternative field name
            "serial_number": controller_id  # Alternative field name
        }
    
    def _build_upload_command(self, program_data: bytes) -> bytes:
        """Build upload command packet"""
        header = b'\x02\x00\x00\x00'  # Upload command
        size = NetworkManager.pack_uint32(len(program_data))
        return header + size
    
    def _build_download_request(self, program_id: str = None) -> bytes:
        """Build download request packet"""
        return b'\x03\x00\x00\x00'  # Download command
    
    def _build_list_request(self) -> bytes:
        """Build program list request"""
        return b'\x04\x00\x00\x00'  # List command
    
    def _parse_list_response(self, data: bytes) -> List[Dict]:
        """Parse program list response"""
        return []
    
    def _parse_upload_response(self, data: bytes) -> bool:
        """Parse upload response"""
        return len(data) > 0
    
    def _convert_program_to_bytes(self, program_data: Dict) -> bytes:
        """Convert program data to controller format"""
        json_str = json.dumps(program_data, ensure_ascii=False)
        return json_str.encode('utf-8')
    
    def _parse_program_data(self, data: bytes) -> Optional[Dict]:
        """Parse program data from controller"""
        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except:
            return None

