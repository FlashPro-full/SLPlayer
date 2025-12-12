import sys
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from datetime import datetime
from controllers.base_controller import BaseController, ControllerType, ConnectionStatus
from controllers.huidu_sdk import HuiduSDK, SDK_PATH
from controllers.network_manager import NetworkManager
from controllers.property_adapter import adapt_element_for_controller
from utils.logger import get_logger

logger = get_logger(__name__)

if SDK_PATH and str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

class HuiduController(BaseController):
    DEFAULT_PORT = 30080
    
    def __init__(self, ip_address: str, port: int = DEFAULT_PORT, sdk_key: str = "", sdk_secret: str = ""):
        super().__init__(ControllerType.HUIDU, ip_address, port)
        from controllers.huidu_sdk import DEFAULT_HOST
        self.sdk = HuiduSDK(DEFAULT_HOST, sdk_key, sdk_secret)
        self.sdk._initialized = False
        self.network_manager = NetworkManager()
        self._screen_created = False
        self._current_program_id: Optional[int] = None
        self._current_area_id: Optional[int] = None
    
    def connect(self) -> bool:
        if self.status == ConnectionStatus.CONNECTED:
            return True
        self.set_status(ConnectionStatus.CONNECTING)
        try:
            from controllers.huidu_sdk import DEFAULT_HOST
            if not self.sdk._initialized:
                self.sdk.initialize(DEFAULT_HOST, self.sdk.sdk_key, self.sdk.sdk_secret)
            
            is_online = self.sdk.is_card_online(self.ip_address)
            if is_online:
                self.set_status(ConnectionStatus.CONNECTED)
                logger.info(f"Connected to Huidu controller at {self.ip_address}")
                return True
            else:
                logger.warning(f"Huidu controller at {self.ip_address} is not online")
                self.set_status(ConnectionStatus.DISCONNECTED)
                return False
        except Exception as e:
            logger.error(f"Error connecting to Huidu controller: {e}", exc_info=True)
            self.set_status(ConnectionStatus.DISCONNECTED)
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
            device_info = {
                "ip": self.ip_address,
                "port": self.port,
                "connection_status": {
                    "sdk_online": self.sdk.is_card_online(self.ip_address)
                }
            }
            
            if not self.sdk.device:
                self.device_info = device_info
                return self.device_info
            
            online_result = self.sdk.device.get_online_devices()
            device_ids = []
            if online_result and online_result.get("message") == "ok":
                online_devices = online_result.get("data", [])
                if online_devices and isinstance(online_devices, list):
                    for device_id in online_devices:
                        if isinstance(device_id, str):
                            device_ids.append(device_id)
            
            if device_ids:
                device_property = self.sdk.get_device_property(device_ids)
                if device_property and device_property.get("message") == "ok":
                    data_array = device_property.get("data", [])
                    if data_array and isinstance(data_array, list):
                        for item in data_array:
                            if isinstance(item, dict) and item.get("message") == "ok":
                                item_data = item.get("data", {})
                                if isinstance(item_data, dict):
                                    device_info.update(item_data)
                                    break
                        
                        required_properties = ["name", "version.app", "version.hardware", "luminance", "eth.ip", "screen.width", "screen.height"]
                        missing_properties = [prop for prop in required_properties if prop not in device_info]
                        
                        if missing_properties:
                            missing_result = self.sdk.get_device_property(device_ids, missing_properties)
                            if missing_result and missing_result.get("message") == "ok":
                                missing_data_array = missing_result.get("data", [])
                                if missing_data_array and isinstance(missing_data_array, list):
                                    for missing_item in missing_data_array:
                                        if isinstance(missing_item, dict) and missing_item.get("message") == "ok":
                                            missing_item_data = missing_item.get("data", {})
                                            if isinstance(missing_item_data, dict):
                                                device_info.update(missing_item_data)
                                                break
            
            self.device_info = device_info
            return self.device_info
        except Exception as e:
            logger.error(f"Error getting device info: {e}", exc_info=True)
            self.device_info = {
                "ip": self.ip_address,
                "port": self.port
            }
            return self.device_info
    
    def upload_program(self, program_data: Dict, file_path: Optional[str] = None) -> bool:
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
            
            play_control_data = program_data.get("play_control", {})
            if play_control_data:
                try:
                    from controllers.property_adapter import convert_play_control_to_sdk
                    sdk_play_control = convert_play_control_to_sdk(play_control_data, "huidu")
                    if sdk_play_control:
                        self.set_progress(15, "Setting program schedule...")
                        play_control_params = {
                            "program_id": program_id,
                            "play_control": sdk_play_control
                        }
                        if hasattr(self.sdk, 'set_program_play_control'):
                            self.sdk.set_program_play_control(play_control_params)
                        else:
                            logger.debug("play_control conversion ready but SDK method not available")
                except Exception as e:
                    logger.debug(f"Could not set play_control on program: {e}")
            
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
    
    def download_program(self, program_id: Optional[str] = None) -> Optional[Dict]:
        logger.warning("Program download not directly supported by Huidu SDK")
        return None
    
    def get_program_list(self) -> List[Dict]:
        logger.warning("Program list not directly supported by Huidu SDK")
        return []
    
    def get_time(self) -> Optional[datetime]:
        try:
            from datetime import datetime
            if not self.device_info:
                self.get_device_info()
            
            if self.device_info and 'time' in self.device_info:
                time_str = self.device_info.get('time')
                if time_str:
                    return datetime.fromisoformat(time_str) if isinstance(time_str, str) else time_str
            return datetime.now()
        except Exception:
            return None
    
    def set_time(self, time: datetime) -> bool:
        try:
            from datetime import datetime
            if not isinstance(time, datetime):
                return False
            
            result = self.sdk.set_device_property({
                "time": time.isoformat(),
                "date": time.strftime('%Y-%m-%d'),
                "timezone": "UTC"
            })
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error setting time: {e}")
            return False
    
    def get_brightness(self) -> Optional[int]:
        try:
            if self.device_info and "luminance" in self.device_info:
                try:
                    return int(self.device_info["luminance"])
                except:
                    pass
            
            if not self.device_info:
                self.get_device_info()
            
            if self.device_info and "luminance" in self.device_info:
                try:
                    return int(self.device_info["luminance"])
                except:
                    pass
        except Exception:
            pass
        return None
    
    def set_brightness(self, brightness: int, brightness_settings: Optional[Dict] = None) -> bool:
        try:
            if brightness_settings and brightness_settings.get("time_ranges"):
                time_ranges = brightness_settings.get("time_ranges", [])
                for time_range in time_ranges:
                    pass
            
            if brightness_settings and brightness_settings.get("sensor", {}).get("enabled"):
                pass
            
            result = self.sdk.set_luminance(brightness)
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
        return False
    
    def get_power_schedule(self) -> Optional[Dict]:
        try:
            if not self.device_info:
                self.get_device_info()
            
            if self.device_info and 'power_schedule' in self.device_info:
                return self.device_info.get('power_schedule')
            
            result = self.sdk.get_device_status()
            if result and result.get("message") == "ok":
                data = result.get("data", [])
                if data and len(data) > 0:
                    schedule_data = data[0].get("power_schedule") or data[0].get("schedule")
                    if schedule_data:
                        return schedule_data
            
            return None
        except Exception as e:
            logger.debug(f"Error getting power schedule: {e}")
            return None
    
    def set_power_schedule(self, schedule: Dict) -> bool:
        try:
            from sdk.data.task.ScheduledTaskInfo import ScheduledTaskInfo # type: ignore
            
            screen_tasks = []
            
            if isinstance(schedule, list):
                for day_schedule in schedule:
                    if not day_schedule.get("enabled", True):
                        continue
                    
                    on_time = day_schedule.get("on_time", "08:00")
                    off_time = day_schedule.get("off_time", "22:00")
                    day = day_schedule.get("day", "").lower()
                    
                    on_hour, on_min = map(int, on_time.split(':'))
                    off_hour, off_min = map(int, off_time.split(':'))
                    
                    on_time_str = f"{on_hour:02d}:{on_min:02d}:00"
                    off_time_str = f"{off_hour:02d}:{off_min:02d}:00"
                    
                    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    day_map = {
                        "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
                        "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"
                    }
                    
                    if day:
                        week_filter = day_map.get(day, day.capitalize()[:3])
                    else:
                        week_filter = ",".join(week_days)
                    
                    screen_tasks.append(ScheduledTaskInfo(
                        data="true",
                        time_range=f"{on_time_str}~{off_time_str}",
                        week_filter=week_filter,
                        month_filter="Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"
                    ))
                    screen_tasks.append(ScheduledTaskInfo(
                        data="false",
                        time_range=f"{off_time_str}~{on_time_str}",
                        week_filter=week_filter,
                        month_filter="Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"
                    ))
            elif isinstance(schedule, dict):
                if "on_time" in schedule and "off_time" in schedule:
                    on_time = schedule.get("on_time", "08:00")
                    off_time = schedule.get("off_time", "22:00")
                    enabled = schedule.get("enabled", True)
                    
                    if enabled:
                        on_hour, on_min = map(int, on_time.split(':'))
                        off_hour, off_min = map(int, off_time.split(':'))
                        
                        on_time_str = f"{on_hour:02d}:{on_min:02d}:00"
                        off_time_str = f"{off_hour:02d}:{off_min:02d}:00"
                        
                        screen_tasks.append(ScheduledTaskInfo(
                            data="true",
                            time_range=f"{on_time_str}~{off_time_str}",
                            week_filter="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
                            month_filter="Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"
                        ))
                        screen_tasks.append(ScheduledTaskInfo(
                            data="false",
                            time_range=f"{off_time_str}~{on_time_str}",
                            week_filter="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
                            month_filter="Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"
                        ))
            
            if screen_tasks:
                tasks = {"screen": screen_tasks}
                result = self.sdk.set_time_switch(tasks)
                return result.get("message") == "ok"
            
            return False
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
        if not self.device_info:
            self.get_device_info()
        return self.device_info
    
    def set_network_config(self, network_config: Dict) -> bool:
        try:
            huidu_config = {}
            if "ip" in network_config or "ip_address" in network_config:
                huidu_config["ip"] = network_config.get("ip") or network_config.get("ip_address")
            if "subnet" in network_config or "subnet_mask" in network_config or "netmask" in network_config:
                huidu_config["netmask"] = network_config.get("subnet") or network_config.get("subnet_mask") or network_config.get("netmask")
            if "gateway" in network_config:
                huidu_config["gateway"] = network_config.get("gateway")
            if "dhcp" in network_config:
                huidu_config["dhcp"] = "true" if network_config.get("dhcp") else "false"
            
            result = self.sdk.set_ip(huidu_config)
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error setting network config: {e}")
            return False
    
    def get_wifi_config(self) -> Optional[Dict]:
        if not self.device_info:
            self.get_device_info()
        return self.device_info
    
    def set_wifi_config(self, wifi_config: Dict) -> bool:
        try:
            result = self.sdk.set_device_property({
                "wifi.enabled": "true" if wifi_config.get("enabled", False) else "false",
                "wifi.ssid": wifi_config.get("ssid", ""),
                "wifi.password": wifi_config.get("password", "")
            })
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error setting wifi config: {e}")
            return False
    
    def reboot(self) -> bool:
        try:
            result = self.sdk.set_device_property({"reboot": "true"})
            return result.get("message") == "ok"
        except Exception as e:
            logger.error(f"Error rebooting controller: {e}")
            return False
    
    def delete_program(self, program_id: str) -> bool:
        logger.warning("Program deletion not directly supported by Huidu SDK")
        return False
    
    def test_connection(self) -> bool:
        try:
            ping_success = True
            if self.ip_address != "127.0.0.1":
                ping_success = self.network_manager.ping_host(self.ip_address)
            if not ping_success:
                logger.warning(f"Ping test failed for {self.ip_address}")
                return False
            
            port_success = True
            if self.port and self.port > 0:
                port_success = self.network_manager.test_port_connection(
                    self.ip_address, self.port, timeout=3.0
                )
                if not port_success:
                    logger.warning(f"Port {self.port} test failed for {self.ip_address}")
            
            sdk_success = self.sdk.is_card_online(self.ip_address)
            if not sdk_success:
                logger.warning(f"SDK is_card_online check failed for {self.ip_address}")
            
            overall_success = ping_success and (port_success or sdk_success)
            
            if overall_success:
                logger.info(f"Connection test successful for {self.ip_address}")
            else:
                logger.warning(f"Connection test failed for {self.ip_address}")
            
            return overall_success
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return False
    
    def test_connection_detailed(self) -> Dict[str, bool]:
        results = {
            'ping': False,
            'port': False,
            'sdk': False,
            'overall': False
        }
        
        try:
            results['ping'] = self.network_manager.ping_host(self.ip_address)
            
            if self.port and self.port > 0:
                results['port'] = self.network_manager.test_port_connection(
                    self.ip_address, self.port, timeout=3.0
                )
            else:
                results['port'] = True
            
            results['sdk'] = self.sdk.is_card_online(self.ip_address)
            results['overall'] = results['ping'] and (results['port'] or results['sdk'])
            
        except Exception as e:
            logger.error(f"Error in detailed connection test: {e}")
        
        return results
    
    @staticmethod
    def find_controller_ip() -> Optional[str]:
        network_manager = NetworkManager()
        return network_manager.find_controller_ip(controller_type="huidu")

