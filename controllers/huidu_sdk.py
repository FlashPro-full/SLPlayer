import sys
import os
import subprocess
import socket
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from utils.logger import get_logger

logger = get_logger(__name__)

_api_server_process = None

def _get_sdk_path():
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent
    
    possible_paths = [
        base_path / "publish",
        base_path / "_internal" / "publish",
    ]
    
    for sdk_path in possible_paths:
        if sdk_path.exists():
            if (sdk_path / "sdk").exists():
                return sdk_path
            elif (sdk_path / "huidu_sdk").exists() and (sdk_path / "huidu_sdk" / "sdk").exists():
                return sdk_path / "huidu_sdk"
    
    return None

SDK_PATH = _get_sdk_path()
if SDK_PATH:
    sdk_path_str = str(SDK_PATH)
    if sdk_path_str not in sys.path:
        sys.path.insert(0, sdk_path_str)
        logger.debug(f"Huidu SDK path added to sys.path: {sdk_path_str}")
else:
    logger.warning("Huidu SDK path not found. SDK may not be available.")

try:
    from sdk.common.Config import Config  # type: ignore
    from sdk.Device import Device as SDKDevice  # type: ignore
    from sdk.Program import Program as SDKProgram  # type: ignore
    from sdk.File import File as SDKFile # type: ignore
    from sdk.data.ProgramNode import ProgramNode # type: ignore
    from sdk.data.area.AreaNode import AreaNode # type: ignore
    from sdk.data.area.TextNode import TextNode # type: ignore
    from sdk.data.area.ImageNode import ImageNode # type: ignore
    from sdk.data.area.VideoNode import VideoNode # type: ignore
    from sdk.data.area.DigitalClockNode import DigitalClockNode # type: ignore
    from sdk.data.area.DialClockNode import DialClockNode # type: ignore
    from sdk.data.area.DynamicNode import DynamicNode # type: ignore
    from sdk.data.other.Effect import Effect # type: ignore
    from sdk.data.other.Font import Font # type: ignore
    from sdk.data.other.Border import Border # type: ignore
    from sdk.data.other.PlayControl import PlayControl # type: ignore
    from sdk.deviceTask.ScheduledTask import ScheduledTask # type: ignore
    from sdk.deviceTask.PeriodicTask import PeriodicTask # type: ignore
    from sdk.deviceTask.PushStatusTask import PushStatusTask # type: ignore
    SDK_AVAILABLE = True
    if SDK_PATH:
        logger.debug(f"Huidu SDK imported successfully from {SDK_PATH}")
    else:
        logger.warning("Huidu SDK imported but SDK_PATH was not found (may be using system-installed SDK)")
except ImportError as e:
    if SDK_PATH:
        logger.error(f"Failed to import Huidu SDK from {SDK_PATH}: {e}")
    else:
        logger.error(f"Failed to import Huidu SDK (SDK path not found): {e}")
    SDK_AVAILABLE = False
    Config = None
    SDKDevice = None
    SDKProgram = None
    SDKFile = None
except Exception as e:
    logger.error(f"Unexpected error importing Huidu SDK: {e}", exc_info=True)
    SDK_AVAILABLE = False
    Config = None
    SDKDevice = None
    SDKProgram = None
    SDKFile = None

DEFAULT_SDK_KEY = "a718fbe8aaa8aeef"
DEFAULT_SDK_SECRET = "8fd529ef3f88986d40e6ef8d4d7f2d0c"
DEFAULT_HOST = "http://127.0.0.1:30080"

def validate_device_id(device_id: str) -> bool:
    if not device_id or not isinstance(device_id, str):
        return False
    parts = device_id.split('-')
    if len(parts) >= 2:
        return 'D' in parts[1].upper()
    return 'D' in device_id.upper() and '-' in device_id

def _get_api_server_path() -> Optional[Path]:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent
    
    possible_paths = [
        base_path / "publish" / "huidu_sdk" / "cn.huidu.device.api.exe",
        base_path / "_internal" / "publish" / "huidu_sdk" / "cn.huidu.device.api.exe",
    ]
    
    for exe_path in possible_paths:
        if exe_path.exists():
            return exe_path
    
    return None

