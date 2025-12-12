from typing import Optional, Dict, List
from pathlib import Path
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.huidu_sdk import HuiduSDK, DEFAULT_HOST, SDK_AVAILABLE
from controllers.network_manager import NetworkManager
from controllers.property_adapter import adapt_element_for_controller
from utils.logger import get_logger

logger = get_logger(__name__)

class HuiduController(BaseController):
    DEFAULT_PORT = 30080
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.HUIDU, ip_address, port)
        self._device_id: Optional[str] = None
        self.sdk: Optional[HuiduSDK] = None
        self.network_manager = NetworkManager()
        self._screen_created = False
        self._current_program_id: Optional[int] = None
        self._current_area_id: Optional[int] = None
    
    def _find_device_id_by_ip(self) -> Optional[str]:
        if not SDK_AVAILABLE or not self.sdk or not self.sdk.device:
            return None
        
        try:
            result = self.sdk.device.get_online_devices()
            if result.get("message") != "ok":
                return None
            
            devices = result.get("data", [])
            if not devices:
                return None
            
            ip_clean = self.ip_address.split(':')[0].strip()
            
            for device_id in devices:
                if isinstance(device_id, str):
                    if ip_clean == "127.0.0.1" or ip_clean == "localhost":
                        return device_id
                    property_result = self.sdk.get_device_property([device_id])
                    if property_result.get("message") == "ok":
                        data_array = property_result.get("data", [])
                        if data_array and len(data_array) > 0:
                            device_data = data_array[0].get("data", {})
                            device_ip = device_data.get("eth.ip")
                            if device_ip == ip_clean:
                                return device_id
                elif isinstance(device_id, dict):
                    if device_id.get("ip") == ip_clean or device_id.get("ip_address") == ip_clean:
                        return device_id.get("id", device_id.get("controller_id", ""))
            
            if ip_clean == "127.0.0.1" or ip_clean == "localhost":
                if devices and isinstance(devices[0], str):
                    return devices[0]
            
            return None
        except Exception as e:
            logger.error(f"Error finding device ID: {e}")
            return None
    
    def connect(self) -> bool:
        if self.status == ConnectionStatus.CONNECTED:
            return True
        
        self.set_status(ConnectionStatus.CONNECTING)
        
        try:
            if not SDK_AVAILABLE:
                logger.error("Huidu SDK is not available")
                self.set_status(ConnectionStatus.ERROR)
                return False
            
            host = DEFAULT_HOST
            self.sdk = HuiduSDK(host)
            
            self._device_id = self._find_device_id_by_ip()
            if not self._device_id:
                logger.warning(f"Could not find device ID for IP {self.ip_address}")
                self.set_status(ConnectionStatus.ERROR)
                return False
            
            info = self.get_device_info()
            if info and info.get("controller_id"):
                self.set_status(ConnectionStatus.CONNECTED)
                logger.info(f"Connected to Huidu controller {self._device_id} at {self.ip_address}")
                return True
            else:
                logger.warning(f"Failed to get device info for Huidu controller at {self.ip_address}")
                self.set_status(ConnectionStatus.ERROR)
                return False
        except Exception as e:
            logger.error(f"Error connecting to Huidu controller: {e}", exc_info=True)
            self.set_status(ConnectionStatus.ERROR)
            return False
    
    def disconnect(self):
        self._device_id = None
        self.sdk = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
        logger.info(f"Disconnected from Huidu controller at {self.ip_address}")
    
    def get_device_info(self) -> Optional[Dict]:
        if not self.sdk or not self._device_id:
            return None
        
        try:
            property_result = self.sdk.get_device_property([self._device_id])
            if property_result.get("message") != "ok":
                return None
            
            data_array = property_result.get("data", [])
            if not data_array or len(data_array) == 0:
                return None
            
            device_data = data_array[0].get("data", {})
            if not device_data:
                return None
            
            import re
            ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
            
            device_ip = device_data.get("eth.ip")
            if not device_ip or not ip_pattern.match(device_ip) or device_ip == "127.0.0.1":
                device_ip = self.ip_address
            
            device_name = device_data.get("name", f"Huidu_{self._device_id}")
            screen_width = device_data.get("screen.width", "64")
            screen_height = device_data.get("screen.height", "32")
            firmware_version = device_data.get("version.app", "")
            hardware_version = device_data.get("version.hardware", "")
            model = hardware_version or device_data.get("model", "Huidu")
            
            self.device_info = {
                "controller_id": self._device_id,
                "controllerId": self._device_id,
                "id": self._device_id,
                "ip": device_ip,
                "port": self.port,
                "name": device_name,
                "device_name": device_name,
                "display_name": device_name,
                "model": model,
                "firmware_version": firmware_version,
                "version": firmware_version,
                "version.app": firmware_version,
                "version.hardware": hardware_version,
                "screen.width": screen_width,
                "screen.height": screen_height,
                "display_resolution": f"{screen_width}x{screen_height}",
                "mac_address": self._device_id,
                "serial_number": self._device_id,
                "connection_status": {
                    "ping": True,
                    "port": True,
                    "sdk_online": True
                }
            }
            
            return self.device_info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
            return None
    
    def test_connection(self) -> bool:
        if not self.sdk or not self._device_id or not self.sdk.device:
            return False
        
        try:
            result = self.sdk.device.get_online_devices()
            if result.get("message") == "ok":
                devices = result.get("data", [])
                return self._device_id in devices if self._device_id else False
            return False
        except Exception:
            return False
    
    def upload_program(self, program_data: Dict, file_path: Optional[str] = None) -> bool:
        if self.status != ConnectionStatus.CONNECTED:
            if not self.connect():
                return False
        
        if not self.sdk or not self._device_id:
            logger.error("SDK not initialized or device ID not found")
            return False
        
        try:
            from controllers.huidu_sdk import ProgramNode, AreaNode
            from controllers.huidu_sdk import TextNode, ImageNode, VideoNode
            from controllers.huidu_sdk import DigitalClockNode, DialClockNode, DynamicNode
            
            elements = program_data.get("elements", [])
            if not elements:
                logger.warning("No elements to upload")
                return False
            
            content_nodes = []
            for element in elements:
                adapted_element = adapt_element_for_controller(element, "huidu")
                element_type = adapted_element.get("type")
                properties = adapted_element.get("properties", {})
                
                x = int(adapted_element.get("x", 0))
                y = int(adapted_element.get("y", 0))
                width = int(adapted_element.get("width", 200))
                height = int(adapted_element.get("height", 100))
                
                if element_type == "text" or element_type == "singleline_text":
                    text_node = TextNode(properties.get("text", ""))
                    text_node.x = x
                    text_node.y = y
                    text_node.width = width
                    text_node.height = height
                    if properties.get("color"):
                        text_node.color = properties.get("color")
                    if properties.get("font_family"):
                        text_node.font_family = properties.get("font_family")
                    if properties.get("font_size"):
                        text_node.font_size = int(properties.get("font_size", 24))
                    content_nodes.append(text_node)
                
                elif element_type == "photo" or element_type == "image":
                    image_path = properties.get("file_path", "")
                    if image_path:
                        image_node = ImageNode(image_path)
                        image_node.x = x
                        image_node.y = y
                        image_node.width = width
                        image_node.height = height
                        content_nodes.append(image_node)
                
                elif element_type == "video":
                    video_path = properties.get("file_path", "")
                    if video_path:
                        video_node = VideoNode(video_path)
                        video_node.x = x
                        video_node.y = y
                        video_node.width = width
                        video_node.height = height
                        content_nodes.append(video_node)
                
                elif element_type == "clock" or element_type == "digital_clock":
                    clock_node = DigitalClockNode()
                    clock_node.x = x
                    clock_node.y = y
                    clock_node.width = width
                    clock_node.height = height
                    content_nodes.append(clock_node)
                
                elif element_type == "dial_clock":
                    clock_node = DialClockNode()
                    clock_node.x = x
                    clock_node.y = y
                    clock_node.width = width
                    clock_node.height = height
                    content_nodes.append(clock_node)
                
                elif element_type == "animation" or element_type == "dynamic":
                    dynamic_node = DynamicNode()
                    dynamic_node.x = x
                    dynamic_node.y = y
                    dynamic_node.width = width
                    dynamic_node.height = height
                    content_nodes.append(dynamic_node)
            
            if not content_nodes:
                logger.warning("No valid content nodes created")
                return False
            
            area_node = AreaNode(content_nodes)
            program_node = ProgramNode([area_node])
            
            self.set_progress(50, "Uploading program...")
            if not self.sdk.program:
                logger.error("SDK program interface not available")
                return False
            
            result = self.sdk.program.replace([self._device_id], program_node)
            
            if result.get("message") == "ok":
                self.set_progress(100, "Upload complete")
                logger.info(f"Program '{program_data.get('name')}' uploaded successfully")
                return True
            else:
                logger.error(f"Upload failed: {result}")
                return False
        except Exception as e:
            logger.error(f"Error uploading program: {e}", exc_info=True)
            return False
    
    def download_program(self, program_id: Optional[str] = None) -> Optional[Dict]:
        if not self.sdk or not self._device_id:
            return None
        
        try:
            result = self.sdk.get_programs([self._device_id])
            if result.get("message") != "ok":
                return None
            
            data_array = result.get("data", [])
            if not data_array:
                return None
            
            programs = []
            for item in data_array:
                if isinstance(item, dict):
                    prog_id = item.get("id") or item.get("program_id")
                    program_name = item.get("name") or f"Program_{prog_id}"
                    programs.append({
                        "id": prog_id,
                        "name": program_name,
                        "data": item
                    })
            
            selected_program = None
            if programs and program_id:
                for prog in programs:
                    if str(prog.get("id")) == str(program_id):
                        selected_program = prog
                        break
            
            if not selected_program and programs:
                selected_program = programs[0]
            
            if selected_program:
                program_data = selected_program.get("data", {})
                if program_data:
                    from core.program_converter import ProgramConverter
                    from controllers.huidu_sdk import ProgramNode
                    
                    if isinstance(program_data, ProgramNode):
                        sdk_dict = program_data.to_dict() if hasattr(program_data, 'to_dict') else {}
                    elif isinstance(program_data, dict):
                        sdk_dict = program_data
                    else:
                        sdk_dict = {}
                    
                    if sdk_dict:
                        converted = ProgramConverter.sdk_to_soo(sdk_dict, "huidu")
                        converted["id"] = selected_program.get("id")
                        return converted
                else:
                    return {
                        "id": selected_program.get("id"),
                        "name": selected_program.get("name"),
                        "elements": [],
                        "properties": {},
                        "play_mode": {"mode": "play_times", "play_times": 1, "fixed_length": "0:00:30"},
                        "play_control": {
                            "specified_time": {"enabled": False, "time": ""},
                            "specify_week": {"enabled": False, "days": []},
                            "specify_date": {"enabled": False, "date": ""}
                        }
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error downloading program: {e}", exc_info=True)
            return None
    
    def get_program_list(self) -> List[Dict]:
        if not self.sdk or not self._device_id:
            return []
        
        try:
            result = self.sdk.get_programs([self._device_id])
            if result.get("message") != "ok":
                return []
            
            data_array = result.get("data", [])
            if not data_array:
                return []
            
            programs = []
            for item in data_array:
                if isinstance(item, dict):
                    program_id = item.get("id") or item.get("program_id")
                    program_name = item.get("name") or f"Program_{program_id}"
                    programs.append({
                        "id": program_id,
                        "name": program_name,
                        "program_id": program_id
                    })
            
            return programs
        except Exception as e:
            logger.error(f"Error getting program list: {e}", exc_info=True)
            return []
    
    def delete_program(self, program_id: str) -> bool:
        if not self.sdk or not self._device_id or not self.sdk.program:
            return False
        
        try:
            result = self.sdk.program.remove([self._device_id], [program_id])
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error deleting program: {e}", exc_info=True)
            return False
    
    def get_brightness(self) -> Optional[int]:
        if not self.sdk or not self._device_id:
            return None
        
        try:
            property_result = self.sdk.get_device_property([self._device_id])
            if property_result.get("message") == "ok":
                data_array = property_result.get("data", [])
                if data_array and len(data_array) > 0:
                    device_data = data_array[0].get("data", {})
                    luminance = device_data.get("luminance", "100")
                    return int(luminance)
            return None
        except Exception as e:
            logger.error(f"Error getting brightness: {e}")
            return None
    
    def set_brightness(self, brightness: int, brightness_settings: Optional[Dict] = None) -> bool:
        if not self.sdk or not self._device_id or not self.sdk.device:
            return False
        
        try:
            result = self.sdk.device.set_device_property([self._device_id], "luminance", str(brightness))
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error setting brightness: {e}", exc_info=True)
            return False
    
    def get_network_config(self) -> Optional[Dict]:
        if not self.sdk or not self._device_id:
            return None
        
        try:
            property_result = self.sdk.get_device_property([self._device_id])
            if property_result.get("message") == "ok":
                data_array = property_result.get("data", [])
                if data_array and len(data_array) > 0:
                    device_data = data_array[0].get("data", {})
                    
                    network_config = {
                        "eth": {
                            "ip": device_data.get("eth.ip", ""),
                            "dhcp": device_data.get("eth.dhcp", "false") == "true"
                        },
                        "wifi": {
                            "enabled": device_data.get("wifi.enabled", "false") == "true",
                            "mode": device_data.get("wifi.mode", ""),
                            "ssid": device_data.get("wifi.ap.ssid", ""),
                            "password": device_data.get("wifi.ap.passwd", "")
                        }
                    }
                    
                    return network_config
            return None
        except Exception as e:
            logger.error(f"Error getting network config: {e}", exc_info=True)
            return None
    
    def set_network_config(self, network_config: Dict) -> bool:
        if not self.sdk or not self._device_id:
            return False
        
        try:
            properties = {}
            
            if "eth" in network_config:
                eth = network_config["eth"]
                if "ip" in eth:
                    properties["eth.ip"] = eth["ip"]
                if "dhcp" in eth:
                    properties["eth.dhcp"] = "true" if eth["dhcp"] else "false"
            
            if "wifi" in network_config:
                wifi = network_config["wifi"]
                if "enabled" in wifi:
                    properties["wifi.enabled"] = "true" if wifi["enabled"] else "false"
                if "mode" in wifi:
                    properties["wifi.mode"] = wifi["mode"]
                if "ssid" in wifi:
                    properties["wifi.ap.ssid"] = wifi["ssid"]
                if "password" in wifi:
                    properties["wifi.ap.passwd"] = wifi["password"]
            
            if properties and self.sdk.device:
                result = self.sdk.device.set_device_property([self._device_id], properties)
                return result.get("message") == "ok"
            
            return False
        except Exception as e:
            logger.error(f"Error setting network config: {e}", exc_info=True)
            return False
    
    def get_wifi_config(self) -> Optional[Dict]:
        network_config = self.get_network_config()
        if network_config and "wifi" in network_config:
            return network_config["wifi"]
        return None
    
    def set_wifi_config(self, wifi_config: Dict) -> bool:
        network_config = {"wifi": wifi_config}
        return self.set_network_config(network_config)
    
    def reboot(self) -> bool:
        if not self.sdk or not self._device_id or not self.sdk.device:
            return False
        
        try:
            result = self.sdk.device.set_device_property([self._device_id], "reboot", "true")
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error rebooting device: {e}", exc_info=True)
            return False

