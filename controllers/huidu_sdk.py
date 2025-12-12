import sys
import os
import subprocess
import socket
import time
from pathlib import Path
from typing import Optional, Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)

_api_server_process = None

DEFAULT_SDK_KEY = "a718fbe8aaa8aeef"
DEFAULT_SDK_SECRET = "8fd529ef3f88986d40e6ef8d4d7f2d0c"
DEFAULT_HOST = "http://127.0.0.1:30080"

def _get_sdk_path():
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent
    
    possible_paths = [
        base_path / "publish" / "huidu_sdk",
        base_path / "_internal" / "publish" / "huidu_sdk",
    ]
    
    for sdk_path in possible_paths:
        if sdk_path.exists():
            if (sdk_path / "sdk").exists():
                return sdk_path
    
    return None

def _get_api_server_path() -> Optional[Path]:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent
    
    possible_paths = [
        Path(__file__).parent.parent / "publish" / "huidu_sdk" / "cn.huidu.device.api.exe",
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        logger.info(f"Started Huidu API server: {exe_path}")
        
        max_retries = 10
        for i in range(max_retries):
            if _is_port_open("127.0.0.1", 30080, timeout=0.5):
                logger.info("API server is ready on 127.0.0.1:30080")
                return True
            time.sleep(0.5)
        
        logger.warning("API server started but port 30080 is not ready after waiting")
        return True
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        return False

def _stop_api_server() -> bool:
    global _api_server_process
    
    if _api_server_process is not None:
        try:
            if _api_server_process.poll() is None:
                logger.info("Stopping tracked API server process...")
                _api_server_process.terminate()
                try:
                    _api_server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Tracked API server did not terminate, forcing kill...")
                    _api_server_process.kill()
                    _api_server_process.wait()
                logger.info("Tracked API server process stopped.")
        except Exception as e:
            logger.error(f"Error stopping tracked API server process: {e}")
        finally:
            _api_server_process = None
    
    api_server_exe_name = "cn.huidu.device.api.exe"
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", api_server_exe_name], check=False, capture_output=True)
            logger.info(f"Attempted to kill all '{api_server_exe_name}' processes on Windows.")
        else:
            subprocess.run(["pkill", "-f", api_server_exe_name], check=False, capture_output=True)
            logger.info(f"Attempted to kill all '{api_server_exe_name}' processes on non-Windows.")
        return True
    except Exception as e:
        logger.error(f"Error ensuring all API server processes are stopped: {e}")
        return False

SDK_PATH = _get_sdk_path()
SDK_AVAILABLE = SDK_PATH is not None

if SDK_PATH:
    sdk_path_str = str(SDK_PATH)
    if sdk_path_str not in sys.path:
        sys.path.insert(0, sdk_path_str)
        logger.debug(f"Huidu SDK path added to sys.path: {sdk_path_str}")
else:
    logger.warning("Huidu SDK path not found. SDK may not be available.")

try:
    from sdk.common.Config import Config
    from sdk.Device import Device as SDKDevice
    from sdk.Program import Program as SDKProgram
    from sdk.File import File as SDKFile
    from sdk.data.ProgramNode import ProgramNode
    from sdk.data.area.AreaNode import AreaNode
    from sdk.data.area.TextNode import TextNode
    from sdk.data.area.ImageNode import ImageNode
    from sdk.data.area.VideoNode import VideoNode
    from sdk.data.area.DigitalClockNode import DigitalClockNode
    from sdk.data.area.DialClockNode import DialClockNode
    from sdk.data.area.DynamicNode import DynamicNode
    from sdk.data.other.Effect import Effect
    from sdk.data.other.Font import Font
    from sdk.data.other.PlayControl import PlayControl
except ImportError as e:
    SDK_AVAILABLE = False
    logger.warning(f"Huidu SDK imports failed: {e}")

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
        
        if host:
            self.initialize(host, self.sdk_key, self.sdk_secret)
    
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
            
            self.device = SDKDevice()
            self.program = SDKProgram()
            self.file = SDKFile()
            
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
        
        if ip_clean in ("127.0.0.1", "localhost"):
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
            return False
        
        try:
            result = self.device.get_online_devices()
            if result.get("message") == "ok":
                devices = result.get("data", [])
                for device_id in devices:
                    if isinstance(device_id, str) and ip_clean in device_id:
                        return True
                    if isinstance(device_id, dict) and (device_id.get("ip") == ip_clean or device_id.get("ip_address") == ip_clean):
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking if card is online: {e}")
            return False
    
    def get_screen_params(self, ip_address: str = None, send_type: int = 0) -> Optional[Dict]:
        if not self._initialized or not self.device:
            return None
        
        try:
            device_ids = []
            if ip_address:
                ip_clean = ip_address.split(':')[0].strip()
                
                is_valid_ip = False
                try:
                    ip_parts = ip_clean.split('.')
                    if len(ip_parts) == 4 and all(0 <= int(p) <= 255 for p in ip_parts):
                        is_valid_ip = True
                except (ValueError, AttributeError):
                    pass
                
                if ip_clean in ("localhost", "127.0.0.1"):
                    is_valid_ip = True
                
                if not is_valid_ip:
                    return None
                
                result = self.device.get_online_devices()
                if result.get("message") == "ok":
                    devices = result.get("data", [])
                    for device_id in devices:
                        if isinstance(device_id, str) and ip_clean in device_id:
                            device_ids = [device_id]
                            break
                        if isinstance(device_id, dict) and (device_id.get("ip") == ip_clean or device_id.get("ip_address") == ip_clean):
                            device_ids = [device_id.get("id", device_id.get("controller_id", ""))]
                            break
            
            if not device_ids:
                return None
            
            result = self.device.get_device_property(device_ids)
            if result.get("message") == "ok":
                data_array = result.get("data", [])
                if data_array and len(data_array) > 0:
                    device_data = data_array[0].get("data", {})
                    return {
                        "width": int(device_data.get("screen.width", 64)),
                        "height": int(device_data.get("screen.height", 32)),
                        "color": 1,
                        "gray": 1,
                        "card_type": 0
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting screen params: {e}")
            return None
    
    def get_device_property(self, device_ids: List[str] = None) -> Dict:
        if not self._initialized or not self.device:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            result = self.device.get_online_devices()
            if result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.device.get_device_property(device_ids, None)
        except Exception as e:
            logger.error(f"Error getting device property: {e}")
            return {"message": "error", "data": str(e)}
    
    def get_programs(self, device_ids: List[str] = None) -> Dict:
        if not self._initialized or not self.program:
            return {"message": "error", "data": "SDK not initialized"}
        
        if not device_ids:
            device_ids = []
            result = self.device.get_online_devices()
            if result.get("message") == "ok":
                devices = result.get("data", [])
                device_ids = [d for d in devices if isinstance(d, str)]
        
        if not device_ids:
            return {"message": "error", "data": "No device IDs available"}
        
        try:
            return self.program.get_program_ids(device_ids)
        except Exception as e:
            logger.error(f"Error getting programs: {e}")
            return {"message": "error", "data": str(e)}