def _is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _start_api_server() -> bool:
    global _api_server_process
    
    if _api_server_process is not None:
        if _api_server_process.poll() is None:
            logger.debug("API server is already running")
            return True
    
    exe_path = _get_api_server_path()
    if not exe_path:
        logger.warning("API server executable not found")
        return False
    
    try:
        _api_server_process = subprocess.Popen(
            [str(exe_path)],
            cwd=str(exe_path.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        logger.info(f"Started API server: {exe_path.name}")
        
        max_retries = 10
        for i in range(max_retries):
            if _is_port_open("127.0.0.1", 30080, timeout=0.5):
                logger.info("API server is ready on 127.0.0.1:30080")
                return True
            time.sleep(0.5)
        
        logger.warning("API server started but port 30080 not responding")
        return False
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        _api_server_process = None
        return False

def _stop_api_server() -> bool:
    global _api_server_process
    
    try:
        if _api_server_process is not None:
            try:
                if _api_server_process.poll() is None:
                    logger.info("Stopping tracked API server...")
                    _api_server_process.terminate()
                    
                    try:
                        _api_server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning("API server did not terminate, forcing kill...")
                        _api_server_process.kill()
                        _api_server_process.wait()
            except Exception as e:
                logger.warning(f"Error stopping tracked API server: {e}")
            
            _api_server_process = None
        
        logger.info("Stopping all cn.huidu.device.api.exe processes...")
        if os.name == 'nt':
            try:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', 'cn.huidu.device.api.exe'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info("All API server processes stopped")
                elif "not found" in result.stdout.lower() or "not found" in result.stderr.lower():
                    logger.debug("No API server processes found")
                else:
                    logger.warning(f"Error stopping API server processes: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning("Timeout stopping API server processes")
            except Exception as e:
                logger.error(f"Error stopping API server processes: {e}")
        else:
            try:
                result = subprocess.run(
                    ['pkill', '-f', 'cn.huidu.device.api'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info("All API server processes stopped")
                else:
                    logger.debug("No API server processes found")
            except Exception as e:
                logger.error(f"Error stopping API server processes: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error in _stop_api_server: {e}")
        return False

class HuiduSDK:
    DEFAULT_PORT = 30080
    
    def __init__(self, host: Optional[str] = None, sdk_key: str = DEFAULT_SDK_KEY, sdk_secret: str = DEFAULT_SDK_SECRET):
        if not SDK_AVAILABLE:
            raise RuntimeError("Huidu SDK is not available. Check SDK installation.")
        
        if not host:
            host = DEFAULT_HOST
        
        self.host = host
        self.sdk_key = sdk_key or DEFAULT_SDK_KEY
        self.sdk_secret = sdk_secret or DEFAULT_SDK_SECRET
        self.device: Optional[SDKDevice] = None
        self.program: Optional[SDKProgram] = None
        self.file: Optional[SDKFile] = None
        self._initialized = False
    
    def initialize(self, host: str, sdk_key: str = DEFAULT_SDK_KEY, sdk_secret: str = DEFAULT_SDK_SECRET):
        try:
            if not host.startswith("http://") and not host.startswith("https://"):
                host = f"http://{host}"
            
            if not host.endswith("/"):
                host = host.rstrip("/")
            
            if "127.0.0.1" in host:
                _start_api_server()
            
            Config.init_sdk(host, sdk_key, sdk_secret)
            self.host = Config.host
            self.sdk_key = sdk_key
            self.sdk_secret = sdk_secret
            self.device = SDKDevice(host)
            self.program = SDKProgram(host)
            self.file = SDKFile(host)
            self._initialized = True
            logger.info(f"HuiduSDK initialized with host: {self.host}")
        except Exception as e:
            logger.error(f"Failed to initialize HuiduSDK: {e}")
            raise
    
    def get_last_error(self) -> int:
        return 0
    
    def is_card_online(self, ip_address: str, send_type: int = 0) -> bool:
        if not ip_address or not isinstance(ip_address, str):
            return False
        
        ip_clean = ip_address.split(':')[0].strip()
        
        if ip_clean == "127.0.0.1":
            return True
        
        try:
            ip_parts = ip_clean.split('.')
            if len(ip_parts) != 4 or not all(0 <= int(p) <= 255 for p in ip_parts):
                logger.debug(f"Invalid IP address format: {ip_address}")
                return False
        except (ValueError, AttributeError):
            logger.debug(f"Invalid IP address format: {ip_address}")
            return False
        
        if not self._initialized:
            try:
                self.initialize(DEFAULT_HOST, self.sdk_key, self.sdk_secret)
            except Exception as e:
                logger.debug(f"SDK initialization failed: {e}")
                return False
        
        if not self.device:
            return False
        
        try:
            result = self.device.get_online_devices()
            if result.get("message") == "ok":
                devices = result.get("data", [])
                if isinstance(devices, list):
                    for device_id in devices:
                        if isinstance(device_id, str) and ip_clean in device_id:
                            return True
                        if isinstance(device_id, dict):
                            device_ip = device_id.get("ip") or device_id.get("ip_address") or device_id.get("host")
                            if device_ip == ip_clean:
                                return True
                    return len(devices) > 0
            return False
        except Exception as e:
            logger.error(f"Error checking if card is online: {e}")
            return False
    
    def create_screen(self, width: int, height: int, color: int = 1, gray: int = 1, card_type: int = 0) -> bool:
        return True
    
    def add_program(self, border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        return 1
    
    def add_area(self, program_id: int, x: int, y: int, width: int, height: int,
                 border_img_path: Optional[str] = None, border_effect: int = 0, border_speed: int = 5) -> Optional[int]:
        return 1
    
    def add_text_item(self, area_id: int, text: str, font_name: str = "Arial", font_size: int = 24,
                     text_color: Tuple[int, int, int] = (255, 255, 255), bg_color: int = 0,
                     style: int = 4, show_effect: int = 0, show_speed: int = 25,
                     clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        return 1
    
    def add_image_item(self, area_id: int, image_path: str, show_effect: int = 0,
                      show_speed: int = 30, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        return 1
    
    def add_time_item(self, area_id: int, show_date: bool = True, show_time: bool = True,
                     font_name: str = "Arial", font_size: int = 16,
                     text_color: Tuple[int, int, int] = (0, 255, 0),
                     date_style: int = 0, time_style: int = 0, diff_hour: int = 0, diff_min: int = 0) -> Optional[int]:
        return 1
    
    def add_sensor_item(self, area_id: int, sensor_type: int = 0, text_color: Tuple[int, int, int] = (255, 255, 255),
                       font_name: str = "Arial", font_size: int = 16, show_effect: int = 0,
                       show_speed: int = 25, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        return 1
    
    def add_count_item(self, area_id: int, count_type: int = 0, count_value: int = 0,
                      text_color: Tuple[int, int, int] = (255, 255, 255),
                      font_name: str = "Arial", font_size: int = 16, show_effect: int = 0,
                      show_speed: int = 25, clear_type: int = 201, stay_time: int = 3) -> Optional[int]:
        return 1
    
    def get_color(self, r: int, g: int, b: int) -> int:
        return (r << 16) | (g << 8) | b
    
    def send_screen(self, ip_address: str, send_type: int = 0) -> bool:
        return True
    
    def set_program_param(self, program_id: int, play_mode: int = 0, play_length: int = 0,
                         week_flags: int = 0, start_date: int = 0, end_date: int = 0,
                         start_time: int = 0, end_time: int = 0) -> bool:
        return True
    
    def save_screen(self, file_path: str) -> bool:
        return True
    
    def create_program(self, program_node: ProgramNode, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.append(device_ids, program_node)
        except Exception as e:
            logger.error(f"Error creating program: {e}")
            return {"message": "error", "data": str(e)}
    
    def update_program(self, program_node: ProgramNode, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.update(device_ids, program_node)
        except Exception as e:
            logger.error(f"Error updating program: {e}")
            return {"message": "error", "data": str(e)}
    
    def replace_program(self, program_node: ProgramNode, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.replace(device_ids, program_node)
        except Exception as e:
            logger.error(f"Error replacing program: {e}")
            return {"message": "error", "data": str(e)}
    
    def remove_program(self, program_id: str, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.remove(device_ids, [program_id])
        except Exception as e:
            logger.error(f"Error removing program: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_programs(self, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.get_program_ids(device_ids)
        except Exception as e:
            logger.error(f"Error getting programs: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_device_property(self, device_ids: Optional[List[str]] = None, properties: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            property_list = properties if properties else []
            logger.info(f"getDeviceProperty request - device_ids: {device_ids}, properties: {property_list}")
            result = self.device.get_device_property(device_ids, property_list)
            import json
            logger.info(f"getDeviceProperty raw response: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            logger.error(f"Error getting device property: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_device_property(self, properties: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.device.set_device_property(device_ids, properties)
        except Exception as e:
            logger.error(f"Error setting device property: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_device_status(self, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.device.get_device_status(device_ids)
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {"message": "error", "data": str(e)}
    
    def upload_file(self, file_path: str) -> Dict:
        if not self._initialized or not self.file:
            return {"message": "error", "data": "SDK not initialized"}
        
        try:
            return self.file.upload_file(file_path)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_luminance(self, brightness: int, device_ids: Optional[List[str]] = None) -> Dict:
        return self.set_device_property({"luminance": str(brightness)}, device_ids)
    
    def get_scheduled_task(self, task_keys: Optional[List[str]] = None, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            scheduled_task = ScheduledTask(self.host)
            return scheduled_task.get_scheduled_task(device_ids, task_keys)
        except Exception as e:
            logger.error(f"Error getting scheduled task: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_scheduled_task(self, tasks: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            from sdk.data.task.ScheduledTaskInfo import ScheduledTaskInfo  # type: ignore
            task_infos: Dict[str, List] = {}
            for task_key, task_list in tasks.items():
                task_infos[task_key] = []
                for task in task_list:
                    if isinstance(task, dict):
                        task_info = ScheduledTaskInfo.from_dict(task)
                        task_infos[task_key].append(task_info)
                    elif isinstance(task, ScheduledTaskInfo):
                        task_infos[task_key].append(task)
            
            scheduled_task = ScheduledTask(self.host)
            return scheduled_task.set_scheduled_task(device_ids, task_infos)
        except Exception as e:
            logger.error(f"Error setting scheduled task: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_periodic_task(self, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            periodic_task = PeriodicTask(self.host)
            return periodic_task.get_periodic_task(device_ids)
        except Exception as e:
            logger.error(f"Error getting periodic task: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_periodic_task(self, tasks: List[Dict], device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            from sdk.data.task.PeriodicTaskInfo import PeriodicTaskInfo  # type: ignore
            task_infos = []
            for task in tasks:
                if isinstance(task, dict):
                    task_info = PeriodicTaskInfo.from_dict(task)
                    task_infos.append(task_info)
                elif isinstance(task, PeriodicTaskInfo):
                    task_infos.append(task)
            
            periodic_task = PeriodicTask(self.host)
            return periodic_task.set_periodic_task(device_ids, task_infos)
        except Exception as e:
            logger.error(f"Error setting periodic task: {e}")
            return {"message": "error", "data": str(e)}
    
    def push_status(self, status_data: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            push_task = PushStatusTask(self.host)
            return push_task.push_status(device_ids, status_data)
        except Exception as e:
            logger.error(f"Error pushing status: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_time_switch(self, tasks: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        return self.set_scheduled_task(tasks, device_ids)
        if not self._initialized:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            device_ids = []
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            scheduled_task = ScheduledTask(self.host)
            return scheduled_task.set_scheduled_task(device_ids, tasks)
        except Exception as e:
            logger.error(f"Error setting time switch: {e}")
            return {"message": "error", "data": str(e)}
    
    def set_ip(self, ip_config: Dict, device_ids: Optional[List[str]] = None) -> Dict:
        properties = {}
        if "ip" in ip_config:
            properties["eth.ip"] = ip_config["ip"]
        if "gateway" in ip_config:
            properties["eth.gateway"] = ip_config["gateway"]
        if "subnet" in ip_config:
            properties["eth.netmask"] = ip_config["subnet"]
        if "dhcp" in ip_config:
            properties["eth.dhcp"] = "true" if ip_config["dhcp"] else "false"
        
        return self.set_device_property(properties, device_ids)
    
    def reboot_device(self, delay: int = 5, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            method_body = {
                "method": "rebootDevice",
                "id": ",".join(device_ids),
                "data": {"delay": delay}
            }
            import json
            body_str = json.dumps(method_body)
            response_str = self.device.device(body_str)
            response = json.loads(response_str) if isinstance(response_str, str) else response_str
            return response
        except Exception as e:
            logger.error(f"Error rebooting device: {e}")
            return {"message": "error", "data": str(e)}
    
    def open_device_screen(self, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.device.device(device_ids, "openDeviceScreen", {})
        except Exception as e:
            logger.error(f"Error opening device screen: {e}")
            return {"message": "error", "data": str(e)}
    
    def close_device_screen(self, device_ids: Optional[List[str]] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            if not self.device:
                return {"message": "error", "data": "SDK not initialized"}
            result = self.device.get_online_devices()
            if result and result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.device.device(device_ids, "closeDeviceScreen", {})
        except Exception as e:
            logger.error(f"Error closing device screen: {e}")
            return {"message": "error", "data": str(e)}
