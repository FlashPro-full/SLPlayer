from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime
import ctypes
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.huidu_sdk import HuiduSDK
from controllers.property_adapter import adapt_element_for_controller
from utils.logger import get_logger

logger = get_logger(__name__)

class HuiduController(BaseController):
    DEFAULT_PORT = 5000
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT):
        super().__init__(ControllerType.HUIDU, ip_address, port)
        self.sdk = HuiduSDK()
        self._screen_created = False
        self._current_program_id: Optional[int] = None
        self._current_area_id: Optional[int] = None
    
    def connect(self) -> bool:
        if self.status == ConnectionStatus.CONNECTED:
            return True
        self.set_status(ConnectionStatus.CONNECTING)
        try:
            if not self.sdk.is_card_online(self.ip_address):
                logger.warning(f"Huidu controller at {self.ip_address} is not online")
                self.set_status(ConnectionStatus.ERROR)
                return False
            info = self.get_device_info()
            if info:
                self.set_status(ConnectionStatus.CONNECTED)
                logger.info(f"Connected to Huidu controller at {self.ip_address}")
                return True
            else:
                self.set_status(ConnectionStatus.ERROR)
                return False
        except Exception as e:
            logger.error(f"Error connecting to Huidu controller: {e}", exc_info=True)
            self.set_status(ConnectionStatus.ERROR)
            return False
    
    def disconnect(self):
        self._screen_created = False
        self._current_program_id = None
        self._current_area_id = None
        self.set_status(ConnectionStatus.DISCONNECTED)
        self.device_info = None
        logger.info(f"Disconnected from Huidu controller at {self.ip_address}")
    
    def get_device_info(self) -> Optional[Dict]:
        try:
            params = self.sdk.get_screen_params(self.ip_address)
            if params:
                controller_id = f"HD-{self.ip_address.replace('.', '-')}"
                self.device_info = {
                    "name": "Huidu Controller",
                    "model": "Gen6",
                    "version": "2.0.2",
                    "ip": self.ip_address,
                    "controller_id": controller_id,
                    "controllerId": controller_id,
                    "serial_number": controller_id,
                    "width": params.get("width", 64),
                    "height": params.get("height", 32),
                    "color": params.get("color", 1),
                    "gray": params.get("gray", 1),
                    "card_type": params.get("card_type", 0)
                }
                return self.device_info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
        controller_id = f"HD-{self.ip_address.replace('.', '-')}"
        self.device_info = {
            "name": "Huidu Controller",
            "model": "Gen6",
            "version": "2.0.2",
            "ip": self.ip_address,
            "controller_id": controller_id
        }
        return self.device_info
    
    def upload_program(self, program_data: Dict, file_path: str = None) -> bool:
        if self.status != ConnectionStatus.CONNECTED:
            if not self.connect():
                return False
        try:
            self.set_progress(0, "Preparing program...")
            width = program_data.get("width", 64)
            height = program_data.get("height", 32)
            if not self.sdk.create_screen(width, height):
                error = self.sdk.get_last_error()
                logger.error(f"Failed to create screen: error {error}")
                return False
            self._screen_created = True
            self.set_progress(10, "Screen created")
            program_id = self.sdk.add_program()
            if not program_id:
                error = self.sdk.get_last_error()
                logger.error(f"Failed to add program: error {error}")
                return False
            self._current_program_id = program_id
            self.set_progress(20, "Program added")
            elements = program_data.get("elements", [])
            total_elements = len(elements)
            for idx, element in enumerate(elements):
                self.set_progress(20 + int((idx / total_elements) * 60), f"Processing element {idx + 1}/{total_elements}")
                if not self._add_element_to_sdk(element, program_id, width, height):
                    logger.warning(f"Failed to add element: {element.get('type', 'unknown')}")
            self.set_progress(90, "Sending to device...")
            if not self.sdk.send_screen(self.ip_address):
                error = self.sdk.get_last_error()
                logger.error(f"Failed to send screen: error {error}")
                return False
            self.set_progress(100, "Upload complete")
            logger.info(f"Program '{program_data.get('name', 'Unknown')}' uploaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error uploading program: {e}", exc_info=True)
            return False
    
    def _add_element_to_sdk(self, element: Dict, program_id: int, screen_width: int, screen_height: int) -> bool:
        adapted_element = adapt_element_for_controller(element, "huidu")
        element_type = adapted_element.get("type")
        properties = adapted_element.get("properties", {})
        x = adapted_element.get("x", 0)
        y = adapted_element.get("y", 0)
        width = adapted_element.get("width", 200)
        height = adapted_element.get("height", 100)
        area_id = self.sdk.add_area(program_id, x, y, width, height)
        if not area_id:
            return False
        if element_type == "text" or element_type == "singleline_text":
            text = properties.get("text", "")
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#000000")
            color_rgb = self._hex_to_rgb(color_hex)
            item_id = self.sdk.add_text_item(
                area_id, text, font_family, font_size,
                color_rgb, 0, 4, 0, 25, 201, 3
            )
            return item_id is not None
        elif element_type == "animation":
            text = properties.get("text", "")
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#FFFFFF")
            color_rgb = self._hex_to_rgb(color_hex)
            item_id = self.sdk.add_text_item(
                area_id, text, font_family, font_size,
                color_rgb, 0, 4, 0, 25, 201, 3
            )
            return item_id is not None
        elif element_type == "weather":
            text = properties.get("text", "")
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#FFFFFF")
            color_rgb = self._hex_to_rgb(color_hex)
            item_id = self.sdk.add_text_item(
                area_id, text, font_family, font_size,
                color_rgb, 0, 4, 0, 25, 201, 3
            )
            return item_id is not None
        elif element_type == "photo":
            file_path = properties.get("file_path", "")
            if file_path and Path(file_path).exists():
                item_id = self.sdk.add_image_item(area_id, file_path, 0, 30, 201, 3)
                return item_id is not None
        elif element_type == "clock":
            show_date = properties.get("show_date", True)
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 48)
            color_hex = properties.get("color", "#000000")
            color_rgb = self._hex_to_rgb(color_hex)
            item_id = self.sdk.add_time_item(
                area_id, show_date, True, font_family, font_size, color_rgb
            )
            return item_id is not None
        elif element_type == "sensor":
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#FFFFFF")
            color_rgb = self._hex_to_rgb(color_hex)
            sensor_type = properties.get("sensor_type", 0)
            item_id = self.sdk.add_sensor_item(
                area_id, sensor_type, color_rgb, font_family, font_size
            )
            return item_id is not None
        elif element_type == "timing":
            font_family = properties.get("font_family", "Arial")
            font_size = properties.get("font_size", 24)
            color_hex = properties.get("color", "#FFFFFF")
            color_rgb = self._hex_to_rgb(color_hex)
            count_type = properties.get("count_type", 0)
            count_value = properties.get("count_value", 0)
            item_id = self.sdk.add_count_item(
                area_id, count_type, count_value, color_rgb, font_family, font_size
            )
            return item_id is not None
        logger.warning(f"Element type {element_type} not fully supported by Huidu SDK")
        return False
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (0, 0, 0)
    
    def download_program(self, program_id: str = None) -> Optional[Dict]:
        logger.warning("Program download not directly supported by Huidu SDK")
        return None
    
    def get_program_list(self) -> List[Dict]:
        logger.warning("Program list not directly supported by Huidu SDK")
        return []
    
    def get_time(self) -> Optional[datetime]:
        try:
            from datetime import datetime
            return datetime.now()
        except Exception:
            return None
    
    def get_brightness(self) -> Optional[int]:
        try:
            device_info = self.get_device_info()
            if device_info:
                return device_info.get("brightness")
        except Exception:
            pass
        return None
    
    def set_brightness(self, brightness: int) -> bool:
        try:
            if hasattr(self.sdk, 'set_luminance'):
                return self.sdk.set_luminance(self.ip_address, brightness)
            elif hasattr(self.sdk.dll, 'Cmd_SetLuminance'):
                ip_w = ctypes.c_wchar_p(self.ip_address)
                result = self.sdk.dll.Cmd_SetLuminance(0, ip_w, brightness, None)
                return result == 0
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
        return False
    
    def get_power_schedule(self) -> Optional[Dict]:
        logger.warning("Power schedule get not directly supported by Huidu SDK")
        return None
    
    def set_power_schedule(self, on_time: str, off_time: str, enabled: bool = True) -> bool:
        try:
            if hasattr(self.sdk.dll, 'Cmd_TimeSwitch'):
                on_seconds = self._time_str_to_seconds(on_time)
                off_seconds = self._time_str_to_seconds(off_time)
                ip_w = ctypes.c_wchar_p(self.ip_address)
                result = self.sdk.dll.Cmd_TimeSwitch(0, ip_w, 1 if enabled else 0, on_seconds, off_seconds, None)
                return result == 0
        except Exception as e:
            logger.error(f"Error setting power schedule: {e}")
        return False
    
    def _time_str_to_seconds(self, time_str: str) -> int:
        try:
            parts = time_str.split(':')
            if len(parts) >= 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours * 3600 + minutes * 60
        except Exception:
            pass
        return 0
    
    def get_network_config(self) -> Optional[Dict]:
        try:
            device_info = self.get_device_info()
            if device_info:
                return {
                    "ip": device_info.get("ip"),
                    "gateway": device_info.get("gateway"),
                    "subnet": device_info.get("subnet")
                }
        except Exception:
            pass
        return None
    
    def set_network_config(self, network_config: Dict) -> bool:
        try:
            if hasattr(self.sdk.dll, 'Cmd_SetIP'):
                src_ip = ctypes.c_wchar_p(self.ip_address)
                dest_ip = ctypes.c_wchar_p(network_config.get("ip", self.ip_address))
                mask = ctypes.c_wchar_p(network_config.get("subnet", "255.255.255.0"))
                gateway = ctypes.c_wchar_p(network_config.get("gateway", ""))
                result = self.sdk.dll.Cmd_SetIP(src_ip, dest_ip, mask, gateway, None)
                return result == 0
        except Exception as e:
            logger.error(f"Error setting network config: {e}")
        return False
    
    def delete_program(self, program_id: str) -> bool:
        logger.warning("Program deletion not directly supported by Huidu SDK")
        return False
    
    def test_connection(self) -> bool:
        try:
            return self.sdk.is_card_online(self.ip_address)
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False

