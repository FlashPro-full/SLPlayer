import ctypes
from ctypes import c_int, c_char_p, c_void_p, POINTER, Structure
from typing import Optional, Dict, Callable
from utils.logger import get_logger

logger = get_logger(__name__)


class HDMIInfo(Structure):
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("refresh_rate", c_int),
        ("is_connected", c_int)
    ]


class HDMIConnection:
    
    def __init__(self):
        self._dll = None
        self._connected = False
        self._device_handle = None
        self._display_mode = "Full Screen Zoom"
        self._init_dll()
    
    def _init_dll(self):
        try:
            self._dll = ctypes.CDLL("hdmi_interface.dll")
            self._setup_function_signatures()
        except OSError:
            logger.warning("HDMI interface DLL not found, using mock implementation")
            self._dll = None
    
    def _setup_function_signatures(self):
        if not self._dll:
            return
        
        self._dll.hdmi_initialize.argtypes = []
        self._dll.hdmi_initialize.restype = c_int
        
        self._dll.hdmi_connect.argtypes = [c_int]
        self._dll.hdmi_connect.restype = c_int
        
        self._dll.hdmi_disconnect.argtypes = []
        self._dll.hdmi_disconnect.restype = c_int
        
        self._dll.hdmi_get_info.argtypes = [POINTER(HDMIInfo)]
        self._dll.hdmi_get_info.restype = c_int
        
        self._dll.hdmi_set_display_mode.argtypes = [c_int]
        self._dll.hdmi_set_display_mode.restype = c_int
        
        self._dll.hdmi_start_capture.argtypes = [c_int, c_int]
        self._dll.hdmi_start_capture.restype = c_int
        
        self._dll.hdmi_stop_capture.argtypes = []
        self._dll.hdmi_stop_capture.restype = c_int
        
        self._dll.hdmi_get_frame.argtypes = [c_void_p, c_int]
        self._dll.hdmi_get_frame.restype = c_int
        
        self._dll.hdmi_cleanup.argtypes = []
        self._dll.hdmi_cleanup.restype = c_int
    
    def initialize(self) -> bool:
        if not self._dll:
            logger.info("HDMI: Mock initialization successful")
            return True
        
        try:
            result = self._dll.hdmi_initialize()
            if result == 0:
                logger.info("HDMI initialized successfully")
                return True
            else:
                logger.error(f"HDMI initialization failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI initialization error: {e}")
            return False
    
    def connect(self, device_index: int = 0) -> bool:
        if not self._dll:
            self._connected = True
            self._device_handle = device_index
            logger.info(f"HDMI: Mock connection to device {device_index}")
            return True
        
        try:
            result = self._dll.hdmi_connect(device_index)
            if result == 0:
                self._connected = True
                self._device_handle = device_index
                logger.info(f"HDMI connected to device {device_index}")
                return True
            else:
                logger.error(f"HDMI connection failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        if not self._dll:
            self._connected = False
            self._device_handle = None
            logger.info("HDMI: Mock disconnection")
            return True
        
        try:
            result = self._dll.hdmi_disconnect()
            if result == 0:
                self._connected = False
                self._device_handle = None
                logger.info("HDMI disconnected")
                return True
            else:
                logger.error(f"HDMI disconnection failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI disconnection error: {e}")
            return False
    
    def get_device_info(self) -> Optional[Dict]:
        if not self._dll:
            return {
                "width": 1920,
                "height": 1080,
                "refresh_rate": 60,
                "is_connected": self._connected
            }
        
        try:
            info = HDMIInfo()
            result = self._dll.hdmi_get_info(ctypes.byref(info))
            if result == 0:
                return {
                    "width": info.width,
                    "height": info.height,
                    "refresh_rate": info.refresh_rate,
                    "is_connected": bool(info.is_connected)
                }
            else:
                logger.error(f"HDMI get info failed with code: {result}")
                return None
        except Exception as e:
            logger.error(f"HDMI get info error: {e}")
            return None
    
    def set_display_mode(self, mode: str) -> bool:
        self._display_mode = mode
        
        if not self._dll:
            logger.info(f"HDMI: Mock display mode set to {mode}")
            return True
        
        try:
            mode_code = 0 if mode == "Full Screen Zoom" else 1
            result = self._dll.hdmi_set_display_mode(mode_code)
            if result == 0:
                logger.info(f"HDMI display mode set to {mode}")
                return True
            else:
                logger.error(f"HDMI set display mode failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI set display mode error: {e}")
            return False
    
    def start_capture(self, width: int, height: int) -> bool:
        if not self._dll:
            logger.info(f"HDMI: Mock capture started at {width}x{height}")
            return True
        
        try:
            result = self._dll.hdmi_start_capture(width, height)
            if result == 0:
                logger.info(f"HDMI capture started at {width}x{height}")
                return True
            else:
                logger.error(f"HDMI start capture failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI start capture error: {e}")
            return False
    
    def stop_capture(self) -> bool:
        if not self._dll:
            logger.info("HDMI: Mock capture stopped")
            return True
        
        try:
            result = self._dll.hdmi_stop_capture()
            if result == 0:
                logger.info("HDMI capture stopped")
                return True
            else:
                logger.error(f"HDMI stop capture failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI stop capture error: {e}")
            return False
    
    def get_frame(self, buffer: bytes, buffer_size: int) -> int:
        if not self._dll:
            return 0
        
        try:
            result = self._dll.hdmi_get_frame(buffer, buffer_size)
            return result
        except Exception as e:
            logger.error(f"HDMI get frame error: {e}")
            return -1
    
    def cleanup(self) -> bool:
        if not self._dll:
            logger.info("HDMI: Mock cleanup")
            return True
        
        try:
            result = self._dll.hdmi_cleanup()
            if result == 0:
                logger.info("HDMI cleaned up")
                return True
            else:
                logger.error(f"HDMI cleanup failed with code: {result}")
                return False
        except Exception as e:
            logger.error(f"HDMI cleanup error: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    @property
    def display_mode(self) -> str:
        return self._display_mode

